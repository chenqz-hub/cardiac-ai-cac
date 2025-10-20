"""
DICOM Series Selection for AI-CAC
=================================

This module provides smart DICOM series selection logic, matching the behavior
of the Colab version (NB10). It's more flexible than AI-CAC's filter_series.py,
which requires Series Description keywords.

Key Features:
- Primary: Select series with 4-6mm slice thickness
- Fallback: If no 4-6mm series, select the series with fewest files (likely thick slice)
- No dependency on Series Description keywords (works with empty descriptions)

Author: NB10 Windows Tool
Version: 1.0.0
Date: 2025-10-14
"""

import pydicom
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


def identify_dicom_series(dicom_dir: Path, sample_size: int = 20) -> Dict:
    """
    Identify all DICOM series in a directory and extract metadata.

    Args:
        dicom_dir: Directory containing DICOM files
        sample_size: Number of files to sample for metadata extraction

    Returns:
        Dictionary mapping SeriesInstanceUID to series info:
        {
            'series_uid': {
                'files': [list of file paths],
                'thickness': float,
                'description': str,
                'positions': [list of Z positions]
            }
        }
    """
    dcm_files = list(Path(dicom_dir).glob("*.dcm"))

    if len(dcm_files) == 0:
        return {}

    series_info = defaultdict(lambda: {
        'files': [],
        'thickness': None,
        'description': None,
        'positions': []
    })

    # PERFORMANCE FIX: Single-pass reading - collect files and metadata in one loop
    # Previously: Read sample for metadata, then read ALL files again for positions
    # This was causing severe performance degradation on repeated runs
    for dcm_file in dcm_files:
        try:
            ds = pydicom.dcmread(str(dcm_file), stop_before_pixels=True)
            series_uid = getattr(ds, 'SeriesInstanceUID', 'Unknown')

            # Extract metadata from first file of each series
            if series_info[series_uid]['thickness'] is None:
                thickness = getattr(ds, 'SliceThickness', None)
                if thickness is not None:
                    series_info[series_uid]['thickness'] = float(thickness)

                series_info[series_uid]['description'] = getattr(ds, 'SeriesDescription', '')

            # Get Z position from ImagePositionPatient
            ipp = getattr(ds, 'ImagePositionPatient', None)
            if ipp:
                series_info[series_uid]['positions'].append(float(ipp[2]))

            series_info[series_uid]['files'].append(str(dcm_file))
        except Exception:
            continue

    return dict(series_info)


def select_best_series(series_info: Dict) -> Tuple[List[str], List[float], str]:
    """
    Select the best DICOM series for AI-CAC processing.

    Selection Logic:
    1. Priority: Series with slice thickness in 4-6mm range
    2. Tie-breaker: Among candidates, select the one with fewest files
    3. Fallback: If no 4-6mm series, select the series with fewest files

    This logic matches the Colab version and is more flexible than AI-CAC's
    filter_series.py, which requires Series Description keywords.

    Args:
        series_info: Dictionary from identify_dicom_series()

    Returns:
        Tuple of (file_paths, axial_positions, selection_message)
    """
    # Build list of candidates with 4-6mm thickness
    candidates = []

    for series_uid, info in series_info.items():
        thickness = info['thickness']
        if thickness and 4.0 <= thickness <= 6.0:
            candidates.append({
                'series_uid': series_uid,
                'thickness': thickness,
                'file_count': len(info['files']),
                'files': info['files'],
                'positions': info['positions'],
                'description': info['description']
            })

    if not candidates:
        # Fallback: No 4-6mm series found, select series with fewest files
        all_series = []
        for series_uid, info in series_info.items():
            all_series.append({
                'series_uid': series_uid,
                'thickness': info['thickness'],
                'file_count': len(info['files']),
                'files': info['files'],
                'positions': info['positions'],
                'description': info['description']
            })

        if all_series:
            selected = min(all_series, key=lambda x: x['file_count'])
            message = f"Fallback: Selected by file count (thickness={selected['thickness']}mm, {selected['file_count']} files)"
            return selected['files'], selected['positions'], message
        else:
            return [], [], "No series found"

    # Select the candidate with fewest files (usually the thick-slice reconstruction)
    selected = min(candidates, key=lambda x: x['file_count'])
    message = f"Selected 5mm series (thickness={selected['thickness']}mm, {selected['file_count']} files)"

    return selected['files'], selected['positions'], message


def prepare_dicom_for_aicac(dicom_folder: Path) -> Optional[Dict]:
    """
    Prepare DICOM data for AI-CAC inference.

    This is the main entry point that combines identify_dicom_series()
    and select_best_series().

    Args:
        dicom_folder: Path to patient's DICOM folder

    Returns:
        Dictionary with:
        {
            'file_paths': [sorted list of DICOM file paths],
            'axial_positions': [corresponding Z positions],
            'selection_info': str (description of selection)
        }
        Or None if no suitable series found.
    """
    series_info = identify_dicom_series(dicom_folder)

    if not series_info:
        return None

    files, positions, message = select_best_series(series_info)

    if not files:
        return None

    # Sort by axial position
    sorted_pairs = sorted(zip(files, positions), key=lambda x: x[1])
    sorted_files = [fp for fp, _ in sorted_pairs]
    sorted_positions = [pos for _, pos in sorted_pairs]

    return {
        'file_paths': sorted_files,
        'axial_positions': sorted_positions,
        'selection_info': message,
        'num_files': len(sorted_files)
    }


if __name__ == '__main__':
    # Test module
    import sys
    if len(sys.argv) > 1:
        test_dir = Path(sys.argv[1])
        print(f"Testing on: {test_dir}")
        result = prepare_dicom_for_aicac(test_dir)
        if result:
            print(f"✅ Success: {result['selection_info']}")
            print(f"   Files: {result['num_files']}")
        else:
            print("❌ Failed: No suitable series found")
