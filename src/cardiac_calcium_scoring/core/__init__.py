"""
NB10 Windows Tool - Core Module

Week 3 Migration: Now uses shared modules for cross-platform compatibility.

Migration Strategy:
- Hardware detection → shared.hardware
- AI-CAC model → shared.models.ai_cac
- Config management → shared.utils.config (keeping local for backward compatibility)
- CPU optimization → shared.hardware.cpu_optimizer (NEW)

Author: Chen Doctor Team
Date: 2025-10-18 (Week 3 migration)
"""

__version__ = "2.0.0-alpha"  # Week 3 version with shared modules
__author__ = "Chen Doctor Team"
__license__ = "MIT"

# Version info
VERSION_INFO = {
    "version": __version__,
    "python_requires": ">=3.10,<3.13",
    "torch_version": "2.1.0",
    "monai_version": "1.3.2",  # CRITICAL: Do not upgrade
    "release_date": "2025-10-18"
}

import sys
from pathlib import Path

# Add shared modules to path
SHARED_PATH = Path(__file__).parent.parent.parent.parent / "shared"
if SHARED_PATH.exists() and str(SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(SHARED_PATH))

# ========================================
# Import from Shared Modules (Week 3)
# ========================================

try:
    # Hardware detection and optimization
    from shared.hardware import (
        detect_hardware,
        get_optimal_config,
        CPUOptimizer,
        get_optimal_cpu_config,
        apply_cpu_optimizations,
    )

    # AI-CAC model
    from shared.models.ai_cac import (
        create_ai_cac_model,
        ModelConfig as AICACModelConfig,  # Alias for compatibility
    )

    # Environment presets
    from shared.presets import (
        get_hospital_cpu_preset,
        HOSPITAL_CPU_STANDARD,
    )

    SHARED_MODULES_AVAILABLE = True

except ImportError as e:
    import warnings
    warnings.warn(f"Shared modules not available, using local implementations: {e}")
    SHARED_MODULES_AVAILABLE = False

    # Fallback to local implementations
    detect_hardware = None
    get_optimal_config = None
    CPUOptimizer = None
    get_optimal_cpu_config = None
    apply_cpu_optimizations = None
    create_ai_cac_model = None
    AICACModelConfig = None
    get_hospital_cpu_preset = None
    HOSPITAL_CPU_STANDARD = None

# ========================================
# Local Implementations (Backward Compatibility)
# ========================================

# Config manager - keep local for backward compatibility
from .config_manager import ConfigManager, create_default_config

# Local AI-CAC implementation (fallback)
try:
    from .ai_cac_inference_lib import create_model as create_model_local
    from .ai_cac_inference_lib import run_inference_on_dicom_folder
except ImportError as e:
    create_model_local = None
    run_inference_on_dicom_folder = None
    import warnings
    warnings.warn(f"Local AI-CAC inference library not available: {e}")

# ========================================
# Unified Interface
# ========================================

def create_model(device='cuda', checkpoint_path=None, **kwargs):
    """
    Create AI-CAC model (unified interface)

    Week 3: Uses shared.models.ai_cac if available, otherwise falls back to local implementation

    Args:
        device: Device to use ('cuda' or 'cpu')
        checkpoint_path: Path to model checkpoint
        **kwargs: Additional arguments

    Returns:
        Model instance
    """
    if SHARED_MODULES_AVAILABLE and create_ai_cac_model is not None:
        # Use shared module (Week 3+)
        return create_ai_cac_model(
            device=device,
            checkpoint_path=checkpoint_path,
            **kwargs
        )
    else:
        # Fallback to local implementation
        if create_model_local is None:
            raise RuntimeError("Neither shared nor local AI-CAC model available")
        return create_model_local(device=device, checkpoint_path=checkpoint_path)


# ========================================
# Export Components
# ========================================

__all__ = [
    # Version info
    "__version__",
    "VERSION_INFO",

    # Config management (local)
    "ConfigManager",
    "create_default_config",

    # Model interface (unified)
    "create_model",
    "run_inference_on_dicom_folder",

    # Hardware detection (shared, Week 3)
    "detect_hardware",
    "get_optimal_config",

    # CPU optimization (shared, Week 3)
    "CPUOptimizer",
    "get_optimal_cpu_config",
    "apply_cpu_optimizations",

    # Presets (shared, Week 3)
    "get_hospital_cpu_preset",
    "HOSPITAL_CPU_STANDARD",

    # Shared modules availability flag
    "SHARED_MODULES_AVAILABLE",
]
