#!/bin/bash
#
# Offline Deployment Package Creation Script
# 离线部署包创建脚本
#
# Creates complete offline installation package for Cardiac Calcium Scoring (NB10)
# 为冠脉钙化评分模块创建完整离线安装包
#
# Per WEEK7_PLUS_DEPLOYMENT_PLAN.md Section 3:
# - All scripts in English (i18n compliance)
# - Include pip offline packages
# - Include AI-CAC model (1.2GB)
# - Test on CPU-only environment
#
# Author: Cardiac ML Research Team
# Created: 2025-10-19
# Version: 1.0.0

set -e  # Exit on error

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
MODULE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
MODULE_NAME="cardiac_calcium_scoring"
VERSION="1.1.4"
PACKAGE_NAME="${MODULE_NAME}_offline_v${VERSION}"
OUTPUT_DIR="${MODULE_DIR}/dist"
TEMP_DIR="${OUTPUT_DIR}/${PACKAGE_NAME}"

# Colors for output (English messages)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Helper Functions
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "========================================================================"
    echo "$1"
    echo "========================================================================"
    echo ""
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 is not installed or not in PATH"
        return 1
    fi
    return 0
}

get_size_mb() {
    local path="$1"
    if [ -d "$path" ]; then
        du -sm "$path" | cut -f1
    elif [ -f "$path" ]; then
        stat -c%s "$path" 2>/dev/null | awk '{print int($1/1024/1024)}' || \
        stat -f%z "$path" 2>/dev/null | awk '{print int($1/1024/1024)}'
    else
        echo "0"
    fi
}

# ============================================================================
# Main Functions
# ============================================================================

check_prerequisites() {
    print_header "Step 1/6: Checking Prerequisites"

    log_info "Checking required commands..."

    check_command python3 || exit 1
    check_command pip3 || exit 1
    check_command tar || exit 1

    log_success "All required commands are available"

    # Check if in virtual environment
    if [ -z "$VIRTUAL_ENV" ]; then
        log_warning "Not in virtual environment. Activating venv..."
        if [ -f "${PROJECT_ROOT}/venv/bin/activate" ]; then
            source "${PROJECT_ROOT}/venv/bin/activate"
            log_success "Virtual environment activated"
        else
            log_error "Virtual environment not found at ${PROJECT_ROOT}/venv"
            exit 1
        fi
    else
        log_info "Virtual environment: $VIRTUAL_ENV"
    fi

    # Check Python version
    python_version=$(python3 --version | awk '{print $2}')
    log_info "Python version: $python_version"
}

create_package_structure() {
    print_header "Step 2/6: Creating Package Structure"

    # Clean and create temp directory
    if [ -d "$TEMP_DIR" ]; then
        log_info "Removing existing package directory..."
        rm -rf "$TEMP_DIR"
    fi

    mkdir -p "$TEMP_DIR"
    log_success "Created package directory: $TEMP_DIR"

    # Create subdirectories
    mkdir -p "${TEMP_DIR}/module"
    mkdir -p "${TEMP_DIR}/dependencies"
    mkdir -p "${TEMP_DIR}/models"
    mkdir -p "${TEMP_DIR}/scripts"
    mkdir -p "${TEMP_DIR}/docs"
    mkdir -p "${TEMP_DIR}/shared"

    log_success "Created package subdirectories"
}

copy_module_files() {
    print_header "Step 3/6: Copying Module Files"

    log_info "Copying module source code..."

    # Copy main module directories
    for dir in cli config core data examples scripts tools; do
        if [ -d "${MODULE_DIR}/${dir}" ]; then
            cp -r "${MODULE_DIR}/${dir}" "${TEMP_DIR}/module/"
            log_info "  Copied: ${dir}/"
        fi
    done

    # Copy individual files
    for file in menu.py README.md CHANGELOG.md HOW_TO_RUN.md module_info.yaml; do
        if [ -f "${MODULE_DIR}/${file}" ]; then
            cp "${MODULE_DIR}/${file}" "${TEMP_DIR}/module/"
            log_info "  Copied: ${file}"
        fi
    done

    # Copy shared modules
    log_info "Copying shared modules..."
    if [ -d "${PROJECT_ROOT}/shared" ]; then
        # Copy only necessary shared modules
        for dir in data hardware models processing utils menu i18n; do
            if [ -d "${PROJECT_ROOT}/shared/${dir}" ]; then
                mkdir -p "${TEMP_DIR}/shared/${dir}"
                cp -r "${PROJECT_ROOT}/shared/${dir}"/* "${TEMP_DIR}/shared/${dir}/"
                log_info "  Copied shared: ${dir}/"
            fi
        done

        # Copy shared __init__.py
        if [ -f "${PROJECT_ROOT}/shared/__init__.py" ]; then
            cp "${PROJECT_ROOT}/shared/__init__.py" "${TEMP_DIR}/shared/"
        fi
    fi

    log_success "Module files copied successfully"

    # Get module size
    module_size=$(get_size_mb "${TEMP_DIR}/module")
    shared_size=$(get_size_mb "${TEMP_DIR}/shared")
    log_info "Module size: ${module_size}MB"
    log_info "Shared modules size: ${shared_size}MB"
}

download_dependencies() {
    print_header "Step 4/6: Downloading Python Dependencies"

    log_info "Downloading pip packages (CPU version)..."

    # Use CPU requirements
    req_file="${MODULE_DIR}/deployment/requirements_cpu.txt"

    if [ ! -f "$req_file" ]; then
        log_error "Requirements file not found: $req_file"
        exit 1
    fi

    log_info "Using requirements: $req_file"

    # Download packages
    pip3 download -r "$req_file" -d "${TEMP_DIR}/dependencies" --no-deps 2>&1 | grep -v "Requirement already satisfied" || true

    # Also download with dependencies for completeness
    log_info "Downloading packages with dependencies..."
    pip3 download -r "$req_file" -d "${TEMP_DIR}/dependencies" 2>&1 | grep -v "Requirement already satisfied" || true

    # Count downloaded packages
    wheel_count=$(ls -1 "${TEMP_DIR}/dependencies" | wc -l)
    dep_size=$(get_size_mb "${TEMP_DIR}/dependencies")

    log_success "Downloaded ${wheel_count} packages (${dep_size}MB)"
}

copy_models() {
    print_header "Step 5/6: Copying AI Models"

    log_info "Checking for AI-CAC model..."

    model_file="${MODULE_DIR}/models/va_non_gated_ai_cac_model.pth"

    if [ -f "$model_file" ]; then
        log_info "Copying AI-CAC model..."
        cp "$model_file" "${TEMP_DIR}/models/"

        model_size=$(get_size_mb "$model_file")
        log_success "Model copied (${model_size}MB)"
    else
        log_warning "AI-CAC model not found at: $model_file"
        log_warning "Please download model manually or run: python3 deployment/download_models.py"
    fi
}

create_installation_scripts() {
    print_header "Step 6/6: Creating Installation Scripts"

    log_info "Creating installation scripts..."

    # Create install.sh (Linux/Mac)
    cat > "${TEMP_DIR}/install.sh" <<'INSTALL_SH_EOF'
#!/bin/bash
#
# Offline Installation Script for Cardiac Calcium Scoring
# 冠脉钙化评分离线安装脚本
#
# Usage: ./install.sh
#
# Author: Cardiac ML Research Team
# Version: 1.0.0

set -e

# English-only output (per i18n guidelines)
echo "========================================================================"
echo "Cardiac Calcium Scoring - Offline Installation"
echo "Version: 1.1.4"
echo "========================================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    exit 1
fi

python_version=$(python3 --version)
echo "[INFO] Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
    echo "[SUCCESS] Virtual environment created"
else
    echo "[INFO] Virtual environment already exists"
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

# Install dependencies from offline packages
echo "[INFO] Installing dependencies from offline packages..."
pip3 install --no-index --find-links=dependencies -r module/config/requirements_cpu.txt

# Copy shared modules
echo "[INFO] Setting up shared modules..."
mkdir -p ../../../shared
cp -r shared/* ../../../shared/

# Copy module
echo "[INFO] Setting up module..."
mkdir -p ../../../tools/cardiac_calcium_scoring
cp -r module/* ../../../tools/cardiac_calcium_scoring/

# Copy models
if [ -d "models" ] && [ "$(ls -A models)" ]; then
    echo "[INFO] Copying AI models..."
    mkdir -p ../../../tools/cardiac_calcium_scoring/models
    cp models/* ../../../tools/cardiac_calcium_scoring/models/
fi

echo ""
echo "========================================================================"
echo "Installation Complete!"
echo "========================================================================"
echo ""
echo "To run the module:"
echo "  cd ../../../tools/cardiac_calcium_scoring"
echo "  source ../../venv/bin/activate"
echo "  python3 menu.py"
echo ""
INSTALL_SH_EOF

    chmod +x "${TEMP_DIR}/install.sh"
    log_success "Created: install.sh"

    # Create install.bat (Windows)
    cat > "${TEMP_DIR}/install.bat" <<'INSTALL_BAT_EOF'
@echo off
REM Offline Installation Script for Cardiac Calcium Scoring (Windows)
REM Version: 1.0.0

echo ========================================================================
echo Cardiac Calcium Scoring - Offline Installation
echo Version: 1.1.4
echo ========================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [INFO] Python version: %PYTHON_VERSION%

REM Create virtual environment
if not exist venv (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [INFO] Installing dependencies from offline packages...
pip install --no-index --find-links=dependencies -r module\config\requirements_cpu.txt

REM Copy shared modules
echo [INFO] Setting up shared modules...
if not exist ..\..\..\shared mkdir ..\..\..\shared
xcopy /E /I /Y shared ..\..\..\shared

REM Copy module
echo [INFO] Setting up module...
if not exist ..\..\..\tools\cardiac_calcium_scoring mkdir ..\..\..\tools\cardiac_calcium_scoring
xcopy /E /I /Y module ..\..\..\tools\cardiac_calcium_scoring

REM Copy models
if exist models (
    echo [INFO] Copying AI models...
    if not exist ..\..\..\tools\cardiac_calcium_scoring\models mkdir ..\..\..\tools\cardiac_calcium_scoring\models
    copy /Y models\* ..\..\..\tools\cardiac_calcium_scoring\models\
)

echo.
echo ========================================================================
echo Installation Complete!
echo ========================================================================
echo.
echo To run the module:
echo   cd ..\..\..\tools\cardiac_calcium_scoring
echo   call ..\..\venv\Scripts\activate.bat
echo   python menu.py
echo.
pause
INSTALL_BAT_EOF

    log_success "Created: install.bat"

    # Create README
    cat > "${TEMP_DIR}/README.txt" <<'README_EOF'
========================================================================
Cardiac Calcium Scoring - Offline Installation Package
冠脉钙化评分 - 离线安装包
========================================================================

Version: 1.1.4
Created: 2025-10-19
Author: Cardiac ML Research Team

========================================================================
Package Contents
========================================================================

/module/          - Main module source code
/shared/          - Shared utility modules
/dependencies/    - Python package wheels (offline)
/models/          - AI-CAC model files (if included)
/docs/            - Documentation
install.sh        - Linux/Mac installation script
install.bat       - Windows installation script
README.txt        - This file

========================================================================
System Requirements
========================================================================

- Python 3.8 or higher
- CPU-only mode supported (no GPU required)
- Recommended: 8+ CPU cores, 16GB+ RAM
- Disk space: ~2GB for complete installation

========================================================================
Installation Instructions
========================================================================

Linux/Mac:
  1. Extract package: tar -xzf cardiac_calcium_scoring_offline_v1.1.4.tar.gz
  2. cd cardiac_calcium_scoring_offline_v1.1.4
  3. ./install.sh

Windows:
  1. Extract package using 7-Zip or WinRAR
  2. cd cardiac_calcium_scoring_offline_v1.1.4
  3. Run install.bat

========================================================================
Quick Start
========================================================================

After installation:

  cd tools/cardiac_calcium_scoring
  source venv/bin/activate    # Linux/Mac
  call venv\Scripts\activate.bat  # Windows
  python3 menu.py

Select mode:
  - Test mode: Process 1 sample for testing
  - Pilot mode: Process limited samples
  - Full mode: Process all samples

========================================================================
Performance Notes
========================================================================

CPU-only mode performance (tested on Intel CPU):
  - Average: ~305 seconds per patient
  - With 8+ cores: ~60-120 seconds per patient

For best performance:
  - Use multi-core CPU (8+ cores recommended)
  - Ensure 6GB+ RAM available
  - Close other applications during processing

========================================================================
Support
========================================================================

For issues or questions, please contact:
  Cardiac ML Research Team

Documentation: See docs/ directory or README.md in module/

========================================================================
License
========================================================================

This is a hospital-grade medical imaging analysis tool.
For research and clinical use only.

========================================================================
README_EOF

    log_success "Created: README.txt"

    # Copy documentation
    log_info "Copying documentation..."
    for doc in README.md HOW_TO_RUN.md CHANGELOG.md MENU_GUIDE.md; do
        if [ -f "${MODULE_DIR}/${doc}" ]; then
            cp "${MODULE_DIR}/${doc}" "${TEMP_DIR}/docs/"
            log_info "  Copied: ${doc}"
        fi
    done
}

create_archive() {
    print_header "Creating Final Package Archive"

    log_info "Creating tar.gz archive..."

    cd "$OUTPUT_DIR"
    tar -czf "${PACKAGE_NAME}.tar.gz" "$PACKAGE_NAME"

    cd - > /dev/null

    if [ -f "${OUTPUT_DIR}/${PACKAGE_NAME}.tar.gz" ]; then
        archive_size=$(get_size_mb "${OUTPUT_DIR}/${PACKAGE_NAME}.tar.gz")
        log_success "Package created: ${PACKAGE_NAME}.tar.gz (${archive_size}MB)"

        log_info "Package location: ${OUTPUT_DIR}/${PACKAGE_NAME}.tar.gz"

        # Calculate SHA256 checksum
        if command -v sha256sum &> /dev/null; then
            checksum=$(sha256sum "${OUTPUT_DIR}/${PACKAGE_NAME}.tar.gz" | awk '{print $1}')
            echo "$checksum  ${PACKAGE_NAME}.tar.gz" > "${OUTPUT_DIR}/${PACKAGE_NAME}.sha256"
            log_info "SHA256: $checksum"
            log_success "Checksum saved: ${PACKAGE_NAME}.sha256"
        fi
    else
        log_error "Failed to create package archive"
        exit 1
    fi
}

print_summary() {
    print_header "Package Creation Summary"

    total_size=$(get_size_mb "${TEMP_DIR}")

    echo "Package Name:     ${PACKAGE_NAME}"
    echo "Version:          ${VERSION}"
    echo "Package Size:     ${total_size}MB (uncompressed)"
    echo "Output Directory: ${OUTPUT_DIR}"
    echo ""
    echo "Package Contents:"
    echo "  - Module code:   $(get_size_mb "${TEMP_DIR}/module")MB"
    echo "  - Shared code:   $(get_size_mb "${TEMP_DIR}/shared")MB"
    echo "  - Dependencies:  $(get_size_mb "${TEMP_DIR}/dependencies")MB ($(ls -1 "${TEMP_DIR}/dependencies" | wc -l) packages)"
    echo "  - Models:        $(get_size_mb "${TEMP_DIR}/models")MB"
    echo "  - Scripts:       $(get_size_mb "${TEMP_DIR}/scripts")MB"
    echo "  - Docs:          $(get_size_mb "${TEMP_DIR}/docs")MB"
    echo ""
    echo "Installation files:"
    echo "  - install.sh  (Linux/Mac)"
    echo "  - install.bat (Windows)"
    echo "  - README.txt"
    echo ""
    echo "Next steps:"
    echo "  1. Test installation on clean system"
    echo "  2. Run CPU performance tests"
    echo "  3. Validate all features work offline"
    echo ""
    echo "To test installation:"
    echo "  tar -xzf ${OUTPUT_DIR}/${PACKAGE_NAME}.tar.gz"
    echo "  cd ${PACKAGE_NAME}"
    echo "  ./install.sh"
    echo ""
}

cleanup_prompt() {
    echo ""
    read -p "Keep temporary directory for inspection? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up temporary directory..."
        rm -rf "$TEMP_DIR"
        log_success "Cleanup complete"
    else
        log_info "Temporary directory kept: $TEMP_DIR"
    fi
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    print_header "Cardiac Calcium Scoring - Offline Package Creation"

    log_info "Module: $MODULE_NAME"
    log_info "Version: $VERSION"
    log_info "Output: $OUTPUT_DIR"

    check_prerequisites
    create_package_structure
    copy_module_files
    download_dependencies
    copy_models
    create_installation_scripts
    create_archive
    print_summary
    cleanup_prompt

    log_success "Package creation complete!"
}

# Run main function
main "$@"
