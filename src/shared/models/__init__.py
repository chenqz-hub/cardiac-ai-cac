"""
Shared Models Module
Deep learning model wrappers for cardiac imaging

Currently includes:
- AI-CAC: Coronary artery calcium scoring (SwinUNETR)
"""

from .ai_cac import (
    # Model class
    AICAModel,

    # Configuration
    ModelConfig,
    InferenceResult,

    # Factory function
    create_ai_cac_model,
)

__all__ = [
    # Model class
    'AICAModel',

    # Configuration
    'ModelConfig',
    'InferenceResult',

    # Factory function
    'create_ai_cac_model',
]
