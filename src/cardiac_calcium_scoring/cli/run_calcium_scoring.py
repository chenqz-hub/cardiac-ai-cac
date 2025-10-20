#!/usr/bin/env python3
"""
NB10 AI-CAC Command-Line Tool

Usage:
    python cli/run_nb10.py --config config/config.yaml --mode pilot
    python cli/run_nb10.py --mode full --device cuda

Author: Chen Doctor Team
License: MIT
"""

import sys
import os
from pathlib import Path
import argparse
import logging
from datetime import datetime
from typing import List, Dict
import warnings

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)
os.environ['PYTHONWARNINGS'] = 'ignore'

import pandas as pd
import torch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Add AI-CAC to path (will be configured in setup)
AI_CAC_PATH = Path(__file__).parent.parent / "external" / "AI-CAC"
if AI_CAC_PATH.exists():
    sys.path.insert(0, str(AI_CAC_PATH))

from core import ConfigManager, create_model, run_inference_on_dicom_folder


__version__ = "2.0.0-alpha"  # Week 4: Integrated CPU optimizer


def load_processed_cache(cache_file: Path, logger: logging.Logger) -> set:
    """
    Load processed cases from cache file

    Args:
        cache_file: Path to cache CSV file
        logger: Logger instance

    Returns:
        Set of processed patient IDs (only successful cases)
    """
    if not cache_file.exists():
        return set()

    try:
        df = pd.read_csv(cache_file)
        # Only return successfully processed cases
        if 'status' in df.columns and 'patient_id' in df.columns:
            successful = df[df['status'] == 'success']['patient_id'].tolist()
            logger.info(f"Resume: Found {len(successful)} successfully processed cases in cache")
            return set(successful)
        else:
            logger.warning(f"Resume: Cache file exists but missing required columns")
            return set()
    except Exception as e:
        logger.warning(f"Resume: Failed to load cache file: {e}")
        logger.warning(f"Resume: Starting fresh (cache will be recreated)")
        return set()


def append_to_cache(cache_file: Path, result: dict, logger: logging.Logger):
    """
    Append processing result to cache file (incremental save)

    Args:
        cache_file: Path to cache CSV file
        result: Processing result dictionary (must include all result fields)
        logger: Logger instance
    """
    try:
        # v1.1.3-rc2: Save complete result to cache (not just basic fields)
        # This ensures complete CSV has all patient information
        cache_record = {
            'patient_id': result['patient_id'],
            'status': result['status'],
            'error': result.get('error', ''),
            'agatston_score': result.get('agatston_score'),
            'calcium_volume_mm3': result.get('calcium_volume_mm3'),
            'calcium_mass_mg': result.get('calcium_mass_mg'),
            'num_slices': result.get('num_slices'),
            'has_calcification': result.get('has_calcification'),
            'patient_age': result.get('patient_age'),
            'patient_sex': result.get('patient_sex'),
            'is_premature_cad': result.get('is_premature_cad'),
            'timestamp': datetime.now().isoformat()
        }

        df_new = pd.DataFrame([cache_record])

        # Append or create new file
        if cache_file.exists():
            df_new.to_csv(cache_file, mode='a', header=False, index=False)
        else:
            df_new.to_csv(cache_file, mode='w', header=True, index=False)
            logger.debug(f"Resume: Created cache file: {cache_file}")
    except Exception as e:
        logger.warning(f"Resume: Failed to append to cache: {e}")


def clear_resume_cache(cache_file: Path, logger: logging.Logger) -> bool:
    """
    Clear resume cache file

    Args:
        cache_file: Path to cache file
        logger: Logger instance

    Returns:
        True if cache was cleared, False otherwise
    """
    if cache_file.exists():
        try:
            cache_file.unlink()
            logger.info(f"Resume: Cache cleared: {cache_file}")
            return True
        except Exception as e:
            logger.error(f"Resume: Failed to clear cache: {e}")
            return False
    return False


def setup_logging(config: ConfigManager) -> logging.Logger:
    """
    Setup logging system

    Args:
        config: ConfigManager instance

    Returns:
        Logger instance
    """
    log_dir = Path(config.get('paths.log_dir', './logs'))
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create log file with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f"nb10_{timestamp}.log"

    # Configure logging
    log_level = config.get('logging.level', 'INFO')
    log_to_file = config.get('logging.log_to_file', True)
    log_to_console = config.get('logging.log_to_console', True)

    # Create logger
    logger = logging.getLogger('nb10')
    logger.setLevel(getattr(logging, log_level))

    # Clear existing handlers
    logger.handlers = []

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # File handler
    if log_to_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logger.info(f"NB10 AI-CAC Tool v{__version__}")
    logger.info(f"Log file: {log_file}")

    return logger


def scan_dicom_folders(data_dir: Path, logger: logging.Logger, max_depth: int = 2) -> List[Path]:
    """
    Scan for DICOM folders in data directory (supports nested group directories)

    Args:
        data_dir: Data directory path
        logger: Logger instance
        max_depth: Maximum depth to scan (default: 2, supports data/group/patient structure)

    Returns:
        List of DICOM folder paths

    Example directory structures:
        - Flat: data/patient001/, data/patient002/
        - Grouped: data/chd/patient001/, data/normal/patient002/
    """
    logger.info(f"Scanning DICOM folders in: {data_dir}")

    if not data_dir.exists():
        logger.error(f"Data directory does not exist: {data_dir}")
        logger.error("")
        logger.error("FIRST-TIME SETUP REQUIRED:")
        logger.error("  1. Edit configuration file: config/config.yaml")
        logger.error("  2. Update 'data_dir' to your DICOM data location:")
        logger.error("     Example (Windows): data_dir: \"D:/DICOM_Data\"")
        logger.error("     Example (Linux):   data_dir: \"/home/user/DICOM_Data\"")
        logger.error("  3. Ensure your DICOM data is organized with patient subdirectories")
        logger.error("")
        return []

    # Recursively find all subdirectories containing DICOM files
    dicom_folders = []

    def scan_recursive(directory: Path, current_depth: int = 0):
        """Recursively scan for directories containing DICOM files"""
        if current_depth > max_depth:
            return

        for item in directory.iterdir():
            if not item.is_dir():
                continue

            # Check if this directory contains .dcm files
            dcm_files = list(item.glob("*.dcm"))
            if dcm_files:
                dicom_folders.append(item)
                logger.debug(f"Found DICOM folder: {item.relative_to(data_dir)} ({len(dcm_files)} files)")
            else:
                # No .dcm files here, scan subdirectories
                scan_recursive(item, current_depth + 1)

    scan_recursive(data_dir)

    logger.info(f"Found {len(dicom_folders)} DICOM folders")
    return sorted(dicom_folders)


def run_inference_batch(dicom_folders: List[Path], model, config: ConfigManager,
                       logger: logging.Logger, performance_profile=None, safety_monitor=None) -> pd.DataFrame:
    """
    Run inference on batch of DICOM folders with resume support

    Args:
        dicom_folders: List of DICOM folder paths
        model: Loaded AI-CAC model
        config: ConfigManager instance
        logger: Logger instance
        performance_profile: Optional performance profile for optimization
        safety_monitor: Optional safety monitor for OOM protection

    Returns:
        DataFrame with results
    """
    device = config.device
    results = []

    # Setup resume cache
    enable_resume = config.get('processing.enable_resume', True)
    output_dir = Path(config.get('paths.output_dir', './output'))
    cache_file = output_dir / ".nb10_resume_cache.csv"

    # Load processed cases from cache and show resume info FIRST
    processed_ids = set()
    original_count = len(dicom_folders)

    if enable_resume:
        processed_ids = load_processed_cache(cache_file, logger)
        if processed_ids:
            # Filter out processed cases
            dicom_folders = [f for f in dicom_folders if f.name not in processed_ids]
            skipped_count = original_count - len(dicom_folders)

            logger.info(f"Resume: Skipping {skipped_count} already processed cases")
            logger.info(f"Resume: Remaining {len(dicom_folders)} cases to process")

            # Show resume info to console BEFORE "Processing X cases"
            print("RESUME MODE DETECTED")
            print("="*70)
            print(f"  Total cases found: {original_count}")
            print(f"  Previously processed: {skipped_count} cases")
            print(f"  Remaining to process: {len(dicom_folders)} cases")
            print(f"  Cache file: {cache_file.relative_to(output_dir.parent)}")
            print("="*70)
            print()

    if not dicom_folders:
        logger.info("Resume: All cases already processed!")
        print()
        print("✓ All cases already processed!")
        print(f"  Check results in: {output_dir}")
        print()
        # Return empty DataFrame
        return pd.DataFrame()

    # Show processing start message
    print(f"Processing {len(dicom_folders)} cases...")
    print("="*70)

    logger.info(f"Starting inference on {len(dicom_folders)} cases")
    logger.info(f"Device: {device}")
    logger.info(f"Resume: {'ENABLED' if enable_resume else 'DISABLED'}")

    if safety_monitor:
        logger.info(f"Safety monitor: ENABLED")

    # Get configuration
    if performance_profile:
        clear_cache_interval = performance_profile.clear_cache_interval
        logger.info(f"Using optimized configuration: {performance_profile.tier_name}")
        logger.info(f"  - num_workers: {performance_profile.num_workers}")
        logger.info(f"  - pin_memory: {performance_profile.pin_memory}")
        logger.info(f"  - Expected speedup: {performance_profile.expected_speedup}")
    else:
        clear_cache_interval = config.get('performance.clear_cache_interval', 5)
        logger.info("Using default configuration (no optimization)")

    import time as time_module
    start_time = time_module.time()

    for i, folder_path in enumerate(dicom_folders, 1):
        patient_id = folder_path.name
        case_start = time_module.time()

        # Show progress to console with percentage
        percent = int(100 * i / len(dicom_folders))
        print(f"[{i}/{len(dicom_folders)} - {percent}%] Processing: {patient_id}")
        print(f"  - Loading DICOM files...", flush=True)

        logger.info(f"[{i}/{len(dicom_folders)}] Processing: {patient_id}")

        try:
            # Monitor resources periodically (every 10 patients)
            if safety_monitor and i % 10 == 1:
                from core.safety_monitor import SafetyLevel
                status = safety_monitor.check_status()
                logger.info(f"  Resource check: RAM {status.ram_available_gb:.1f}GB, " +
                          f"VRAM {status.vram_free_gb:.1f}GB - {status.overall_level.value}")

                if status.overall_level == SafetyLevel.CRITICAL:
                    logger.warning(f"  {status.details}")
                    safety_monitor.clear_gpu_cache()

            # Show AI processing status with estimated time
            if device == 'cpu':
                est_time_msg = "~3-5 minutes"
            else:
                est_time_msg = "~10-20 seconds"
            print(f"  - Running AI analysis (estimated: {est_time_msg})...", flush=True)

            # Run inference with performance profile and safety monitor
            result = run_inference_on_dicom_folder(
                str(folder_path),
                model,
                device=device,
                performance_profile=performance_profile,
                safety_monitor=safety_monitor
            )

            # Add metadata
            result['patient_id'] = patient_id
            result['status'] = 'success'
            result['error'] = ''

            results.append(result)

            # Save to cache immediately (incremental save)
            if enable_resume:
                append_to_cache(cache_file, result, logger)

            # Log and show result with time
            agatston = result['agatston_score']
            case_time = time_module.time() - case_start

            # Calculate remaining time estimate
            avg_time = (time_module.time() - start_time) / i
            remaining_cases = len(dicom_folders) - i
            est_remaining_sec = avg_time * remaining_cases

            if est_remaining_sec < 60:
                time_str = f"{int(est_remaining_sec)}s"
            else:
                time_str = f"{int(est_remaining_sec/60)}m {int(est_remaining_sec%60)}s"

            print(f"  ✓ Complete - Agatston Score: {agatston:.1f} (took {int(case_time)}s)")
            if remaining_cases > 0:
                print(f"  Estimated remaining time: {time_str}")
            print()
            logger.info(f"  ✓ Success - Agatston Score: {agatston:.2f} (time: {case_time:.1f}s)")

            # Clear GPU cache periodically
            if device == 'cuda' and i % clear_cache_interval == 0:
                torch.cuda.empty_cache()
                logger.debug(f"  Cleared GPU cache (interval: {clear_cache_interval})")

        except Exception as e:
            error_msg = str(e)
            print(f"  ✗ Failed - {error_msg}")
            print()
            logger.error(f"  ✗ Failed - {error_msg}")
            failed_result = {
                'patient_id': patient_id,
                'status': 'failed',
                'error': error_msg,
                'agatston_score': None,
                'calcium_volume_mm3': None,
                'calcium_mass_mg': None,
                'num_slices': None,
                'has_calcification': None
            }
            results.append(failed_result)

            # Save failed case to cache (will not be skipped on resume)
            if enable_resume:
                append_to_cache(cache_file, failed_result, logger)

    # Convert to DataFrame
    df = pd.DataFrame(results)

    # Log summary
    success_count = (df['status'] == 'success').sum()
    failed_count = (df['status'] == 'failed').sum()
    logger.info(f"\nInference Complete:")
    logger.info(f"  Success: {success_count}/{len(dicom_folders)}")
    logger.info(f"  Failed:  {failed_count}/{len(dicom_folders)}")

    if success_count > 0:
        success_df = df[df['status'] == 'success']
        mean_score = success_df['agatston_score'].mean()
        median_score = success_df['agatston_score'].median()
        max_score = success_df['agatston_score'].max()
        logger.info(f"  Mean Agatston Score: {mean_score:.2f}")
        logger.info(f"  Median Agatston Score: {median_score:.2f}")
        logger.info(f"  Max Agatston Score: {max_score:.2f}")

    return df


def save_results(df: pd.DataFrame, config: ConfigManager, logger: logging.Logger):
    """
    Save results to CSV file

    Args:
        df: Results DataFrame
        config: ConfigManager instance
        logger: Logger instance
    """
    output_dir = Path(config.get('paths.output_dir', './output'))
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"nb10_results_{timestamp}.csv"

    # Get encoding from config
    encoding = config.get('output.csv_encoding', 'utf-8-sig')

    # Save to CSV
    df.to_csv(output_file, index=False, encoding=encoding)
    logger.info(f"\nResults saved to: {output_file}")

    # Also save a 'latest' copy
    latest_file = output_dir / "nb10_results_latest.csv"
    df.to_csv(latest_file, index=False, encoding=encoding)
    logger.info(f"Latest copy: {latest_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='NB10 AI-CAC Coronary Calcium Scoring Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run pilot mode (10 cases) with config file
  python cli/run_nb10.py --config config/config.yaml --mode pilot

  # Run full mode with all cases
  python cli/run_nb10.py --config config/config.yaml --mode full

  # Force CPU mode
  python cli/run_nb10.py --config config/config.yaml --device cpu

  # Use custom data directory
  python cli/run_nb10.py --config config/config.yaml --data-dir D:/cardiac_data/dicom

  # Resume from interruption (automatic if enable_resume: true in config)
  python cli/run_nb10.py --config config/config.yaml --mode full

  # Clear cache and start fresh
  python cli/run_nb10.py --config config/config.yaml --mode full --clear-cache

  # Disable resume feature
  python cli/run_nb10.py --config config/config.yaml --mode full --no-resume
        """
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file (default: config/config.yaml)'
    )

    parser.add_argument(
        '--mode',
        type=str,
        choices=['pilot', 'full'],
        help='Processing mode: pilot (limited cases) or full (all cases)'
    )

    parser.add_argument(
        '--device',
        type=str,
        choices=['cuda', 'cpu'],
        help='Device to use: cuda or cpu (overrides config)'
    )

    parser.add_argument(
        '--data-dir',
        type=str,
        help='Data directory path (overrides config)'
    )

    parser.add_argument(
        '--model-path',
        type=str,
        help='Model file path (overrides config)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory path (overrides config)'
    )

    parser.add_argument(
        '--pilot-limit',
        type=int,
        help='Number of cases to process in pilot mode (overrides config)'
    )

    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear resume cache and start fresh (process all cases again)'
    )

    parser.add_argument(
        '--no-resume',
        action='store_true',
        help='Disable resume feature (do not save/load cache)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'NB10 AI-CAC Tool v{__version__}'
    )

    args = parser.parse_args()

    # Don't print title - already shown by start_nb10.bat
    # Just show initialization

    try:
        # Show initialization steps
        print("Initializing...")
        print("  - Loading configuration...", flush=True)

        # Load configuration quietly
        config = ConfigManager(args.config)

        # Setup logging (only to file, not console initially)
        log_dir = Path(config.get('paths.log_dir', './logs'))
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f"nb10_{timestamp}.log"

        logger = logging.getLogger('nb10')
        logger.setLevel(logging.INFO)
        logger.handlers = []

        # Only file handler for detailed logs
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        logger.addHandler(file_handler)

        logger.info("="*70)
        logger.info(f"NB10 AI-CAC Tool v{__version__}")
        logger.info("="*70)

        # Override config with command-line arguments
        if args.mode:
            config.set('processing.mode', args.mode)
        if args.device:
            config.set('processing.device', args.device)
        if args.data_dir:
            config.set('paths.data_dir', args.data_dir)
        if args.model_path:
            config.set('paths.model_path', args.model_path)
        if args.output_dir:
            config.set('paths.output_dir', args.output_dir)
        if args.pilot_limit:
            config.set('processing.pilot_limit', args.pilot_limit)
        if args.no_resume:
            config.set('processing.enable_resume', False)

        # Handle cache clearing
        if args.clear_cache:
            output_dir = Path(config.get('paths.output_dir', './output'))
            cache_file = output_dir / ".nb10_resume_cache.csv"
            if cache_file.exists():
                print("Clearing resume cache...")
                clear_resume_cache(cache_file, logger)
                print("✓ Cache cleared - will process all cases")
                print()
            else:
                print("No cache file found - nothing to clear")
                print()

        # Validate configuration quietly
        config.validate()

        # Log configuration to file only
        logger.info(f"Mode: {config.mode}")
        logger.info(f"Device: {config.device}")
        logger.info(f"Data directory: {config.data_dir}")
        logger.info(f"Model path: {config.model_path}")
        logger.info(f"Log file: {log_file}")

        # Show hardware detection info
        print("  - Detecting hardware...", flush=True)

        # Import and detect hardware early (before heavy imports)
        from core.hardware_profiler import detect_hardware
        from core.performance_profiles import select_profile_by_hardware

        # Week 4: Import CPU optimizer from shared modules
        try:
            from core import SHARED_MODULES_AVAILABLE, CPUOptimizer, get_hospital_cpu_preset
            cpu_optimizer_available = SHARED_MODULES_AVAILABLE
        except ImportError:
            cpu_optimizer_available = False
            CPUOptimizer = None
            get_hospital_cpu_preset = None

        hw_info = detect_hardware()
        performance_profile = select_profile_by_hardware(hw_info)

        # Week 4: Initialize CPU optimizer if available
        cpu_optimizer = None
        cpu_config = None
        hospital_preset = None

        if cpu_optimizer_available and CPUOptimizer:
            try:
                cpu_optimizer = CPUOptimizer()
                cpu_config = cpu_optimizer.get_optimal_config()

                # Get hospital preset for additional info
                if get_hospital_cpu_preset:
                    hospital_preset = get_hospital_cpu_preset()

                logger.info(f"CPU Optimizer: Enabled (Tier: {cpu_config.tier.value})")
            except Exception as e:
                logger.warning(f"CPU Optimizer initialization failed: {e}")
                cpu_optimizer_available = False

        print(f"  ✓ Configuration loaded")
        print()

        # Show system info with CPU optimizer details
        print("=" * 70)
        print("SYSTEM INFORMATION")
        print("=" * 70)
        print()

        print(f"Software:")
        print(f"  Version: NB10 AI-CAC v{__version__}")
        print(f"  Mode: {config.mode}")
        if config.mode == 'pilot':
            pilot_limit = config.get('processing.pilot_limit', 10)
            print(f"    → Test mode - will process up to {pilot_limit} cases")
        else:
            print(f"    → Full mode - will process all cases")
        print()

        print(f"Hardware:")
        print(f"  Device: {config.device}")
        if config.device == 'cpu':
            # Week 4: Show CPU optimization details
            if cpu_optimizer_available and cpu_config:
                print(f"  CPU Cores: {cpu_optimizer.cpu_count} physical, {cpu_optimizer.cpu_count_logical} logical")
                print(f"  Memory: {cpu_optimizer.total_memory_gb:.1f} GB total, {hw_info.ram.available_gb:.1f} GB available")
                print(f"  CPU Tier: {cpu_config.tier.value}")
                print()
                print(f"CPU Optimization:")
                print(f"  PyTorch Threads: {cpu_config.torch_threads}")
                print(f"  Data Workers: {cpu_config.num_workers}")
                print(f"  Batch Size: {cpu_config.batch_size}")
                print(f"  Memory Limit: {cpu_config.max_memory_usage_gb:.1f} GB")
                if cpu_config.enable_mkldnn:
                    print(f"  MKL-DNN: Enabled")

                # Show expected performance
                min_t, max_t = cpu_config.expected_time_per_patient_sec
                print()
                print(f"Expected Performance:")
                print(f"  Time per patient: {min_t}-{max_t} seconds")

                if hospital_preset:
                    preset_name = hospital_preset.get('name', 'Unknown')
                    print(f"  Configuration: {preset_name}")
            else:
                print("    → CPU mode (standard configuration)")
                print("    → Estimated: ~3-5 min per case")
        else:
            print(f"    → GPU: {hw_info.gpu.device_name}")
            print(f"    → VRAM: {hw_info.gpu.vram_total_gb:.1f} GB")
            print(f"    → Estimated: ~10-20 sec per case")

        print()
        print(f"Performance Profile: {performance_profile.tier_name}")
        print("=" * 70)
        print()

        # Check data directory with interactive prompt
        data_dir = Path(config.data_dir)
        if not data_dir.exists():
            print("="*70)
            print("⚠️  DATA DIRECTORY NOT FOUND")
            print("="*70)
            print()
            print(f"Current setting: {data_dir}")
            print()
            print("Options:")
            print("  1. Edit config/config.yaml and restart")
            print("  2. Enter path now (temporary)")
            print("  3. Exit")
            print()

            choice = input("Your choice (1-3): ").strip()

            if choice == '2':
                new_path = input("\nEnter DICOM data directory path: ").strip().strip('"')
                data_dir = Path(new_path)
                if not data_dir.exists():
                    print(f"\n✗ Error: Directory does not exist: {data_dir}")
                    return 1
                config.set('paths.data_dir', str(data_dir))
                print(f"✓ Using: {data_dir}")
                print()
            elif choice == '3' or choice == '':
                print("\nExiting...")
                return 0
            else:
                print("\nPlease edit config/config.yaml and restart.")
                print(f"Update: data_dir: \"{data_dir}\"")
                return 0

        # Scan DICOM folders (supports nested group directories)
        print("Scanning DICOM data...")
        dicom_folders = []

        def scan_for_dicom(directory: Path, max_depth: int = 2, current_depth: int = 0):
            """Recursively scan for directories containing DICOM files"""
            if current_depth > max_depth:
                return

            for item in directory.iterdir():
                if not item.is_dir():
                    continue

                # Check if this directory contains .dcm files
                dcm_files = list(item.glob("*.dcm"))
                if dcm_files:
                    dicom_folders.append(item)
                    logger.debug(f"Found DICOM folder: {item.relative_to(data_dir)} ({len(dcm_files)} files)")
                else:
                    # No .dcm files, scan subdirectories
                    scan_for_dicom(item, max_depth, current_depth + 1)

        scan_for_dicom(data_dir)
        logger.info(f"Found {len(dicom_folders)} DICOM folders")

        if not dicom_folders:
            print(f"✗ No DICOM folders found in: {data_dir}")
            print("\nPlease check:")
            print("  - Data directory path is correct")
            print("  - Directory contains patient subdirectories")
            print("  - Each subdirectory contains .dcm files")
            return 1

        print(f"✓ Found {len(dicom_folders)} patient folders")
        print()

        # Apply pilot mode limit
        original_count = len(dicom_folders)
        if config.mode == 'pilot':
            pilot_limit = config.get('processing.pilot_limit', 10)
            dicom_folders = dicom_folders[:pilot_limit]
            if original_count > pilot_limit:
                print(f"Pilot Mode Limit:")
                print(f"  Will process: {len(dicom_folders)} cases (first {pilot_limit})")
                print(f"  Remaining: {original_count - pilot_limit} cases")
                print(f"  (Use '--mode full' to process all cases)")
                print()

        # Estimate processing time (Week 4: Use CPU optimizer estimates)
        cases_to_process = len(dicom_folders)

        if config.device == 'cpu' and cpu_optimizer_available and cpu_config:
            # Use CPU optimizer's performance estimates
            time_est = cpu_optimizer.estimate_processing_time(cases_to_process, cpu_config)
            est_time_str = time_est['avg_time_str']
            min_time_str = time_est['min_time_str']
            max_time_str = time_est['max_time_str']

            print(f"Ready to Process:")
            print(f"  Cases: {cases_to_process}")
            print(f"  Estimated time: {min_time_str} - {max_time_str} (avg: {est_time_str})")
            print(f"    (Based on {cpu_config.tier.value} tier performance)")
        else:
            # Fallback to original estimation
            if config.device == 'cpu':
                est_time_per_case = 4  # minutes
            else:
                est_time_per_case = 0.25  # minutes (15 seconds)

            total_est_minutes = cases_to_process * est_time_per_case
            if total_est_minutes < 1:
                est_time_str = f"~{int(total_est_minutes * 60)} seconds"
            else:
                est_time_str = f"~{int(total_est_minutes)} minutes"

            print(f"Ready to Process:")
            print(f"  Cases: {cases_to_process}")
            print(f"  Estimated time: {est_time_str}")

        print()

        # Interactive confirmation
        print("Press ENTER to start processing (or Ctrl+C to cancel)...")
        try:
            input()
        except KeyboardInterrupt:
            print("\n\nCancelled by user.")
            return 0

        print()

        # Prepare for processing (import heavy modules)
        print("Preparing AI model...")
        print("  - Loading libraries (this may take ~30 seconds)...", flush=True)

        from core.safety_monitor import get_monitor
        safety_monitor = get_monitor(enable_auto_downgrade=True)

        logger.info(f"Hardware: {hw_info.gpu.device_name if hw_info.gpu.available else 'CPU only'}")
        logger.info(f"Profile: {performance_profile.tier_name}")

        # Load model with progress indicator
        print("  - Initializing model architecture...", flush=True)
        model = create_model(
            device=config.device,
            checkpoint_path=str(config.model_path)
        )
        print("  - Loading weights...", flush=True)

        # Week 4: Apply CPU optimizations after model loading
        if config.device == 'cpu' and cpu_optimizer_available and cpu_config:
            print("  - Applying CPU optimizations...", flush=True)
            try:
                cpu_optimizer.apply_torch_optimizations(cpu_config)
                logger.info(f"CPU optimizations applied: {cpu_config.torch_threads} threads, MKL-DNN: {cpu_config.enable_mkldnn}")
                print(f"    → PyTorch threads set to {cpu_config.torch_threads}")
                if cpu_config.enable_mkldnn:
                    print(f"    → MKL-DNN optimization enabled")
            except Exception as e:
                logger.warning(f"Failed to apply CPU optimizations: {e}")

        print("✓ Model ready")
        print()

        # Run inference with performance profile and safety monitor
        # Note: run_inference_batch will show resume info if applicable
        print("="*70)
        results_df = run_inference_batch(dicom_folders, model, config, logger,
                                        performance_profile, safety_monitor)

        # Save results
        output_dir = Path(config.get('paths.output_dir', './output'))
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save current run results (with timestamp)
        output_file = output_dir / f"nb10_results_{timestamp}.csv"
        results_df.to_csv(output_file, index=False, encoding='utf-8-sig')

        # v1.1.3-rc2: If resume is enabled, also save/update complete results
        enable_resume = config.get('processing.enable_resume', True)
        if enable_resume:
            cache_file = output_dir / ".nb10_resume_cache.csv"
            complete_csv = output_dir / "nb10_results_complete.csv"

            # Build complete results from cache (single source of truth)
            if cache_file.exists():
                try:
                    cache_df = pd.read_csv(cache_file)
                    # Only include successful cases
                    complete_df = cache_df[cache_df['status'] == 'success'].copy()

                    # Save complete results
                    complete_df.to_csv(complete_csv, index=False, encoding='utf-8-sig')

                    logger.info(f"Complete results saved: {complete_csv} ({len(complete_df)} cases)")
                except Exception as e:
                    logger.warning(f"Failed to generate complete results: {e}")

        # Show summary
        print()
        print("="*70)
        print("✓ PROCESSING COMPLETE")
        print("="*70)
        success_count = (results_df['status'] == 'success').sum()
        failed_count = (results_df['status'] == 'failed').sum()
        print(f"  Success: {success_count}/{len(dicom_folders)}")
        if failed_count > 0:
            print(f"  Failed:  {failed_count}/{len(dicom_folders)}")
        if success_count > 0:
            mean_score = results_df[results_df['status'] == 'success']['agatston_score'].mean()
            print(f"  Mean Agatston Score: {mean_score:.1f}")
        print()
        print(f"  Results saved to:")
        print(f"    {output_file}")
        print("="*70)
        print()
        print("Next steps:")
        print("  1. Open the results CSV file in Excel to review scores")
        print("  2. Check the log file for detailed information:")
        print(f"     {log_file}")
        print()
        # Note: Pause is handled by start_nb10.bat, no need to pause here

        return 0

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease check:")
        print("  1. Configuration file exists")
        print("  2. Model file exists (run: python deployment/download_models.py)")
        print("  3. Data directory exists")
        return 1

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
