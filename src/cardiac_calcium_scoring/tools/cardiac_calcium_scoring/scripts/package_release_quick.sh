#!/bin/bash

# ====================================================================
# Week 7 Quick Release Packaging Script (No Dependency Download)
# ====================================================================
# Purpose: Create release package without downloading dependencies
# Version: v1.0.0 (Week 7 Quick)
# Date: 2025-10-18
# Note: Use this for quick local testing
# ====================================================================

set -e  # Exit on error

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================"
echo "  Cardiac Calcium Scoring System"
echo "  Week 7 Quick Release Package"
echo "  Version: v2.0.0-alpha"
echo "  Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo -e "========================================${NC}\n"

# ====================================================================
# 1. Environment Check
# ====================================================================
echo -e "${YELLOW}[1/5] Checking environment...${NC}"

# Check current directory
if [ ! -f "calcium_scoring.bat" ] && [ ! -f "calcium_scoring.sh" ]; then
    echo -e "${RED}ERROR: Please run this script in tools/cardiac_calcium_scoring directory${NC}"
    exit 1
fi

# Check AI-CAC model
if [ ! -f "models/va_non_gated_ai_cac_model.pth" ]; then
    echo -e "${RED}ERROR: AI-CAC model file missing${NC}"
    echo "Expected location: models/va_non_gated_ai_cac_model.pth"
    exit 1
fi

MODEL_SIZE=$(du -h models/va_non_gated_ai_cac_model.pth | cut -f1)
echo -e "${GREEN}OK: AI-CAC model ready (${MODEL_SIZE})${NC}\n"

# ====================================================================
# 2. Create Release Directory
# ====================================================================
echo -e "${YELLOW}[2/5] Creating release directory...${NC}"

RELEASE_NAME="cardiac_calcium_scoring_v2.0.0_week7_quick_$(date +%Y%m%d_%H%M%S)"
RELEASE_DIR="releases/${RELEASE_NAME}"

# Clean old release if exists
if [ -d "${RELEASE_DIR}" ]; then
    echo "Cleaning old release directory..."
    rm -rf "${RELEASE_DIR}"
fi

mkdir -p "${RELEASE_DIR}"
echo -e "${GREEN}OK: Created ${RELEASE_DIR}${NC}\n"

# ====================================================================
# 3. Copy Core Files
# ====================================================================
echo -e "${YELLOW}[3/5] Copying core files...${NC}"

# Copy directories
cp -r cli "${RELEASE_DIR}/"
cp -r core "${RELEASE_DIR}/"
cp -r config "${RELEASE_DIR}/"
cp -r models "${RELEASE_DIR}/"
cp -r deployment "${RELEASE_DIR}/"

# Create output and logs directories
mkdir -p "${RELEASE_DIR}/output"
mkdir -p "${RELEASE_DIR}/logs"

# Copy startup scripts
cp calcium_scoring.bat "${RELEASE_DIR}/" 2>/dev/null || true
cp calcium_scoring.sh "${RELEASE_DIR}/" 2>/dev/null || true
cp start_calcium_scoring.bat "${RELEASE_DIR}/" 2>/dev/null || true
cp menu.py "${RELEASE_DIR}/" 2>/dev/null || true

# Copy README
if [ -f "README.md" ]; then
    cp README.md "${RELEASE_DIR}/"
else
    echo "# Cardiac Calcium Scoring System v2.0.0" > "${RELEASE_DIR}/README.md"
fi

echo -e "${GREEN}OK: Core files copied${NC}\n"

# ====================================================================
# 4. Copy Documentation
# ====================================================================
echo -e "${YELLOW}[4/5] Copying documentation...${NC}"

mkdir -p "${RELEASE_DIR}/docs"

# Copy deployment docs
cp ../../docs/deployment/DEPLOYMENT_GUIDE.md "${RELEASE_DIR}/docs/" 2>/dev/null || true
cp ../../docs/deployment/USER_MANUAL.md "${RELEASE_DIR}/docs/" 2>/dev/null || true
cp ../../docs/deployment/TECHNICAL_SPECS.md "${RELEASE_DIR}/docs/" 2>/dev/null || true
cp ../../docs/deployment/FAQ.md "${RELEASE_DIR}/docs/" 2>/dev/null || true
cp ../../WEEK6_PROGRESS.md "${RELEASE_DIR}/docs/" 2>/dev/null || true

DOC_COUNT=$(ls "${RELEASE_DIR}/docs" 2>/dev/null | wc -l)
echo -e "${GREEN}OK: Copied ${DOC_COUNT} documentation files${NC}\n"

# ====================================================================
# 5. Create Deployment README
# ====================================================================
echo -e "${YELLOW}[5/5] Generating deployment README...${NC}"

cat > "${RELEASE_DIR}/README_DEPLOYMENT.md" << 'EOF'
# Cardiac Calcium Scoring System v2.0.0 - Quick Release Package

## Package Type

**Quick Release** - This package contains all core files but does NOT include Python dependencies.

To create a complete offline package with dependencies, use `package_release_week7.sh` instead.

## Contents

```
cardiac_calcium_scoring_v2.0.0_week7_quick/
├── cli/                    # CLI interface
├── core/                   # Core modules
├── config/                 # Configuration files
├── models/                 # AI-CAC model (~450MB)
├── deployment/             # Deployment resources
│   └── requirements.txt    # Dependency list
├── docs/                   # Documentation
│   ├── DEPLOYMENT_GUIDE.md
│   ├── USER_MANUAL.md
│   ├── TECHNICAL_SPECS.md
│   ├── FAQ.md
│   └── WEEK6_PROGRESS.md
├── output/                 # Output directory (empty)
├── logs/                   # Log directory (empty)
├── calcium_scoring.bat     # Windows launcher
├── calcium_scoring.sh      # Linux launcher
└── README_DEPLOYMENT.md    # This file
```

## Installation (Requires Internet)

### Linux/WSL

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies (requires internet)
pip install -r deployment/requirements.txt

# 4. Launch
./calcium_scoring.sh --help
```

### Windows

```cmd
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
venv\Scripts\activate.bat

# 3. Install dependencies (requires internet)
pip install -r deployment\requirements.txt

# 4. Launch
calcium_scoring.bat --help
```

## System Requirements

### Minimum
- **OS**: Windows 10/11 or Linux (Ubuntu 20.04+)
- **Python**: 3.10+
- **RAM**: 8GB
- **CPU**: 2 cores
- **Disk**: 10GB free
- **Speed**: ~300 sec/patient (CPU)

### Recommended
- **OS**: Windows 10/11 Pro or Linux
- **Python**: 3.10+
- **RAM**: 16GB+
- **CPU**: 8+ cores
- **GPU**: NVIDIA RTX 2060+ (optional)
- **Disk**: 20GB free
- **Speed**: ~15 sec/patient (GPU)

## Week 6 Test Results

- **Total**: 196/197 success (99.5%)
- **CHD Group**: 100/101 success - Mean score 356.6
- **Normal Group**: 96/96 success - Mean score 6.3
- **Performance**: GPU 15 sec/patient, CPU 305 sec/patient

See: `docs/WEEK6_PROGRESS.md`

## Documentation

- **DEPLOYMENT_GUIDE.md** - IT admin deployment guide
- **USER_MANUAL.md** - Doctor/technician manual
- **TECHNICAL_SPECS.md** - Technical specifications
- **FAQ.md** - Frequently asked questions

## Version

- **Version**: v2.0.0-alpha (Week 7 Quick Release)
- **Release Date**: 2025-10-18
- **Validation**: Production-ready (196-case complete test)

---

**Generated with Claude Code**
EOF

echo -e "${GREEN}OK: Deployment README generated${NC}\n"

# ====================================================================
# 6. Generate Release Notes
# ====================================================================
cat > "releases/${RELEASE_NAME}_release_notes.txt" << EOF
====================================================================
Cardiac Calcium Scoring System v2.0.0-alpha - Week 7 Quick Release
====================================================================
Release Date: $(date '+%Y-%m-%d %H:%M:%S')
Release Type: Quick Release (No Dependencies Included)

Package Type
------------
QUICK RELEASE - Contains core files only
- Does NOT include Python dependencies
- Requires internet connection for pip install
- For offline deployment, use package_release_week7.sh

Version Information
-------------------
- Version: v2.0.0-alpha
- Code Name: cardiac_calcium_scoring (renamed from nb10_windows)
- Validation: Production-ready (99.5% success, 196/197 cases)

Package Contents
----------------
1. Core Program
   - CLI interface (cli/)
   - Core modules (core/)
   - AI-CAC model (~450MB)
   - Configuration files (config/)

2. Documentation
   - DEPLOYMENT_GUIDE.md (IT admin guide)
   - USER_MANUAL.md (User manual)
   - TECHNICAL_SPECS.md (Technical specs)
   - FAQ.md (FAQ)
   - WEEK6_PROGRESS.md (Week 6 report)

3. Deployment Resources
   - requirements.txt (dependency list)
   - Startup scripts (.bat/.sh)

Performance Metrics (Week 6 Testing)
-------------------------------------
- Test Scale: 196/197 success (99.5%)
- CHD Group: 100/101 success, mean score 356.6
- Normal Group: 96/96 success, mean score 6.3
- GPU Performance: 15 sec/patient (RTX 2060)
- CPU Performance: 305 sec/patient (8 cores)

Installation Steps
------------------
1. Extract package
2. Create venv: python3 -m venv venv
3. Activate venv: source venv/bin/activate
4. Install deps: pip install -r deployment/requirements.txt
5. Launch: ./calcium_scoring.sh --help

System Requirements
-------------------
Minimum:
- Python 3.10+
- 8GB RAM
- 2-core CPU
- 10GB disk space
- Internet connection (for pip install)

Recommended:
- Python 3.10+
- 16GB+ RAM
- 8+ core CPU
- NVIDIA GPU (optional, RTX 2060+)
- 20GB disk space

Package Files
-------------
- ${RELEASE_NAME}/ (extracted directory)

Notes
-----
- This is a QUICK release for testing
- For production offline deployment, use package_release_week7.sh
- All user-facing prompts and filenames use ENGLISH
- Documentation may contain Chinese content

====================================================================
Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
====================================================================
EOF

# ====================================================================
# Complete
# ====================================================================
echo -e "${GREEN}========================================"
echo "  Package Build Complete!"
echo -e "========================================${NC}\n"

echo "Release Package Location:"
echo "  - releases/${RELEASE_NAME}/"
echo ""
echo "Release Notes:"
echo "  - releases/${RELEASE_NAME}_release_notes.txt"
echo ""
echo "Package Size:"
du -sh "releases/${RELEASE_NAME}" 2>/dev/null || echo "  - Calculating..."
echo ""
echo "Next Steps:"
echo "  1. Test package: cd releases/${RELEASE_NAME}"
echo "  2. Create venv: python3 -m venv venv"
echo "  3. Install deps: pip install -r deployment/requirements.txt"
echo "  4. Launch: ./calcium_scoring.sh --help"
echo ""
echo "Note: This is a QUICK package (no dependencies included)"
echo "For offline deployment with dependencies, use: bash scripts/package_release_week7.sh"
echo ""
