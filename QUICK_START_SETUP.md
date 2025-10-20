# Quick Start: Setting Up Release Repository

**Goal**: Create independent public release repository with automated Windows/Linux builds

**Time**: 30-60 minutes

---

## Prerequisites

- [ ] GitHub account
- [ ] Git installed
- [ ] Development repository at: `~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research`
- [ ] Template files at: `/tmp/cardiac-ai-cac-template/`

---

## Step 1: Create GitHub Repository (5 minutes)

### 1.1 Go to GitHub

Visit: https://github.com/new

### 1.2 Repository Settings

```
Repository name:    cardiac-ai-cac
Description:        AI-based Coronary Artery Calcium Scoring - Hospital Deployment Ready
Visibility:         ☐ Public  (recommended)
                    ☑ Private (for testing first, make public later)

Initialize:
☑ Add README file
☑ Add .gitignore (Python template)
☐ Choose a license (add later based on commercialization needs)
```

Click **Create repository**

### 1.3 Clone Repository

```bash
cd ~/projects/
git clone git@github.com:YOUR_USERNAME/cardiac-ai-cac.git
cd cardiac-ai-cac
```

✅ **Checkpoint**: You should see the GitHub README in your local directory

---

## Step 2: Copy Template Files (5 minutes)

```bash
# Copy all template files
cp -r /tmp/cardiac-ai-cac-template/* .
cp -r /tmp/cardiac-ai-cac-template/.github .

# Verify
ls -la
# Should see: README.md, README_CN.md, CHANGELOG.md, .github/, scripts/, etc.
```

✅ **Checkpoint**: Run `ls -la` and verify you see `.github/workflows/` directory

---

## Step 3: Customize README Files (5 minutes)

Edit the following placeholders in `README.md` and `README_CN.md`:

1. Replace `USERNAME` with your GitHub username
2. Replace `your-email@example.com` with your actual email
3. (Optional) Add your institution/organization name

**Quick replace (if comfortable with sed):**

```bash
# Replace USERNAME
sed -i 's/USERNAME/your-actual-username/g' README.md README_CN.md

# Replace email
sed -i 's/your-email@example.com/your@email.com/g' README.md README_CN.md
```

**Or manually edit:**
```bash
# Use your preferred editor
code README.md      # VS Code
nano README.md      # nano
vim README.md       # vim
```

✅ **Checkpoint**: Open README.md and verify no placeholders remain

---

## Step 4: Sync Source Code from Dev Repo (10 minutes)

### 4.1 Use the sync script

```bash
# Set dev repo path (adjust if different)
export DEV_REPO_PATH=~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research

# Run sync script
chmod +x scripts/sync_from_dev.sh
./scripts/sync_from_dev.sh
```

When prompted:
```
Enter version to sync (e.g., v1.1.4): v1.1.4
```

### 4.2 Verify sync

```bash
# Check what was synced
ls -R src/

# Should see:
# src/cardiac_calcium_scoring/
# src/shared/
```

✅ **Checkpoint**: Verify `src/` directory contains production code

---

## Step 5: First Commit (5 minutes)

```bash
# Stage all files
git add .

# Commit
git commit -m "Initial release repository setup

- Add README (EN/CN)
- Add CHANGELOG
- Add source code (v1.1.4)
- Add requirements files
- Setup GitHub Actions for Windows/Linux builds
- Add sync and verification scripts

🤖 Generated with Claude Code
"

# Push to GitHub
git push origin main
```

✅ **Checkpoint**: Visit `https://github.com/YOUR_USERNAME/cardiac-ai-cac` and see your files

---

## Step 6: Test GitHub Actions (15 minutes)

### 6.1 Manual Test (Windows Build)

1. Go to: `https://github.com/YOUR_USERNAME/cardiac-ai-cac/actions`
2. Click **"Build Windows Package"** in the left sidebar
3. Click **"Run workflow"** button (top right)
4. Click green **"Run workflow"** button in dropdown
5. Wait 10-15 minutes for build to complete

### 6.2 Check Results

After build completes:
- Click on the workflow run
- Scroll down to **"Artifacts"**
- Download `windows-package-manual-YYYYMMDD-HHMMSS.zip`

### 6.3 Test Linux Build (Optional)

Repeat same process for **"Build Linux Package"**

✅ **Checkpoint**: Successfully download package artifact from GitHub Actions

---

## Step 7: Verify Package (5 minutes)

### 7.1 Extract and verify

```bash
# Create test directory
mkdir -p ~/test-release
cd ~/test-release

# Download and extract the artifact from GitHub
unzip ~/Downloads/windows-package-*.zip

# (Or for Linux package)
tar -xzf ~/Downloads/cardiac-ai-cac-linux-*.tar.gz
```

### 7.2 Run verification script

```bash
# From release repo
cd ~/projects/cardiac-ai-cac
./scripts/verify_package.sh ~/test-release/cardiac-ai-cac
```

Expected output:
```
✅ Package verification PASSED
```

✅ **Checkpoint**: Verification script passes with no errors

---

## Step 8: Create First Official Release (10 minutes)

### 8.1 Update CHANGELOG

Edit `CHANGELOG.md` and verify v1.1.4 section is accurate.

### 8.2 Create and push tag

```bash
cd ~/projects/cardiac-ai-cac

# Create tag
git tag -a v1.1.4 -m "Release v1.1.4 - First public release

- Core AI-CAC functionality
- CPU optimization
- Offline deployment support
- Multi-language support
- License management system
"

# Push tag
git push origin v1.1.4
```

### 8.3 Wait for automatic build

This will automatically trigger:
- Windows package build
- Linux package build
- GitHub Release creation

Go to: `https://github.com/YOUR_USERNAME/cardiac-ai-cac/releases`

You should see **v1.1.4** release with both packages attached!

✅ **Checkpoint**: See v1.1.4 release on GitHub with download links

---

## Step 9: Test Installation on Clean System (Recommended)

### Windows Testing

If you have a Windows PC available:

1. Download `cardiac-ai-cac-windows-v1.1.4.zip` from GitHub Release
2. Extract to `C:\cardiac-ai-cac`
3. Run `install.bat`
4. After installation, run `cardiac-ai-cac.bat`
5. Test with pilot mode (1 patient)

### Linux Testing

On a clean Ubuntu/CentOS system (or VM):

```bash
# Download
wget https://github.com/YOUR_USERNAME/cardiac-ai-cac/releases/download/v1.1.4/cardiac-ai-cac-linux-v1.1.4.tar.gz

# Extract
tar -xzf cardiac-ai-cac-linux-v1.1.4.tar.gz
cd cardiac-ai-cac

# Install
./install.sh

# Run
./cardiac-ai-cac.sh
```

✅ **Checkpoint**: Successfully install and run on clean system

---

## Troubleshooting

### Issue: GitHub Actions fails

**Check**:
1. Workflow YAML syntax (use yamllint)
2. Requirements file exists: `requirements/requirements-cpu.txt`
3. Model download URL is accessible

**Debug**:
- Go to Actions tab → Click failed run → View logs
- Look for error messages in red

### Issue: "Permission denied" when running scripts

**Fix**:
```bash
chmod +x scripts/*.sh
chmod +x cardiac-ai-cac.sh
chmod +x install.sh
```

### Issue: Model download fails in GitHub Actions

**Fix**:
- Verify Google Drive file ID: `1uD12kphnWlJ5R6K-mDQnxS8LjYhPGSfm`
- Check if file is publicly accessible
- Alternative: Upload model to GitHub Releases manually

### Issue: Windows package too large (>2GB)

**GitHub Limitations**:
- Release assets: 2GB max per file
- Repository: 100GB max total

**Solutions**:
1. Model file: Provide separate download link in README
2. Dependencies: Document installation from PyPI as fallback
3. Use Git LFS for large files

---

## Next Steps After Setup

### Week 1: Testing Phase
- [ ] Test Windows package on hospital PC
- [ ] Test Linux package on server
- [ ] Collect feedback from users
- [ ] Fix any installation issues

### Week 2: Automation
- [ ] Setup automated sync from dev repo (cron job or GitHub Action)
- [ ] Test full CI/CD pipeline with new changes
- [ ] Document sync process for team

### Week 3: Public Launch
- [ ] Make repository public (if currently private)
- [ ] Announce to stakeholders (hospitals, collaborators)
- [ ] Monitor GitHub Issues for user feedback
- [ ] Create FAQ based on common questions

---

## Quick Reference Commands

```bash
# Sync from dev repo
cd ~/projects/cardiac-ai-cac
./scripts/sync_from_dev.sh

# Commit changes
git add .
git commit -m "Update to v1.1.5"
git push origin main

# Create new release
git tag -a v1.1.5 -m "Release v1.1.5 - Bug fixes"
git push origin v1.1.5

# Verify package
./scripts/verify_package.sh /path/to/package

# Check GitHub Actions status
# Visit: https://github.com/YOUR_USERNAME/cardiac-ai-cac/actions
```

---

## Summary

✅ **What you built:**
- Independent public release repository
- Automated cross-platform package builds (Windows + Linux)
- Professional documentation (English + Chinese)
- CI/CD pipeline with GitHub Actions
- Hospital-ready offline deployment packages

🎯 **Key achievements:**
- No Windows machine needed for Windows builds
- Automated releases on git tag push
- Separate development and release repositories
- Production-ready distribution system

⏱️ **Total time**: 30-60 minutes for initial setup

---

## Getting Help

If you encounter issues during setup:

1. **Check logs**: GitHub Actions → View workflow logs
2. **Verify files**: Run `./scripts/verify_package.sh`
3. **Review docs**: See [RELEASE_REPO_IMPLEMENTATION_GUIDE.md](docs/deployment/RELEASE_REPO_IMPLEMENTATION_GUIDE.md)
4. **Ask for help**: Create GitHub Issue or Discussion

---

**Ready to deploy!** 🚀

After completing these steps, you'll have a professional release repository that automatically builds Windows and Linux packages for hospital deployment.
