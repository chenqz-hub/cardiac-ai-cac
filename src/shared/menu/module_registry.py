"""
Module Registry for Cardiac ML Research Extensible Menu System
模块注册中心 - 可扩展菜单系统核心

This module implements dynamic module discovery and management.
It scans the tools/ directory and automatically detects available modules
based on module_info.yaml files.

Key Features:
- Dynamic module discovery (scan tools/ directory)
- Dependency resolution
- Hardware capability filtering (GPU/CPU)
- Category-based organization
- License checking integration

Author: Cardiac ML Research Team
Created: 2025-10-19
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Set
import logging
from dataclasses import dataclass

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from menu.module_metadata import ModuleMetadata, ModuleStatus, ModuleCategory

# Optional hardware detection
try:
    from hardware.detector import detect_hardware
    HARDWARE_DETECTION_AVAILABLE = True
except ImportError:
    detect_hardware = None
    HARDWARE_DETECTION_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class RegistryConfig:
    """Configuration for ModuleRegistry"""
    tools_dir: Path                    # Root directory containing modules
    auto_scan: bool = True             # Automatically scan on init
    check_dependencies: bool = True    # Verify dependencies
    check_hardware: bool = True        # Check hardware requirements
    check_license: bool = False        # Check license (disabled by default)
    metadata_filename: str = 'module_info.yaml'  # Standard metadata filename


class ModuleRegistry:
    """
    Central registry for managing cardiac analysis modules

    This class implements the extensible menu system architecture described
    in WEEK7_PLUS_DEPLOYMENT_PLAN.md Section 1.

    Design principles:
    1. Dynamic discovery: Scan tools/ directory for modules
    2. Metadata-driven: Each module has module_info.yaml
    3. Dependency-aware: Resolve module dependencies
    4. Hardware-aware: Filter based on GPU/CPU availability
    5. Extensible: Easy to add new modules

    Example:
        >>> registry = ModuleRegistry(tools_dir=Path('tools'))
        >>> available_modules = registry.get_available_modules()
        >>> ccs_module = registry.get_module('cardiac_calcium_scoring')
    """

    def __init__(self, config: Optional[RegistryConfig] = None):
        """
        Initialize module registry

        Args:
            config: Registry configuration. If None, uses default config.
        """
        # Use default config if not provided
        if config is None:
            # Determine project root (go up 2 levels from shared/menu/)
            project_root = Path(__file__).parent.parent.parent
            tools_dir = project_root / 'tools'

            config = RegistryConfig(
                tools_dir=tools_dir,
                auto_scan=True,
                check_dependencies=True,
                check_hardware=True,
                check_license=False  # Disabled for now
            )

        self.config = config
        self._modules: Dict[str, ModuleMetadata] = {}
        self._scan_errors: List[str] = []

        # Hardware detection
        if self.config.check_hardware and HARDWARE_DETECTION_AVAILABLE:
            try:
                hw_info = detect_hardware()
                self.hardware = hw_info
                self.has_gpu = hw_info.gpu.available
            except Exception as e:
                logger.warning(f"Hardware detection failed: {e}")
                self.hardware = None
                self.has_gpu = False
        else:
            self.hardware = None
            self.has_gpu = False

        # License checking (placeholder for now)
        self.has_license = not self.config.check_license

        # Auto-scan if enabled
        if self.config.auto_scan:
            self.scan_modules()

        logger.info(f"ModuleRegistry initialized: {len(self._modules)} modules found")

    def scan_modules(self) -> int:
        """
        Scan tools directory for module_info.yaml files and register modules

        Returns:
            Number of modules successfully registered
        """
        self._modules.clear()
        self._scan_errors.clear()

        if not self.config.tools_dir.exists():
            error_msg = f"Tools directory not found: {self.config.tools_dir}"
            logger.error(error_msg)
            self._scan_errors.append(error_msg)
            return 0

        logger.info(f"Scanning modules in: {self.config.tools_dir}")

        # Scan all subdirectories in tools/
        for module_dir in self.config.tools_dir.iterdir():
            if not module_dir.is_dir():
                continue

            # Skip hidden directories and __pycache__
            if module_dir.name.startswith('.') or module_dir.name == '__pycache__':
                continue

            # Look for module_info.yaml
            metadata_file = module_dir / self.config.metadata_filename

            if metadata_file.exists():
                try:
                    metadata = ModuleMetadata.from_yaml_file(metadata_file)
                    self._modules[metadata.module_id] = metadata
                    logger.debug(f"Registered module: {metadata.module_id} ({metadata.medical_name})")

                except Exception as e:
                    error_msg = f"Failed to load {metadata_file}: {e}"
                    logger.warning(error_msg)
                    self._scan_errors.append(error_msg)
            else:
                # Module directory exists but no metadata file
                logger.debug(f"No {self.config.metadata_filename} in {module_dir.name}")

        logger.info(f"Scan complete: {len(self._modules)} modules registered, "
                   f"{len(self._scan_errors)} errors")

        return len(self._modules)

    def get_module(self, module_id: str) -> Optional[ModuleMetadata]:
        """
        Get module metadata by ID

        Args:
            module_id: Module identifier (e.g., 'cardiac_calcium_scoring')

        Returns:
            ModuleMetadata if found, None otherwise
        """
        return self._modules.get(module_id)

    def get_all_modules(self) -> List[ModuleMetadata]:
        """Get all registered modules"""
        return list(self._modules.values())

    def get_available_modules(self, category: Optional[ModuleCategory] = None) -> List[ModuleMetadata]:
        """
        Get available modules filtered by hardware capabilities and status

        Args:
            category: Optional category filter

        Returns:
            List of available modules
        """
        available = []

        for module in self._modules.values():
            # Check if module is available given current capabilities
            if not module.is_available(has_gpu=self.has_gpu, has_license=self.has_license):
                continue

            # Category filter
            if category is not None and module.category != category:
                continue

            available.append(module)

        return available

    def get_modules_by_category(self) -> Dict[ModuleCategory, List[ModuleMetadata]]:
        """
        Get available modules organized by category

        Returns:
            Dictionary mapping categories to module lists
        """
        categorized = {}

        for module in self.get_available_modules():
            if module.category not in categorized:
                categorized[module.category] = []
            categorized[module.category].append(module)

        return categorized

    def check_dependencies(self, module_id: str, visited: Optional[Set[str]] = None) -> tuple[bool, List[str]]:
        """
        Check if all dependencies for a module are satisfied

        Args:
            module_id: Module to check
            visited: Set of visited modules (for cycle detection)

        Returns:
            Tuple of (all_satisfied: bool, missing_modules: List[str])
        """
        if visited is None:
            visited = set()

        # Cycle detection
        if module_id in visited:
            logger.warning(f"Circular dependency detected: {module_id}")
            return False, [f"CIRCULAR: {module_id}"]

        visited.add(module_id)

        module = self.get_module(module_id)
        if module is None:
            return False, [module_id]

        missing = []

        for dep in module.dependencies:
            # Check if dependency exists
            dep_module = self.get_module(dep.module_id)

            if dep_module is None:
                if not dep.optional:
                    missing.append(dep.module_id)
                continue

            # Check if dependency is available
            if not dep_module.is_available(has_gpu=self.has_gpu, has_license=self.has_license):
                if not dep.optional:
                    missing.append(f"{dep.module_id} (unavailable)")
                continue

            # Recursively check dependency's dependencies
            dep_satisfied, dep_missing = self.check_dependencies(dep.module_id, visited.copy())
            if not dep_satisfied and not dep.optional:
                missing.extend(dep_missing)

        return len(missing) == 0, missing

    def get_dependency_chain(self, module_id: str) -> List[str]:
        """
        Get ordered list of dependencies (topological sort)

        Args:
            module_id: Module to get dependencies for

        Returns:
            List of module IDs in execution order (dependencies first)
        """
        chain = []
        visited = set()

        def visit(mid: str):
            if mid in visited:
                return
            visited.add(mid)

            module = self.get_module(mid)
            if module is None:
                return

            # Visit dependencies first
            for dep in module.dependencies:
                if not dep.optional:
                    visit(dep.module_id)

            chain.append(mid)

        visit(module_id)
        return chain

    def get_module_path(self, module_id: str) -> Optional[Path]:
        """
        Get absolute path to module directory

        Args:
            module_id: Module identifier

        Returns:
            Path to module directory, or None if not found
        """
        module = self.get_module(module_id)
        if module is None:
            return None

        # Module directory name should match module_id
        module_dir = self.config.tools_dir / module_id

        if not module_dir.exists():
            logger.warning(f"Module directory not found: {module_dir}")
            return None

        return module_dir

    def get_module_entry_point(self, module_id: str) -> Optional[Path]:
        """
        Get absolute path to module entry point script

        Args:
            module_id: Module identifier

        Returns:
            Path to entry point script, or None if not found
        """
        module = self.get_module(module_id)
        if module is None:
            return None

        module_dir = self.get_module_path(module_id)
        if module_dir is None:
            return None

        entry_point = module_dir / module.entry_point

        if not entry_point.exists():
            logger.warning(f"Entry point not found: {entry_point}")
            return None

        return entry_point

    def get_scan_errors(self) -> List[str]:
        """Get errors encountered during last scan"""
        return self._scan_errors.copy()

    def get_statistics(self) -> Dict[str, any]:
        """
        Get registry statistics

        Returns:
            Dictionary with registry statistics
        """
        total = len(self._modules)
        available = len(self.get_available_modules())
        by_status = {}
        by_category = {}

        for module in self._modules.values():
            # Count by status
            status_key = module.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1

            # Count by category
            category_key = module.category.value
            by_category[category_key] = by_category.get(category_key, 0) + 1

        return {
            'total': total,
            'available': available,
            'unavailable': total - available,
            'by_status': by_status,
            'by_category': by_category,
            'has_gpu': self.has_gpu,
            'has_license': self.has_license,
            'scan_errors': len(self._scan_errors)
        }

    def print_summary(self):
        """Print formatted summary of registered modules"""
        stats = self.get_statistics()

        print("=" * 70)
        print("Module Registry Summary")
        print("=" * 70)
        print(f"Total modules: {stats['total']}")
        print(f"Available modules: {stats['available']}")
        print(f"Unavailable modules: {stats['unavailable']}")
        print(f"\nHardware capabilities:")
        print(f"  GPU available: {stats['has_gpu']}")
        print(f"  License valid: {stats['has_license']}")

        if stats['scan_errors'] > 0:
            print(f"\nScan errors: {stats['scan_errors']}")

        print(f"\nModules by status:")
        for status, count in sorted(stats['by_status'].items()):
            print(f"  {status}: {count}")

        print(f"\nModules by category:")
        for category, count in sorted(stats['by_category'].items()):
            print(f"  {category}: {count}")

        print("\nAvailable modules:")
        for category, modules in self.get_modules_by_category().items():
            print(f"\n  {category.value.upper()}:")
            for module in sorted(modules, key=lambda m: m.module_id):
                gpu_info = "GPU" if module.gpu_required else "CPU"
                time_info = f"{module.estimated_time_cpu}s" if module.estimated_time_cpu else "N/A"
                print(f"    - {module.medical_name} ({module.abbreviation}) "
                      f"[{gpu_info}, ~{time_info}/patient]")

        print("=" * 70)

    def __len__(self):
        """Return number of registered modules"""
        return len(self._modules)

    def __contains__(self, module_id: str):
        """Check if module is registered"""
        return module_id in self._modules

    def __iter__(self):
        """Iterate over module IDs"""
        return iter(self._modules.keys())


def create_default_registry(tools_dir: Optional[Path] = None) -> ModuleRegistry:
    """
    Create a ModuleRegistry with default configuration

    Args:
        tools_dir: Optional custom tools directory. If None, auto-detects.

    Returns:
        Configured ModuleRegistry instance
    """
    if tools_dir is not None:
        config = RegistryConfig(tools_dir=tools_dir)
    else:
        config = None  # Will use default auto-detection

    return ModuleRegistry(config=config)


if __name__ == '__main__':
    # Example usage and testing
    print("=== Module Registry Test ===\n")

    # Create registry
    registry = create_default_registry()

    # Print summary
    registry.print_summary()

    # Test specific module lookup
    print("\n=== Module Lookup Test ===")
    test_module_id = 'cardiac_calcium_scoring'

    if test_module_id in registry:
        module = registry.get_module(test_module_id)
        print(f"\nFound module: {module.medical_name}")
        print(f"  Version: {module.version}")
        print(f"  Status: {module.status.value}")
        print(f"  Entry point: {module.entry_point}")

        # Check dependencies
        satisfied, missing = registry.check_dependencies(test_module_id)
        print(f"  Dependencies satisfied: {satisfied}")
        if missing:
            print(f"  Missing: {missing}")

        # Get module paths
        module_dir = registry.get_module_path(test_module_id)
        entry_point = registry.get_module_entry_point(test_module_id)
        print(f"  Module directory: {module_dir}")
        print(f"  Entry point path: {entry_point}")
        print(f"  Entry point exists: {entry_point.exists() if entry_point else False}")
    else:
        print(f"Module '{test_module_id}' not found")

    # Statistics
    print("\n=== Statistics ===")
    stats = registry.get_statistics()
    print(f"Total: {stats['total']}, Available: {stats['available']}")
