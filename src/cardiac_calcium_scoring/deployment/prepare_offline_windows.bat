@echo off
REM ============================================================
REM NB10 Offline Package Preparation (Windows)
REM ============================================================
REM
REM Purpose: Prepare complete offline installation packages
REM Platform: Windows (NOT WSL/Linux!)
REM Requirements: Python, pip, internet connection
REM Output: deployment/offline_wheels/cpu/ and gpu/
REM
REM ============================================================

echo ============================================================
echo NB10 Offline Package Preparation for Windows
echo ============================================================
echo.
echo This will download ~5GB of packages for offline installation.
echo.
echo Requirements:
echo   - Windows OS (NOT WSL/Linux!)
echo   - Python 3.10, 3.11, or 3.12
echo   - Internet connection
echo   - ~5GB free disk space
echo.
echo Output directories:
echo   - deployment\offline_wheels\cpu\  (~1.5GB)
echo   - deployment\offline_wheels\gpu\  (~3.5GB)
echo.

REM Detect script directory and set working directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%.."

echo Current working directory: %CD%
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python first:
    echo   https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected:
python --version
echo.

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip not found!
    echo.
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo [OK] pip detected:
pip --version
echo.

REM Confirm with user
echo ============================================================
echo Ready to Download
echo ============================================================
echo.
echo This will:
echo   1. Create offline_wheels directories
echo   2. Download CPU packages (~1.5GB, 15-30 min)
echo   3. Download GPU packages (~3.5GB, 20-40 min)
echo.
echo Press Ctrl+C to cancel, or
pause

REM Create directories
echo.
echo [1/4] Creating directories...
if not exist "deployment\offline_wheels\cpu" mkdir "deployment\offline_wheels\cpu"
if not exist "deployment\offline_wheels\gpu" mkdir "deployment\offline_wheels\gpu"
echo   [OK] Directories created
echo.

REM Download CPU packages
echo [2/4] Downloading CPU packages (~1.5GB)...
echo   This may take 15-30 minutes depending on network speed
echo   Location: deployment\offline_wheels\cpu\
echo.

pip download -r deployment\requirements_cpu.txt -d deployment\offline_wheels\cpu\

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to download CPU packages
    echo.
    echo Possible causes:
    echo   - Network connection issues
    echo   - Insufficient disk space
    echo   - PyPI temporary unavailable
    echo.
    pause
    exit /b 1
)

echo.
echo   [OK] CPU packages downloaded successfully
echo.

REM Download GPU packages
echo [3/4] Downloading GPU packages (~3.5GB)...
echo   This may take 20-40 minutes depending on network speed
echo   Location: deployment\offline_wheels\gpu\
echo.

pip download -r deployment\requirements_gpu.txt -d deployment\offline_wheels\gpu\

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to download GPU packages
    echo.
    echo Possible causes:
    echo   - Network connection issues
    echo   - Insufficient disk space
    echo   - PyPI temporary unavailable
    echo.
    pause
    exit /b 1
)

echo.
echo   [OK] GPU packages downloaded successfully
echo.

REM Verify downloads
echo [4/4] Verifying downloads...

set "CPU_COUNT=0"
for %%f in (deployment\offline_wheels\cpu\*.whl) do set /a CPU_COUNT+=1

set "GPU_COUNT=0"
for %%f in (deployment\offline_wheels\gpu\*.whl) do set /a GPU_COUNT+=1

echo   CPU packages: %CPU_COUNT% files
echo   GPU packages: %GPU_COUNT% files

if %CPU_COUNT% LSS 10 (
    echo.
    echo [WARNING] CPU packages seem incomplete (less than 10 files)
    echo   Expected: ~40 files
    echo   Found: %CPU_COUNT% files
    echo.
)

if %GPU_COUNT% LSS 10 (
    echo.
    echo [WARNING] GPU packages seem incomplete (less than 10 files)
    echo   Expected: ~40 files
    echo   Found: %GPU_COUNT% files
    echo.
)

REM Show directory sizes
echo.
echo Directory sizes:
dir deployment\offline_wheels\cpu\ | find "File(s)"
dir deployment\offline_wheels\gpu\ | find "File(s)"

echo.
echo ============================================================
echo Download Complete!
echo ============================================================
echo.
echo Next steps:
echo   1. Verify package counts (should be ~40 files each)
echo   2. Package entire nb10_windows folder for distribution
echo   3. See DISTRIBUTION_GUIDE.md for packaging instructions
echo.
echo Distribution package will include:
echo   - Application code (~10MB)
echo   - CPU offline wheels (~1.5GB)
echo   - GPU offline wheels (~3.5GB)
echo   - AI model file (~1.2GB, download separately)
echo   Total: ~6-7GB
echo.
pause
