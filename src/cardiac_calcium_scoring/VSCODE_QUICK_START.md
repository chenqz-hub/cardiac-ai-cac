# VS Code Terminal Quick Start Guide

## 🚀 How to Run the Application in VS Code Terminal

This guide shows you how to run the **Cardiac Calcium Scoring System** directly in VS Code's integrated WSL Terminal.

---

## ✅ Prerequisites

1. **VS Code** installed with WSL extension
2. **WSL** (Ubuntu) configured
3. **Virtual environment** already created at `../../venv`
4. **AI-CAC model** downloaded (~1.2GB) in `models/` directory

---

## 📍 Step 1: Open VS Code Terminal

```
Method 1: Press Ctrl + ` (backtick)
Method 2: Menu → Terminal → New Terminal
Method 3: Press Ctrl + Shift + `
```

**Verify WSL Environment:**
You should see a prompt like:
```bash
user@hostname:/path/to/project$
```

NOT like:
```powershell
PS C:\path\to\project>  # This is PowerShell - switch to WSL!
```

---

## 📂 Step 2: Navigate to Application Directory

```bash
cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/cardiac_calcium_scoring
```

**Verify you're in the right place:**
```bash
pwd
# Should output: /home/wuxia/.../cardiac_calcium_scoring

ls
# Should show: calcium_scoring.sh, cli/, core/, models/, etc.
```

---

## 🎯 Step 3: Choose Your Running Method

### Method 1: Interactive Menu (Recommended for Beginners)

```bash
bash calcium_scoring.sh
```

**What you'll see:**
```
========================================================================
                   NB10 AI-CAC 冠状动脉钙化评分工具
========================================================================
                      统一管理界面 v1.1.0
========================================================================

  【快速处理】
  1. 快速测试 (Pilot模式 - 5例)              [./nb10.sh test]
  2. 处理CHD组 (完整模式)                     [./nb10.sh chd]
  3. 处理Normal组 (完整模式)                  [./nb10.sh normal]

  【统计分析】
  4. CHD vs Normal组对比分析                 [./nb10.sh analyze]

  【系统管理】
  5. 查看系统配置                            [./nb10.sh config]
  6. 查看操作日志                            [./nb10.sh logs]
  7. 查看帮助文档                            [./nb10.sh help]
  ...
```

### Method 2: Direct Command (For Quick Tasks)

**Quick test (5 patients):**
```bash
bash calcium_scoring.sh test
```

**Process CHD group:**
```bash
bash calcium_scoring.sh chd
```

**Process Normal group:**
```bash
bash calcium_scoring.sh normal
```

**View system config:**
```bash
bash calcium_scoring.sh config
```

**View help:**
```bash
bash calcium_scoring.sh help
```

### Method 3: Direct Python CLI (For Advanced Users)

**Activate virtual environment first:**
```bash
source ../../venv/bin/activate
```

**Run pilot test (10 patients):**
```bash
python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 10
```

**Run full processing (all patients):**
```bash
python cli/run_calcium_scoring.py --config config/config.yaml --mode full
```

**View all options:**
```bash
python cli/run_calcium_scoring.py --help
```

---

## 📊 Understanding the Modes

| Mode | Description | Speed | Use Case |
|------|-------------|-------|----------|
| **pilot** | Test mode - process limited patients | Fast (5-10 patients) | Quick testing, validation |
| **full** | Complete mode - process all patients | Slow (100+ patients) | Production run |

---

## 🎨 Example Session in VS Code Terminal

Here's what a typical session looks like:

```bash
# 1. Open Terminal in VS Code (Ctrl + `)
# 2. Navigate to directory
cd /home/wuxia/projects/.../cardiac_calcium_scoring

# 3. Run quick test
bash calcium_scoring.sh test

# Output:
========================================================================
                        快速测试 (Pilot模式)
========================================================================

此模式将处理5例患者数据，用于快速验证系统功能。
预计耗时: 约2-3分钟

按Enter继续...

正在运行快速测试...

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
    → Pilot mode - will process 5 test cases

Hardware:
  Device: cuda
    → GPU: NVIDIA GeForce RTX 2060
    → VRAM: 6.0 GB
    → Estimated: ~10-20 sec per case

Performance Profile: Professional
======================================================================

Processing 5 cases...
[1/5 - 20%] Processing: patient_001
  ✓ Complete - Agatston Score: 123.0 (took 15s)
...
```

---

## 📁 Output Files Location

After processing, find results here:

```bash
# Results CSV
ls output/*.csv

# Example output:
output/nb10_results_20251018_163032.csv
output/nb10_results_latest.csv  # Symlink to latest

# Logs
ls logs/*.log

# Example:
logs/nb10_20251018_160631.log
logs/menu/nb10_menu_20251018_180000.log
```

---

## 🔍 Monitoring Progress in Real-Time

**Open a second terminal tab:**
```bash
# Tab 1: Run processing
bash calcium_scoring.sh chd

# Tab 2: Monitor log (in another terminal tab)
tail -f logs/nb10_*.log
```

**Or use VS Code's split terminal:**
```
1. Click the "Split Terminal" icon in terminal panel
2. Run processing in one pane
3. Monitor logs in another pane
```

---

## ⚡ Quick Commands Reference

```bash
# Quick test (5 patients)
bash calcium_scoring.sh test

# View system info
bash calcium_scoring.sh config

# Show help
bash calcium_scoring.sh help

# Direct Python run (pilot mode, 10 patients)
source ../../venv/bin/activate
python cli/run_calcium_scoring.py --mode pilot --pilot-limit 10

# Check GPU status
nvidia-smi

# Check recent results
ls -lht output/*.csv | head -5

# Check recent logs
ls -lht logs/*.log | head -5
```

---

## 🐛 Troubleshooting in VS Code Terminal

### Issue: "Command not found"

```bash
# Make sure script is executable
chmod +x calcium_scoring.sh

# Run with bash explicitly
bash calcium_scoring.sh
```

### Issue: "Virtual environment not found"

```bash
# Check venv location
ls -la ../../venv

# If missing, create it
cd ../..
python3 -m venv venv
source venv/bin/activate
pip install -r tools/cardiac_calcium_scoring/deployment/requirements.txt
```

### Issue: "AI-CAC model not found"

```bash
# Check model file
ls -lh models/va_non_gated_ai_cac_model.pth

# Should show: ~1.2GB file
# If missing, download from model repository
```

### Issue: Terminal shows PowerShell (PS>)

```bash
# Switch to WSL:
# 1. Click the dropdown in terminal panel
# 2. Select "Ubuntu (WSL)"
# 3. Or create new terminal: Ctrl + Shift + `
```

---

## 💡 Pro Tips for VS Code Terminal

1. **Multiple Terminals**: Open multiple tabs for parallel work
   - Ctrl + Shift + ` : New terminal
   - Ctrl + PgUp/PgDn : Switch between terminals

2. **Split Terminal**: View output side-by-side
   - Click split icon in terminal panel
   - Run process in left, monitor logs in right

3. **Search in Terminal**: Find specific output
   - Ctrl + F : Search in terminal output
   - Useful for finding errors or specific patient IDs

4. **Clear Terminal**: Clean up cluttered output
   - Type `clear` or press Ctrl + L

5. **Command History**: Repeat previous commands
   - Press Up Arrow : Previous command
   - Press Ctrl + R : Search command history

6. **Auto-completion**: Save typing
   - Press Tab : Auto-complete file/directory names
   - Double Tab : Show all possible completions

---

## 📚 Related Documentation

- **User Manual**: [docs/USER_MANUAL.md](docs/USER_MANUAL.md)
- **Deployment Guide**: [docs/DEPLOYMENT_GUIDE.md](../../docs/deployment/DEPLOYMENT_GUIDE.md)
- **Technical Specs**: [docs/TECHNICAL_SPECS.md](../../docs/deployment/TECHNICAL_SPECS.md)
- **FAQ**: [docs/FAQ.md](../../docs/deployment/FAQ.md)

---

## 🎉 You're Ready!

Now you can run the Cardiac Calcium Scoring System directly from VS Code Terminal!

**Quick start command:**
```bash
cd /home/wuxia/projects/.../cardiac_calcium_scoring
bash calcium_scoring.sh test
```

**For help at any time:**
```bash
bash calcium_scoring.sh help
```

---

**Generated with Claude Code**
