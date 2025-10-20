"""
Hospital CPU Preset Configurations

Pre-configured settings for typical hospital deployment scenarios where GPU is not available.
These presets are designed to maximize CPU performance while maintaining system stability.

Target Hardware:
- Standard Hospital Workstation: 8-core CPU, 16GB RAM (most common)
- Minimal Hospital Workstation: 4-core CPU, 8GB RAM (older systems)
- Performance Hospital Workstation: 16-core CPU, 32GB RAM (newer systems)

Performance Goals:
- Standard: <60 seconds per patient (acceptable for clinical workflow)
- Minimal: <180 seconds per patient (acceptable for batch processing)
- Performance: <30 seconds per patient (excellent for clinical workflow)

Author: Cardiac ML Research Team
Date: 2025-10-18 (Week 3)
"""

from typing import Dict, Any

# Import with fallback for different import contexts
try:
    # Try relative import first (when imported as package)
    from ..hardware.cpu_optimizer import CPUTier, CPUOptimizationConfig
except ImportError:
    # Fallback to absolute import (when running standalone or from test)
    try:
        from hardware.cpu_optimizer import CPUTier, CPUOptimizationConfig
    except ImportError:
        # Last resort: import from shared package
        from shared.hardware.cpu_optimizer import CPUTier, CPUOptimizationConfig


# ========================================
# Preset Configurations
# ========================================

# Minimal Hospital Configuration
# - Typical: 4-core CPU, 8GB RAM
# - Use Case: Older workstations, batch processing (overnight)
# - Performance: ~2-3 minutes per patient
# - Strategy: Conservative, memory-efficient
HOSPITAL_CPU_MINIMAL = {
    'name': 'Hospital CPU - Minimal',
    'description': 'Older hospital workstation (4-core CPU, 8GB RAM)',

    # Hardware assumptions
    'expected_cpu_cores': 4,
    'expected_memory_gb': 8,

    # Processing settings
    'processing': {
        'device': 'cpu',
        'num_workers': 0,  # Single-threaded to avoid overhead
        'batch_size': 1,
        'prefetch_factor': 2,
        'pin_memory': False,
    },

    # PyTorch settings
    'torch': {
        'threads': 2,  # Conservative thread count
        'enable_mkldnn': True,
        'grad_enabled': False,
    },

    # Memory management
    'memory': {
        'max_usage_gb': 4.0,  # Leave plenty for system
        'enable_efficient_mode': True,
        'clear_cache_interval': 3,  # Clear frequently
    },

    # Model settings
    'model': {
        'slice_batch_size': 1,  # Process 1 slice at a time
        'enable_amp': False,  # CPU doesn't benefit from AMP
    },

    # Performance expectations
    'performance': {
        'expected_time_per_patient_sec': (120, 180),  # 2-3 minutes
        'max_concurrent_patients': 1,
    },

    # Recommendations
    'recommendations': [
        "Schedule processing overnight or during off-hours",
        "Consider upgrading to 8-core system for better performance",
        "Monitor system resources during processing",
        "Process in smaller batches (10-20 patients at a time)",
    ]
}


# Standard Hospital Configuration
# - Typical: 8-core CPU, 16GB RAM
# - Use Case: Most common hospital workstation setup
# - Performance: ~40-60 seconds per patient
# - Strategy: Balanced performance and stability
# - TARGET CONFIGURATION FOR MEDICAL DEPLOYMENT
HOSPITAL_CPU_STANDARD = {
    'name': 'Hospital CPU - Standard',
    'description': 'Typical hospital workstation (8-core CPU, 16GB RAM)',

    # Hardware assumptions
    'expected_cpu_cores': 8,
    'expected_memory_gb': 16,

    # Processing settings
    'processing': {
        'device': 'cpu',
        'num_workers': 2,  # 2 parallel workers for data loading
        'batch_size': 2,
        'prefetch_factor': 2,
        'pin_memory': False,
    },

    # PyTorch settings
    'torch': {
        'threads': 4,  # Use half of CPU cores for PyTorch
        'enable_mkldnn': True,
        'grad_enabled': False,
    },

    # Memory management
    'memory': {
        'max_usage_gb': 8.0,  # Use ~50% of total memory
        'enable_efficient_mode': True,
        'clear_cache_interval': 5,
    },

    # Model settings
    'model': {
        'slice_batch_size': 2,  # Process 2 slices at a time
        'enable_amp': False,
    },

    # Performance expectations
    'performance': {
        'expected_time_per_patient_sec': (40, 60),  # Target: <60s
        'max_concurrent_patients': 1,
    },

    # Recommendations
    'recommendations': [
        "This configuration is suitable for clinical use",
        "Processing time allows real-time analysis during consultation",
        "Can process 50-100 patients per day during working hours",
        "Monitor memory usage if processing large datasets",
    ]
}


# Performance Hospital Configuration
# - Typical: 16-core CPU, 32GB RAM
# - Use Case: Newer high-end workstations or dedicated analysis machines
# - Performance: ~20-30 seconds per patient
# - Strategy: Maximize CPU utilization for fast processing
HOSPITAL_CPU_PERFORMANCE = {
    'name': 'Hospital CPU - Performance',
    'description': 'High-end hospital workstation (16-core CPU, 32GB RAM)',

    # Hardware assumptions
    'expected_cpu_cores': 16,
    'expected_memory_gb': 32,

    # Processing settings
    'processing': {
        'device': 'cpu',
        'num_workers': 4,  # 4 parallel workers
        'batch_size': 4,
        'prefetch_factor': 2,
        'pin_memory': False,
    },

    # PyTorch settings
    'torch': {
        'threads': 8,  # Use half of CPU cores
        'enable_mkldnn': True,
        'grad_enabled': False,
    },

    # Memory management
    'memory': {
        'max_usage_gb': 16.0,  # Can use more memory
        'enable_efficient_mode': False,  # Favor speed over memory
        'clear_cache_interval': 10,
    },

    # Model settings
    'model': {
        'slice_batch_size': 4,  # Process 4 slices at a time
        'enable_amp': False,
    },

    # Performance expectations
    'performance': {
        'expected_time_per_patient_sec': (20, 30),
        'max_concurrent_patients': 1,
    },

    # Recommendations
    'recommendations': [
        "Excellent performance for clinical use",
        "Can process 100-200 patients per day",
        "Consider this configuration for radiology departments",
        "Fast enough for real-time analysis during patient visits",
    ]
}


# ========================================
# Preset Selection Functions
# ========================================

def get_hospital_cpu_preset(cpu_cores: int = None, memory_gb: float = None) -> Dict[str, Any]:
    """
    Get hospital CPU preset based on hardware resources

    Args:
        cpu_cores: Number of CPU cores (auto-detected if None)
        memory_gb: Total memory in GB (auto-detected if None)

    Returns:
        Preset configuration dictionary

    Example:
        >>> preset = get_hospital_cpu_preset(cpu_cores=8, memory_gb=16)
        >>> print(preset['name'])
        Hospital CPU - Standard
    """
    # Auto-detect hardware if not provided
    if cpu_cores is None or memory_gb is None:
        import psutil
        if cpu_cores is None:
            cpu_cores = psutil.cpu_count(logical=False)
        if memory_gb is None:
            memory_gb = psutil.virtual_memory().total / (1024**3)

    # Select preset based on hardware
    if cpu_cores <= 4 or memory_gb <= 8:
        return HOSPITAL_CPU_MINIMAL.copy()
    elif cpu_cores <= 8 or memory_gb <= 16:
        return HOSPITAL_CPU_STANDARD.copy()
    else:
        return HOSPITAL_CPU_PERFORMANCE.copy()


def apply_hospital_cpu_preset(config_dict: Dict[str, Any],
                              preset: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply hospital CPU preset to configuration dictionary

    Args:
        config_dict: Base configuration dictionary
        preset: Hospital CPU preset dictionary

    Returns:
        Updated configuration dictionary

    Example:
        >>> config = {'paths': {'data_dir': '/data'}}
        >>> preset = get_hospital_cpu_preset()
        >>> config = apply_hospital_cpu_preset(config, preset)
        >>> config['processing']['device']
        'cpu'
    """
    # Deep copy to avoid modifying original
    import copy
    config = copy.deepcopy(config_dict)

    # Apply processing settings
    if 'processing' not in config:
        config['processing'] = {}
    config['processing'].update(preset['processing'])

    # Apply torch settings
    if 'torch' not in config:
        config['torch'] = {}
    config['torch'].update(preset['torch'])

    # Apply memory settings
    if 'memory' not in config:
        config['memory'] = {}
    config['memory'].update(preset['memory'])

    # Apply model settings
    if 'model' not in config:
        config['model'] = {}
    config['model'].update(preset['model'])

    # Store metadata
    config['_preset_info'] = {
        'name': preset['name'],
        'description': preset['description'],
        'expected_cpu_cores': preset['expected_cpu_cores'],
        'expected_memory_gb': preset['expected_memory_gb'],
    }

    return config


def print_hospital_cpu_preset_info(preset: Dict[str, Any] = None):
    """
    Print hospital CPU preset information

    Args:
        preset: Hospital CPU preset (auto-selected if None)
    """
    if preset is None:
        preset = get_hospital_cpu_preset()

    print("=" * 70)
    print("HOSPITAL CPU PRESET CONFIGURATION")
    print("=" * 70)
    print()
    print(f"Preset Name: {preset['name']}")
    print(f"Description: {preset['description']}")
    print()
    print("Expected Hardware:")
    print(f"  CPU Cores: {preset['expected_cpu_cores']}")
    print(f"  Memory: {preset['expected_memory_gb']} GB")
    print()
    print("Processing Configuration:")
    print(f"  Device: {preset['processing']['device']}")
    print(f"  Workers: {preset['processing']['num_workers']}")
    print(f"  Batch Size: {preset['processing']['batch_size']}")
    print()
    print("PyTorch Configuration:")
    print(f"  Threads: {preset['torch']['threads']}")
    print(f"  MKL-DNN: {preset['torch']['enable_mkldnn']}")
    print()
    print("Memory Configuration:")
    print(f"  Max Usage: {preset['memory']['max_usage_gb']} GB")
    print(f"  Efficient Mode: {preset['memory']['enable_efficient_mode']}")
    print()
    print("Expected Performance:")
    min_t, max_t = preset['performance']['expected_time_per_patient_sec']
    print(f"  Time per Patient: {min_t}-{max_t} seconds")
    print()
    print("Recommendations:")
    for i, rec in enumerate(preset['recommendations'], 1):
        print(f"  {i}. {rec}")
    print()
    print("=" * 70)


# ========================================
# Integration with CPUOptimizer
# ========================================

def convert_preset_to_cpu_config(preset: Dict[str, Any]) -> CPUOptimizationConfig:
    """
    Convert hospital preset to CPUOptimizationConfig

    Args:
        preset: Hospital CPU preset dictionary

    Returns:
        CPUOptimizationConfig instance
    """
    # Determine CPU tier based on expected cores
    cpu_cores = preset['expected_cpu_cores']
    if cpu_cores <= 4:
        tier = CPUTier.MINIMAL
    elif cpu_cores <= 8:
        tier = CPUTier.STANDARD
    elif cpu_cores <= 16:
        tier = CPUTier.PERFORMANCE
    elif cpu_cores <= 32:
        tier = CPUTier.PROFESSIONAL
    else:
        tier = CPUTier.ENTERPRISE

    # Create CPUOptimizationConfig
    return CPUOptimizationConfig(
        tier=tier,
        num_workers=preset['processing']['num_workers'],
        batch_size=preset['processing']['batch_size'],
        prefetch_factor=preset['processing']['prefetch_factor'],
        pin_memory=preset['processing']['pin_memory'],
        torch_threads=preset['torch']['threads'],
        enable_mkldnn=preset['torch']['enable_mkldnn'],
        max_memory_usage_gb=preset['memory']['max_usage_gb'],
        enable_memory_efficient_mode=preset['memory']['enable_efficient_mode'],
        expected_time_per_patient_sec=preset['performance']['expected_time_per_patient_sec'],
        description=preset['description'],
    )


# ========================================
# Example Usage
# ========================================

if __name__ == "__main__":
    print("Hospital CPU Preset - Standalone Test")
    print()

    # Test auto-detection
    print("Auto-detecting hardware and selecting preset...")
    preset = get_hospital_cpu_preset()
    print_hospital_cpu_preset_info(preset)
    print()

    # Test all presets
    print("\nAll Available Presets:")
    print("=" * 70)
    for preset_name, preset_dict in [
        ('Minimal', HOSPITAL_CPU_MINIMAL),
        ('Standard', HOSPITAL_CPU_STANDARD),
        ('Performance', HOSPITAL_CPU_PERFORMANCE),
    ]:
        print(f"\n{preset_name}:")
        print(f"  Cores: {preset_dict['expected_cpu_cores']}, " +
              f"Memory: {preset_dict['expected_memory_gb']}GB")
        min_t, max_t = preset_dict['performance']['expected_time_per_patient_sec']
        print(f"  Performance: {min_t}-{max_t}s per patient")

    # Test conversion to CPUOptimizationConfig
    print("\n\nConverting to CPUOptimizationConfig:")
    print("=" * 70)
    cpu_config = convert_preset_to_cpu_config(preset)
    print(f"Tier: {cpu_config.tier.value}")
    print(f"Workers: {cpu_config.num_workers}")
    print(f"Batch Size: {cpu_config.batch_size}")
    print(f"PyTorch Threads: {cpu_config.torch_threads}")
