# Week 7 Release Packaging Scripts

This directory contains scripts for creating Week 7 release packages.

## Available Scripts

### 1. **package_release_windows.ps1** (⭐ Recommended for Windows/WSL)

**Platform**: PowerShell (Windows / WSL)
**Speed**: Fast (~5 seconds)
**Dependencies**: NO (requires internet for pip install)
**Use Case**: Local testing, works with WSL paths

**Usage**:
```powershell
# From PowerShell (even in WSL paths like \\wsl.localhost\Ubuntu\...)
.\scripts\package_release_windows.ps1
```

**Features**:
- ✅ PowerShell script (works with WSL paths)
- ✅ All prompts in English with color output
- ✅ Handles both WSL and Windows paths
- ✅ Includes all core files, models, and documentation
- ❌ Does NOT include Python dependencies

**Output**:
```
releases\cardiac_calcium_scoring_v2.0.0_week7_quick_[timestamp]\
├── cli/
├── core/
├── models/                 (~450MB)
├── docs/                   (5 files)
├── deployment/
├── calcium_scoring.bat
└── README_DEPLOYMENT.md
```

### 2. **package_release_windows.bat** (Windows CMD only - not for WSL)

**Platform**: Windows CMD (native paths only)
**Speed**: Fast (~5 seconds)
**Dependencies**: NO (requires internet for pip install)
**Use Case**: Native Windows paths (C:\, D:\) only

**Usage**:
```cmd
# Only works in native Windows paths
# Does NOT work in WSL paths (\\wsl.localhost\...)
cd C:\path\to\tools\cardiac_calcium_scoring
scripts\package_release_windows.bat
```

**Important**: ⚠️ If you get "UNC paths are not supported" error, use `package_release_windows.ps1` instead.

### 3. **package_release_quick.sh** (For WSL/Linux)

**Platform**: WSL / Linux / macOS
**Speed**: Fast (~5 seconds)
**Dependencies**: NO (requires internet for pip install)
**Use Case**: Local testing, Linux development

**Usage**:
```bash
cd tools/cardiac_calcium_scoring
bash scripts/package_release_quick.sh
```

**Features**:
- ✅ Bash script with color output
- ✅ All prompts in English
- ✅ Fast packaging
- ✅ Includes all core files, models, and documentation
- ❌ Does NOT include Python dependencies

### 4. **package_release_week7.sh** (For Offline Deployment)

**Platform**: WSL / Linux / macOS
**Speed**: Slow (10-30 minutes - downloads dependencies)
**Dependencies**: YES (complete offline package)
**Use Case**: Hospital deployment, isolated networks

**Usage**:
```bash
cd tools/cardiac_calcium_scoring
bash scripts/package_release_week7.sh
```

**Features**:
- ✅ Complete offline deployment package
- ✅ Downloads all Python dependencies (~2-3GB)
- ✅ Creates .tar.gz and .zip archives
- ✅ Suitable for networks without internet access
- ⚠️ Takes 10-30 minutes to complete

**Output**:
```
releases\cardiac_calcium_scoring_v2.0.0_week7_[date]\
├── dependencies/           (~2-3GB Python packages)
├── cli/
├── core/
├── models/                 (~450MB)
├── docs/
└── install_offline.sh
```

## Installation Instructions

### Quick Release Package (Windows)

After running `package_release_windows.bat`:

```cmd
cd releases\cardiac_calcium_scoring_v2.0.0_week7_quick_[timestamp]

REM Create virtual environment
python -m venv venv

REM Activate virtual environment
venv\Scripts\activate.bat

REM Install dependencies (requires internet)
pip install -r deployment\requirements.txt

REM Test installation
calcium_scoring.bat --help
```

### Quick Release Package (Linux/WSL)

After running `package_release_quick.sh`:

```bash
cd releases/cardiac_calcium_scoring_v2.0.0_week7_quick_[timestamp]

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies (requires internet)
pip install -r deployment/requirements.txt

# Test installation
./calcium_scoring.sh --help
```

### Complete Offline Package

After running `package_release_week7.sh`:

```bash
cd releases/cardiac_calcium_scoring_v2.0.0_week7_[date]

# Run offline installer
./install_offline.sh

# Test installation
./calcium_scoring.sh --help
```

## Git Ignore Rules

The following files/directories are automatically excluded from git:

- `tools/cardiac_calcium_scoring/releases/` - Release packages
- `**/dependencies/` - Downloaded Python packages
- `package_*.zip` - Compressed packages
- `package_*.tar.gz` - Compressed packages
- `*_release_notes.txt` - Release notes

## Package Contents

All packages include:

1. **Core Application**
   - `cli/` - Command-line interface
   - `core/` - Core processing modules
   - `models/` - AI-CAC model (~450MB)
   - `config/` - Configuration files

2. **Documentation** (5 files, 4,095 lines)
   - `DEPLOYMENT_GUIDE.md` - IT admin guide (868 lines)
   - `USER_MANUAL.md` - User manual (862 lines)
   - `TECHNICAL_SPECS.md` - Technical specs (939 lines)
   - `FAQ.md` - Frequently asked questions (1,208 lines)
   - `WEEK6_PROGRESS.md` - Week 6 test report (243 lines)

3. **Deployment Resources**
   - `deployment/requirements.txt` - Python dependencies list
   - `calcium_scoring.bat` - Windows launcher
   - `calcium_scoring.sh` - Linux launcher
   - `README_DEPLOYMENT.md` - Deployment instructions

## Week 6 Validation Results

All packages are based on Week 6 validated system:

- **Test Scale**: 196/197 cases (99.5% success)
- **CHD Group**: 100/101 success - Mean score 356.6
- **Normal Group**: 96/96 success - Mean score 6.3
- **GPU Performance**: 15 sec/patient (RTX 2060)
- **CPU Performance**: 305 sec/patient (8 cores)
- **Clinical Validation**: CHD vs Normal ratio 56.5x (P<0.001)

## System Requirements

### Minimum Configuration
- **OS**: Windows 10/11 or Linux (Ubuntu 20.04+)
- **Python**: 3.10+
- **RAM**: 8GB
- **CPU**: 2 cores
- **Disk**: 10GB free space
- **Speed**: ~300 sec/patient (CPU)

### Recommended Configuration
- **OS**: Windows 10/11 Pro or Linux
- **Python**: 3.10+
- **RAM**: 16GB+
- **CPU**: 8+ cores
- **GPU**: NVIDIA RTX 2060+ (optional)
- **Disk**: 20GB free space
- **Speed**: ~15 sec/patient (GPU)

## Troubleshooting

### Windows: "Permission Denied"
- Run CMD as Administrator
- Or: Right-click script → Run as Administrator

### Windows: "Execution Policy"
If running .bat files is blocked:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Linux: "Permission Denied"
```bash
chmod +x scripts/*.sh
```

### Package Size Too Large
- Quick packages: ~1.2GB (model only)
- Complete packages: ~3-4GB (includes dependencies)
- This is normal and expected

## Important Notes

1. **All prompts and filenames use ENGLISH**
   - Menus, error messages, file names: English
   - Documentation content may contain Chinese

2. **Temporary files are excluded from git**
   - Release packages not committed
   - Downloaded dependencies not committed
   - Clean working tree after packaging

3. **For hospital deployment**
   - Use `package_release_week7.sh` for complete offline package
   - Include all dependencies for isolated networks
   - Test installation in isolated environment first

## Version Information

- **Version**: v2.0.0-alpha
- **Release**: Week 7 Quick Release
- **Date**: 2025-10-18
- **Validation**: Production-ready (196-case complete test)

---

**Generated with Claude Code**
