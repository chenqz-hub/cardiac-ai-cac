#!/bin/bash
# NB10 AI-CAC Lite Release Packaging Script (WITHOUT Model) - ENGLISH ONLY
# Usage: ./scripts/package_release_lite_en.sh [version]

set -e

VERSION=${1:-"1.1.3-rc2"}
RELEASE_NAME="nb10-ai-cac-lite-v${VERSION}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="${PROJECT_ROOT}/dist"
PACKAGE_DIR="${DIST_DIR}/${RELEASE_NAME}"

echo "=========================================="
echo "NB10 AI-CAC LITE Release Packaging"
echo "Version: ${VERSION}"
echo "NOTE: Model file NOT included (separate download)"
echo "=========================================="
echo ""

# 1. Clean old builds
echo "[1/8] Cleaning old builds..."
rm -rf "${PACKAGE_DIR}"
mkdir -p "${PACKAGE_DIR}/nb10_windows"

# 2. Copy core files
echo "[2/8] Copying application files..."
cd "${PROJECT_ROOT}"

# Copy core code directories
cp -r cli core config deployment scripts examples "${PACKAGE_DIR}/nb10_windows/"

# Copy documentation
mkdir -p "${PACKAGE_DIR}/nb10_windows/docs"
cp docs/USER_MANUAL.md "${PACKAGE_DIR}/nb10_windows/docs/" 2>/dev/null || true
cp docs/INSTALLATION_GUIDE.md "${PACKAGE_DIR}/nb10_windows/docs/" 2>/dev/null || true
cp docs/PACKAGING_DEPLOYMENT_GUIDE.md "${PACKAGE_DIR}/nb10_windows/docs/" 2>/dev/null || true

# Copy project docs
cp README.md "${PACKAGE_DIR}/nb10_windows/"
cp CHANGELOG.md "${PACKAGE_DIR}/nb10_windows/" 2>/dev/null || echo "# Changelog" > "${PACKAGE_DIR}/nb10_windows/CHANGELOG.md"

# Clean temporary files
echo "  - Cleaning temporary files from nb10_windows root..."
cd "${PACKAGE_DIR}/nb10_windows"
rm -f compare_psm_vs_nonpsm.py integrate_multimodal_data.py investigate_failed_merges.py trace_unmatched_patients.py menu.py
rm -f DOCUMENT_CLEANUP_PLAN.md *_PROGRESS.md *_SUMMARY*.md *_REPORT*.md *_STATUS*.md *_LOG*.md
rm -f QUICK_*.md SESSION_*.md NEXT_*.md FINAL_*.md COLAB_*.md SOLUTION_*.md VALIDATION_*.md README_FIRST.txt
cd "${PROJECT_ROOT}"

# 3. Create directories
echo "[3/8] Creating output directories..."
mkdir -p "${PACKAGE_DIR}/nb10_windows/"{output,logs,data/cache,tests,models}
echo "# Output Directory" > "${PACKAGE_DIR}/nb10_windows/output/README.md"
echo "# Logs Directory" > "${PACKAGE_DIR}/nb10_windows/logs/README.md"
echo "# Cache Directory" > "${PACKAGE_DIR}/nb10_windows/data/cache/README.md"
echo "# Tests Directory" > "${PACKAGE_DIR}/nb10_windows/tests/README.md"

# 4. Create model download instructions
echo "[4/8] Creating model download instructions..."
cat > "${PACKAGE_DIR}/nb10_windows/models/README.md" << 'EOF'
# AI-CAC Model File Download Instructions

**IMPORTANT**: This lite version does NOT include the model file. Download separately.

## Model Information

- **Filename**: `va_non_gated_ai_cac_model.pth`
- **Size**: ~1.2GB
- **Location**: Place in this directory (`models/`)

## Download Methods

### Method 1: From Hospital IT Department

Contact your hospital IT department for the model file.

### Method 2: Cloud Storage

- Baidu Pan: [Link TBD]
- Google Drive: [Link TBD]

### Method 3: Internal Server

If available, copy from: `\\hospital-server\shared\nb10-models\va_non_gated_ai_cac_model.pth`

## Installation Steps

1. Download `va_non_gated_ai_cac_model.pth` (~1.2GB)
2. Place it in: `nb10_windows\models\va_non_gated_ai_cac_model.pth`
3. Verify the file path is correct
4. Run the program

## Verification

```cmd
cd nb10_windows
python -c "import os; print('OK: Model found' if os.path.exists('models/va_non_gated_ai_cac_model.pth') else 'ERROR: Model not found')"
```

## Support

Contact: support@example.com
EOF

cat > "${PACKAGE_DIR}/nb10_windows/models/DOWNLOAD_MODEL.txt" << 'EOF'
================================================================================
Model File Download Instructions
================================================================================

IMPORTANT: This lite version does NOT include the AI model file!

Model File:
  Filename: va_non_gated_ai_cac_model.pth
  Size:     ~1.2GB
  Location: Place in models/ folder

Download Options:
  1. Hospital IT department
  2. Cloud storage (Baidu Pan / Google Drive)
  3. Internal server

After Download:
  models/
  ├── va_non_gated_ai_cac_model.pth  ← Downloaded model
  ├── README.md                       ← Details
  └── DOWNLOAD_MODEL.txt              ← This file

See README.md for detailed instructions.

================================================================================
EOF

# 5. Generate Windows batch files (ENGLISH ONLY)
echo "[5/8] Generating Windows batch scripts (English)..."

mkdir -p "${PACKAGE_DIR}/scripts"

# install_gpu.bat - ENGLISH ONLY
cat > "${PACKAGE_DIR}/scripts/install_gpu.bat" << 'EOF'
@echo off
echo ==========================================
echo NB10 AI-CAC GPU Dependencies Installation
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/5] Python version detected:
python --version
echo.

echo [2/5] Checking model file...
if not exist "nb10_windows\models\va_non_gated_ai_cac_model.pth" (
    echo.
    echo [WARNING] Model file not found
    echo.
    echo Model path: nb10_windows\models\va_non_gated_ai_cac_model.pth
    echo Download instructions: nb10_windows\models\README.md
    echo.
    echo Options:
    echo   1. Abort installation and download model first
    echo   2. Continue installation, download model later
    echo.
    choice /C 12 /M "Select option"
    if errorlevel 2 (
        echo.
        echo Continuing installation...
    ) else (
        echo.
        echo Installation aborted.
        pause
        exit /b 0
    )
) else (
    echo   [OK] Model file found
)
echo.

echo [3/5] Creating virtual environment...
REM Remove old venv if exists to ensure clean install
if exist "venv" (
    echo   [INFO] Removing old virtual environment...
    rmdir /s /q venv
)
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo   [OK] Virtual environment created
echo.

echo [4/5] Upgrading pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
echo   [OK] pip upgraded
echo.

echo [5/5] Installing dependencies (this may take several minutes)...
echo.

REM Check for offline wheels (support nested directories like gpu/cpu)
set "OFFLINE_FOUND=0"
set "OFFLINE_DIR="

REM Priority 1: deployment/offline_wheels/gpu/ (check for actual .whl files)
if exist "nb10_windows\deployment\offline_wheels\gpu\*.whl" (
    set "OFFLINE_DIR=nb10_windows\deployment\offline_wheels\gpu"
    set "OFFLINE_FOUND=1"
)

REM Priority 2: deployment/offline_wheels/ (flat structure)
if %OFFLINE_FOUND%==0 if exist "nb10_windows\deployment\offline_wheels\*.whl" (
    set "OFFLINE_DIR=nb10_windows\deployment\offline_wheels"
    set "OFFLINE_FOUND=1"
)

REM Priority 3: offline_packages/gpu_wheels/
if %OFFLINE_FOUND%==0 if exist "offline_packages\gpu_wheels\*.whl" (
    set "OFFLINE_DIR=offline_packages\gpu_wheels"
    set "OFFLINE_FOUND=1"
)

if %OFFLINE_FOUND%==1 (
    echo   [INFO] Using offline packages ^(no network required^)
    echo   [PATH] %OFFLINE_DIR%
    echo.
    pip install --no-index --find-links=%OFFLINE_DIR% -r nb10_windows\deployment\requirements_gpu.txt
) else (
    echo   [INFO] Downloading from PyPI ^(network required^)
    echo   Note: Downloading PyTorch, MONAI, and other large packages...
    echo.
    pip install -r nb10_windows\deployment\requirements_gpu.txt
)

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies
    echo.
    echo Possible causes:
    echo   1. Network connection issues ^(if online mode^)
    echo   2. Incomplete offline packages ^(if offline mode^)
    echo   3. Incompatible CUDA version
    echo.
    echo Suggestions:
    echo   - Offline mode: Check wheel files in deployment/offline_wheels/gpu/
    echo   - Online mode: Check network or try CPU version ^(install_cpu.bat^)
    pause
    exit /b 1
)

REM Verify installation by checking for key packages
echo.
echo Verifying installation...
python -c "import torch, monai, numpy, pandas" 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] Dependency installation failed or incomplete
    echo Possible causes:
    echo   1. Network connection issues
    echo   2. Incompatible CUDA version
    echo   3. Insufficient disk space
    echo.
    echo Suggestion: Check network or try CPU version ^(install_cpu.bat^)
    pause
    exit /b 1
)
echo   [OK] Key packages verified ^(torch, monai, numpy, pandas^)

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.

REM Check model again
if not exist "nb10_windows\models\va_non_gated_ai_cac_model.pth" (
    echo [REMINDER] Model file still not found
    echo.
    echo Next steps:
    echo   1. Download model file ^(~1.2GB^)
    echo      See: nb10_windows\models\README.md
    echo.
    echo   2. Place model at:
    echo      nb10_windows\models\va_non_gated_ai_cac_model.pth
    echo.
    echo   3. Edit config file:
    echo      nb10_windows\config\config.yaml
    echo.
    echo   4. Run program:
    echo      Double-click run_nb10.bat
    echo.
) else (
    echo Next steps:
    echo   1. Edit config file:
    echo      nb10_windows\config\config.yaml
    echo.
    echo   2. Configure DICOM paths in config.yaml:
    echo      paths:
    echo        data_dir: D:/DICOM_Data
    echo        output_dir: D:/NB10_Results
    echo.
    echo   3. Run program:
    echo      Double-click run_nb10.bat
    echo.
)
pause
EOF

# install_cpu.bat - ENGLISH ONLY
cat > "${PACKAGE_DIR}/scripts/install_cpu.bat" << 'EOF'
@echo off
echo ==========================================
echo NB10 AI-CAC CPU Dependencies Installation
echo ==========================================
echo.
echo Note: CPU mode is slower (~50-100 sec/patient)
echo Recommended: Use NVIDIA GPU for best performance (~10-15 sec/patient)
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/5] Python version detected:
python --version
echo.

echo [2/5] Checking model file...
if not exist "nb10_windows\models\va_non_gated_ai_cac_model.pth" (
    echo.
    echo [WARNING] Model file not found
    echo.
    echo Download instructions: nb10_windows\models\README.md
    echo.
    echo Options:
    echo   1. Abort installation and download model first
    echo   2. Continue installation, download model later
    echo.
    choice /C 12 /M "Select option"
    if errorlevel 2 (
        echo Continuing installation...
    ) else (
        echo Installation aborted.
        pause
        exit /b 0
    )
) else (
    echo   [OK] Model file found
)
echo.

echo [3/5] Creating virtual environment...
REM Remove old venv if exists to ensure clean install
if exist "venv" (
    echo   [INFO] Removing old virtual environment...
    rmdir /s /q venv
)
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo   [OK] Virtual environment created
echo.

echo [4/5] Upgrading pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
echo   [OK] Done
echo.

echo [5/5] Installing dependencies (this may take several minutes)...
echo.

REM Check for offline wheels (support nested directories like gpu/cpu)
set "OFFLINE_FOUND=0"
set "OFFLINE_DIR="

REM Priority 1: deployment/offline_wheels/cpu/ (check for actual .whl files)
if exist "nb10_windows\deployment\offline_wheels\cpu\*.whl" (
    set "OFFLINE_DIR=nb10_windows\deployment\offline_wheels\cpu"
    set "OFFLINE_FOUND=1"
)

REM Priority 2: deployment/offline_wheels/ (flat structure)
if %OFFLINE_FOUND%==0 if exist "nb10_windows\deployment\offline_wheels\*.whl" (
    set "OFFLINE_DIR=nb10_windows\deployment\offline_wheels"
    set "OFFLINE_FOUND=1"
)

REM Priority 3: offline_packages/cpu_wheels/
if %OFFLINE_FOUND%==0 if exist "offline_packages\cpu_wheels\*.whl" (
    set "OFFLINE_DIR=offline_packages\cpu_wheels"
    set "OFFLINE_FOUND=1"
)

if %OFFLINE_FOUND%==1 (
    echo   [INFO] Using offline packages ^(no network required^)
    echo   [PATH] %OFFLINE_DIR%
    echo.
    pip install --no-index --find-links=%OFFLINE_DIR% -r nb10_windows\deployment\requirements_cpu.txt
) else (
    echo   [INFO] Downloading from PyPI ^(network required^)
    echo   Note: Downloading packages from PyPI...
    echo.
    pip install -r nb10_windows\deployment\requirements_cpu.txt
)

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies
    echo.
    echo Possible causes:
    echo   1. Network connection issues ^(if online mode^)
    echo   2. Incomplete offline packages ^(if offline mode^)
    echo   3. Incompatible package versions
    echo.
    echo Suggestions:
    echo   - Offline mode: Check wheel files in deployment/offline_wheels/cpu/
    echo   - Online mode: Check network connection and try again
    pause
    exit /b 1
)

REM Verify installation by checking for key packages
echo.
echo Verifying installation...
python -c "import torch, monai, numpy, pandas" 2>nul
if errorlevel 1 (
    echo [ERROR] Dependency installation failed or incomplete
    pause
    exit /b 1
)
echo   [OK] Key packages verified

echo.
echo ==========================================
echo Installation Complete!
echo ==========================================
echo.

if not exist "nb10_windows\models\va_non_gated_ai_cac_model.pth" (
    echo [REMINDER] Please download model file
    echo See: nb10_windows\models\README.md
    echo.
)

echo Next steps:
echo   1. Download model file (if not done)
echo   2. Edit config: nb10_windows\config\config.yaml
echo   3. Run program: Double-click run_nb10.bat
echo.
pause
EOF

# run_nb10.bat - ENGLISH ONLY
cat > "${PACKAGE_DIR}/scripts/run_nb10.bat" << 'EOF'
@echo off
echo ==========================================
echo NB10 AI-CAC Launcher
echo ==========================================
echo.

REM Check virtual environment
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found
    echo.
    echo Please run one of the following first:
    echo   ^- install_gpu.bat  ^(GPU version, recommended^)
    echo   ^- install_cpu.bat  ^(CPU version^)
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check model file
if not exist "nb10_windows\models\va_non_gated_ai_cac_model.pth" (
    echo [ERROR] Model file not found
    echo.
    echo Model path: nb10_windows\models\va_non_gated_ai_cac_model.pth
    echo Download instructions: nb10_windows\models\README.md
    echo.
    pause
    exit /b 1
)

echo [OK] Environment check passed
echo.

REM Enter working directory
cd nb10_windows

echo ==========================================
echo Usage Instructions
echo ==========================================
echo.
echo Command format:
echo   python cli\run_nb10.py [options]
echo.
echo Common options:
echo   --data-dir PATH      DICOM data directory
echo   --mode MODE          pilot (test) or full (complete)
echo   --pilot-limit N      Process N cases in pilot mode
echo.
echo Example:
echo   python cli\run_nb10.py --data-dir "D:\DICOM_Data" --mode pilot --pilot-limit 5
echo.
echo ==========================================
echo.

REM Display help
python cli\run_nb10.py --help

echo.
echo Press any key to exit...
pause >nul
EOF

# check_environment.bat - ENVIRONMENT DIAGNOSTIC TOOL (ENGLISH ONLY)
cat > "${PACKAGE_DIR}/check_environment.bat" << 'EOF'
@echo off
REM =========================================
REM NB10 Environment Check Script
REM =========================================

echo =========================================
echo NB10 Environment Diagnostic Tool
echo =========================================
echo.

echo [1] Checking Python...
python --version 2>nul
if errorlevel 1 (
    echo [FAILED] Python not found in PATH
    echo.
    echo Possible solutions:
    echo   1. Install Python 3.10 from: https://www.python.org/downloads/
    echo   2. During installation, CHECK 'Add Python to PATH'
    echo   3. Restart this script after installation
    echo.
) else (
    echo [OK] Python found:
    python --version
    echo.
)

echo [2] Checking pip...
python -m pip --version 2>nul
if errorlevel 1 (
    echo [FAILED] pip not found
) else (
    echo [OK] pip found:
    python -m pip --version
    echo.
)

echo [3] Checking NVIDIA GPU...
nvidia-smi --version 2>nul
if errorlevel 1 (
    echo [INFO] NVIDIA GPU not detected ^(will use CPU mode^)
    echo [NOTE] CPU mode is slower but works
) else (
    echo [OK] NVIDIA GPU detected:
    nvidia-smi --query-gpu=name --format=csv,noheader 2>nul
    echo.
)

echo [4] Checking model file...
if exist "nb10_windows\models\va_non_gated_ai_cac_model.pth" (
    echo [OK] Model file found
) else (
    echo [WARNING] Model file not found
    echo [PATH] nb10_windows\models\va_non_gated_ai_cac_model.pth
    echo [ACTION] Download model file ^(~1.2GB^) before running
)
echo.

echo [5] Checking virtual environment...
if exist "venv\Scripts\activate.bat" (
    echo [OK] Virtual environment exists
) else (
    echo [INFO] Virtual environment not created yet
    echo [ACTION] Will be created during installation
)
echo.

echo =========================================
echo Diagnostic Complete
echo =========================================
echo.
echo Next steps:
echo   1. If Python is missing, install it first
echo   2. If Python is installed, run: start_nb10.bat
echo   3. For help, see README.txt
echo.
pause
EOF

# start_nb10.bat - ONE-CLICK LAUNCHER (ENGLISH ONLY)
# Version is substituted here, rest uses literal heredoc
cat > "${PACKAGE_DIR}/start_nb10.bat" <<STARTEOF
@echo off
REM =========================================
REM NB10 AI-CAC One-Click Launcher
REM Version: v${VERSION}
REM Features: Auto-detect and install/run NB10
REM =========================================

setlocal enabledelayedexpansion

echo =========================================
echo NB10 AI-CAC Coronary Calcium Scoring
echo One-Click Launcher v${VERSION}
echo =========================================
echo.
STARTEOF

cat >> "${PACKAGE_DIR}/start_nb10.bat" <<'EOF'

REM Check installation status
if exist "venv\Scripts\python.exe" (
    set "INSTALL_STATUS=installed"
    echo [OK] Virtual environment detected
    echo.
) else (
    echo [INFO] First-time setup starting...
    set "INSTALL_STATUS=not_installed"
    echo.
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo.
    echo Please install Python 3.10 or higher:
    echo   Download: https://www.python.org/downloads/
    echo   IMPORTANT: Check 'Add Python to PATH' during installation
    echo.
    pause
    exit /b 1
)

REM Check GPU (only if not installed)
if "%INSTALL_STATUS%"=="not_installed" (
    nvidia-smi >nul 2>&1
    if errorlevel 1 (
        set "GPU_MODE=cpu"
        set "INSTALL_SCRIPT=scripts\install_cpu.bat"
    ) else (
        set "GPU_MODE=gpu"
        set "INSTALL_SCRIPT=scripts\install_gpu.bat"
    )
)

REM Check model file
set "MODEL_PATH=nb10_windows\models\va_non_gated_ai_cac_model.pth"
if exist "%MODEL_PATH%" (
    set "MODEL_STATUS=found"
    echo [OK] Model file found
    echo.
) else (
    set "MODEL_STATUS=not_found"
    echo [WARNING] Model file not found: %MODEL_PATH% ^(~1.2GB^)
    echo.
    if "%INSTALL_STATUS%"=="not_installed" (
        echo Continue installing other components? ^(Y/N^)
        set /p CONTINUE_INSTALL=
        if /i "!CONTINUE_INSTALL!" neq "Y" (
            echo Installation cancelled.
            pause
            exit /b 0
        )
        echo.
    )
)

REM Execute installation (if needed)
if "%INSTALL_STATUS%"=="not_installed" (
    echo [INSTALL] Installing dependencies ^(!GPU_MODE! mode^)...
    echo.

    call %INSTALL_SCRIPT%
    if errorlevel 1 (
        echo.
        echo [ERROR] Installation failed
        echo.
        echo Possible causes:
        echo   ^- Network connection issues
        echo   ^- Insufficient disk space
        echo   ^- Incompatible Python version
        echo.
        pause
        exit /b 1
    )
)

REM Recheck model file (after install)
if not exist "%MODEL_PATH%" (
    echo.
    echo [ERROR] Model file is required to run NB10
    echo.
    echo   Model path: %MODEL_PATH%
    echo   Model size: ~1.2GB
    echo.
    echo   Download instructions: nb10_windows\models\README.md
    echo   Configuration file: nb10_windows\config\config.yaml
    echo.
    echo Please download the model file first, then run this script again.
    echo.
    pause
    exit /b 1
)

REM Verify dependencies if venv already exists
if "%INSTALL_STATUS%"=="installed" (
    call venv\Scripts\activate.bat
    python -c "import pandas, torch, monai, numpy" 2>nul
    if errorlevel 1 (
        echo [ERROR] Virtual environment exists but required packages are missing
        echo.
        echo This usually means installation was incomplete or interrupted.
        echo.
        echo Solution:
        echo   1. Delete the venv folder:  rmdir /s /q venv
        echo   2. Re-run this script to reinstall
        echo.
        pause
        exit /b 1
    )
)

REM Activate venv and launch
echo [OK] All prerequisites met
echo.
echo Starting NB10...
echo   Please wait while loading AI model and libraries (~30 seconds)...
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found
    echo   Delete 'venv' folder and re-run this script
    echo.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Python not found in venv
    echo   Delete 'venv' folder and re-run this script
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Enter nb10_windows directory
cd nb10_windows

REM Run using activated Python (with full virtual environment)
python cli\run_nb10.py

REM Return to parent directory
cd ..

echo.
pause
EOF

# 6. Generate release documents
echo "[6/8] Generating release documents..."

cat > "${PACKAGE_DIR}/README.txt" << EOF
================================================================================
NB10 AI-CAC Coronary Calcium Scoring Tool v${VERSION} (Lite Edition)
================================================================================

IMPORTANT: This is a lite version. Model file requires separate download (~1.2GB)

[KEY FEATURES]
  - Automatic DICOM data processing
  - AI-powered calcium detection
  - Agatston score calculation
  - Hardware adaptive optimization (Phase 1: +17.2% performance)
  - Safety monitoring system (Phase 2: OOM protection)

[SYSTEM REQUIREMENTS]
  Recommended:
    - Windows 10/11 (64-bit)
    - NVIDIA GPU (RTX 2060+, 6GB+ VRAM)
    - 8GB+ System RAM
    - 10GB Disk space

  Minimum:
    - Windows 10/11 (64-bit)
    - CPU mode (slower, 50-100 sec/patient)
    - 4GB+ System RAM
    - 10GB Disk space

[QUICK START - One-Click Launch (Recommended)]
  Double-click: start_nb10.bat
  Auto: Environment detection -> Auto-install -> Run

  This is all you need! Other batch files are in scripts\ directory
  and will be called automatically by start_nb10.bat.

[DIRECTORY STRUCTURE]
  nb10-ai-cac-lite/
  ├── start_nb10.bat          <- [RECOMMENDED] One-click launcher
  ├── check_environment.bat   <- Environment diagnostic tool
  ├── README.txt              <- This file
  ├── VERSION.txt             <- Version info
  ├── CHANGELOG.txt           <- Change log
  ├── scripts/                <- Helper scripts (auto-called)
  │   ├── install_gpu.bat     <- GPU install script
  │   ├── install_cpu.bat     <- CPU install script
  │   └── run_nb10.bat        <- Manual run script
  └── nb10_windows/           <- Main program directory
      ├── cli/                <- Command-line tools
      ├── core/               <- Core code
      ├── config/             <- Config files
      ├── models/             <- Model directory (download required)
      └── docs/               <- Documentation

[INSTALLATION STEPS]
  1. Extract to C: drive (avoid Chinese characters in path)
     Recommended: C:\nb10-ai-cac-lite\

  2. Download model file (IMPORTANT!)
     See: nb10_windows\models\README.md
     Size: ~1.2GB
     Place at: nb10_windows\models\va_non_gated_ai_cac_model.pth

  3. Install Python (if not installed)
     Download: https://www.python.org/downloads/
     Version: Python 3.10 or higher
     IMPORTANT: Check "Add Python to PATH" during installation

  4. One-Click Launch
     Double-click: start_nb10.bat
     Auto:
       - Detect Python
       - Detect GPU/CPU
       - Check model file
       - Install dependencies
       - Launch program

  5. Configure data paths (after first run)
     Edit: nb10_windows\config\config.yaml
     Modify paths:
       paths:
         data_dir: "D:/DICOM_Data"
         output_dir: "D:/NB10_Results"

[ADVANCED USERS - Manual Installation]
  If you need manual control:

  1. Install dependencies
     GPU version: Double-click scripts\install_gpu.bat
     CPU version: Double-click scripts\install_cpu.bat

  2. Run program
     Double-click scripts\run_nb10.bat

[LITE EDITION NOTES]
  - Package size: ~300MB (without model)
  - Model file: Separate download, ~1.2GB
  - Advantage: Fast distribution, network-friendly
  - Note: Must download model before first use

[PERFORMANCE]
  GPU mode (RTX 2060): 10-15 sec/patient
  CPU mode: 50-100 sec/patient

[DOCUMENTATION]
  User Manual: nb10_windows/docs/USER_MANUAL.md
  Installation Guide: nb10_windows/docs/INSTALLATION_GUIDE.md
  Deployment Guide: nb10_windows/docs/PACKAGING_DEPLOYMENT_GUIDE.md

[TECHNICAL SUPPORT]
  Email: support@example.com

[COPYRIGHT]
  © 2025 Chen Doctor Team. All rights reserved.
  For medical research use only. Commercial use prohibited.

================================================================================
EOF

cat > "${PACKAGE_DIR}/VERSION.txt" << EOF
NB10 AI-CAC v${VERSION} (Lite Edition - English)
Build Date: $(date +%Y-%m-%d)
Git Commit: $(cd "${PROJECT_ROOT}" && git rev-parse --short HEAD 2>/dev/null || echo "unknown")
Package Type: LITE (Model NOT included)

================================================================================
Features
================================================================================
- Phase 1: Hardware Adaptive Optimization (+17.2% performance)
- Phase 2: Safety Monitoring System (OOM protection)
- Automatic hardware detection
- Multi-tier performance profiles
- Real-time resource monitoring

================================================================================
Package Information
================================================================================
Package Type: Lite Edition (English)
Package Size: ~300MB (without model)
Model File: SEPARATE DOWNLOAD REQUIRED
  - File: va_non_gated_ai_cac_model.pth
  - Size: ~1.2GB
  - Location: nb10_windows/models/
  - Download: See nb10_windows/models/README.md

================================================================================
Compatibility
================================================================================
Operating System: Windows 10/11 (64-bit)
Python: 3.10+
GPU: CUDA 11.7+ (optional, recommended)
CPU: Supported (slower)

================================================================================
Build Information
================================================================================
Built on: $(date +"%Y-%m-%d %H:%M:%S")
Platform: $(uname -s) $(uname -m)
Git Branch: $(cd "${PROJECT_ROOT}" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
Git Commit: $(cd "${PROJECT_ROOT}" && git rev-parse HEAD 2>/dev/null || echo "unknown")

================================================================================
EOF

cat > "${PACKAGE_DIR}/CHANGELOG.txt" << EOF
# Changelog

## [${VERSION}] - $(date +%Y-%m-%d)

### Added
- Phase 1: Hardware Adaptive Optimization (+17.2% performance)
- Phase 2: Safety Monitoring System (OOM protection)
- Automatic hardware detection
- Multi-tier performance profiles
- Real-time resource monitoring
- All batch files in English (no encoding issues)

### Package Info
- **Lite Edition**: Model file NOT included
- Model file requires separate download (~1.2GB)
- Reduced package size for faster distribution
- All messages in English to avoid encoding issues

### Documentation
- Complete user manual
- Installation guide
- Packaging and deployment guide

### Fixed (v1.0.10)
- **CRITICAL**: Fixed installation verification logic in batch files
  - Previous versions showed "Installation failed" even when successful
  - Now verifies actual package imports (torch, monai, numpy, pandas)
  - Installation success determined by checking key dependencies, not pip exit code
- Memory management improvements
- GPU cache optimization
- Error handling enhancements
- Windows batch file encoding issues (Chinese characters removed)

================================================================================
EOF

# 7. Clean development files
echo "[7/8] Cleaning development files..."
cd "${PACKAGE_DIR}/nb10_windows"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name ".DS_Store" -delete 2>/dev/null || true
find . -type f -name "*.log" -delete 2>/dev/null || true
rm -rf .git .gitignore .pytest_cache 2>/dev/null || true
cd - >/dev/null

# 8. Create archive
echo "[8/8] Creating archive..."
cd "${DIST_DIR}"
if command -v zip >/dev/null 2>&1; then
    zip -r "${RELEASE_NAME}.zip" "${RELEASE_NAME}/" -q
    ARCHIVE_FILE="${RELEASE_NAME}.zip"
    echo "  ✓ ZIP archive created"
else
    tar -czf "${RELEASE_NAME}.tar.gz" "${RELEASE_NAME}/"
    ARCHIVE_FILE="${RELEASE_NAME}.tar.gz"
    echo "  ✓ TAR.GZ archive created"
fi
cd - >/dev/null

# 9. Generate checksum
echo ""
echo "Generating checksums..."
cd "${DIST_DIR}"
sha256sum "${ARCHIVE_FILE}" > "${ARCHIVE_FILE}.sha256"
cd - >/dev/null

# 10. Complete
echo ""
echo "=========================================="
echo "✓ LITE Package created successfully!"
echo "=========================================="
echo ""
echo "Output:"
echo "  Directory: ${PACKAGE_DIR}/"
echo "  Archive:   ${DIST_DIR}/${ARCHIVE_FILE}"
echo "  Checksum:  ${DIST_DIR}/${ARCHIVE_FILE}.sha256"
echo ""

if [ -f "${DIST_DIR}/${ARCHIVE_FILE}" ]; then
    ARCHIVE_SIZE=$(du -sh "${DIST_DIR}/${ARCHIVE_FILE}" | cut -f1)
    echo "Archive size: ${ARCHIVE_SIZE}"
fi

echo "Model file:   NOT included (separate download required)"
echo ""
echo "⚠️  IMPORTANT:"
echo "  All batch files are in ENGLISH to avoid encoding issues"
echo "  Users must download model file separately (~1.2GB)"
echo "  Download instructions: nb10_windows/models/README.md"
echo ""
echo "Next steps:"
echo "  1. Test the package on Windows"
echo "  2. Verify all batch files run without encoding errors"
echo "  3. Distribute both:"
echo "     - ${ARCHIVE_FILE} (app, ~100KB)"
echo "     - va_non_gated_ai_cac_model.pth (model, ~1.2GB)"
echo ""
