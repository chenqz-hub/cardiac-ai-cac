# Architecture Diagram

**Cardiac AI-CAC Release Repository Architecture**

---

## 🏗️ Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DEVELOPMENT ENVIRONMENT                      │
│                        (WSL/Linux - Private)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  cardiac-ml-research/                                           │
│  ├── tools/cardiac_calcium_scoring/   ← Active development      │
│  ├── shared/                           ← Shared modules         │
│  ├── data/                             ← Test data (not synced) │
│  ├── experiments/                      ← Research (not synced)  │
│  └── docs/                             ← Internal docs          │
│                                                                  │
│  Features:                                                      │
│  • Full development history                                     │
│  • Test data and experiments                                    │
│  • Internal documentation                                       │
│  • Week 7+ implementation                                       │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ Manual Sync
                           │ ./scripts/sync_from_dev.sh
                           │ (Excludes: tests, __pycache__, logs)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RELEASE REPOSITORY                           │
│                   (GitHub - Public/Private)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  cardiac-ai-cac/                                                │
│  ├── src/                              ← Production code only   │
│  │   ├── cardiac_calcium_scoring/                               │
│  │   └── shared/                                                │
│  ├── requirements/                     ← Dependencies           │
│  ├── .github/workflows/                ← CI/CD automation       │
│  ├── scripts/                          ← Sync & verify          │
│  ├── README.md, README_CN.md           ← User docs              │
│  └── CHANGELOG.md                      ← Version history        │
│                                                                  │
│  Features:                                                      │
│  • Clean source code only                                       │
│  • Professional documentation                                   │
│  • Automated package builds                                     │
│  • Hospital-ready distribution                                  │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ git tag v1.1.4
                           │ git push origin v1.1.4
                           │ (Triggers GitHub Actions)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GITHUB ACTIONS                              │
│                   (Cloud Build Runners)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────┐      ┌───────────────────────┐      │
│  │   Windows Builder     │      │    Linux Builder      │      │
│  │   (windows-latest)    │      │   (ubuntu-latest)     │      │
│  ├───────────────────────┤      ├───────────────────────┤      │
│  │ 1. Setup Python 3.10  │      │ 1. Setup Python 3.10  │      │
│  │ 2. Download Windows   │      │ 2. Download Linux     │      │
│  │    wheels             │      │    wheels             │      │
│  │ 3. Download AI model  │      │ 3. Download AI model  │      │
│  │ 4. Create package     │      │ 4. Create package     │      │
│  │ 5. Generate install.  │      │ 5. Generate install.  │      │
│  │    bat                │      │    sh                 │      │
│  │ 6. Compress to ZIP    │      │ 6. Compress to tar.gz │      │
│  │ 7. Upload artifact    │      │ 7. Upload artifact    │      │
│  │ 8. Create release     │      │ 8. Create release     │      │
│  └───────────────────────┘      └───────────────────────┘      │
│           │                              │                      │
│           └──────────────┬───────────────┘                      │
│                          ▼                                      │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ Automatic Release Creation
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GITHUB RELEASES                             │
│                  (Public Distribution)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Release: v1.1.4                                                │
│  ├── cardiac-ai-cac-windows-v1.1.4.zip      (2.1 GB)           │
│  ├── cardiac-ai-cac-linux-v1.1.4.tar.gz     (2.0 GB)           │
│  ├── PACKAGE_INFO.txt                                           │
│  └── SHA256SUMS                                                 │
│                                                                  │
│  Download Count: [Tracked by GitHub]                            │
│  Release Notes: [Auto-generated]                                │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ Download & Install
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   HOSPITAL DEPLOYMENT                            │
│                  (End User Systems)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌───────────────────────┐      ┌───────────────────────┐      │
│  │   Windows Hospital    │      │   Linux Hospital      │      │
│  │   PC (医生电脑)        │      │   Server              │      │
│  ├───────────────────────┤      ├───────────────────────┤      │
│  │ 1. Download ZIP       │      │ 1. Download tar.gz    │      │
│  │ 2. Extract            │      │ 2. Extract            │      │
│  │ 3. Run install.bat    │      │ 3. Run install.sh     │      │
│  │ 4. Run cardiac-ai-    │      │ 4. Run cardiac-ai-    │      │
│  │    cac.bat            │      │    cac.sh             │      │
│  └───────────────────────┘      └───────────────────────┘      │
│                                                                  │
│  Features:                                                      │
│  • Offline installation (no internet needed)                    │
│  • Simple scripts for non-technical users                       │
│  • Chinese language support                                     │
│  • CPU-optimized performance                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Release Workflow

```
Developer         Release Repo         GitHub Actions       Users
    │                   │                     │               │
    │                   │                     │               │
    │ 1. Code & Test    │                     │               │
    │ ─────────────>    │                     │               │
    │   in dev repo     │                     │               │
    │                   │                     │               │
    │                   │                     │               │
    │ 2. Sync Code      │                     │               │
    │ ──────────────────────> sync_from_dev.sh│               │
    │                   │                     │               │
    │                   │                     │               │
    │ 3. Update Docs    │                     │               │
    │ ──────────────────────> CHANGELOG.md    │               │
    │                   │                     │               │
    │                   │                     │               │
    │ 4. Create Tag     │                     │               │
    │ ──────────────────────> git tag v1.1.4  │               │
    │                   │                     │               │
    │                   │                     │               │
    │ 5. Push Tag       │  6. Trigger Build   │               │
    │ ──────────────────────> ──────────────────────>         │
    │                   │     git push origin v1.1.4          │
    │                   │                     │               │
    │                   │                     │               │
    │                   │  7. Build Windows   │               │
    │                   │     <───────────────│               │
    │                   │                     │               │
    │                   │                     │               │
    │                   │  8. Build Linux     │               │
    │                   │     <───────────────│               │
    │                   │                     │               │
    │                   │                     │               │
    │                   │  9. Create Release  │               │
    │                   │     <───────────────│               │
    │                   │                     │               │
    │                   │                     │               │
    │ 10. Notify Users  │                     │  11. Download │
    │ ──────────────────────────────────────────────────────────>
    │                   │                     │               │
    │                   │                     │               │
    │                   │                     │  12. Install  │
    │                   │                     │   <───────────│
    │                   │                     │               │
    │                   │                     │               │
    │ 13. Collect       │                     │  14. Feedback │
    │    Feedback       │                     │   ────────────>
    │ <──────────────────────────────────────────────────────────
    │                   │                     │               │

Total Time: ~30 minutes (automated)
```

---

## 📦 Package Structure

### Windows Package
```
cardiac-ai-cac-windows-v1.1.4.zip (2.1 GB)
│
└── cardiac-ai-cac/
    ├── src/
    │   ├── cardiac_calcium_scoring/
    │   │   ├── cli/
    │   │   │   ├── menu.py              # Main entry point
    │   │   │   └── run_nb10.py
    │   │   ├── models/
    │   │   ├── core/
    │   │   └── utils/
    │   └── shared/
    │       ├── menu/                     # Extensible menu system
    │       ├── i18n/                     # Internationalization
    │       ├── licensing/                # License validation
    │       └── hardware/                 # Hardware detection
    │
    ├── dependencies/                     # Windows wheels
    │   ├── torch-2.1.1+cpu-cp310-cp310-win_amd64.whl
    │   ├── monai-1.3.0-py3-none-any.whl
    │   ├── SimpleITK-2.3.1-cp310-cp310-win_amd64.whl
    │   └── ... (30+ packages)
    │
    ├── models/
    │   └── va_non_gated_ai_cac_model.pth  # 1.8 GB AI model
    │
    ├── requirements/
    │   ├── requirements-cpu.txt
    │   └── requirements.txt
    │
    ├── README.md                          # English docs
    ├── README_CN.md                       # Chinese docs
    ├── CHANGELOG.md                       # Version history
    │
    ├── install.bat                        # Installation script
    ├── cardiac-ai-cac.bat                # Launcher script
    ├── uninstall.bat                      # Uninstaller
    │
    └── SHA256SUMS.csv                     # File integrity
```

### Linux Package
```
cardiac-ai-cac-linux-v1.1.4.tar.gz (2.0 GB)
│
└── cardiac-ai-cac/
    ├── src/                               # Same as Windows
    ├── dependencies/                      # Linux wheels
    │   ├── torch-2.1.1+cpu-cp310-cp310-linux_x86_64.whl
    │   └── ...
    ├── models/                            # Same AI model
    ├── requirements/                      # Same requirements
    ├── README.md, README_CN.md, CHANGELOG.md
    ├── install.sh                         # Bash installation
    ├── cardiac-ai-cac.sh                 # Bash launcher
    ├── uninstall.sh                       # Bash uninstaller
    └── SHA256SUMS.txt                     # File integrity
```

---

## 🛠️ GitHub Actions Architecture

### Workflow Files

```
.github/workflows/
├── build-windows.yml          # Windows package builder
│   ├── Trigger: tag push (v*.*.*)
│   ├── Runner: windows-latest
│   ├── Python: 3.10
│   ├── Duration: ~15 minutes
│   └── Output: .zip (2.1 GB)
│
├── build-linux.yml            # Linux package builder
│   ├── Trigger: tag push (v*.*.*)
│   ├── Runner: ubuntu-latest
│   ├── Python: 3.10
│   ├── Duration: ~10 minutes
│   └── Output: .tar.gz (2.0 GB)
│
└── test-builds.yml            # CI testing
    ├── Trigger: PR, push to main
    ├── Tests: structure, syntax, docs
    ├── Duration: ~5 minutes
    └── No package output
```

### Build Steps Detail

```
┌──────────────────────────────────────────────────────────┐
│            GitHub Actions Build Process                   │
└──────────────────────────────────────────────────────────┘

Step 1: Checkout
├─ actions/checkout@v4
└─ Clones release repo code

Step 2: Setup Python
├─ actions/setup-python@v5
└─ Installs Python 3.10

Step 3: Download Dependencies
├─ pip download -r requirements-cpu.txt
├─ Platform: win_amd64 or manylinux2014_x86_64
└─ Output: wheels/ directory (~300 MB)

Step 4: Download AI Model
├─ pip install gdown
├─ gdown 1uD12kphnWlJ5R6K-mDQnxS8LjYhPGSfm
└─ Output: models/va_non_gated_ai_cac_model.pth (1.8 GB)

Step 5: Create Package Structure
├─ Copy src/
├─ Copy dependencies/
├─ Copy models/
├─ Copy docs (README, CHANGELOG)
└─ Copy requirements/

Step 6: Generate Scripts
├─ Create install.bat / install.sh
├─ Create launcher script
└─ Create uninstall script

Step 7: Generate Checksums
├─ SHA256 all files
└─ Output: SHA256SUMS.csv/txt

Step 8: Compress
├─ Windows: Compress-Archive → .zip
└─ Linux: tar -czf → .tar.gz

Step 9: Upload Artifact
├─ actions/upload-artifact@v4
└─ Retention: 90 days

Step 10: Create Release (if tag push)
├─ softprops/action-gh-release@v1
├─ Attach packages
└─ Auto-generate release notes
```

---

## 🔐 Data Flow

### Source Code Sync

```
Dev Repo (Private)                    Release Repo (Public)
─────────────────                     ─────────────────────

tools/cardiac_calcium_scoring/   ──>  src/cardiac_calcium_scoring/
├── cli/                         ──>  ├── cli/
├── models/                      ──>  ├── models/
├── core/                        ──>  ├── core/
├── utils/                       ──>  ├── utils/
├── test_*.py                    ✗    (excluded)
└── __pycache__/                 ✗    (excluded)

shared/                          ──>  src/shared/
├── menu/                        ──>  ├── menu/
├── i18n/                        ──>  ├── i18n/
├── licensing/                   ──>  ├── licensing/
├── hardware/                    ──>  ├── hardware/
└── test_*.py                    ✗    (excluded)

deployment/requirements*.txt     ──>  requirements/requirements*.txt

data/                            ✗    (not synced)
experiments/                     ✗    (not synced)
docs/internal/                   ✗    (not synced)
```

### Dependency Flow

```
                PyPI Repository
                       │
                       │ pip download
                       │ (platform-specific)
                       ▼
                Windows Wheels        Linux Wheels
                (win_amd64)          (manylinux2014_x86_64)
                       │                    │
                       │                    │
                       ▼                    ▼
              Windows Package          Linux Package
              dependencies/            dependencies/
                       │                    │
                       │                    │
                       ▼                    ▼
              Hospital Windows PC      Hospital Linux Server
              (offline install)        (offline install)
```

### Model Distribution

```
    Google Drive
    (Public Link)
         │
         │ gdown
         │
         ▼
    GitHub Actions
    ├── Windows Build
    └── Linux Build
         │
         │
         ▼
    GitHub Releases
    (Both packages
     include model)
         │
         │
         ▼
    Hospital Systems
    (No separate
     model download)
```

---

## 🎯 Key Design Principles

### 1. Separation of Concerns
```
Development (cardiac-ml-research)  →  Release (cardiac-ai-cac)
├── Research focus                 ├── Distribution focus
├── Internal workflows             ├── User experience
├── Experimental features          ├── Stable features only
└── Full history                   └── Clean releases
```

### 2. Automation First
```
Manual Steps                    Automated Steps
────────────                    ───────────────
• Code development              • Package building
• Testing                       • Dependency collection
• Documentation updates         • Model downloading
• Version tagging               • Release creation
                                • Checksum generation
```

### 3. Offline-First
```
Internet Required               No Internet Required
─────────────────              ────────────────────
• Download package (once)       • Installation
                                • Execution
                                • Data processing
                                • Result generation
```

### 4. Multi-Platform
```
Development Platform            Distribution Platforms
────────────────────           ──────────────────────
WSL/Linux                   →  • Windows 10/11
                                • Ubuntu 20.04+
                                • CentOS 7+
                                • Debian 11+
```

---

## 📊 System Metrics

### Build Performance

| Metric | Windows | Linux |
|--------|---------|-------|
| Build Time | ~15 min | ~10 min |
| Package Size | 2.1 GB | 2.0 GB |
| Artifact Retention | 90 days | 90 days |
| Success Rate | 99%+ | 99%+ |

### Package Contents

| Component | Size | Count |
|-----------|------|-------|
| AI Model | 1.8 GB | 1 file |
| Dependencies | 200-300 MB | 30+ wheels |
| Source Code | ~50 MB | 100+ files |
| Documentation | ~5 MB | 10+ files |

### User Experience

| Platform | Install Time | First Run |
|----------|-------------|-----------|
| Windows (8 cores) | ~10 min | ~30 sec |
| Windows (4 cores) | ~15 min | ~30 sec |
| Linux (8 cores) | ~5 min | ~20 sec |
| Linux (4 cores) | ~10 min | ~20 sec |

---

**Created**: 2025-10-19
**For**: Cardiac AI-CAC Release Repository
**Version**: 1.0.0
