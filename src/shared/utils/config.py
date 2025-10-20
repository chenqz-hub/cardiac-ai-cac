"""
Configuration Manager - 共享版本
通用配置管理模块，支持多工具、多环境

提升自: tools/nb10_windows/core/config_manager.py
扩展: 多工具支持、环境变量、配置验证、配置继承
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, List
import yaml
import logging

logger = logging.getLogger(__name__)

__version__ = "2.0.0"


class ConfigManager:
    """
    通用配置管理器（共享版本）

    Features:
    - Load YAML configuration files
    - Validate required fields
    - Normalize paths (Windows/Linux/Colab compatible)
    - Support environment variables
    - Merge with default configuration
    - Support configuration inheritance
    - Multi-tool configuration support
    """

    # 基础默认配置（所有工具共享）
    BASE_DEFAULT_CONFIG = {
        'paths': {
            'data_dir': './data/dicom_original',
            'output_dir': './output',
            'cache_dir': './data/cache',
            'log_dir': './logs'
        },
        'processing': {
            'mode': 'pilot',
            'pilot_limit': 10,
            'device': 'auto',  # auto/cuda/cpu
            'batch_size': 1,
            'enable_resume': True,
        },
        'performance': {
            'gpu_memory_fraction': 0.9,
            'clear_cache_interval': 5,
            'num_workers': 0,
            'pin_memory': True
        },
        'output': {
            'csv_encoding': 'utf-8-sig',
            'save_cache': True,
            'generate_report': True,
        },
        'logging': {
            'level': 'INFO',
            'log_to_file': True,
            'log_to_console': True,
            'max_file_size': 10,  # MB
            'backup_count': 3
        }
    }

    def __init__(
        self,
        config_path: Optional[str] = None,
        base_dir: Optional[str] = None,
        tool_name: Optional[str] = None,
        tool_defaults: Optional[Dict] = None
    ):
        """
        Initialize configuration manager

        Args:
            config_path: Path to config.yaml file (optional)
            base_dir: Base directory for relative paths
            tool_name: Tool name (e.g., 'nb10', 'nb03') for tool-specific defaults
            tool_defaults: Tool-specific default configuration (merged with BASE_DEFAULT_CONFIG)
        """
        self.config_path = config_path
        self.base_dir = Path(base_dir) if base_dir else self._detect_base_dir()
        self.tool_name = tool_name

        # Merge base defaults with tool-specific defaults
        if tool_defaults:
            self.default_config = self._merge_config(self.BASE_DEFAULT_CONFIG, tool_defaults)
        else:
            self.default_config = self.BASE_DEFAULT_CONFIG.copy()

        self.config = self.default_config.copy()

        if config_path:
            self.load_config(config_path)

    def _detect_base_dir(self) -> Path:
        """
        Detect base directory

        Priority:
        1. CARDIAC_ML_ROOT environment variable
        2. Current working directory
        """
        # Check environment variable
        if 'CARDIAC_ML_ROOT' in os.environ:
            return Path(os.environ['CARDIAC_ML_ROOT'])

        # Use current directory
        current = Path.cwd()

        # Try to detect project root (cardiac-ml-research/)
        parts = current.parts
        if 'cardiac-ml-research' in parts:
            idx = parts.index('cardiac-ml-research')
            return Path(*parts[:idx+1])

        # Fallback: current directory
        return current

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file

        Args:
            config_path: Path to config.yaml

        Returns:
            Loaded configuration dict

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid
        """
        config_file = Path(config_path)

        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)

            # Support configuration inheritance (extends field)
            if user_config and 'extends' in user_config:
                parent_path = self._resolve_parent_config(user_config['extends'])
                parent_config = self._load_parent_config(parent_path)
                # Merge: parent <- user
                user_config = self._merge_config(parent_config, user_config)
                # Remove 'extends' field
                user_config.pop('extends', None)

            # Merge with default config
            self.config = self._merge_config(self.default_config, user_config)

            # Normalize paths
            self._normalize_paths()

            # Validate configuration
            self.validate()

            logger.info(f"配置文件加载成功: {config_path}")

            return self.config

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax in {config_path}: {e}")

    def _resolve_parent_config(self, parent_ref: str) -> Path:
        """
        Resolve parent configuration path

        Args:
            parent_ref: Parent config reference (e.g., 'shared/default.yaml' or '../config.yaml')

        Returns:
            Resolved parent config path
        """
        parent_path = Path(parent_ref)
        if not parent_path.is_absolute():
            parent_path = self.base_dir / parent_path
        return parent_path

    def _load_parent_config(self, parent_path: Path) -> Dict:
        """
        Load parent configuration

        Args:
            parent_path: Path to parent config file

        Returns:
            Parent configuration dict
        """
        if not parent_path.exists():
            raise FileNotFoundError(f"Parent config not found: {parent_path}")

        with open(parent_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def _merge_config(self, default: Dict, user: Dict) -> Dict:
        """
        Deep merge user configuration with default configuration

        Args:
            default: Default configuration dict
            user: User configuration dict

        Returns:
            Merged configuration dict
        """
        merged = default.copy()

        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                merged[key] = self._merge_config(merged[key], value)
            else:
                # Override with user value
                merged[key] = value

        return merged

    def _normalize_paths(self):
        """
        Normalize all paths in configuration

        - Convert relative paths to absolute paths
        - Handle environment variables
        - Cross-platform compatibility (Windows/Linux/Colab)
        """
        paths_config = self.config.get('paths', {})

        for key, value in paths_config.items():
            if value:
                paths_config[key] = str(self.normalize_path(value))

        self.config['paths'] = paths_config

    def normalize_path(self, path: str) -> Path:
        """
        Normalize a single path

        Args:
            path: Path string (may contain ~, $VAR, or be relative)

        Returns:
            Normalized absolute Path object
        """
        if not path:
            return Path()

        # Expand environment variables
        path = os.path.expandvars(path)

        # Expand user home directory (~)
        path = os.path.expanduser(path)

        # Convert to Path object
        path_obj = Path(path)

        # If relative, make it relative to base_dir
        if not path_obj.is_absolute():
            path_obj = self.base_dir / path_obj

        # Resolve to absolute path
        return path_obj.resolve()

    def validate(self) -> bool:
        """
        Validate configuration

        Returns:
            True if valid

        Raises:
            ValueError: If configuration is invalid
        """
        # Check required sections exist
        required_sections = ['paths', 'processing']
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")

        # Validate paths
        self._validate_paths()

        # Validate processing config
        self._validate_processing()

        # Auto-detect device if 'auto' is specified
        if self.config['processing']['device'] == 'auto':
            self.config['processing']['device'] = self._auto_detect_device()

        return True

    def _validate_paths(self):
        """Validate paths configuration"""
        paths_config = self.config.get('paths', {})

        # Create output directories if they don't exist
        for key in ['output_dir', 'cache_dir', 'log_dir']:
            if key in paths_config:
                dir_path = Path(paths_config[key])
                if not dir_path.exists():
                    try:
                        dir_path.mkdir(parents=True, exist_ok=True)
                        logger.debug(f"创建目录: {dir_path}")
                    except Exception as e:
                        raise ValueError(f"Cannot create directory {dir_path}: {e}")

    def _validate_processing(self):
        """Validate processing configuration"""
        proc_config = self.config.get('processing', {})

        # Validate mode
        if 'mode' in proc_config:
            valid_modes = ['pilot', 'full', 'test']
            if proc_config['mode'] not in valid_modes:
                raise ValueError(
                    f"Invalid mode: {proc_config['mode']} (must be one of {valid_modes})"
                )

        # Validate device
        if 'device' in proc_config:
            valid_devices = ['cuda', 'cpu', 'auto']
            if proc_config['device'] not in valid_devices:
                raise ValueError(
                    f"Invalid device: {proc_config['device']} (must be one of {valid_devices})"
                )

        # Validate numeric ranges
        if 'batch_size' in proc_config and proc_config['batch_size'] < 1:
            raise ValueError(f"Invalid batch_size: {proc_config['batch_size']} (must be >= 1)")

        if 'pilot_limit' in proc_config and proc_config['pilot_limit'] < 1:
            raise ValueError(f"Invalid pilot_limit: {proc_config['pilot_limit']} (must be >= 1)")

    def _auto_detect_device(self) -> str:
        """
        Auto-detect optimal device (cuda/cpu)

        Returns:
            'cuda' if available, else 'cpu'
        """
        try:
            import torch
            if torch.cuda.is_available():
                logger.info("自动检测: 使用 CUDA (GPU)")
                return 'cuda'
            else:
                logger.info("自动检测: 使用 CPU")
                return 'cpu'
        except ImportError:
            logger.warning("PyTorch未安装，默认使用CPU")
            return 'cpu'

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key

        Supports nested keys with dot notation: 'paths.data_dir'

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value by key

        Supports nested keys with dot notation: 'paths.data_dir'

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config

        # Navigate to nested dict
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set value
        config[keys[-1]] = value

    def update_from_hardware(self, hardware_info):
        """
        Update configuration based on hardware detection (新增功能)

        Args:
            hardware_info: HardwareInfo object from shared.hardware.detect_hardware()
        """
        # Import here to avoid circular dependency
        from shared.hardware import get_optimal_config

        optimal_config = get_optimal_config(hardware_info)

        # Update processing configuration
        self.set('processing.device', optimal_config['device'])
        self.set('performance.num_workers', optimal_config['num_workers'])
        self.set('processing.batch_size', optimal_config['batch_size'])
        self.set('performance.pin_memory', optimal_config['pin_memory'])

        if optimal_config.get('prefetch_factor'):
            self.set('performance.prefetch_factor', optimal_config['prefetch_factor'])

        # CPU优化（医院环境）
        if 'cpu_optimization' in optimal_config:
            cpu_opt = optimal_config['cpu_optimization']
            # Set environment variables for CPU optimization
            os.environ['OMP_NUM_THREADS'] = str(cpu_opt['omp_threads'])
            os.environ['MKL_NUM_THREADS'] = str(cpu_opt['mkl_threads'])

            logger.info(f"CPU优化已启用: {cpu_opt['torch_threads']}线程")

        logger.info(f"配置已根据硬件自动调整: {optimal_config['performance_tier']}档位")

    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access: config['paths']"""
        return self.config[key]

    def __repr__(self) -> str:
        """String representation"""
        tool_str = f", tool={self.tool_name}" if self.tool_name else ""
        return f"ConfigManager(config_path={self.config_path}, base_dir={self.base_dir}{tool_str})"

    # Convenience properties
    @property
    def data_dir(self) -> Path:
        """Shortcut for data directory path"""
        return Path(self.config['paths']['data_dir'])

    @property
    def output_dir(self) -> Path:
        """Shortcut for output directory path"""
        return Path(self.config['paths']['output_dir'])

    @property
    def cache_dir(self) -> Path:
        """Shortcut for cache directory path"""
        return Path(self.config['paths'].get('cache_dir', './data/cache'))

    @property
    def log_dir(self) -> Path:
        """Shortcut for log directory path"""
        return Path(self.config['paths'].get('log_dir', './logs'))

    @property
    def device(self) -> str:
        """Shortcut for processing device"""
        return self.config['processing']['device']

    @property
    def mode(self) -> str:
        """Shortcut for processing mode"""
        return self.config['processing']['mode']

    @property
    def batch_size(self) -> int:
        """Shortcut for batch size"""
        return self.config['processing'].get('batch_size', 1)

    @property
    def num_workers(self) -> int:
        """Shortcut for num_workers"""
        return self.config['performance'].get('num_workers', 0)


def create_default_config(output_path: str = "config/config.yaml", tool_name: Optional[str] = None):
    """
    Create a default configuration file

    Args:
        output_path: Where to save the config file
        tool_name: Tool name for tool-specific defaults
    """
    config_file = Path(output_path)

    if config_file.exists():
        response = input(f"{config_file} already exists. Overwrite? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return

    # Create parent directory if needed
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Use template if available
    template_path = config_file.parent / "config.yaml.template"
    if template_path.exists():
        import shutil
        shutil.copy(template_path, config_file)
        print(f"✓ Created configuration file from template: {config_file}")
    else:
        # Create from BASE_DEFAULT_CONFIG
        manager = ConfigManager(tool_name=tool_name)
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(manager.default_config, f, default_flow_style=False, sort_keys=False)
        print(f"✓ Created default configuration file: {config_file}")

    print(f"\nPlease edit {config_file} to configure:")
    print("  - Data directory path")
    print("  - Output directory path")
    if tool_name:
        print(f"  - {tool_name}-specific settings")


if __name__ == "__main__":
    # Test configuration manager
    logging.basicConfig(level=logging.INFO)

    print("="*60)
    print("Configuration Manager Test (Shared Version)")
    print("="*60)

    # Test 1: Default config
    print("\nTest 1: Default Configuration")
    config = ConfigManager(tool_name='nb10')
    print(f"Tool: {config.tool_name}")
    print(f"Base dir: {config.base_dir}")
    print(f"Data dir: {config.data_dir}")
    print(f"Output dir: {config.output_dir}")
    print(f"Device: {config.device}")
    print(f"Mode: {config.mode}")

    # Test 2: Path normalization
    print("\nTest 2: Path Normalization")
    test_paths = [
        "./data/test",
        "../models/test.pth",
        "~/Documents/data",
        "$HOME/cardiac_data"
    ]
    for path in test_paths:
        try:
            normalized = config.normalize_path(path)
            print(f"  {path} -> {normalized}")
        except Exception as e:
            print(f"  {path} -> Error: {e}")

    # Test 3: Get/Set
    print("\nTest 3: Get/Set Configuration")
    print(f"Get paths.data_dir: {config.get('paths.data_dir')}")
    config.set('processing.pilot_limit', 20)
    print(f"Set pilot_limit to 20: {config.get('processing.pilot_limit')}")

    # Test 4: Hardware-based configuration
    print("\nTest 4: Hardware-based Configuration")
    try:
        from shared.hardware import detect_hardware
        hw = detect_hardware()
        config.update_from_hardware(hw)
        print(f"Device after hardware detection: {config.device}")
        print(f"Num workers: {config.num_workers}")
        print(f"Batch size: {config.batch_size}")
    except Exception as e:
        print(f"Hardware detection test skipped: {e}")

    print("\n" + "="*60)
    print("Configuration Manager Test Complete")
    print("="*60)
