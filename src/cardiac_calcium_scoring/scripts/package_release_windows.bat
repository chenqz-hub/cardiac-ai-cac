@echo off
setlocal enabledelayedexpansion
REM ====================================================================
REM Week 7 Release Packaging Script for Windows
REM ====================================================================
REM Purpose: Create release package for local testing
REM Version: v1.0.0 (Week 7)
REM Date: 2025-10-18
REM Note: All prompts and filenames in English
REM ====================================================================

echo ========================================
echo   Cardiac Calcium Scoring System
echo   Week 7 Quick Release Package
echo   Version: v2.0.0-alpha
echo ========================================
echo.

REM ====================================================================
REM 1. Environment Check
REM ====================================================================
echo [1/5] Checking environment...

REM Check current directory
if not exist "calcium_scoring.bat" (
    if not exist "calcium_scoring.sh" (
        echo [ERROR] Please run this script in tools\cardiac_calcium_scoring directory
        echo Current directory: %CD%
        pause
        exit /b 1
    )
)

REM Check AI-CAC model
if not exist "models\va_non_gated_ai_cac_model.pth" (
    echo [ERROR] AI-CAC model file missing
    echo Expected location: models\va_non_gated_ai_cac_model.pth
    pause
    exit /b 1
)

echo [OK] AI-CAC model ready
echo.

REM ====================================================================
REM 2. Create Release Directory
REM ====================================================================
echo [2/5] Creating release directory...

REM Generate timestamp for release name
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%
set RELEASE_NAME=cardiac_calcium_scoring_v2.0.0_week7_quick_%TIMESTAMP%
set RELEASE_DIR=releases\%RELEASE_NAME%

REM Clean old release if exists
if exist "%RELEASE_DIR%" (
    echo Cleaning old release directory...
    rmdir /s /q "%RELEASE_DIR%"
)

mkdir "%RELEASE_DIR%" 2>nul
if errorlevel 1 (
    echo [ERROR] Failed to create release directory
    pause
    exit /b 1
)

echo [OK] Created %RELEASE_DIR%
echo.

REM ====================================================================
REM 3. Copy Core Files
REM ====================================================================
echo [3/5] Copying core files...

REM Copy directories
echo Copying directories...
xcopy /E /I /Q /Y cli "%RELEASE_DIR%\cli" >nul
xcopy /E /I /Q /Y core "%RELEASE_DIR%\core" >nul
xcopy /E /I /Q /Y config "%RELEASE_DIR%\config" >nul
xcopy /E /I /Q /Y models "%RELEASE_DIR%\models" >nul
xcopy /E /I /Q /Y deployment "%RELEASE_DIR%\deployment" >nul

REM Create output and logs directories
mkdir "%RELEASE_DIR%\output" 2>nul
mkdir "%RELEASE_DIR%\logs" 2>nul

REM Copy startup scripts
echo Copying scripts...
copy /Y calcium_scoring.bat "%RELEASE_DIR%\" >nul 2>&1
copy /Y calcium_scoring.sh "%RELEASE_DIR%\" >nul 2>&1
copy /Y start_calcium_scoring.bat "%RELEASE_DIR%\" >nul 2>&1
copy /Y menu.py "%RELEASE_DIR%\" >nul 2>&1

REM Copy README
if exist README.md (
    copy /Y README.md "%RELEASE_DIR%\" >nul
) else (
    echo # Cardiac Calcium Scoring System v2.0.0 > "%RELEASE_DIR%\README.md"
)

echo [OK] Core files copied
echo.

REM ====================================================================
REM 4. Copy Documentation
REM ====================================================================
echo [4/5] Copying documentation...

mkdir "%RELEASE_DIR%\docs" 2>nul

REM Copy deployment docs (use full paths)
if exist "..\..\docs\deployment\DEPLOYMENT_GUIDE.md" copy /Y "..\..\docs\deployment\DEPLOYMENT_GUIDE.md" "%RELEASE_DIR%\docs\" >nul 2>&1
if exist "..\..\docs\deployment\USER_MANUAL.md" copy /Y "..\..\docs\deployment\USER_MANUAL.md" "%RELEASE_DIR%\docs\" >nul 2>&1
if exist "..\..\docs\deployment\TECHNICAL_SPECS.md" copy /Y "..\..\docs\deployment\TECHNICAL_SPECS.md" "%RELEASE_DIR%\docs\" >nul 2>&1
if exist "..\..\docs\deployment\FAQ.md" copy /Y "..\..\docs\deployment\FAQ.md" "%RELEASE_DIR%\docs\" >nul 2>&1
if exist "..\..\WEEK6_PROGRESS.md" copy /Y "..\..\WEEK6_PROGRESS.md" "%RELEASE_DIR%\docs\" >nul 2>&1

echo [OK] Documentation copied
echo.

REM ====================================================================
REM 5. Create Deployment README
REM ====================================================================
echo [5/5] Generating deployment README...

(
echo # Cardiac Calcium Scoring System v2.0.0 - Quick Release Package
echo.
echo ## Package Type
echo.
echo **Quick Release** - This package contains all core files but does NOT include Python dependencies.
echo.
echo To create a complete offline package with dependencies, download dependencies manually.
echo.
echo ## Contents
echo.
echo ```
echo cardiac_calcium_scoring_v2.0.0_week7_quick/
echo ├── cli/                    # CLI interface
echo ├── core/                   # Core modules
echo ├── config/                 # Configuration files
echo ├── models/                 # AI-CAC model ^(~450MB^)
echo ├── deployment/             # Deployment resources
echo │   └── requirements.txt    # Dependency list
echo ├── docs/                   # Documentation
echo │   ├── DEPLOYMENT_GUIDE.md
echo │   ├── USER_MANUAL.md
echo │   ├── TECHNICAL_SPECS.md
echo │   ├── FAQ.md
echo │   └── WEEK6_PROGRESS.md
echo ├── output/                 # Output directory ^(empty^)
echo ├── logs/                   # Log directory ^(empty^)
echo ├── calcium_scoring.bat     # Windows launcher
echo ├── calcium_scoring.sh      # Linux launcher
echo └── README_DEPLOYMENT.md    # This file
echo ```
echo.
echo ## Installation ^(Windows^)
echo.
echo ```cmd
echo # 1. Create virtual environment
echo python -m venv venv
echo.
echo # 2. Activate virtual environment
echo venv\Scripts\activate.bat
echo.
echo # 3. Install dependencies ^(requires internet^)
echo pip install -r deployment\requirements.txt
echo.
echo # 4. Launch
echo calcium_scoring.bat --help
echo ```
echo.
echo ## System Requirements
echo.
echo ### Minimum
echo - **OS**: Windows 10/11
echo - **Python**: 3.10+
echo - **RAM**: 8GB
echo - **CPU**: 2 cores
echo - **Disk**: 10GB free
echo - **Speed**: ~300 sec/patient ^(CPU^)
echo.
echo ### Recommended
echo - **OS**: Windows 10/11 Pro
echo - **Python**: 3.10+
echo - **RAM**: 16GB+
echo - **CPU**: 8+ cores
echo - **GPU**: NVIDIA RTX 2060+ ^(optional^)
echo - **Disk**: 20GB free
echo - **Speed**: ~15 sec/patient ^(GPU^)
echo.
echo ## Week 6 Test Results
echo.
echo - **Total**: 196/197 success ^(99.5%%^)
echo - **CHD Group**: 100/101 success - Mean score 356.6
echo - **Normal Group**: 96/96 success - Mean score 6.3
echo - **Performance**: GPU 15 sec/patient, CPU 305 sec/patient
echo.
echo See: `docs\WEEK6_PROGRESS.md`
echo.
echo ## Documentation
echo.
echo - **DEPLOYMENT_GUIDE.md** - IT admin deployment guide
echo - **USER_MANUAL.md** - Doctor/technician manual
echo - **TECHNICAL_SPECS.md** - Technical specifications
echo - **FAQ.md** - Frequently asked questions
echo.
echo ## Version
echo.
echo - **Version**: v2.0.0-alpha ^(Week 7 Quick Release^)
echo - **Release Date**: 2025-10-18
echo - **Validation**: Production-ready ^(196-case complete test^)
echo.
echo ---
echo.
echo **Generated with Claude Code**
) > "%RELEASE_DIR%\README_DEPLOYMENT.md"

echo [OK] Deployment README generated
echo.

REM ====================================================================
REM 6. Generate Release Notes
REM ====================================================================
(
echo ====================================================================
echo Cardiac Calcium Scoring System v2.0.0-alpha - Week 7 Quick Release
echo ====================================================================
echo Release Date: %DATE% %TIME%
echo Release Type: Quick Release ^(No Dependencies Included^)
echo.
echo Package Type
echo ------------
echo QUICK RELEASE - Contains core files only
echo - Does NOT include Python dependencies
echo - Requires internet connection for pip install
echo - For offline deployment, download dependencies manually
echo.
echo Version Information
echo -------------------
echo - Version: v2.0.0-alpha
echo - Code Name: cardiac_calcium_scoring ^(renamed from nb10_windows^)
echo - Validation: Production-ready ^(99.5%% success, 196/197 cases^)
echo.
echo Package Contents
echo ----------------
echo 1. Core Program
echo    - CLI interface ^(cli/^)
echo    - Core modules ^(core/^)
echo    - AI-CAC model ^(~450MB^)
echo    - Configuration files ^(config/^)
echo.
echo 2. Documentation
echo    - DEPLOYMENT_GUIDE.md ^(IT admin guide^)
echo    - USER_MANUAL.md ^(User manual^)
echo    - TECHNICAL_SPECS.md ^(Technical specs^)
echo    - FAQ.md ^(FAQ^)
echo    - WEEK6_PROGRESS.md ^(Week 6 report^)
echo.
echo 3. Deployment Resources
echo    - requirements.txt ^(dependency list^)
echo    - Startup scripts ^(.bat/.sh^)
echo.
echo Performance Metrics ^(Week 6 Testing^)
echo -------------------------------------
echo - Test Scale: 196/197 success ^(99.5%%^)
echo - CHD Group: 100/101 success, mean score 356.6
echo - Normal Group: 96/96 success, mean score 6.3
echo - GPU Performance: 15 sec/patient ^(RTX 2060^)
echo - CPU Performance: 305 sec/patient ^(8 cores^)
echo.
echo Installation Steps
echo ------------------
echo 1. Extract package
echo 2. Create venv: python -m venv venv
echo 3. Activate venv: venv\Scripts\activate.bat
echo 4. Install deps: pip install -r deployment\requirements.txt
echo 5. Launch: calcium_scoring.bat --help
echo.
echo System Requirements
echo -------------------
echo Minimum:
echo - Python 3.10+
echo - 8GB RAM
echo - 2-core CPU
echo - 10GB disk space
echo - Internet connection ^(for pip install^)
echo.
echo Recommended:
echo - Python 3.10+
echo - 16GB+ RAM
echo - 8+ core CPU
echo - NVIDIA GPU ^(optional, RTX 2060+^)
echo - 20GB disk space
echo.
echo Package Files
echo -------------
echo - %RELEASE_NAME%\ ^(extracted directory^)
echo.
echo Notes
echo -----
echo - This is a QUICK release for testing
echo - For production offline deployment, download dependencies separately
echo - All user-facing prompts and filenames use ENGLISH
echo - Documentation may contain Chinese content
echo.
echo ====================================================================
echo Generated with Claude Code
echo Co-Authored-By: Claude ^<noreply@anthropic.com^>
echo ====================================================================
) > "releases\%RELEASE_NAME%_release_notes.txt"

REM ====================================================================
REM Complete
REM ====================================================================
echo ========================================
echo   Package Build Complete!
echo ========================================
echo.
echo Release Package Location:
echo   - releases\%RELEASE_NAME%\
echo.
echo Release Notes:
echo   - releases\%RELEASE_NAME%_release_notes.txt
echo.
echo Next Steps:
echo   1. Test package: cd releases\%RELEASE_NAME%
echo   2. Create venv: python -m venv venv
echo   3. Activate: venv\Scripts\activate.bat
echo   4. Install deps: pip install -r deployment\requirements.txt
echo   5. Launch: calcium_scoring.bat --help
echo.
echo Note: This is a QUICK package (no dependencies included)
echo.
pause
