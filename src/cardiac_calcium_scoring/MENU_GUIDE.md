# Menu Systems - Quick Reference Guide

## Overview

The Cardiac Calcium Scoring System now has **two menu systems** that work with the refactored application:

1. **Bash Menu** ([calcium_scoring.sh](calcium_scoring.sh)) - For Linux/WSL Terminal
2. **Python Menu** ([menu.py](menu.py)) - Cross-platform (Windows/Linux/macOS)

Both menus have been updated to use:
- Virtual environment Python: `../../venv/bin/python`
- Refactored CLI: `cli/run_calcium_scoring.py`

---

## Quick Start

### Option 1: Bash Menu (Recommended for WSL/Linux)

```bash
cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/cardiac_calcium_scoring

# Interactive menu
bash calcium_scoring.sh

# Or direct commands
bash calcium_scoring.sh test      # Quick test (5 patients)
bash calcium_scoring.sh chd       # Process CHD group
bash calcium_scoring.sh normal    # Process Normal group
bash calcium_scoring.sh analyze   # CHD vs Normal analysis
bash calcium_scoring.sh config    # View system config
bash calcium_scoring.sh logs      # View operation logs
bash calcium_scoring.sh help      # Show help
```

### Option 2: Python Menu (Cross-platform)

```bash
cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/cardiac_calcium_scoring

../../venv/bin/python menu.py
```

---

## Bash Menu Structure

```
========================================================================
                    NB10 AI-CAC 冠状动脉钙化评分工具
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

  【高级功能】
  8. Python交互式菜单 (跨平台)
  9. 自定义数据目录处理

  0. 退出程序
========================================================================
```

---

## Python Menu Structure

```
================================================================================
                   NB10 AI-CAC 冠状动脉钙化评分工具 v1.0.0
================================================================================

【快速处理】
  1. 快速测试 (Pilot模式 - 处理5例)
  2. 处理CHD组 (完整模式)
  3. 处理Normal组 (完整模式)
  4. 自定义数据目录处理

【统计分析】
  5. CHD vs Normal组对比分析
  6. 查看最新处理结果

【配置管理】
  7. 编辑CHD组配置文件
  8. 编辑Normal组配置文件
  9. 查看系统配置

【工具与帮助】
  A. 查看用户手册
  B. 查看快速参考卡
  C. 检查硬件配置
  D. 查看日志文件

  0. 退出程序
================================================================================
```

---

## Common Use Cases

### Use Case 1: Quick System Validation

**Goal**: Verify the system is working (1-5 patients, ~1-2 min)

**Method A - Bash Menu**:
```bash
bash calcium_scoring.sh test
```

**Method B - Python Menu**:
```bash
../../venv/bin/python menu.py
# Then select: 1
```

**Method C - Direct Command**:
```bash
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 5
```

---

### Use Case 2: Process CHD Group (Full Dataset)

**Goal**: Process all CHD patients (~101 cases, ~30-45 min)

**Method A - Bash Menu**:
```bash
bash calcium_scoring.sh chd
```

**Method B - Python Menu**:
```bash
../../venv/bin/python menu.py
# Then select: 2
```

**What happens**:
1. Loads config from `config/config.yaml`
2. Scans CHD data directory
3. Processes all cases with GPU acceleration
4. Saves results to `output/nb10_results_*.csv`
5. Shows success/failure statistics

---

### Use Case 3: Process Normal Group

**Goal**: Process all Normal control patients (~96 cases)

**Method A - Bash Menu**:
```bash
bash calcium_scoring.sh normal
```

**Method B - Python Menu**:
```bash
../../venv/bin/python menu.py
# Then select: 3
```

**Configuration**: Uses `config/config_normal.yaml`

---

### Use Case 4: CHD vs Normal Statistical Analysis

**Goal**: Compare calcium scores between CHD and Normal groups

**Prerequisites**:
- CHD group must be processed first
- Normal group must be processed first
- Result files must exist in output directories

**Method A - Bash Menu**:
```bash
bash calcium_scoring.sh analyze
```

**Method B - Python Menu**:
```bash
../../venv/bin/python menu.py
# Then select: 5
```

**What it does**:
- Reads CHD results: `output/chd/nb10_results_latest.csv`
- Reads Normal results: `output/normal/nb10_results_latest.csv`
- Performs statistical tests (t-test, Mann-Whitney U)
- Generates comparison report

---

### Use Case 5: Custom Directory Processing

**Goal**: Process DICOM data from a custom location

**Method A - Bash Menu**:
```bash
bash calcium_scoring.sh
# Then select: 9 (自定义数据目录处理)
```

**Method B - Python Menu**:
```bash
../../venv/bin/python menu.py
# Then select: 4
```

**Interactive prompts**:
1. Enter data directory path
   - Example: `/mnt/d/MedicalData/DICOM/test_patients`
2. Choose mode: Pilot or Full
3. If Pilot: specify number of cases (default 10)
4. Confirm and start processing

---

### Use Case 6: View System Configuration

**Goal**: Check GPU, Python version, config files

**Method A - Bash Menu**:
```bash
bash calcium_scoring.sh config
```

**Method B - Python Menu**:
```bash
../../venv/bin/python menu.py
# Then select: 9
```

**Displays**:
- Python version (from virtual environment)
- CUDA availability
- GPU name and VRAM
- Config file paths
- Working directory

---

### Use Case 7: Check Hardware Status

**Goal**: Monitor CPU, RAM, GPU utilization

**Method - Python Menu Only**:
```bash
../../venv/bin/python menu.py
# Then select: C
```

**Shows**:
```
【CPU】
CPU核心数: 8核 (16线程)
CPU使用率: 15.2%

【内存】
总内存: 15.7GB
可用内存: 8.3GB
使用率: 47.1%

【GPU】
CUDA可用: True
GPU 0: NVIDIA GeForce RTX 2060
  显存: 6.0GB
```

---

### Use Case 8: View Processing Results

**Goal**: Open result CSV files

**Method - Python Menu Only**:
```bash
../../venv/bin/python menu.py
# Then select: 6
```

**Options**:
1. Latest results (all groups)
2. CHD group results
3. Normal group results

**Action**: Opens CSV file in default application (Excel/LibreOffice)

---

### Use Case 9: Edit Configuration Files

**Goal**: Modify data paths, pilot limits, GPU settings

**Method - Python Menu Only**:
```bash
../../venv/bin/python menu.py
# Then select: 7 (CHD config) or 8 (Normal config)
```

**Opens**:
- On Linux/WSL: nano editor
- On Windows: Notepad
- Custom: Set `$EDITOR` environment variable

**Common edits**:
```yaml
paths:
  data_dir: "/path/to/your/dicom/data"  # Change this

processing:
  pilot_limit: 10        # Change test size
  device: "auto"         # Options: auto, cuda, cpu
```

---

### Use Case 10: View Recent Logs

**Goal**: Troubleshoot errors or check processing history

**Method A - Bash Menu**:
```bash
bash calcium_scoring.sh logs
```

**Method B - Python Menu**:
```bash
../../venv/bin/python menu.py
# Then select: D
```

**Shows**:
- 5 most recent menu logs: `logs/menu/nb10_menu_*.log`
- 5 most recent processing logs: `logs/nb10_*.log`
- Select by number to open in editor

---

## Menu Features Comparison

| Feature | Bash Menu | Python Menu |
|---------|-----------|-------------|
| Quick test (Pilot) | ✅ | ✅ |
| Process CHD group | ✅ | ✅ |
| Process Normal group | ✅ | ✅ |
| Custom directory | ✅ | ✅ |
| CHD vs Normal analysis | ✅ | ✅ |
| View system config | ✅ | ✅ |
| View logs | ✅ | ✅ |
| Help documentation | ✅ | ❌ |
| **Edit config files** | ❌ | ✅ |
| **View results CSV** | ❌ | ✅ |
| **Hardware monitoring** | ❌ | ✅ |
| **View user manual** | ❌ | ✅ |
| **Quick reference card** | ❌ | ✅ |
| **Color output** | ❌ | ✅ |
| **Cross-platform** | Linux/WSL only | Windows/Linux/macOS |

---

## Technical Details

### Updated Command Paths

Both menus now use:

**Old (before refactoring)**:
```bash
python cli/run_nb10.py --config config/config.yaml --mode pilot
```

**New (after refactoring)**:
```bash
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot
```

**Key changes**:
1. ✅ Uses virtual environment Python: `../../venv/bin/python`
2. ✅ Uses refactored CLI: `cli/run_calcium_scoring.py`
3. ✅ Auto-confirms with `echo ""`  to bypass interactive prompt

---

### Log Files

**Menu operation logs** (Bash menu only):
```
logs/menu/nb10_menu_20251018_211638.log
```

**Processing logs** (both menus):
```
logs/nb10_20251018_205342.log
```

All operations are logged with timestamps and status codes.

---

### Environment Variables

**For Python menu**:

```bash
# Custom editor (default: nano on Linux, notepad on Windows)
export EDITOR=vim

# Custom terminal colors
export TERM=xterm-256color
```

---

## Preparing for Future Notebooks

The menu systems are now ready for expansion. When migrating new notebooks, add entries here:

### For Bash Menu ([calcium_scoring.sh](calcium_scoring.sh)):

Add new ACTION cases around line 90:
```bash
elif [ "$1" = "new_feature" ]; then
    ACTION="new_feature"
```

Add implementation around line 400:
```bash
# ============================================================================
# XX. New Feature
# ============================================================================
if [ "$ACTION" = "new_feature" ]; then
    log "INFO" "执行: New Feature"
    clear
    show_header "New Feature Processing"

    echo "" | $PYTHON_CMD cli/run_new_feature.py --config config/config.yaml
    EXIT_CODE=${PIPESTATUS[0]}

    show_result ${EXIT_CODE} "New Feature"
    read -p "按Enter返回..."
    exec "$0" menu
fi
```

### For Python Menu ([menu.py](menu.py)):

Add menu option around line 85:
```python
print_section("New Features")
print("  X. New Feature Name")
```

Add handler around line 138:
```python
elif choice == 'X':
    new_feature_function()
```

Add function around line 580:
```python
def new_feature_function():
    """New feature processing"""
    clear_screen()
    print_header("New Feature Processing")

    pause("Press Enter to start...")

    print("\nProcessing...\n")
    success = run_command('echo "" | ../../venv/bin/python cli/run_new_feature.py --config config/config.yaml')

    if success:
        print_success("Processing complete!")
    else:
        print_error("Processing failed!")
    pause()
```

---

## Troubleshooting

### Issue 1: "未找到虚拟环境Python"

**Cause**: Virtual environment not found at `../../venv`

**Solution**:
```bash
# Check if venv exists
ls -ld ../../venv

# If missing, create it (from project root)
python3 -m venv venv
source venv/bin/activate
pip install -r tools/cardiac_calcium_scoring/deployment/requirements.txt
```

---

### Issue 2: "CUDA out of memory"

**Cause**: GPU VRAM insufficient for batch processing

**Solution** (in menu):
1. Bash menu → Option 9 (Custom dir) → Choose smaller pilot limit
2. Python menu → Option 7 (Edit CHD config) → Reduce batch size
3. Or force CPU mode in config:
   ```yaml
   processing:
     device: "cpu"
   ```

---

### Issue 3: Menu colors not displaying

**Cause**: Terminal doesn't support ANSI colors

**Solution**:
```bash
# For Bash menu - colors are minimal
# For Python menu - colors should work on most terminals

# If still issues, use:
export TERM=xterm-256color
```

---

### Issue 4: "File not found" when viewing results

**Cause**: Result files haven't been generated yet

**Solution**:
1. First run processing (Option 1, 2, or 3)
2. Then view results (Option 6)

Check if files exist:
```bash
ls -lh output/*.csv
```

---

## Quick Command Reference

### Bash Menu Commands

```bash
cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/cardiac_calcium_scoring

# Start interactive menu
bash calcium_scoring.sh

# Direct commands
bash calcium_scoring.sh test      # Quick test
bash calcium_scoring.sh chd       # Process CHD
bash calcium_scoring.sh normal    # Process Normal
bash calcium_scoring.sh analyze   # Statistical analysis
bash calcium_scoring.sh config    # View config
bash calcium_scoring.sh logs      # View logs
bash calcium_scoring.sh help      # Show help
```

### Python Menu Command

```bash
cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/cardiac_calcium_scoring

../../venv/bin/python menu.py
```

### Direct CLI (No Menu)

```bash
# Quick test
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 5

# Process all CHD
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode full

# Process all Normal
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config_normal.yaml --mode full

# Custom directory
../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --data-dir /path/to/dicom
```

---

## Summary

✅ **Both menu systems are now updated and ready to use**

**Choose your menu**:
- 🐧 **Bash Menu**: Best for Linux/WSL, simple and fast, integrates well with shell
- 🐍 **Python Menu**: Cross-platform, feature-rich, colored output, file editing

**Next steps**:
1. Test the menus with a quick pilot run
2. When migrating new notebooks, follow the expansion guide above
3. All menus automatically use the refactored CLI structure

**Related documentation**:
- [HOW_TO_RUN.md](HOW_TO_RUN.md) - Direct command usage guide
- [VSCODE_QUICK_START.md](VSCODE_QUICK_START.md) - VS Code Terminal guide
- [config/config.yaml](config/config.yaml) - CHD configuration
- [config/config_normal.yaml](config/config_normal.yaml) - Normal configuration

---

**Generated with Claude Code**
