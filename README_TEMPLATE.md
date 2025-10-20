# Cardiac AI-CAC Release Repository Template

**Created**: 2025-10-19
**Purpose**: Complete template for independent cardiac-ai-cac release repository
**Dev Repo**: cardiac-ml-research (private development repository)

---

## 📦 What's in This Template

This directory contains everything you need to create a professional, independent release repository for Cardiac AI-CAC with automated Windows/Linux package builds.

### Directory Structure

```
/tmp/cardiac-ai-cac-template/
├── .github/
│   └── workflows/
│       ├── build-windows.yml        # Windows package builder
│       ├── build-linux.yml          # Linux package builder
│       └── test-builds.yml          # CI tests
├── scripts/
│   ├── sync_from_dev.sh            # Sync code from dev repo
│   └── verify_package.sh           # Package verification
├── README.md                        # Main README (English)
├── README_CN.md                     # Chinese README (中文)
├── CHANGELOG.md                     # Version history
├── QUICK_START_SETUP.md            # Step-by-step setup guide
└── README_TEMPLATE.md              # This file

```

### File Purposes

| File | Purpose | Status |
|------|---------|--------|
| `.github/workflows/build-windows.yml` | Automated Windows package builds on GitHub Actions | ✅ Ready |
| `.github/workflows/build-linux.yml` | Automated Linux package builds on GitHub Actions | ✅ Ready |
| `.github/workflows/test-builds.yml` | CI tests for pull requests | ✅ Ready |
| `scripts/sync_from_dev.sh` | Sync production code from dev repo | ✅ Ready |
| `scripts/verify_package.sh` | Verify package completeness | ✅ Ready |
| `README.md` | Professional user-facing documentation | ✅ Ready (needs customization) |
| `README_CN.md` | Chinese documentation for 医生/technicians | ✅ Ready (needs customization) |
| `CHANGELOG.md` | Complete version history | ✅ Ready |
| `QUICK_START_SETUP.md` | Setup instructions | ✅ Ready |

---

## 🚀 Quick Start

### Option 1: Follow Step-by-Step Guide (Recommended)

```bash
# Read the comprehensive guide
cat /tmp/cardiac-ai-cac-template/QUICK_START_SETUP.md
```

This guide walks you through all 9 steps with checkpoints.

### Option 2: Fast Track (Experienced Users)

```bash
# 1. Create GitHub repo: cardiac-ai-cac

# 2. Clone it
cd ~/projects/
git clone git@github.com:YOUR_USERNAME/cardiac-ai-cac.git
cd cardiac-ai-cac

# 3. Copy template files
cp -r /tmp/cardiac-ai-cac-template/* .
cp -r /tmp/cardiac-ai-cac-template/.github .

# 4. Customize
sed -i 's/USERNAME/your-username/g' README.md README_CN.md
sed -i 's/your-email@example.com/your@email.com/g' README.md README_CN.md

# 5. Sync source code
export DEV_REPO_PATH=~/projects/.../cardiac-ml-research
./scripts/sync_from_dev.sh
# Enter version: v1.1.4

# 6. Commit and push
git add .
git commit -m "Initial release repository setup"
git push origin main

# 7. Create release
git tag -a v1.1.4 -m "Release v1.1.4"
git push origin v1.1.4

# 8. Watch GitHub Actions build packages automatically
# Visit: https://github.com/YOUR_USERNAME/cardiac-ai-cac/actions
```

---

## 📋 Customization Checklist

Before using this template, customize the following:

### README.md & README_CN.md
- [ ] Replace `USERNAME` with your GitHub username
- [ ] Replace `your-email@example.com` with actual email
- [ ] Add institution/organization name (optional)
- [ ] Update star history URL
- [ ] Add website URL if available (optional)

### GitHub Actions Workflows
- [ ] Verify model download URL in `build-windows.yml`
- [ ] Verify model download URL in `build-linux.yml`
- [ ] (Optional) Adjust Python version if needed
- [ ] (Optional) Add custom build steps

### Scripts
- [ ] Update `DEV_REPO_PATH` in `sync_from_dev.sh` if path differs
- [ ] (Optional) Customize verification checks in `verify_package.sh`

### CHANGELOG.md
- [ ] Review v1.1.4 entry
- [ ] Add any missing features or fixes
- [ ] Update future roadmap if needed

---

## 🎯 Key Features

### 1. Automated Cross-Platform Builds

**Problem Solved**: You develop in WSL/Linux but need Windows packages for hospitals.

**Solution**: GitHub Actions builds packages on both platforms automatically.

```yaml
# Windows build runs on: windows-latest
# Linux build runs on: ubuntu-latest
```

### 2. Offline Deployment Support

**Problem Solved**: Hospitals often have air-gapped systems with no internet.

**Solution**: Packages include all dependencies as wheels.

```bash
# Windows
pip install --no-index --find-links=dependencies -r requirements-cpu.txt

# Linux
pip install --no-index --find-links=dependencies -r requirements-cpu.txt
```

### 3. Multi-Language Support

**Audience**: Chinese hospitals + international users

**Solution**:
- README.md (English) - International users, developers
- README_CN.md (Chinese) - 医生, technicians, Chinese hospitals

### 4. Professional Release Management

**Features**:
- Semantic versioning (v1.1.4)
- Automated changelog updates
- GitHub Releases with download links
- SHA256 checksums for verification

---

## 🔧 How It Works

### Development to Release Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Development Repository (cardiac-ml-research)                 │
│ - Private                                                    │
│ - Full history                                              │
│ - Test data                                                 │
│ - Experiments                                               │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ ./scripts/sync_from_dev.sh
                 │ (Manual or automated)
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Release Repository (cardiac-ai-cac)                         │
│ - Public (or private)                                       │
│ - Clean source code only                                    │
│ - Professional documentation                                │
│ - Ready for distribution                                    │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ git tag v1.1.4 && git push origin v1.1.4
                 │ (Triggers GitHub Actions)
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ GitHub Actions                                              │
│ ├── Build Windows Package (windows-latest)                  │
│ │   ├── Download Windows wheels                            │
│ │   ├── Download AI-CAC model                              │
│ │   ├── Create install.bat                                 │
│ │   └── Package as .zip                                    │
│ │                                                           │
│ └── Build Linux Package (ubuntu-latest)                     │
│     ├── Download Linux wheels                              │
│     ├── Download AI-CAC model                              │
│     ├── Create install.sh                                  │
│     └── Package as .tar.gz                                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Automatic GitHub Release
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ GitHub Releases                                             │
│ - cardiac-ai-cac-windows-v1.1.4.zip (2.1 GB)               │
│ - cardiac-ai-cac-linux-v1.1.4.tar.gz (2.0 GB)             │
│ - PACKAGE_INFO.txt                                         │
│ - SHA256SUMS                                               │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Download & Install
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Hospital Deployment                                         │
│ - Windows PC: Extract + Run install.bat                     │
│ - Linux Server: Extract + Run install.sh                    │
│ - Offline installation (no internet needed)                 │
└─────────────────────────────────────────────────────────────┘
```

### GitHub Actions Triggers

1. **Manual Trigger** (for testing):
   - Go to Actions tab
   - Click "Run workflow"
   - Select branch
   - Click "Run workflow"

2. **Automatic on Tag** (production):
   ```bash
   git tag v1.1.4
   git push origin v1.1.4
   ```
   - Automatically builds both Windows and Linux packages
   - Creates GitHub Release
   - Uploads packages as release assets

3. **Pull Request** (CI testing):
   - Runs `test-builds.yml`
   - Verifies package structure
   - Checks documentation
   - No actual packages built

---

## 📊 What Gets Built

### Windows Package Structure
```
cardiac-ai-cac-windows-v1.1.4.zip (2.1 GB)
└── cardiac-ai-cac/
    ├── src/                              # Source code
    │   ├── cardiac_calcium_scoring/
    │   └── shared/
    ├── dependencies/                     # Windows wheels
    │   ├── torch-*.whl
    │   ├── monai-*.whl
    │   └── ... (30+ packages)
    ├── models/                           # AI model
    │   └── va_non_gated_ai_cac_model.pth (1.8 GB)
    ├── requirements/
    │   └── requirements-cpu.txt
    ├── README.md
    ├── README_CN.md
    ├── CHANGELOG.md
    ├── install.bat                       # Installation script
    ├── cardiac-ai-cac.bat               # Launcher script
    ├── uninstall.bat                    # Uninstaller
    └── SHA256SUMS.csv                   # Checksums
```

### Linux Package Structure
```
cardiac-ai-cac-linux-v1.1.4.tar.gz (2.0 GB)
└── cardiac-ai-cac/
    ├── src/                              # Source code
    ├── dependencies/                     # Linux wheels
    ├── models/                           # AI model
    ├── requirements/
    ├── README.md, README_CN.md, CHANGELOG.md
    ├── install.sh                        # Installation script
    ├── cardiac-ai-cac.sh                # Launcher script
    ├── uninstall.sh                     # Uninstaller
    └── SHA256SUMS.txt                   # Checksums
```

---

## 🔒 Security & License

### Model File Access

The AI-CAC model is currently hosted on Google Drive:
```
File ID: 1uD12kphnWlJ5R6K-mDQnxS8LjYhPGSfm
URL: https://drive.google.com/file/d/1uD12kphnWlJ5R6K-mDQnxS8LjYhPGSfm/view
```

**Important**: This file must be publicly accessible for GitHub Actions to download it.

**Alternatives** (if you want more control):
1. Upload model to GitHub Releases manually
2. Host on private server with download link
3. Use GitHub Large File Storage (LFS)

### License Considerations

Current template: **Proprietary License** (not included)

**Options**:
1. **Academic/Research**: MIT, Apache 2.0, GPL
2. **Commercial**: Custom proprietary license
3. **Hybrid**: Dual licensing (academic + commercial)

Add `LICENSE` file before making repository public.

---

## 📈 Version Management

### Semantic Versioning

```
v{MAJOR}.{MINOR}.{PATCH}

MAJOR: Breaking changes (v2.0.0)
MINOR: New features (v1.2.0)
PATCH: Bug fixes (v1.1.5)
```

### Release Process

1. **Development**: Work in dev repo
2. **Testing**: Test thoroughly
3. **Sync**: Run `./scripts/sync_from_dev.sh`
4. **Update CHANGELOG**: Document changes
5. **Commit**: `git commit -m "Prepare v1.1.5"`
6. **Tag**: `git tag -a v1.1.5 -m "Release notes"`
7. **Push**: `git push origin main && git push origin v1.1.5`
8. **Wait**: GitHub Actions builds packages automatically
9. **Verify**: Download and test packages
10. **Announce**: Notify users of new release

---

## 🧪 Testing Checklist

Before creating a release, verify:

### Pre-Release Testing
- [ ] Run all tests in dev repo (100% pass rate)
- [ ] Verify CHANGELOG.md is updated
- [ ] Check that requirements.txt includes all dependencies
- [ ] Test sync script: `./scripts/sync_from_dev.sh`
- [ ] Verify no test files in src/ directory
- [ ] Check no __pycache__ or .pyc files

### Post-Build Testing
- [ ] Download Windows package from GitHub Actions
- [ ] Download Linux package from GitHub Actions
- [ ] Run verification: `./scripts/verify_package.sh`
- [ ] Test Windows installation on clean Windows 10/11
- [ ] Test Linux installation on clean Ubuntu 20.04+
- [ ] Run pilot mode (1 patient) on both platforms
- [ ] Verify results are correct
- [ ] Check logs for errors

### Documentation Testing
- [ ] README.md renders correctly on GitHub
- [ ] README_CN.md renders correctly
- [ ] No placeholder text (USERNAME, email, etc.)
- [ ] All links work
- [ ] CHANGELOG version matches tag

---

## 🐛 Common Issues & Solutions

### Issue: GitHub Actions Fails

**Error**: "Model download failed"
- **Cause**: Google Drive file not accessible
- **Fix**: Verify file ID and permissions

**Error**: "requirements-cpu.txt not found"
- **Cause**: File not synced from dev repo
- **Fix**: Check `./scripts/sync_from_dev.sh` paths

**Error**: "pip download failed"
- **Cause**: Package not available for platform
- **Fix**: Check platform compatibility in requirements

### Issue: Package Too Large (>2GB)

**GitHub Limitation**: Release assets max 2GB per file

**Solutions**:
1. Model file: Provide separate download instructions
2. Dependencies: Use `--no-deps` for some packages
3. Split package: Core + optional components

### Issue: Installation Fails on Windows

**Error**: "Python not found"
- **Fix**: User needs to install Python 3.8-3.12

**Error**: "Access denied"
- **Fix**: Run install.bat as Administrator

**Error**: "pip install failed"
- **Fix**: Check internet connection (if fallback is enabled)

### Issue: Installation Fails on Linux

**Error**: "python3-venv not found"
- **Fix**: `sudo apt install python3-venv`

**Error**: "Permission denied"
- **Fix**: `chmod +x install.sh cardiac-ai-cac.sh`

---

## 📞 Support

For issues with this template:

1. **Check documentation**: Read QUICK_START_SETUP.md
2. **Check logs**: GitHub Actions → View logs
3. **Verify files**: Run `./scripts/verify_package.sh`
4. **Review guide**: docs/deployment/RELEASE_REPO_IMPLEMENTATION_GUIDE.md

---

## 🎓 Summary

### What This Template Provides

✅ **Automated Builds**: Windows + Linux packages via GitHub Actions
✅ **Cross-Platform**: Develop on WSL, build for Windows
✅ **Offline Support**: Complete dependency packages
✅ **Professional Docs**: English + Chinese documentation
✅ **CI/CD Pipeline**: Automated testing and releases
✅ **Easy Sync**: Scripts to sync from dev repo
✅ **Verification**: Package integrity checking
✅ **Hospital-Ready**: Installation scripts for non-technical users

### Time Investment

- **Initial Setup**: 30-60 minutes
- **Each Release**: 5-10 minutes (mostly automated)
- **Testing**: 15-30 minutes per release

### Long-Term Benefits

- No Windows machine needed for Windows builds
- Professional public presence
- Separate development and release workflows
- Automatic version management
- Easy distribution to hospitals and users

---

**Template Version**: 1.0.0
**Last Updated**: 2025-10-19
**Created For**: Cardiac ML Research Project
