"""
AI-CAC Inference Library - Refactored for Library Use

This is a refactored version of AI-CAC's main_inference.py that can be imported
and used as a Python library without executing code at import time.

Original: https://github.com/Raffi-Hagopian/AI-CAC
License: MIT
"""

__version__ = "2.1.1"  # v1.1.4: Fix DataLoader hanging on last patient

import os
import sys
import torch
import pandas as pd
from torch.utils.data import DataLoader
from monai.networks.nets import SwinUNETR

# Add AI-CAC to path (will be done by caller)
# sys.path.insert(0, '/content/AI-CAC')


def extract_patient_demographics(dicom_folder_path):
    """
    Extract patient age and sex from DICOM metadata

    Args:
        dicom_folder_path: Path to folder containing DICOM files

    Returns:
        dict: {
            'patient_age': int or None,
            'patient_sex': str or None ('M' or 'F'),
            'is_premature_cad': bool or None  # Male <55, Female <65
        }
    """
    import pydicom
    from pathlib import Path

    result = {
        'patient_age': None,
        'patient_sex': None,
        'is_premature_cad': None
    }

    try:
        # Find first DICOM file
        folder = Path(dicom_folder_path)
        dcm_files = list(folder.rglob("*.dcm"))
        if not dcm_files:
            return result

        # Read first DICOM file (all files should have same patient info)
        dcm = pydicom.dcmread(dcm_files[0], stop_before_pixels=True)

        # Extract age
        if hasattr(dcm, 'PatientAge'):
            age_str = str(dcm.PatientAge)
            if age_str.endswith('Y'):
                try:
                    result['patient_age'] = int(age_str[:-1])
                except:
                    pass

        # If no direct age, calculate from birth date and study date
        if result['patient_age'] is None:
            if hasattr(dcm, 'PatientBirthDate') and hasattr(dcm, 'StudyDate'):
                try:
                    birth_year = int(str(dcm.PatientBirthDate)[:4])
                    study_year = int(str(dcm.StudyDate)[:4])
                    result['patient_age'] = study_year - birth_year
                except:
                    pass

        # Extract sex
        if hasattr(dcm, 'PatientSex'):
            sex = str(dcm.PatientSex).upper()
            if sex in ['M', 'F']:
                result['patient_sex'] = sex

        # Check premature CAD criteria
        if result['patient_age'] is not None and result['patient_sex'] is not None:
            if result['patient_sex'] == 'M' and result['patient_age'] < 55:
                result['is_premature_cad'] = True
            elif result['patient_sex'] == 'F' and result['patient_age'] < 65:
                result['is_premature_cad'] = True
            else:
                result['is_premature_cad'] = False

    except Exception:
        # Silently fail - demographics are optional
        pass

    return result


def create_model(device='cuda', checkpoint_path=None):
    """
    Create and load AI-CAC SwinUNETR model

    Args:
        device: 'cuda' or 'cpu'
        checkpoint_path: Path to model weights (.pth file)

    Returns:
        Loaded model in eval mode
    """
    # v1.1.3: CPU线程优化 - 必须在第一次并行操作前设置（仅设置一次）
    if device == 'cpu':
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        torch_threads = min(cpu_count - 1, 8)  # 保留1核给系统，最多8线程

        # 仅在未设置时设置（避免重复调用create_model时报错）
        try:
            torch.set_num_threads(torch_threads)
            torch.set_num_interop_threads(2)  # 操作间并行
        except RuntimeError:
            # 已经设置过，忽略错误
            pass

    RESAMPLE_IMAGE_SIZE = (512, 512)

    model = SwinUNETR(
        spatial_dims=2,
        img_size=RESAMPLE_IMAGE_SIZE,
        in_channels=1,
        out_channels=1,
        feature_size=96,
        use_checkpoint=True,
        drop_rate=0.2,
    ).to(device)

    if checkpoint_path:
        checkpoint = torch.load(checkpoint_path, map_location=device)
        state_dict = checkpoint['model_state_dict']

        # Remove 'module.' prefix if exists (DataParallel)
        if any(key.startswith('module.') for key in state_dict.keys()):
            new_state_dict = {}
            for key, value in state_dict.items():
                new_key = key.replace('module.', '')
                new_state_dict[new_key] = value
            state_dict = new_state_dict

        model.load_state_dict(state_dict)

    model.eval()
    return model


def run_inference_on_dicom_folder(dicom_folder_path, model, device='cuda',
                                   batch_size=1, num_workers=0, performance_profile=None,
                                   safety_monitor=None, extract_demographics=True):
    """
    Run AI-CAC inference on a single patient's DICOM folder

    Args:
        dicom_folder_path: Path to folder containing DICOM files
        model: Loaded SwinUNETR model
        device: 'cuda' or 'cpu'
        batch_size: DataLoader batch size (default 1, process one patient at a time)
        num_workers: Number of DataLoader workers (default 0, auto-detect if profile provided)
        performance_profile: Optional PerformanceProfile for hardware-optimized settings
        safety_monitor: Optional SafetyMonitor for resource monitoring and OOM protection
        extract_demographics: Extract age and gender from DICOM metadata (default True)

    Returns:
        dict: {
            'agatston_score': float,
            'calcium_volume_mm3': float,
            'calcium_mass_mg': float,
            'num_slices': int,
            'has_calcification': bool,
            'patient_age': int or None,
            'patient_sex': str or None,
            'is_premature_cad': bool or None  # Male <55, Female <65
        }
    """
    # Import AI-CAC modules from core directory
    from pathlib import Path
    import_path = Path(__file__).parent
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

    from dataset_generator_inference import CTChestDataset_nongated
    from processing import compute_agatston_for_batch
    from dicom_series_selector import prepare_dicom_for_aicac

    # Step 0: Extract patient demographics if requested
    demographics = {
        'patient_age': None,
        'patient_sex': None,
        'is_premature_cad': None
    }
    if extract_demographics:
        demographics = extract_patient_demographics(dicom_folder_path)

    # Step 1 & 2: Use Colab-compatible DICOM series selection
    # This is more flexible than AI-CAC's filter_series.py:
    # - Works with empty Series Description
    # - Primary: Select 4-6mm thickness
    # - Fallback: Select series with fewest files
    study_name = os.path.basename(dicom_folder_path)

    series_result = prepare_dicom_for_aicac(Path(dicom_folder_path))

    if series_result is None:
        raise ValueError(f"No suitable series found in {dicom_folder_path}")

    # Step 3: Build study_files structure
    study_files = {
        study_name: {
            'file_paths': series_result['file_paths'],
            'axial_positions': series_result['axial_positions']
        }
    }

    # Step 4: Create dataset (using official API structure)
    study_ids = list(study_files.keys())

    # ✅ Official structure: list of tuples [(file_path, axial_position), ...]
    study_paths = []
    for study_id in study_ids:
        file_paths = study_files[study_id]['file_paths']
        axial_positions = study_files[study_id]['axial_positions']

        # Create list of tuples for this study
        study_tuple_list = [(fp, ap) for fp, ap in zip(file_paths, axial_positions)]
        study_paths.append(study_tuple_list)

    study_labels = [-1] * len(study_ids)  # Placeholder for inference (no ground truth)

    # ✅ Official API: positional arguments
    dataset = CTChestDataset_nongated(study_ids, study_paths, study_labels)

    # Apply hardware-optimized DataLoader settings
    if performance_profile:
        dl_num_workers = performance_profile.num_workers
        dl_pin_memory = performance_profile.pin_memory
        dl_prefetch = performance_profile.prefetch_factor
    else:
        # Fallback to passed parameters or defaults
        dl_num_workers = num_workers
        dl_pin_memory = False
        dl_prefetch = None

    # v1.1.3-rc3: CRITICAL FIX - Force num_workers=0 for single-patient inference
    # Issue: DataLoader with num_workers>0 hangs after last patient due to
    # worker process cleanup issues. Since we process one patient at a time,
    # multiprocessing overhead provides no benefit and causes hangs.
    # Solution: Always use num_workers=0 for single patient (main process loading)
    dl_num_workers = 0
    dl_prefetch = None  # Not applicable when num_workers=0

    # Always use batch_size=1 for single patient inference to avoid OOM
    dataloader = DataLoader(
        dataset,
        batch_size=1,
        shuffle=False,
        num_workers=dl_num_workers,
        pin_memory=dl_pin_memory,
        prefetch_factor=dl_prefetch
    )

    # Safety check: Verify resources before starting
    if safety_monitor:
        from core.safety_monitor import SafetyLevel
        initial_status = safety_monitor.check_status()
        if initial_status.overall_level == SafetyLevel.EMERGENCY:
            raise RuntimeError(f"资源严重不足，无法启动推理: {initial_status.details}")
        elif initial_status.overall_level == SafetyLevel.CRITICAL:
            # Clear cache before starting
            safety_monitor.clear_gpu_cache()

    # Step 5: Run inference
    # CTChestDataset_nongated returns tuple: (study_id, inputs, targets, hu_vols, vox_dims)

    # v1.1.3: CPU优化 - 根据device动态调整batch size
    if device == 'cpu':
        # CPU可以使用更大的batch（没有VRAM限制）
        SLICE_BATCH_SIZE = performance_profile.slice_batch_size if performance_profile else 8
    else:
        # GPU模式：保守配置（考虑VRAM限制）
        SLICE_BATCH_SIZE = performance_profile.slice_batch_size if performance_profile else 4

    score_data = []

    # v1.1.3-rc3: Wrap DataLoader iteration in try-finally to ensure cleanup
    try:
        with torch.no_grad():
            for study_id, inputs, targets, hu_vols, vox_dims in dataloader:
                study_id = study_id[0]  # Extract study ID from batch

                # Convert to torch tensors and move to device
                # Dataset returns numpy arrays, need to convert
                if not torch.is_tensor(inputs):
                    inputs = torch.from_numpy(inputs)
                if not torch.is_tensor(hu_vols):
                    hu_vols = torch.from_numpy(hu_vols)

                inputs = inputs.to(device)
                hu_vols = hu_vols.to(device)

                # inputs shape should be [batch=1, 1, 512, 512, 64]
                # But DataLoader might return [1, 512, 512, 64] if batch_size=1
                if inputs.dim() == 4:
                    # Add batch dimension if missing
                    inputs = inputs.unsqueeze(0)

                # Initialize prediction volume with same shape as inputs
                pred_vol = torch.zeros(inputs.shape, dtype=torch.float, device=device)
                num_slices = inputs.shape[-1]  # Last dimension is depth

                # Process slice by slice in batches (matching AI-CAC implementation)
                for start_idx in range(0, num_slices, SLICE_BATCH_SIZE):
                    # Safety check: Monitor resources every 20 slices
                    if safety_monitor and start_idx % 20 == 0 and start_idx > 0:
                        from core.safety_monitor import SafetyLevel
                        status = safety_monitor.check_status()
                        if status.overall_level == SafetyLevel.CRITICAL:
                            # Clear GPU cache to free memory
                            safety_monitor.clear_gpu_cache()

                    end_idx = min(start_idx + SLICE_BATCH_SIZE, num_slices)

                    # Extract slice batch: [1, 1, 512, 512, N]
                    batch = inputs[..., start_idx:end_idx]
                    # Remove batch dim and permute: [N, 1, 512, 512]
                    batch = batch.squeeze(0).permute(3, 0, 1, 2)

                    # Model inference
                    batch_out = model(batch.float())  # [N, 1, 512, 512]

                    # Reshape back to volume format: [1, 1, 512, 512, N]
                    batch_out = batch_out.unsqueeze(0).permute(0, 2, 3, 4, 1)

                    # Store predictions in volume
                    pred_vol[..., start_idx:end_idx] = batch_out

                    # Clear intermediate tensors to free GPU memory
                    del batch, batch_out

                # Compute Agatston score - must move tensors to CPU first
                scores = compute_agatston_for_batch(
                    inputs.cpu(),
                    pred_vol.cpu(),
                    vox_dims
                )

                score_data.append({
                    'study_id': study_id,
                    'agatston_score': scores[0] if isinstance(scores, list) else scores
                })

                # Clear GPU cache after each patient to avoid OOM
                if device == 'cuda':
                    del inputs, hu_vols, pred_vol
                    if safety_monitor:
                        safety_monitor.clear_gpu_cache()
                    else:
                        torch.cuda.empty_cache()
    finally:
        # v1.1.3-rc3: Explicitly cleanup DataLoader to prevent hanging
        # This ensures worker processes are terminated even if exception occurs
        if hasattr(dataloader, '_iterator') and dataloader._iterator is not None:
            try:
                dataloader._iterator._shutdown_workers()
            except:
                pass
        del dataloader

    # Step 6: Aggregate results
    if len(score_data) == 0:
        result = {
            'agatston_score': 0.0,
            'calcium_volume_mm3': 0.0,
            'calcium_mass_mg': 0.0,
            'num_slices': 0,
            'has_calcification': False
        }
        # Add demographics
        result.update(demographics)
        return result

    # Sum scores across all batches for this patient
    total_score = sum([item['agatston_score'] for item in score_data])

    # Estimate volume and mass (simplified)
    # These are rough estimates - actual computation is in processing.py
    calcium_volume_mm3 = total_score * 0.5  # Rough conversion factor
    calcium_mass_mg = calcium_volume_mm3 * 1.2  # Assuming density ~1.2

    result = {
        'agatston_score': float(total_score),
        'calcium_volume_mm3': float(calcium_volume_mm3),
        'calcium_mass_mg': float(calcium_mass_mg),
        'num_slices': len(dataset),
        'has_calcification': total_score > 0
    }

    # Add demographics
    result.update(demographics)

    return result


def batch_inference(dicom_folders, model, device='cuda', progress_callback=None,
                   performance_profile=None, safety_monitor=None, extract_demographics=True):
    """
    Run inference on multiple DICOM folders

    Args:
        dicom_folders: List of paths to DICOM folders
        model: Loaded SwinUNETR model
        device: 'cuda' or 'cpu'
        progress_callback: Optional callback function(current, total, patient_id, result)
        performance_profile: Optional PerformanceProfile for hardware-optimized settings
        safety_monitor: Optional SafetyMonitor for resource monitoring
        extract_demographics: Extract age and gender from DICOM metadata (default True)

    Returns:
        pd.DataFrame with results
    """
    results = []

    for i, folder_path in enumerate(dicom_folders):
        patient_id = os.path.basename(folder_path)

        try:
            result = run_inference_on_dicom_folder(
                folder_path, model, device,
                performance_profile=performance_profile,
                safety_monitor=safety_monitor,
                extract_demographics=extract_demographics
            )
            result['patient_id'] = patient_id
            result['status'] = 'success'
            result['error'] = ''
            results.append(result)

            if progress_callback:
                progress_callback(i+1, len(dicom_folders), patient_id, result)

        except Exception as e:
            results.append({
                'patient_id': patient_id,
                'status': 'failed',
                'error': str(e),
                'agatston_score': None,
                'calcium_volume_mm3': None,
                'calcium_mass_mg': None
            })

            if progress_callback:
                progress_callback(i+1, len(dicom_folders), patient_id, None)

    return pd.DataFrame(results)
