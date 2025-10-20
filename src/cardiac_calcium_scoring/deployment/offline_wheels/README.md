# Offline Installation Packages

This directory is for storing offline installation packages (wheel files) to enable installation without internet access.

## Directory Structure

```
offline_wheels/
├── cpu/           # CPU version packages (~1.5GB)
│   ├── torch-*.whl
│   ├── monai-*.whl
│   └── ...
├── gpu/           # GPU version packages (~3.5GB)
│   ├── torch-*.whl
│   ├── monai-*.whl
│   └── ...
└── README.md      # This file
```

## Quick Start

### Option 1: Download Offline Packages (Recommended for Hospital Deployment)

If you need to install NB10 on computers without internet access:

```bash
# Navigate to project root
cd /path/to/nb10_windows

# Run the download script
bash deployment/download_offline_packages.sh
```

This will download:
- **CPU packages**: ~1.5GB to `deployment/offline_wheels/cpu/`
- **GPU packages**: ~3.5GB to `deployment/offline_wheels/gpu/`

**Time estimate**: 15-30 minutes depending on network speed

### Option 2: Online Installation (Default)

If the `offline_wheels/cpu/` or `offline_wheels/gpu/` directories are **empty** or don't contain `.whl` files, the installation scripts will automatically fall back to online installation from PyPI.

**This is the default behavior** - no offline packages needed!

## How Detection Works

The installation scripts check for wheel files in this priority order:

### For GPU Installation (`install_gpu.bat`)
1. `deployment/offline_wheels/gpu/*.whl` (Priority 1)
2. `deployment/offline_wheels/*.whl` (Priority 2)
3. `offline_packages/gpu_wheels/*.whl` (Priority 3)
4. **Fallback**: Online installation from PyPI

### For CPU Installation (`install_cpu.bat`)
1. `deployment/offline_wheels/cpu/*.whl` (Priority 1)
2. `deployment/offline_wheels/*.whl` (Priority 2)
3. `offline_packages/cpu_wheels/*.whl` (Priority 3)
4. **Fallback**: Online installation from PyPI

**Key Point**: The scripts check for actual `.whl` files, not just directory existence. Empty directories will trigger online installation.

## Troubleshooting

### Problem: "No matching distribution found for torch"

**Cause**: Offline wheels directory is empty or missing required packages

**Solution**:
1. Check if `.whl` files exist:
   ```bash
   ls deployment/offline_wheels/cpu/*.whl
   ls deployment/offline_wheels/gpu/*.whl
   ```

2. If empty, either:
   - Run `bash deployment/download_offline_packages.sh`, OR
   - Let the installer use online mode (no action needed)

### Problem: Installation still tries offline mode with empty directory

**Cause**: Old version of installation scripts (before v1.1.0)

**Solution**:
- Update to v1.1.0 or later
- Scripts now check for `.whl` files, not just directories

---

**Note**: Empty directories are normal if you're using online installation. The offline packages are only needed for hospital environments without internet access.
