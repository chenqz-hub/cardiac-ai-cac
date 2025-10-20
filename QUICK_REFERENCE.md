# Quick Reference Card

**Cardiac AI-CAC Release Repository**

---

## 🚀 First-Time Setup (60 min)

```bash
# 1. Create repo on GitHub: cardiac-ai-cac

# 2. Clone and setup
cd ~/projects/
git clone git@github.com:YOUR_USERNAME/cardiac-ai-cac.git
cd cardiac-ai-cac
cp -r /tmp/cardiac-ai-cac-template/* .
cp -r /tmp/cardiac-ai-cac-template/.github .

# 3. Customize
sed -i 's/USERNAME/your-username/g' README.md README_CN.md
sed -i 's/your-email@example.com/your@email.com/g' README.md README_CN.md

# 4. Sync code
export DEV_REPO_PATH=~/projects/.../cardiac-ml-research
./scripts/sync_from_dev.sh  # Enter: v1.1.4

# 5. Commit
git add .
git commit -m "Initial release repository setup"
git push origin main

# 6. Create release
git tag -a v1.1.4 -m "Release v1.1.4"
git push origin v1.1.4
```

---

## 📦 Creating a New Release (10 min)

```bash
# 1. Sync from dev repo
cd ~/projects/cardiac-ai-cac
./scripts/sync_from_dev.sh  # Enter new version

# 2. Update CHANGELOG.md
# Edit manually with changes

# 3. Commit
git add .
git commit -m "Prepare v1.1.5 release"
git push origin main

# 4. Create release
git tag -a v1.1.5 -m "Release v1.1.5 - <summary>"
git push origin v1.1.5

# GitHub Actions automatically builds packages
```

---

## 🧪 Testing Builds

### Manual Test (No Release)

1. Go to: https://github.com/YOUR_USERNAME/cardiac-ai-cac/actions
2. Click "Build Windows Package" or "Build Linux Package"
3. Click "Run workflow" → "Run workflow"
4. Wait 10-15 minutes
5. Download artifact from run page

### Verify Package

```bash
./scripts/verify_package.sh /path/to/extracted/package
```

Expected: `✅ Package verification PASSED`

---

## 📁 Important Paths

| What | Path |
|------|------|
| Template | `/tmp/cardiac-ai-cac-template/` |
| Dev Repo | `~/projects/.../cardiac-ml-research/` |
| Release Repo | `~/projects/cardiac-ai-cac/` |
| GitHub Actions | https://github.com/YOUR_USERNAME/cardiac-ai-cac/actions |
| Releases | https://github.com/YOUR_USERNAME/cardiac-ai-cac/releases |

---

## 🔧 Common Commands

```bash
# Check template files
ls -la /tmp/cardiac-ai-cac-template/

# Sync from dev
./scripts/sync_from_dev.sh

# Verify package
./scripts/verify_package.sh /path/to/package

# List tags
git tag -l

# Delete tag (if mistake)
git tag -d v1.1.4
git push origin :refs/tags/v1.1.4

# View GitHub Actions status
# Visit: https://github.com/YOUR_USERNAME/cardiac-ai-cac/actions
```

---

## 📊 Package Outputs

| Platform | File | Size |
|----------|------|------|
| Windows | `cardiac-ai-cac-windows-v1.1.4.zip` | ~2.1 GB |
| Linux | `cardiac-ai-cac-linux-v1.1.4.tar.gz` | ~2.0 GB |

**Contains**:
- Source code
- All dependencies (offline install)
- AI-CAC model (1.8 GB)
- Installation scripts
- Documentation

---

## 🐛 Troubleshooting

### Build Fails

1. Check Actions logs: GitHub → Actions → Click run → View logs
2. Common issues:
   - Model download fails → Check Google Drive permissions
   - Requirements missing → Check requirements-cpu.txt in repo
   - Wheel download fails → Check package availability

### Package Too Large

- Artifact: 2GB limit (usually OK, model is 1.8GB)
- Release: 2GB per file (usually OK)
- If over: Provide model as separate download

### Installation Fails

**Windows**:
- Need Python 3.8-3.12 installed
- Run install.bat as Administrator

**Linux**:
- Need `python3-venv`: `sudo apt install python3-venv`
- Make executable: `chmod +x install.sh`

---

## 📖 Documentation

| File | Purpose |
|------|---------|
| `QUICK_START_SETUP.md` | Step-by-step first-time setup |
| `README_TEMPLATE.md` | Complete template documentation |
| `RELEASE_REPO_IMPLEMENTATION_GUIDE.md` | Detailed implementation guide |
| `RELEASE_REPOSITORY_DESIGN.md` | Architecture and design |
| `RELEASE_REPO_COMPLETE_PACKAGE.md` | Summary and inventory |

---

## ✅ Pre-Release Checklist

- [ ] CHANGELOG.md updated
- [ ] Version number correct in all docs
- [ ] No placeholder text (USERNAME, email)
- [ ] Source code synced from dev repo
- [ ] Tests passing in dev repo
- [ ] Manual build tested via GitHub Actions
- [ ] Package verified with verify_package.sh

---

## 🎯 Version Naming

```
v{MAJOR}.{MINOR}.{PATCH}

v1.1.4
 │ │ └─ Patch: Bug fixes
 │ └─── Minor: New features (backward compatible)
 └───── Major: Breaking changes

Examples:
v1.1.4 → v1.1.5  (bug fix)
v1.1.5 → v1.2.0  (new feature)
v1.2.0 → v2.0.0  (breaking change)
```

---

## 📞 Support

**Template Issues**:
- Check: QUICK_START_SETUP.md
- Check: README_TEMPLATE.md

**Production Issues**:
- GitHub Issues: https://github.com/YOUR_USERNAME/cardiac-ai-cac/issues
- Discussions: https://github.com/YOUR_USERNAME/cardiac-ai-cac/discussions

---

**Template Version**: 1.0.0
**Last Updated**: 2025-10-19
