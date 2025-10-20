#!/usr/bin/env python3
"""
Download AI-CAC Model File

Downloads the VA Non-Gated AI-CAC model (1.12 GB) from Google Drive.
"""

import sys
import os
from pathlib import Path
import requests
from tqdm import tqdm


__version__ = "1.0.0"


# Model information
MODEL_INFO = {
    'name': 'va_non_gated_ai_cac_model.pth',
    'size_gb': 1.12,
    'google_drive_id': '1uD12kphnWlJ5R6K-mDQnxS8LjYhPGSfm',
    'description': 'U.S. Department of Veterans Affairs Non-Gated AI-CAC Model'
}


def get_confirm_token(response):
    """Extract confirmation token from Google Drive response"""
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None


def download_from_google_drive(file_id: str, destination: Path):
    """
    Download file from Google Drive

    Args:
        file_id: Google Drive file ID
        destination: Destination file path
    """
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params={'id': file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    # Get file size
    total_size = int(response.headers.get('content-length', 0))

    # Download with progress bar
    with open(destination, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=destination.name) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))


def main():
    """Main entry point"""
    print("="*70)
    print("NB10 AI-CAC Model Downloader")
    print("="*70)
    print()

    # Determine models directory
    script_dir = Path(__file__).parent
    models_dir = script_dir.parent / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    model_path = models_dir / MODEL_INFO['name']

    # Check if model already exists
    if model_path.exists():
        file_size_gb = model_path.stat().st_size / (1024**3)
        print(f"Model file already exists: {model_path}")
        print(f"Size: {file_size_gb:.2f} GB")
        print()

        response = input("Re-download? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Skipped. Using existing model file.")
            return 0

    # Display model information
    print(f"Model: {MODEL_INFO['description']}")
    print(f"File: {MODEL_INFO['name']}")
    print(f"Size: {MODEL_INFO['size_gb']:.2f} GB")
    print(f"Destination: {model_path}")
    print()

    # Confirm download
    print("⚠️ This will download ~1.12 GB of data.")
    response = input("Continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Aborted.")
        return 0

    print()
    print("Downloading model from Google Drive...")
    print("This may take several minutes depending on your network speed.")
    print()

    try:
        # Download
        download_from_google_drive(MODEL_INFO['google_drive_id'], model_path)

        print()
        print("="*70)
        print("✓ Model downloaded successfully!")
        print("="*70)
        print(f"Location: {model_path}")
        print(f"Size: {model_path.stat().st_size / (1024**3):.2f} GB")
        print()
        print("You can now run NB10 with:")
        print("  python cli/run_nb10.py --config config/config.yaml")
        print()

        return 0

    except Exception as e:
        print()
        print("="*70)
        print(f"✗ Download failed: {e}")
        print("="*70)
        print()
        print("Alternative download methods:")
        print("1. Manual download from Google Drive:")
        print(f"   https://drive.google.com/file/d/{MODEL_INFO['google_drive_id']}/view")
        print(f"   Save to: {model_path}")
        print()
        print("2. Use gdown (if installed):")
        print(f"   gdown {MODEL_INFO['google_drive_id']} -O {model_path}")
        print()
        print("3. Contact the research team for alternative download links")
        print()

        # Clean up partial download
        if model_path.exists():
            model_path.unlink()

        return 1


if __name__ == "__main__":
    sys.exit(main())
