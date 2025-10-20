# AI-CAC Model Files

The AI-CAC model file (`va_non_gated_ai_cac_model.pth`, ~1.2GB) is **not included** in this repository due to GitHub file size limitations.

## 📥 Model Download

### Automatic Download (Recommended)

The model will be **automatically downloaded** during package build via GitHub Actions when you create a release.

### Manual Download

If you need to download the model manually:

**Download Link:**
- Google Drive: https://drive.google.com/file/d/1uD12kphnWlJ5R6K-mDQnxS8LjYhPGSfm/view

**File Information:**
- Filename: `va_non_gated_ai_cac_model.pth`
- Size: ~1.2GB (1,181 MB)

**Using gdown (command line):**
```bash
pip install gdown
gdown 1uD12kphnWlJ5R6K-mDQnxS8LjYhPGSfm -O va_non_gated_ai_cac_model.pth
```

## 📁 Installation

After downloading, place the model file in this directory:
```
src/cardiac_calcium_scoring/models/va_non_gated_ai_cac_model.pth
```

## 🔍 Model Details

- **Architecture**: SwinUNETR (Swin Transformer + U-Net)
- **Framework**: PyTorch (MONAI)
- **Training**: Clinical CT scans
- **Validation**: 195 patients, 99.5% success rate
- **Purpose**: AI-based coronary artery calcium scoring

## ⚠️ Note

This model file is automatically downloaded during:
- GitHub Actions builds (Windows/Linux packages)
- Installation script execution
- First run of the application (if not present)

No manual download is required for normal package installation.

---

**For developers**: The model is excluded from git via `.gitignore` to keep the repository size manageable.
