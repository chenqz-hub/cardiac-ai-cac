# How to Run the Cardiac Calcium Scoring Application

## Quick Start Guide for VS Code Terminal

This guide shows you exactly how to run the refactored **Cardiac Calcium Scoring System** in VS Code Terminal.

---

## ✅ Verified System Status (2025-10-18)

Your system is **ready to run**:

- ✅ **AI-CAC Model**: 1.2GB model file exists at `models/va_non_gated_ai_cac_model.pth`
- ✅ **Virtual Environment**: Python venv configured at `../../venv`
- ✅ **GPU Available**: NVIDIA GeForce RTX 2060 (6GB VRAM)
- ✅ **Data Directory**: 101 CHD patient DICOM folders detected
- ✅ **Previous Results**: 197 cases already processed successfully

---

## 📍 Step 1: Open VS Code Terminal

```bash
# Press Ctrl + ` (backtick) to open terminal
# OR Menu → Terminal → New Terminal
```

**Make sure you're in WSL/Ubuntu terminal**, not PowerShell!

---

## 📂 Step 2: Navigate to Application Directory

```bash
cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/cardiac_calcium_scoring
```

**Verify location:**
```bash
pwd
# Should output: .../cardiac_calcium_scoring

ls -lh models/va_non_gated_ai_cac_model.pth
# Should show: ~1.2GB model file
```

---

## 🚀 Step 3: Run the Application

### Method 1: Direct Python Command (Recommended)

This is the **most reliable method** for the refactored application.

**Quick 1-patient test:**
```bash
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 1
```

**Process 5 patients (quick test):**
```bash
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 5
```

**Process all CHD patients (full mode):**
```bash
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode full
```

**Clear cache and reprocess:**
```bash
../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 5 --clear-cache
```

### Method 2: Interactive Python (Manual Control)

If you want to manually confirm before processing:

```bash
../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 5
# Then press ENTER when prompted to start processing
```

### Method 3: View Help and All Options

```bash
../../venv/bin/python cli/run_calcium_scoring.py --help
```

**Available options:**
- `--config CONFIG` - Config file path (default: config/config.yaml)
- `--mode {pilot,full}` - Processing mode
- `--pilot-limit N` - Number of cases in pilot mode
- `--device {cuda,cpu}` - Force CPU or GPU
- `--data-dir PATH` - Override data directory
- `--clear-cache` - Start fresh (ignore resume cache)
- `--no-resume` - Disable resume feature

---

## 📊 Expected Output

When you run the application, you'll see:

```
Initializing...
  - Loading configuration...
  - Detecting hardware...
  ✓ Configuration loaded

======================================================================
SYSTEM INFORMATION
======================================================================

Software:
  Version: NB10 AI-CAC v2.0.0-alpha
  Mode: pilot
    → Test mode - will process up to 5 cases

Hardware:
  Device: cuda
    → GPU: NVIDIA GeForce RTX 2060
    → VRAM: 6.0 GB
    → Estimated: ~10-20 sec per case

Performance Profile: Standard
======================================================================

Scanning DICOM data...
✓ Found 101 patient folders

Pilot Mode Limit:
  Will process: 5 cases (first 5)
  Remaining: 96 cases

Ready to Process:
  Cases: 5
  Estimated time: ~75 seconds

Press ENTER to start processing (or Ctrl+C to cancel)...

Preparing AI model...
  - Loading libraries (this may take ~30 seconds)...
  - Initializing model architecture...
  - Loading weights...
  ✓ Model ready

Processing DICOM data: 100%|████████████████████| 5/5 [01:15<00:00, 15.1s/it]

======================================================================
✓ PROCESSING COMPLETE
======================================================================

Results Summary:
  Total cases: 5
  Successful: 5 (100.0%)
  Failed: 0

Output Files:
  - Results CSV: /home/.../output/nb10_results_20251018_205342.csv
  - Latest (symlink): /home/.../output/nb10_results_latest.csv
  - Log file: /home/.../logs/nb10_20251018_205342.log

Agatston Score Statistics:
  Mean: 245.6
  Median: 123.0
  Range: 0.0 - 747.0

  Risk Categories:
    - No calcification (0): 2 cases (40.0%)
    - Mild (1-100): 0 cases (0.0%)
    - Moderate (101-400): 2 cases (40.0%)
    - Severe (>400): 1 case (20.0%)
```

---

## 📁 Finding Your Results

After processing, results are saved in multiple files:

### 1. **CSV Results File**

```bash
# View latest results
ls -lht output/*.csv | head -3

# Quick preview with Python
../../venv/bin/python -c "
import pandas as pd
df = pd.read_csv('output/nb10_results_complete.csv')
print(f'Total cases: {len(df)}')
print(df[['patient_id', 'status', 'agatston_score', 'has_calcification']].head())
"
```

**Current results file**: `output/nb10_results_complete.csv` (197 cases)

**Columns in CSV:**
- `patient_id` - Patient identifier
- `status` - success/failed
- `agatston_score` - Calcium score
- `calcium_volume_mm3` - Volume in cubic mm
- `calcium_mass_mg` - Mass in milligrams
- `num_slices` - Number of DICOM slices processed
- `has_calcification` - Boolean flag
- `patient_age` - Age (if available)
- `patient_sex` - Sex (if available)
- `is_premature_cad` - Premature CAD flag
- `timestamp` - Processing timestamp

### 2. **Log Files**

```bash
# View recent logs
ls -lht logs/*.log | head -5

# Tail latest log in real-time
tail -f logs/nb10_*.log
```

### 3. **Cache File (Resume Feature)**

```bash
# Check resume cache
ls -lh output/.nb10_resume_cache.csv
```

This file tracks which cases have been processed, allowing you to resume after interruptions.

---

## 🔄 Resume Feature

The application automatically saves progress and can resume if interrupted:

**How it works:**
1. Each successfully processed case is saved to `.nb10_resume_cache.csv`
2. If you run again, it skips already-processed cases
3. Only new or failed cases are processed

**To start fresh (clear cache):**
```bash
../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 5 --clear-cache
```

---

## 🎯 Common Use Cases

### Use Case 1: Quick System Test (1 patient)
```bash
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 1
```
**Time**: ~15 seconds

### Use Case 2: Validation Test (10 patients)
```bash
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 10
```
**Time**: ~2-3 minutes

### Use Case 3: Process All CHD Patients
```bash
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode full
```
**Time**: ~30-45 minutes for 101 patients

### Use Case 4: Force CPU Mode (No GPU)
```bash
../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 5 --device cpu
```
**Time**: ~5 minutes per patient (much slower)

### Use Case 5: Process Custom Directory
```bash
../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 5 --data-dir /path/to/other/dicom/data
```

### Use Case 6: Process Normal Group
```bash
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config_normal.yaml --mode full
```
(This uses the `config_normal.yaml` which points to Normal group data directory)

---

## 📈 Monitoring Progress

### Option 1: Watch in Single Terminal

The progress bar shows real-time status:
```
Processing DICOM data: 42%|████████▎        | 21/50 [05:15<07:15, 15.0s/it]
```

### Option 2: Split Terminal (Side-by-Side)

1. Click **"Split Terminal"** icon in VS Code terminal panel
2. **Left pane**: Run processing command
3. **Right pane**: Monitor log file
   ```bash
   tail -f logs/nb10_*.log
   ```

### Option 3: Multiple Terminal Tabs

```bash
# Tab 1: Run processing
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 10

# Tab 2 (Ctrl + Shift + `): Monitor logs
tail -f logs/nb10_*.log

# Tab 3: Check GPU usage
nvidia-smi -l 5  # Update every 5 seconds
```

---

## 🛠️ Troubleshooting

### Issue 1: "CUDA out of memory"

**Solution**: Reduce batch size or use CPU
```bash
../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 5 --device cpu
```

### Issue 2: "ModuleNotFoundError"

**Solution**: Verify virtual environment
```bash
ls -ld ../../venv
../../venv/bin/python -c "import torch; print(torch.__version__)"
```

If missing packages:
```bash
../../venv/bin/pip install -r deployment/requirements.txt
```

### Issue 3: "Model file not found"

**Solution**: Check model path
```bash
ls -lh models/va_non_gated_ai_cac_model.pth
# Should show: ~1.2GB file

# If missing, download it (instructions in deployment docs)
```

### Issue 4: EOFError when running

This happens if the script waits for ENTER but receives EOF. **Solution**: Use `echo "" |` prefix:
```bash
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 5
```

---

## ⚙️ Configuration Files

### CHD Group Config
**File**: `config/config.yaml`

Key settings:
```yaml
paths:
  data_dir: "/home/.../ct_images_dicom/chd"  # CHD data

processing:
  mode: "full"
  pilot_limit: 10
  device: "auto"  # GPU if available
```

### Normal Group Config
**File**: `config/config_normal.yaml`

Key settings:
```yaml
paths:
  data_dir: "/home/.../ct_images_dicom/normal"  # Normal data
```

**To edit config:**
```bash
nano config/config.yaml  # or use VS Code editor
```

---

## 📋 Quick Command Reference

```bash
# Navigate to application directory
cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/cardiac_calcium_scoring

# Quick 1-patient test
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 1

# 10-patient validation
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 10

# Process all CHD patients
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode full

# Process all Normal patients
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config_normal.yaml --mode full

# Force CPU mode
../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 5 --device cpu

# Clear cache and reprocess
../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 5 --clear-cache

# View help
../../venv/bin/python cli/run_calcium_scoring.py --help

# Check GPU status
nvidia-smi

# View recent results
ls -lht output/*.csv | head -5

# Quick results preview
../../venv/bin/python -c "import pandas as pd; df = pd.read_csv('output/nb10_results_complete.csv'); print(df[['patient_id','status','agatston_score']].head(10))"

# Monitor logs
tail -f logs/nb10_*.log
```

---

## 📚 Related Documentation

- **[VSCODE_QUICK_START.md](VSCODE_QUICK_START.md)** - Detailed VS Code Terminal guide
- **[config/config.yaml](config/config.yaml)** - CHD group configuration
- **[config/config_normal.yaml](config/config_normal.yaml)** - Normal group configuration
- **Week 6 Test Results** - 196/197 successful cases (99.5%)

---

## 🎉 Current System Status

As of **2025-10-18 20:53**:

- **Total Cases Processed**: 197 (CHD: 101, Normal: 96)
- **Success Rate**: 99.5% (196/197)
- **Latest Results File**: `output/nb10_results_complete.csv`
- **GPU**: NVIDIA RTX 2060 (6GB)
- **Average Processing Time**: ~15 seconds per case (GPU mode)

**Sample Results (from nb10_results_complete.csv):**
```
patient_id                     status  agatston_score  has_calcification
dicom_7308118.zip_3893171      success       0.0             False
dicom_7378446.zip_2922834      success     532.0             True
dicom_8247598.zip_3906672      success     747.0             True
dicom_6567397.zip_3677701      success       0.0             False
dicom_6499278.zip_1899967      success       0.0             False
```

---

**You're all set to run the application!** 🚀

For quick start, just copy and paste:
```bash
cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/cardiac_calcium_scoring
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 5
```

---

**Generated with Claude Code**
