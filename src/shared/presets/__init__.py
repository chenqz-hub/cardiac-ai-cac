"""
Environment Presets Module

Provides pre-configured settings for different deployment environments:
- Hospital CPU: Typical hospital workstation without GPU
- Hospital GPU: Hospital workstation with GPU
- Colab: Google Colab environment
- Research Workstation: High-end research workstation

Author: Cardiac ML Research Team
Date: 2025-10-18 (Week 3)
"""

from .hospital_cpu import (
    get_hospital_cpu_preset,
    HOSPITAL_CPU_STANDARD,
    HOSPITAL_CPU_MINIMAL,
    HOSPITAL_CPU_PERFORMANCE,
    apply_hospital_cpu_preset,
    print_hospital_cpu_preset_info,
    convert_preset_to_cpu_config,
)

__all__ = [
    'get_hospital_cpu_preset',
    'HOSPITAL_CPU_STANDARD',
    'HOSPITAL_CPU_MINIMAL',
    'HOSPITAL_CPU_PERFORMANCE',
    'apply_hospital_cpu_preset',
    'print_hospital_cpu_preset_info',
    'convert_preset_to_cpu_config',
]
