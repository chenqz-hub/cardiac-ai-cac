"""
Extensible Menu System for Cardiac ML Research

Provides dynamic module discovery and management.
"""

from .module_metadata import (
    ModuleMetadata,
    ModuleStatus,
    ModuleCategory,
    ModuleDependency,
    create_nb10_metadata
)
from .module_registry import ModuleRegistry, RegistryConfig, create_default_registry

__all__ = [
    'ModuleMetadata',
    'ModuleStatus',
    'ModuleCategory',
    'ModuleDependency',
    'create_nb10_metadata',
    'ModuleRegistry',
    'RegistryConfig',
    'create_default_registry'
]
