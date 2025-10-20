# ====================================================================
# Week 7 Release Packaging Script for Windows (PowerShell)
# ====================================================================
# Purpose: Create release package for local testing
# Version: v1.0.0 (Week 7)
# Date: 2025-10-18
# Note: Works with WSL paths and native Windows paths
# ====================================================================

Write-Host "========================================" -ForegroundColor Green
Write-Host "  Cardiac Calcium Scoring System" -ForegroundColor Green
Write-Host "  Week 7 Quick Release Package" -ForegroundColor Green
Write-Host "  Version: v2.0.0-alpha" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

# ====================================================================
# 1. Environment Check
# ====================================================================
Write-Host "[1/5] Checking environment..." -ForegroundColor Yellow

# Get current directory (handles WSL paths)
$CurrentPath = Get-Location

# Check if we're in the right directory
if (-not (Test-Path "calcium_scoring.bat") -and -not (Test-Path "calcium_scoring.sh")) {
    Write-Host "[ERROR] Please run this script in tools\cardiac_calcium_scoring directory" -ForegroundColor Red
    Write-Host "Current path: $CurrentPath" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check AI-CAC model
if (-not (Test-Path "models\va_non_gated_ai_cac_model.pth")) {
    Write-Host "[ERROR] AI-CAC model file missing" -ForegroundColor Red
    Write-Host "Expected location: models\va_non_gated_ai_cac_model.pth" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

$ModelSize = (Get-Item "models\va_non_gated_ai_cac_model.pth").Length / 1GB
Write-Host "[OK] AI-CAC model ready ($([math]::Round($ModelSize, 2)) GB)`n" -ForegroundColor Green

# ====================================================================
# 2. Create Release Directory
# ====================================================================
Write-Host "[2/5] Creating release directory..." -ForegroundColor Yellow

# Generate timestamp
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ReleaseName = "cardiac_calcium_scoring_v2.0.0_week7_quick_$Timestamp"
$ReleaseDir = "releases\$ReleaseName"

# Clean old release if exists
if (Test-Path $ReleaseDir) {
    Write-Host "Cleaning old release directory..."
    Remove-Item -Path $ReleaseDir -Recurse -Force
}

# Create release directory
New-Item -ItemType Directory -Path $ReleaseDir -Force | Out-Null
Write-Host "[OK] Created $ReleaseDir`n" -ForegroundColor Green

# ====================================================================
# 3. Copy Core Files
# ====================================================================
Write-Host "[3/5] Copying core files..." -ForegroundColor Yellow

# Copy directories
Write-Host "Copying directories..."
Copy-Item -Path "cli" -Destination "$ReleaseDir\cli" -Recurse -Force
Copy-Item -Path "core" -Destination "$ReleaseDir\core" -Recurse -Force
Copy-Item -Path "config" -Destination "$ReleaseDir\config" -Recurse -Force
Copy-Item -Path "models" -Destination "$ReleaseDir\models" -Recurse -Force
Copy-Item -Path "deployment" -Destination "$ReleaseDir\deployment" -Recurse -Force

# Create output and logs directories
New-Item -ItemType Directory -Path "$ReleaseDir\output" -Force | Out-Null
New-Item -ItemType Directory -Path "$ReleaseDir\logs" -Force | Out-Null

# Copy startup scripts
Write-Host "Copying scripts..."
if (Test-Path "calcium_scoring.bat") { Copy-Item "calcium_scoring.bat" "$ReleaseDir\" -Force }
if (Test-Path "calcium_scoring.sh") { Copy-Item "calcium_scoring.sh" "$ReleaseDir\" -Force }
if (Test-Path "start_calcium_scoring.bat") { Copy-Item "start_calcium_scoring.bat" "$ReleaseDir\" -Force }
if (Test-Path "menu.py") { Copy-Item "menu.py" "$ReleaseDir\" -Force }

# Copy README
if (Test-Path "README.md") {
    Copy-Item "README.md" "$ReleaseDir\" -Force
} else {
    "# Cardiac Calcium Scoring System v2.0.0" | Out-File "$ReleaseDir\README.md" -Encoding UTF8
}

Write-Host "[OK] Core files copied`n" -ForegroundColor Green

# ====================================================================
# 4. Copy Documentation
# ====================================================================
Write-Host "[4/5] Copying documentation..." -ForegroundColor Yellow

New-Item -ItemType Directory -Path "$ReleaseDir\docs" -Force | Out-Null

# Copy deployment docs
$DocsPath = "..\..\docs\deployment"
if (Test-Path "$DocsPath\DEPLOYMENT_GUIDE.md") { Copy-Item "$DocsPath\DEPLOYMENT_GUIDE.md" "$ReleaseDir\docs\" -Force }
if (Test-Path "$DocsPath\USER_MANUAL.md") { Copy-Item "$DocsPath\USER_MANUAL.md" "$ReleaseDir\docs\" -Force }
if (Test-Path "$DocsPath\TECHNICAL_SPECS.md") { Copy-Item "$DocsPath\TECHNICAL_SPECS.md" "$ReleaseDir\docs\" -Force }
if (Test-Path "$DocsPath\FAQ.md") { Copy-Item "$DocsPath\FAQ.md" "$ReleaseDir\docs\" -Force }
if (Test-Path "..\..\WEEK6_PROGRESS.md") { Copy-Item "..\..\WEEK6_PROGRESS.md" "$ReleaseDir\docs\" -Force }

$DocCount = (Get-ChildItem "$ReleaseDir\docs" -File).Count
Write-Host "[OK] Copied $DocCount documentation files`n" -ForegroundColor Green

# ====================================================================
# 5. Create Deployment README
# ====================================================================
Write-Host "[5/5] Generating deployment README..." -ForegroundColor Yellow

@"
# Cardiac Calcium Scoring System v2.0.0 - Quick Release Package

## Package Type

**Quick Release** - This package contains all core files but does NOT include Python dependencies.

To create a complete offline package with dependencies, download dependencies manually.

## Contents

``````
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
``````

## Installation (Windows)

``````cmd
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
venv\Scripts\activate.bat

# 3. Install dependencies (requires internet)
pip install -r deployment\requirements.txt

# 4. Launch
calcium_scoring.bat --help
``````

## System Requirements

### Minimum
- **OS**: Windows 10/11
- **Python**: 3.10+
- **RAM**: 8GB
- **CPU**: 2 cores
- **Disk**: 10GB free
- **Speed**: ~300 sec/patient (CPU)

### Recommended
- **OS**: Windows 10/11 Pro
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

See: ``docs\WEEK6_PROGRESS.md``

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
"@ | Out-File "$ReleaseDir\README_DEPLOYMENT.md" -Encoding UTF8

Write-Host "[OK] Deployment README generated`n" -ForegroundColor Green

# ====================================================================
# 6. Generate Release Notes
# ====================================================================
$ReleaseNotes = @"
====================================================================
Cardiac Calcium Scoring System v2.0.0-alpha - Week 7 Quick Release
====================================================================
Release Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Release Type: Quick Release (No Dependencies Included)

Package Type
------------
QUICK RELEASE - Contains core files only
- Does NOT include Python dependencies
- Requires internet connection for pip install
- For offline deployment, download dependencies manually

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
2. Create venv: python -m venv venv
3. Activate venv: venv\Scripts\activate.bat
4. Install deps: pip install -r deployment\requirements.txt
5. Launch: calcium_scoring.bat --help

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
- $ReleaseName\ (extracted directory)

Notes
-----
- This is a QUICK release for testing
- For production offline deployment, download dependencies separately
- All user-facing prompts and filenames use ENGLISH
- Documentation may contain Chinese content

====================================================================
Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
====================================================================
"@

$ReleaseNotes | Out-File "releases\${ReleaseName}_release_notes.txt" -Encoding UTF8

# ====================================================================
# Complete
# ====================================================================
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Package Build Complete!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Release Package Location:"
Write-Host "  - releases\$ReleaseName\`n"

Write-Host "Release Notes:"
Write-Host "  - releases\${ReleaseName}_release_notes.txt`n"

Write-Host "Package Size:"
$PackageSize = (Get-ChildItem -Path $ReleaseDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1GB
Write-Host "  - $([math]::Round($PackageSize, 2)) GB`n"

Write-Host "Next Steps:"
Write-Host "  1. Test package: cd releases\$ReleaseName"
Write-Host "  2. Create venv: python -m venv venv"
Write-Host "  3. Activate: venv\Scripts\activate.bat"
Write-Host "  4. Install deps: pip install -r deployment\requirements.txt"
Write-Host "  5. Launch: calcium_scoring.bat --help`n"

Write-Host "Note: This is a QUICK package (no dependencies included)`n" -ForegroundColor Yellow

Read-Host "Press Enter to exit"
