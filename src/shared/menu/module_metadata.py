"""
Module Metadata Management for Cardiac ML Research
模块元数据管理

This module provides dataclasses and utilities for managing module metadata
in the extensible menu system.

Author: Cardiac ML Research Team
Created: 2025-10-19
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
from pathlib import Path
import yaml


class ModuleStatus(Enum):
    """Module availability status"""
    AVAILABLE = "available"           # Ready to use
    IN_DEVELOPMENT = "in_development" # Under development
    REQUIRES_GPU = "requires_gpu"     # Needs GPU (not available on CPU-only)
    REQUIRES_LICENSE = "requires_license"  # Needs valid license
    DEPRECATED = "deprecated"         # No longer recommended


class ModuleCategory(Enum):
    """Module functional categories"""
    PREPROCESSING = "preprocessing"   # Data preprocessing (DICOM conversion, etc.)
    SEGMENTATION = "segmentation"     # Image segmentation
    QUANTIFICATION = "quantification" # Feature extraction/quantification
    RADIOMICS = "radiomics"          # Radiomics feature extraction
    ANALYSIS = "analysis"            # Multi-modal analysis
    UTILITY = "utility"              # Utility tools


@dataclass
class ModuleDependency:
    """Module dependency specification"""
    module_id: str                    # Required module ID
    reason: str                       # Why this dependency is needed
    optional: bool = False            # Is this dependency optional?


@dataclass
class ModuleMetadata:
    """
    Complete metadata for a cardiac analysis module

    This class follows the medical terminology naming convention from
    MASTER_PROJECT_PLAN_SUPPLEMENT.md Section 1.

    Attributes:
        module_id: Unique identifier (e.g., 'cardiac_calcium_scoring')
        medical_name: Medical terminology name (e.g., 'Cardiac Calcium Scoring')
        abbreviation: Short abbreviation (e.g., 'CCS')
        notebook_ref: Original notebook reference (e.g., 'NB10')
        category: Module category
        status: Current availability status
        version: Module version (e.g., '1.1.4')
        description_en: English description
        description_zh: Chinese description
        entry_point: Main executable path (relative to module dir)
        output_dir: Default output directory name
        dependencies: List of required modules
        gpu_required: Whether GPU is required
        cpu_capable: Whether CPU-only mode is supported
        estimated_time_cpu: Estimated time per patient on CPU (seconds)
        estimated_time_gpu: Estimated time per patient on GPU (seconds)
        sample_count: Number of samples processed in original study
        config_file: Path to module config file (relative to module dir)
        icon: Icon identifier for UI (optional)
        tags: List of tags for searching/filtering
        authors: List of authors/contributors
        created_date: Creation date (YYYY-MM-DD)
        last_updated: Last update date (YYYY-MM-DD)
    """

    # Core identifiers
    module_id: str
    medical_name: str
    abbreviation: str
    notebook_ref: str  # e.g., 'NB10'

    # Classification
    category: ModuleCategory
    status: ModuleStatus
    version: str

    # Descriptions
    description_en: str
    description_zh: str

    # Paths
    entry_point: str  # e.g., 'cli/run_calcium_scoring.py'
    output_dir: str   # e.g., 'cardiac_calcium'

    # Dependencies and requirements
    dependencies: List[ModuleDependency] = field(default_factory=list)
    gpu_required: bool = False
    cpu_capable: bool = True

    # Performance estimates
    estimated_time_cpu: Optional[int] = None  # seconds per patient
    estimated_time_gpu: Optional[int] = None  # seconds per patient

    # Study information
    sample_count: Optional[int] = None  # Number of samples in original study

    # Configuration
    config_file: Optional[str] = None  # e.g., 'config/config.yaml'

    # UI/UX
    icon: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    # Metadata
    authors: List[str] = field(default_factory=list)
    created_date: Optional[str] = None
    last_updated: Optional[str] = None

    # Additional custom fields
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization"""
        return {
            'module_id': self.module_id,
            'medical_name': self.medical_name,
            'abbreviation': self.abbreviation,
            'notebook_ref': self.notebook_ref,
            'category': self.category.value,
            'status': self.status.value,
            'version': self.version,
            'description': {
                'en': self.description_en,
                'zh': self.description_zh
            },
            'paths': {
                'entry_point': self.entry_point,
                'output_dir': self.output_dir,
                'config_file': self.config_file
            },
            'dependencies': [
                {
                    'module_id': dep.module_id,
                    'reason': dep.reason,
                    'optional': dep.optional
                }
                for dep in self.dependencies
            ],
            'requirements': {
                'gpu_required': self.gpu_required,
                'cpu_capable': self.cpu_capable
            },
            'performance': {
                'estimated_time_cpu': self.estimated_time_cpu,
                'estimated_time_gpu': self.estimated_time_gpu
            },
            'study': {
                'sample_count': self.sample_count
            },
            'ui': {
                'icon': self.icon,
                'tags': self.tags
            },
            'metadata': {
                'authors': self.authors,
                'created_date': self.created_date,
                'last_updated': self.last_updated
            },
            'extra': self.extra
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModuleMetadata':
        """Create from dictionary (YAML deserialization)"""

        # Parse dependencies
        dependencies = []
        for dep_data in data.get('dependencies', []):
            dependencies.append(ModuleDependency(
                module_id=dep_data['module_id'],
                reason=dep_data['reason'],
                optional=dep_data.get('optional', False)
            ))

        return cls(
            module_id=data['module_id'],
            medical_name=data['medical_name'],
            abbreviation=data['abbreviation'],
            notebook_ref=data['notebook_ref'],
            category=ModuleCategory(data['category']),
            status=ModuleStatus(data['status']),
            version=data['version'],
            description_en=data['description']['en'],
            description_zh=data['description']['zh'],
            entry_point=data['paths']['entry_point'],
            output_dir=data['paths']['output_dir'],
            dependencies=dependencies,
            gpu_required=data['requirements']['gpu_required'],
            cpu_capable=data['requirements']['cpu_capable'],
            estimated_time_cpu=data['performance'].get('estimated_time_cpu'),
            estimated_time_gpu=data['performance'].get('estimated_time_gpu'),
            sample_count=data['study'].get('sample_count'),
            config_file=data['paths'].get('config_file'),
            icon=data['ui'].get('icon'),
            tags=data['ui'].get('tags', []),
            authors=data['metadata'].get('authors', []),
            created_date=data['metadata'].get('created_date'),
            last_updated=data['metadata'].get('last_updated'),
            extra=data.get('extra', {})
        )

    @classmethod
    def from_yaml_file(cls, yaml_path: Path) -> 'ModuleMetadata':
        """Load metadata from YAML file"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    def to_yaml_file(self, yaml_path: Path) -> None:
        """Save metadata to YAML file"""
        yaml_path.parent.mkdir(parents=True, exist_ok=True)
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, allow_unicode=True, sort_keys=False)

    def is_available(self, has_gpu: bool = False, has_license: bool = True) -> bool:
        """
        Check if module is available given current system capabilities

        Args:
            has_gpu: Whether GPU is available
            has_license: Whether valid license exists

        Returns:
            True if module can be run
        """
        # Check status
        if self.status == ModuleStatus.DEPRECATED:
            return False

        if self.status == ModuleStatus.IN_DEVELOPMENT:
            return False

        if self.status == ModuleStatus.REQUIRES_LICENSE and not has_license:
            return False

        if self.status == ModuleStatus.REQUIRES_GPU and not has_gpu:
            return False

        # Check GPU requirement
        if self.gpu_required and not has_gpu and not self.cpu_capable:
            return False

        # Check dependencies (basic check, full check done by ModuleRegistry)
        # This is just for quick filtering

        return True

    def get_display_name(self, language: str = 'zh') -> str:
        """Get display name in specified language"""
        if language == 'en':
            return self.medical_name
        else:
            # For Chinese, we can use the description or medical name
            # For now, return English medical name
            # TODO: Add dedicated Chinese medical names if needed
            return self.medical_name

    def get_description(self, language: str = 'zh') -> str:
        """Get description in specified language"""
        if language == 'en':
            return self.description_en
        else:
            return self.description_zh

    def __str__(self) -> str:
        """String representation"""
        return (f"ModuleMetadata(id={self.module_id}, "
                f"name={self.medical_name}, "
                f"status={self.status.value}, "
                f"version={self.version})")

    def __repr__(self) -> str:
        return self.__str__()


# Example factory functions for common module types

def create_nb10_metadata() -> ModuleMetadata:
    """Create metadata for NB10 (Cardiac Calcium Scoring) - reference implementation"""
    return ModuleMetadata(
        module_id='cardiac_calcium_scoring',
        medical_name='Cardiac Calcium Scoring (AI-CAC)',
        abbreviation='CCS',
        notebook_ref='NB10',
        category=ModuleCategory.QUANTIFICATION,
        status=ModuleStatus.AVAILABLE,
        version='1.1.4',
        description_en='AI-based coronary artery calcification scoring using deep learning model',
        description_zh='基于AI的冠状动脉钙化评分，使用深度学习模型自动检测和量化冠脉钙化',
        entry_point='cli/run_calcium_scoring.py',
        output_dir='cardiac_calcium',
        dependencies=[],  # No dependencies
        gpu_required=False,
        cpu_capable=True,
        estimated_time_cpu=305,  # seconds per patient
        estimated_time_gpu=120,  # estimated
        sample_count=195,
        config_file='config/config.yaml',
        icon='heart',
        tags=['calcium', 'coronary', 'cac', 'ai', 'quantification'],
        authors=['Cardiac ML Research Team'],
        created_date='2025-10-15',
        last_updated='2025-10-18'
    )


if __name__ == '__main__':
    # Example usage
    print("=== Module Metadata Example ===\n")

    # Create NB10 metadata
    nb10_meta = create_nb10_metadata()
    print(f"Created: {nb10_meta}\n")

    # Check availability
    print(f"Available on CPU-only system: {nb10_meta.is_available(has_gpu=False)}")
    print(f"Available with GPU: {nb10_meta.is_available(has_gpu=True)}\n")

    # Get localized info
    print(f"Display name (ZH): {nb10_meta.get_display_name('zh')}")
    print(f"Display name (EN): {nb10_meta.get_display_name('en')}\n")
    print(f"Description (ZH): {nb10_meta.get_description('zh')[:50]}...")

    # Save to YAML
    test_yaml = Path('/tmp/test_module_metadata.yaml')
    nb10_meta.to_yaml_file(test_yaml)
    print(f"\nSaved to: {test_yaml}")

    # Load from YAML
    loaded_meta = ModuleMetadata.from_yaml_file(test_yaml)
    print(f"Loaded: {loaded_meta}")
    print(f"Match: {loaded_meta.module_id == nb10_meta.module_id}")
