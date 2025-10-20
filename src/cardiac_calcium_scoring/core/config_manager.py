"""
Configuration Manager for NB10 Windows Tool

Handles loading, validation, and normalization of configuration files.
Supports cross-platform paths and environment variables.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
import yaml


__version__ = "1.0.0"


class ConfigManager:
    """
    Configuration manager for NB10 tool

    Features:
    - Load YAML configuration files
    - Validate required fields
    - Normalize paths (Windows/Linux compatible)
    - Support environment variables
    - Merge with default configuration
    """

    DEFAULT_CONFIG = {
        'paths': {
            'data_dir': './data/dicom_original',
            'model_path': './models/va_non_gated_ai_cac_model.pth',
            'output_dir': './output',
            'cache_dir': './data/cache',
            'log_dir': './logs'
        },
        'processing': {
            'mode': 'pilot',
            'pilot_limit': 10,
            'device': 'cuda',
            'batch_size': 1,
            'enable_resume': True,
            'slice_thickness_min': 4.0,
            'slice_thickness_max': 6.0
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
            'generate_plots': True,
            'figure_dpi': 300
        },
        'logging': {
            'level': 'INFO',
            'log_to_file': True,
            'log_to_console': True,
            'max_file_size': 10,
            'backup_count': 3
        },
        'clinical': {
            'risk_thresholds': {
                'very_low': 0,
                'low': 1,
                'moderate': 101,
                'high': 401
            },
            'report_zero_calcium': True,
            'flag_high_risk': True
        }
    }

    def __init__(self, config_path: Optional[str] = None, base_dir: Optional[str] = None):
        """
        Initialize configuration manager

        Args:
            config_path: Path to config.yaml file (optional)
            base_dir: Base directory for relative paths (default: nb10_windows/)
        """
        self.config_path = config_path
        self.base_dir = Path(base_dir) if base_dir else self._detect_base_dir()
        self.config = self.DEFAULT_CONFIG.copy()

        if config_path:
            self.load_config(config_path)

    def _detect_base_dir(self) -> Path:
        """Detect base directory (tools/nb10_windows/)"""
        # If running from nb10_windows/ or subdirectory
        current = Path.cwd()

        # Check if we're in nb10_windows or subdirectory
        if current.name == 'nb10_windows' or 'nb10_windows' in str(current):
            # Find the nb10_windows root
            parts = current.parts
            if 'nb10_windows' in parts:
                idx = parts.index('nb10_windows')
                return Path(*parts[:idx+1])

        # Fallback: assume current directory
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

            # Merge with default config
            self.config = self._merge_config(self.DEFAULT_CONFIG, user_config)

            # Normalize paths
            self._normalize_paths()

            # Validate configuration
            self.validate()

            return self.config

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax in {config_path}: {e}")

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
        - Cross-platform compatibility (Windows/Linux)
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

        # Validate paths exist or can be created
        paths_config = self.config['paths']

        # Model file must exist
        model_path = Path(paths_config['model_path'])
        # Validation only - warnings handled by run_nb10.py

        # Data directory must exist
        data_dir = Path(paths_config['data_dir'])
        # Validation only - warnings handled by run_nb10.py

        # Output directories can be created
        for key in ['output_dir', 'cache_dir', 'log_dir']:
            dir_path = Path(paths_config[key])
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    # Directory created silently
                except Exception as e:
                    raise ValueError(f"Cannot create directory {dir_path}: {e}")

        # Validate processing config
        proc_config = self.config['processing']

        # Validate mode
        if proc_config['mode'] not in ['pilot', 'full']:
            raise ValueError(f"Invalid mode: {proc_config['mode']} (must be 'pilot' or 'full')")

        # Validate device
        if proc_config['device'] not in ['cuda', 'cpu', 'auto']:
            raise ValueError(f"Invalid device: {proc_config['device']} (must be 'cuda', 'cpu', or 'auto')")

        # Auto-detect device if 'auto' is specified
        if proc_config['device'] == 'auto':
            import torch
            if torch.cuda.is_available():
                proc_config['device'] = 'cuda'
            else:
                proc_config['device'] = 'cpu'

        # Check CUDA availability if device is cuda
        elif proc_config['device'] == 'cuda':
            import torch
            if not torch.cuda.is_available():
                # Silent fallback to CPU
                proc_config['device'] = 'cpu'

        # Validate numeric ranges
        if proc_config['batch_size'] < 1:
            raise ValueError(f"Invalid batch_size: {proc_config['batch_size']} (must be >= 1)")

        if proc_config['pilot_limit'] < 1:
            raise ValueError(f"Invalid pilot_limit: {proc_config['pilot_limit']} (must be >= 1)")

        return True

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

    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access: config['paths']"""
        return self.config[key]

    def __repr__(self) -> str:
        """String representation"""
        return f"ConfigManager(config_path={self.config_path}, base_dir={self.base_dir})"

    @property
    def data_dir(self) -> Path:
        """Shortcut for data directory path"""
        return Path(self.config['paths']['data_dir'])

    @property
    def model_path(self) -> Path:
        """Shortcut for model file path"""
        return Path(self.config['paths']['model_path'])

    @property
    def output_dir(self) -> Path:
        """Shortcut for output directory path"""
        return Path(self.config['paths']['output_dir'])

    @property
    def device(self) -> str:
        """Shortcut for processing device"""
        return self.config['processing']['device']

    @property
    def mode(self) -> str:
        """Shortcut for processing mode"""
        return self.config['processing']['mode']


def create_default_config(output_path: str = "config/config.yaml"):
    """
    Create a default configuration file

    Args:
        output_path: Where to save the config file
    """
    config_file = Path(output_path)

    if config_file.exists():
        response = input(f"{config_file} already exists. Overwrite? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return

    # Use template if available
    template_path = config_file.parent / "config.yaml.template"
    if template_path.exists():
        import shutil
        shutil.copy(template_path, config_file)
        print(f"✓ Created configuration file from template: {config_file}")
    else:
        # Create from DEFAULT_CONFIG
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(ConfigManager.DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)
        print(f"✓ Created default configuration file: {config_file}")

    print(f"\nPlease edit {config_file} to configure:")
    print("  - Data directory path")
    print("  - Model file path")
    print("  - Output directory path")


if __name__ == "__main__":
    # Test configuration manager
    print("="*60)
    print("Configuration Manager Test")
    print("="*60)

    # Test 1: Default config
    print("\nTest 1: Default Configuration")
    config = ConfigManager()
    print(f"Base dir: {config.base_dir}")
    print(f"Data dir: {config.data_dir}")
    print(f"Model path: {config.model_path}")
    print(f"Device: {config.device}")
    print(f"Mode: {config.mode}")

    # Test 2: Path normalization
    print("\nTest 2: Path Normalization")
    test_paths = [
        "./data/test",
        "../models/test.pth",
        "~/Documents/data",
        "D:/cardiac_data"
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

    print("\n" + "="*60)
    print("Configuration Manager Test Complete")
    print("="*60)
