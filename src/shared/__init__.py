"""
Shared Modules Library
Shared module library for cardiac-ml-research

Version: 2.0.0 (Week 1 - Basic Infrastructure)
"""

__version__ = "2.0.0-alpha"

# Quick imports for common functions
from .hardware import detect_hardware, HardwareInfo
from .environment import detect_runtime, RuntimeEnvironment
from .utils import ConfigManager

__all__ = [
    # Version
    '__version__',

    # Hardware detection
    'detect_hardware',
    'HardwareInfo',

    # Environment detection
    'detect_runtime',
    'RuntimeEnvironment',

    # Configuration management
    'ConfigManager',
]
