"""
AI-CAC Model Module - Shared Version
AI-CAC coronary artery calcium scoring model

Elevated from: tools/nb10_windows/core/ai_cac_inference_lib.py
Enhancements:
- Generic model interface for multi-environment support
- CPU optimization for hospital deployments
- Integrated with shared hardware detection
- Modular design for easy testing

Original: https://github.com/Raffi-Hagopian/AI-CAC
License: MIT
"""

__version__ = "2.2.0"

import os
import sys
import torch
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass

import pandas as pd
from torch.utils.data import DataLoader
from monai.networks.nets import SwinUNETR

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """AI-CAC model configuration"""
    device: str = 'cuda'
    checkpoint_path: Optional[str] = None
    image_size: Tuple[int, int] = (512, 512)
    feature_size: int = 96
    use_checkpoint: bool = True
    drop_rate: float = 0.2

    # CPU optimization (hospital environment)
    cpu_threads: Optional[int] = None
    cpu_interop_threads: int = 2

    # Performance settings
    slice_batch_size: int = 4  # Number of slices to process at once


@dataclass
class InferenceResult:
    """Single patient inference result"""
    patient_id: str
    agatston_score: float
    calcium_volume_mm3: float
    calcium_mass_mg: float
    num_slices: int
    has_calcification: bool

    # Demographics (optional)
    patient_age: Optional[int] = None
    patient_sex: Optional[str] = None  # 'M' or 'F'
    is_premature_cad: Optional[bool] = None  # Male <55, Female <65

    # Processing metadata
    processing_time_seconds: Optional[float] = None
    status: str = 'success'
    error: Optional[str] = None


class AICAModel:
    """
    AI-CAC Model Wrapper

    Provides a clean interface for AI-CAC inference with:
    - Automatic device detection
    - CPU optimization for hospital environments
    - Resource monitoring integration
    - Progress callback support
    """

    def __init__(
        self,
        config: Optional[ModelConfig] = None,
        hardware_info: Optional[Any] = None,
        auto_optimize: bool = True
    ):
        """
        Initialize AI-CAC model

        Args:
            config: Model configuration (default: auto-detect from hardware)
            hardware_info: HardwareInfo from shared.hardware (for auto-optimization)
            auto_optimize: Enable automatic hardware-based optimization
        """
        self.config = config or ModelConfig()
        self.hardware_info = hardware_info
        self.model = None
        self.is_loaded = False

        # Auto-optimize based on hardware
        if auto_optimize and hardware_info:
            self._auto_optimize_config()

    def _auto_optimize_config(self):
        """Auto-optimize configuration based on hardware"""
        hw = self.hardware_info

        # Device selection
        if self.config.device == 'auto':
            self.config.device = 'cuda' if hw.gpu.available else 'cpu'

        # CPU optimization (hospital critical)
        if self.config.device == 'cpu':
            if self.config.cpu_threads is None:
                # Use all but one core, max 8 threads
                self.config.cpu_threads = min(hw.cpu.physical_cores - 1, 8)

            # Larger batch size for CPU (no VRAM limit)
            if hw.cpu.physical_cores >= 8:
                self.config.slice_batch_size = 8
            else:
                self.config.slice_batch_size = 4
        else:
            # GPU mode: conservative batch size
            self.config.slice_batch_size = 4

        logger.info(f"Auto-optimized config: device={self.config.device}, "
                   f"slice_batch={self.config.slice_batch_size}")

    def load_model(self, checkpoint_path: Optional[str] = None) -> 'AICAModel':
        """
        Load model weights

        Args:
            checkpoint_path: Path to .pth file (overrides config)

        Returns:
            self (for method chaining)
        """
        if checkpoint_path:
            self.config.checkpoint_path = checkpoint_path

        if not self.config.checkpoint_path:
            raise ValueError("checkpoint_path must be provided")

        # CPU thread optimization (must be set before first parallel operation)
        if self.config.device == 'cpu':
            try:
                if self.config.cpu_threads:
                    torch.set_num_threads(self.config.cpu_threads)
                torch.set_num_interop_threads(self.config.cpu_interop_threads)
                logger.info(f"CPU threads: {self.config.cpu_threads}, "
                           f"interop: {self.config.cpu_interop_threads}")
            except RuntimeError as e:
                logger.warning(f"Failed to set CPU threads: {e}")

        # Create model
        self.model = SwinUNETR(
            spatial_dims=2,
            img_size=self.config.image_size,
            in_channels=1,
            out_channels=1,
            feature_size=self.config.feature_size,
            use_checkpoint=self.config.use_checkpoint,
            drop_rate=self.config.drop_rate,
        ).to(self.config.device)

        # Load weights
        checkpoint = torch.load(
            self.config.checkpoint_path,
            map_location=self.config.device
        )
        state_dict = checkpoint['model_state_dict']

        # Remove 'module.' prefix if exists (DataParallel compatibility)
        if any(key.startswith('module.') for key in state_dict.keys()):
            state_dict = {
                key.replace('module.', ''): value
                for key, value in state_dict.items()
            }

        self.model.load_state_dict(state_dict)
        self.model.eval()
        self.is_loaded = True

        logger.info(f"Model loaded: {self.config.checkpoint_path}")
        logger.info(f"Device: {self.config.device}")

        return self

    def extract_demographics(self, dicom_folder: Path) -> Dict[str, Any]:
        """
        Extract patient demographics from DICOM metadata

        Args:
            dicom_folder: Path to folder containing DICOM files

        Returns:
            dict with patient_age, patient_sex, is_premature_cad
        """
        import pydicom

        result = {
            'patient_age': None,
            'patient_sex': None,
            'is_premature_cad': None
        }

        try:
            # Find first DICOM file
            dcm_files = list(Path(dicom_folder).rglob("*.dcm"))
            if not dcm_files:
                return result

            # Read metadata only (fast)
            dcm = pydicom.dcmread(dcm_files[0], stop_before_pixels=True)

            # Extract age
            if hasattr(dcm, 'PatientAge'):
                age_str = str(dcm.PatientAge)
                if age_str.endswith('Y'):
                    try:
                        result['patient_age'] = int(age_str[:-1])
                    except ValueError:
                        pass

            # Fallback: calculate from birth date
            if result['patient_age'] is None:
                if hasattr(dcm, 'PatientBirthDate') and hasattr(dcm, 'StudyDate'):
                    try:
                        birth_year = int(str(dcm.PatientBirthDate)[:4])
                        study_year = int(str(dcm.StudyDate)[:4])
                        result['patient_age'] = study_year - birth_year
                    except (ValueError, TypeError):
                        pass

            # Extract sex
            if hasattr(dcm, 'PatientSex'):
                sex = str(dcm.PatientSex).upper()
                if sex in ['M', 'F']:
                    result['patient_sex'] = sex

            # Check premature CAD criteria (ACCF/AHA guidelines)
            if result['patient_age'] and result['patient_sex']:
                if result['patient_sex'] == 'M' and result['patient_age'] < 55:
                    result['is_premature_cad'] = True
                elif result['patient_sex'] == 'F' and result['patient_age'] < 65:
                    result['is_premature_cad'] = True
                else:
                    result['is_premature_cad'] = False

        except Exception as e:
            logger.debug(f"Failed to extract demographics: {e}")

        return result

    def infer_single_patient(
        self,
        dicom_folder: Path,
        extract_demographics: bool = True,
        progress_callback: Optional[Callable] = None
    ) -> InferenceResult:
        """
        Run inference on a single patient

        Args:
            dicom_folder: Path to patient's DICOM folder
            extract_demographics: Extract age/sex from DICOM metadata
            progress_callback: Optional callback(slice_idx, total_slices)

        Returns:
            InferenceResult object
        """
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        import time
        start_time = time.time()

        patient_id = Path(dicom_folder).name

        try:
            # Extract demographics
            demographics = {}
            if extract_demographics:
                demographics = self.extract_demographics(dicom_folder)

            # Prepare DICOM data
            # Note: This requires nb10's DICOM processing utilities
            # For Week 2, we'll create placeholders; full integration in Week 3

            # TODO: Integrate with shared/data/dicom_io.py (Week 2)
            # For now, return a placeholder result for testing

            processing_time = time.time() - start_time

            return InferenceResult(
                patient_id=patient_id,
                agatston_score=0.0,  # Placeholder
                calcium_volume_mm3=0.0,
                calcium_mass_mg=0.0,
                num_slices=0,
                has_calcification=False,
                **demographics,
                processing_time_seconds=processing_time,
                status='success'
            )

        except Exception as e:
            logger.error(f"Inference failed for {patient_id}: {e}")

            return InferenceResult(
                patient_id=patient_id,
                agatston_score=0.0,
                calcium_volume_mm3=0.0,
                calcium_mass_mg=0.0,
                num_slices=0,
                has_calcification=False,
                status='failed',
                error=str(e)
            )

    def infer_batch(
        self,
        dicom_folders: List[Path],
        extract_demographics: bool = True,
        progress_callback: Optional[Callable] = None
    ) -> List[InferenceResult]:
        """
        Run inference on multiple patients

        Args:
            dicom_folders: List of patient DICOM folder paths
            extract_demographics: Extract age/sex from DICOM metadata
            progress_callback: Optional callback(current, total, patient_id, result)

        Returns:
            List of InferenceResult objects
        """
        results = []

        for i, folder in enumerate(dicom_folders):
            result = self.infer_single_patient(
                folder,
                extract_demographics=extract_demographics
            )
            results.append(result)

            if progress_callback:
                progress_callback(i + 1, len(dicom_folders), result.patient_id, result)

        return results

    def results_to_dataframe(self, results: List[InferenceResult]) -> pd.DataFrame:
        """
        Convert inference results to pandas DataFrame

        Args:
            results: List of InferenceResult objects

        Returns:
            pandas DataFrame
        """
        data = []
        for r in results:
            data.append({
                'patient_id': r.patient_id,
                'agatston_score': r.agatston_score,
                'calcium_volume_mm3': r.calcium_volume_mm3,
                'calcium_mass_mg': r.calcium_mass_mg,
                'num_slices': r.num_slices,
                'has_calcification': r.has_calcification,
                'patient_age': r.patient_age,
                'patient_sex': r.patient_sex,
                'is_premature_cad': r.is_premature_cad,
                'processing_time_seconds': r.processing_time_seconds,
                'status': r.status,
                'error': r.error
            })

        return pd.DataFrame(data)


# Factory function for easy model creation
def create_ai_cac_model(
    checkpoint_path: str,
    device: str = 'auto',
    hardware_info: Optional[Any] = None
) -> AICAModel:
    """
    Factory function to create and load AI-CAC model

    Args:
        checkpoint_path: Path to model weights (.pth file)
        device: 'cuda', 'cpu', or 'auto'
        hardware_info: Optional HardwareInfo for auto-optimization

    Returns:
        Loaded AICAModel instance

    Example:
        >>> from shared.hardware import detect_hardware
        >>> from shared.models import create_ai_cac_model
        >>>
        >>> hw = detect_hardware()
        >>> model = create_ai_cac_model(
        >>>     'models/va_non_gated_ai_cac_model.pth',
        >>>     device='auto',
        >>>     hardware_info=hw
        >>> )
        >>> result = model.infer_single_patient('data/PATIENT001')
    """
    config = ModelConfig(device=device, checkpoint_path=checkpoint_path)
    model = AICAModel(config=config, hardware_info=hardware_info)
    model.load_model()
    return model


if __name__ == "__main__":
    # Test model creation
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    print("\n" + "="*70)
    print("AI-CAC Model Module Test")
    print("="*70)

    # Test 1: Model configuration
    print("\nTest 1: Model Configuration")
    config = ModelConfig(device='cpu', slice_batch_size=8)
    print(f"  Device: {config.device}")
    print(f"  Slice batch size: {config.slice_batch_size}")
    print(f"  Image size: {config.image_size}")

    # Test 2: Auto-optimization with hardware info
    print("\nTest 2: Hardware-based Auto-optimization")
    try:
        from shared.hardware import detect_hardware
        hw = detect_hardware()
        model = AICAModel(hardware_info=hw, auto_optimize=True)
        print(f"  Auto-detected device: {model.config.device}")
        print(f"  CPU threads: {model.config.cpu_threads}")
        print(f"  Slice batch size: {model.config.slice_batch_size}")
    except ImportError:
        print("  Skipped: shared.hardware not available")

    # Test 3: Demographics extraction (mock)
    print("\nTest 3: Demographics Extraction (mock)")
    print("  Note: Requires DICOM files for full test")

    print("\n" + "="*70)
    print("AI-CAC Model Module Test Complete")
    print("Note: Full inference testing requires model file and DICOM data")
    print("="*70)
