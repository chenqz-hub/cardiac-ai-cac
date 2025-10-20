# NB10 Windows Tool - 用户手册

**版本**: 1.1.1
**更新日期**: 2025-10-17

---

## 📋 目录

1. [简介](#简介)
2. [快速开始](#快速开始)
3. [基础使用](#基础使用)
4. [高级功能](#高级功能)
5. [输出结果](#输出结果)
6. [性能优化](#性能优化)
7. [故障排除](#故障排除)

---

## 简介

### 什么是NB10 AI-CAC工具？

NB10是一个基于深度学习的冠状动脉钙化(CAC)自动评分工具，能够在常规非门控、非对比增强胸部CT扫描上进行钙化检测和Agatston评分计算。

**核心功能**:
- 🔍 自动检测冠状动脉钙化
- 📊 计算Agatston评分
- 🎯 风险分层（0, 1-100, 101-400, >400）
- 📈 批量处理和统计分析
- 💾 CSV格式结果导出

**临床应用**:
- 心血管风险评估
- 冠心病筛查
- 预后预测
- 临床研究数据分析

---

## 快速开始

### 🎯 三种运行方式（选择一种）

系统提供三种运行方式，根据您的使用习惯选择：

#### 方式1: Bash菜单（Linux/WSL推荐）⭐

**最简单的交互式菜单**:
```bash
bash calcium_scoring.sh
```

**快捷命令**:
```bash
bash calcium_scoring.sh test      # 快速测试（5例）
bash calcium_scoring.sh chd       # 处理CHD组
bash calcium_scoring.sh normal    # 处理Normal组
bash calcium_scoring.sh help      # 查看帮助
```

特性: 自动日志记录、虚拟环境检测、错误追踪

详见: [MENU_GUIDE.md](../MENU_GUIDE.md)

---

#### 方式2: Python菜单（跨平台）

**功能丰富的彩色菜单**（支持Windows/Linux/macOS）:
```bash
../../venv/bin/python menu.py
```

特性: 配置编辑、硬件监控、结果查看、用户手册访问

详见: [MENU_GUIDE.md](../MENU_GUIDE.md)

---

#### 方式3: 直接命令行（开发者/高级用户）

**完全控制的命令行方式**:
```bash
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 5
```

详见: [HOW_TO_RUN.md](../HOW_TO_RUN.md)

---

### 最简单的使用流程（直接命令行）

1. **准备DICOM数据**
   ```
   your_data/
   ├── patient_001/
   │   ├── IM-0001.dcm
   │   ├── IM-0002.dcm
   │   └── ...
   └── patient_002/
       ├── IM-0001.dcm
       └── ...
   ```

2. **配置config.yaml**
   ```yaml
   paths:
     data_dir: "/path/to/your_data"
     output_dir: "./output"
   processing:
     mode: "pilot"
     device: "cuda"  # 或 "cpu"
   ```

3. **运行推理**（三种方式任选其一）

   **方式A - 使用Bash菜单**:
   ```bash
   bash calcium_scoring.sh test
   ```

   **方式B - 使用Python菜单**:
   ```bash
   ../../venv/bin/python menu.py
   # 然后选择选项 1 (快速测试)
   ```

   **方式C - 直接命令**:
   ```bash
   echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot
   ```

4. **查看结果**
   ```bash
   # 查看CSV结果
   cat output/nb10_results_latest.csv

   # 查看日志
   tail -f logs/nb10_*.log
   ```

---

### 🩺 临床研究快速开始（CHD vs Normal对照研究）

**适用场景**: 医生需要分析CHD组和Normal组（对照组）的冠脉钙化差异

#### 1. 数据组织

**典型数据结构**：
```
cardiac_function_extraction/
└── data/
    └── ct_images/
        └── ct_images_dicom/
            ├── chd/              # CHD组（101例）
            │   ├── dicom_7084967/
            │   ├── dicom_7085009/
            │   └── ...
            └── normal/           # Normal组（96例）
                ├── dicom_1230845/
                ├── dicom_1231057/
                └── ...
```

#### 2. 准备配置文件

**CHD组配置** (`config/config_chd.yaml`):
```yaml
paths:
  data_dir: "/home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac_function_extraction/data/ct_images/ct_images_dicom/chd"
  output_dir: "./output/chd"
  model_path: "./models/va_non_gated_ai_cac_model.pth"

processing:
  mode: "full"
  device: "cuda"
  enable_resume: true
```

**Normal组配置** (`config/config_normal.yaml`):
```yaml
paths:
  data_dir: "/home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac_function_extraction/data/ct_images/ct_images_dicom/normal"
  output_dir: "./output/normal"
  model_path: "./models/va_non_gated_ai_cac_model.pth"

processing:
  mode: "full"
  device: "cuda"
  enable_resume: true
```

#### 3. 运行分析

```bash
# 步骤1: 处理CHD组
python cli/run_nb10.py --config config/config_chd.yaml --mode full

# 步骤2: 处理Normal组
python cli/run_nb10.py --config config/config_normal.yaml --mode full

# 步骤3: 统计分析对比
python scripts/analyze_chd_vs_normal.py \
  output/chd/nb10_results_latest.csv \
  output/normal/nb10_results_latest.csv
```

#### 4. 查看结果

**CHD组结果**: `output/chd/nb10_results_latest.csv`
**Normal组结果**: `output/normal/nb10_results_latest.csv`
**统计对比**: 屏幕输出包含均值、中位数、风险分层、p值等

#### 5. 导出用于论文

```bash
# 将结果复制到论文目录
cp output/chd/nb10_results_latest.csv ~/论文/数据/chd_ai_cac_scores.csv
cp output/normal/nb10_results_latest.csv ~/论文/数据/normal_ai_cac_scores.csv
```

---

## 基础使用

### 1. 命令行基础

#### 基本语法

```bash
python cli/run_nb10.py [选项]
```

#### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--config` | 配置文件路径 | `--config config/config.yaml` |

#### 可选参数

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--mode` | 处理模式 | config.yaml | `--mode pilot` |
| `--device` | 设备选择 | config.yaml | `--device cuda` |
| `--data-dir` | **数据目录（重要）** | config.yaml | `--data-dir /path/to/data` |
| `--output-dir` | 输出目录 | config.yaml | `--output-dir ./results` |
| `--pilot-limit` | Pilot模式案例数 | 10 | `--pilot-limit 5` |
| `--clear-cache` | 清除断点续传缓存 | 否 | `--clear-cache` |
| `--no-resume` | 禁用断点续传 | 否 | `--no-resume` |

> **💡 重要提示**: `--data-dir` 参数允许您灵活选择本地数据目录，无需修改配置文件。这在对照研究（如CHD vs Normal）中特别有用。

---

### 2. 灵活选择数据目录（重要功能）

#### 为什么需要灵活选择数据目录？

在临床研究中，您可能需要：
- ✅ 处理不同分组的患者（CHD组、Normal组、其他对照组）
- ✅ 使用不同位置的数据备份
- ✅ 测试不同批次的患者数据
- ✅ 在不同服务器或工作站之间切换

**NB10提供三种方式指定数据目录，优先级从高到低：**

#### 方式1: 命令行参数 `--data-dir`（推荐，最灵活）

**优点**: 无需修改配置文件，适合快速切换不同数据集

```bash
# 处理CHD组
python cli/run_nb10.py \
  --config config/config.yaml \
  --mode full \
  --data-dir "/path/to/cardiac_function_extraction/data/ct_images/ct_images_dicom/chd"

# 处理Normal组（无需修改配置文件）
python cli/run_nb10.py \
  --config config/config.yaml \
  --mode full \
  --data-dir "/path/to/cardiac_function_extraction/data/ct_images/ct_images_dicom/normal"

# 处理其他位置的数据
python cli/run_nb10.py \
  --config config/config.yaml \
  --mode pilot \
  --data-dir "/mnt/external_drive/patient_data" \
  --pilot-limit 5
```

#### 方式2: 配置文件（适合固定工作流程）

**优点**: 配置一次，重复使用；适合标准化流程

编辑 `config/config.yaml`:
```yaml
paths:
  data_dir: "/path/to/your/data"
  # ...
```

然后直接运行：
```bash
python cli/run_nb10.py --config config/config.yaml --mode full
```

#### 方式3: 多个配置文件（适合多项目管理）

**优点**: 每个研究项目有独立配置，清晰管理

创建多个配置文件：
- `config/config_chd.yaml` - CHD组配置
- `config/config_normal.yaml` - Normal组配置
- `config/config_pilot.yaml` - 测试配置

**示例**: `config/config_chd.yaml`
```yaml
paths:
  data_dir: "/path/to/chd_group"
  output_dir: "./output/chd"
  model_path: "./models/va_non_gated_ai_cac_model.pth"

processing:
  mode: "full"
  device: "cuda"
```

使用：
```bash
# 处理CHD组
python cli/run_nb10.py --config config/config_chd.yaml

# 处理Normal组
python cli/run_nb10.py --config config/config_normal.yaml
```

#### 实战示例：对照研究工作流程

**场景**: 比较CHD组 vs Normal组的冠脉钙化差异

**方法A: 使用命令行参数（推荐，快速灵活）**
```bash
# 设置基础路径变量
BASE_DATA="/home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac_function_extraction/data/ct_images/ct_images_dicom"

# 处理CHD组
python cli/run_nb10.py \
  --config config/config.yaml \
  --mode full \
  --data-dir "$BASE_DATA/chd" \
  --output-dir "./output/chd"

# 处理Normal组
python cli/run_nb10.py \
  --config config/config.yaml \
  --mode full \
  --data-dir "$BASE_DATA/normal" \
  --output-dir "./output/normal"

# 统计分析
python scripts/analyze_chd_vs_normal.py \
  output/chd/nb10_results_latest.csv \
  output/normal/nb10_results_latest.csv
```

**方法B: 使用多配置文件（推荐，清晰管理）**
```bash
# 一次性创建好配置文件，后续使用更简单

# 处理CHD组
python cli/run_nb10.py --config config/config_chd.yaml --mode full

# 处理Normal组
python cli/run_nb10.py --config config/config_normal.yaml --mode full

# 统计分析（同上）
python scripts/analyze_chd_vs_normal.py \
  output/chd/nb10_results_latest.csv \
  output/normal/nb10_results_latest.csv
```

#### Windows路径注意事项

**WSL环境下访问Windows路径**:
```bash
# Windows路径: D:\MedicalData\DICOM
# WSL路径: /mnt/d/MedicalData/DICOM

python cli/run_nb10.py \
  --config config/config.yaml \
  --data-dir "/mnt/d/MedicalData/DICOM/chd"
```

**路径包含空格**（使用引号）:
```bash
python cli/run_nb10.py \
  --config config/config.yaml \
  --data-dir "/mnt/d/Medical Data/DICOM/chd"
```

**网络共享路径**:
```bash
# 先挂载网络共享
mount -t drvfs '\\server\share' /mnt/network_data

# 使用挂载路径
python cli/run_nb10.py \
  --config config/config.yaml \
  --data-dir "/mnt/network_data/dicom/chd"
```

#### 数据目录有效性检查

运行前可以先检查数据目录：
```bash
# 列出患者文件夹
ls -l /path/to/data/

# 统计患者数量
ls -l /path/to/data/ | grep "^d" | wc -l

# 检查第一个患者的DICOM文件
ls /path/to/data/patient_001/*.dcm | head -5
```

#### 常见问题

**Q: 命令行参数和配置文件都指定了data_dir，以哪个为准？**
A: 命令行参数优先级更高，会覆盖配置文件中的设置。

**Q: 可以同时处理多个数据目录吗？**
A: 目前不支持。需要分别运行，或将数据合并到同一目录。

**Q: 相对路径和绝对路径都可以吗？**
A: 都可以，但建议使用绝对路径以避免混淆。
- 绝对路径: `/home/user/data` （推荐）
- 相对路径: `../../data` （需确保工作目录正确）

---

### 3. 处理模式

#### Pilot模式（测试模式）

处理有限数量的案例，用于快速测试和验证。

```bash
python cli/run_nb10.py --config config/config.yaml --mode pilot --pilot-limit 10
```

**适用场景**:
- 首次使用，验证安装
- 测试新数据集
- 调试配置
- 性能测试

**优点**: 快速，低资源占用
**缺点**: 仅处理部分数据

---

#### Full模式（完整模式）

处理数据目录中的所有案例。

```bash
python cli/run_nb10.py --config config/config.yaml --mode full
```

**适用场景**:
- 生产环境批量处理
- 完整数据集分析
- 论文数据准备

**优点**: 处理所有数据
**缺点**: 耗时较长，需要更多资源

---

### 3. 设备选择

#### GPU模式（推荐）

使用NVIDIA GPU加速推理。

```bash
python cli/run_nb10.py --config config/config.yaml --device cuda
```

**性能**: ~30秒/例
**要求**: NVIDIA GPU (≥6GB显存)
**适用**: 批量处理，实时分析

---

#### CPU模式

使用CPU进行推理（较慢但无GPU要求）。

```bash
python cli/run_nb10.py --config config/config.yaml --device cpu
```

**性能**: ~10-20分钟/例
**要求**: 仅CPU
**适用**: 无GPU环境，单例分析

---

### 4. 数据准备

#### DICOM数据要求

**文件格式**: DICOM (.dcm)

**扫描参数要求**:
- **层厚**: 4-6mm（推荐5mm）
- **类型**: 非门控、非对比增强胸部CT
- **重建**: 标准重建或软组织窗

**目录结构**:
```
data_dir/
├── patient_001/        # 每个患者一个文件夹
│   ├── IM-0001.dcm
│   ├── IM-0002.dcm
│   └── ...
├── patient_002/
│   └── ...
└── patient_N/
    └── ...
```

#### 数据组织建议

**选项1**: 扁平结构
```
data/
├── patient_001/
├── patient_002/
└── patient_003/
```

**选项2**: 分组结构（推荐用于对照研究）
```
data/
├── chd/              # 冠心病组
│   ├── patient_001/
│   └── patient_002/
└── control/          # 对照组
    ├── patient_101/
    └── patient_102/
```

---

## 高级功能

### 1. 配置文件详解

#### 完整配置示例

```yaml
# 路径配置
paths:
  data_dir: "/data/cardiac/dicom"
  model_path: "./models/va_non_gated_ai_cac_model.pth"
  output_dir: "./output"
  cache_dir: "./data/cache"
  log_dir: "./logs"

# 处理配置
processing:
  mode: "pilot"               # pilot 或 full
  pilot_limit: 10             # pilot模式案例数
  device: "cuda"              # cuda 或 cpu
  batch_size: 1               # 批大小（建议保持1）
  enable_resume: true         # 启用断点续传
  slice_thickness_min: 4.0    # 最小层厚(mm)
  slice_thickness_max: 6.0    # 最大层厚(mm)

# 性能配置
performance:
  clear_cache_interval: 5     # GPU缓存清理间隔
  num_workers: 0              # DataLoader workers
  pin_memory: false           # Pin memory（GPU）

# 输出配置
output:
  csv_encoding: "utf-8-sig"   # CSV编码（BOM for Excel）
  save_intermediate: false    # 保存中间结果
  save_masks: false           # 保存分割掩码

# 日志配置
logging:
  level: "INFO"               # DEBUG, INFO, WARNING, ERROR
  log_to_file: true
  log_to_console: true

# 临床配置
clinical:
  agatston_thresholds:        # 风险分层阈值
    minimal: 0
    mild: 100
    moderate: 400
    severe: 1000
```

---

### 2. 批量处理策略

#### 小批量测试

```bash
# 测试前5个案例
python cli/run_nb10.py --config config/config.yaml --mode pilot --pilot-limit 5
```

#### 分批处理大数据集

```bash
# 处理第1-50例
python cli/run_nb10.py --config config/config.yaml --mode pilot --pilot-limit 50

# 处理第51-100例（修改配置或使用多个data_dir）
python cli/run_nb10.py --config config/config.yaml --mode pilot --pilot-limit 100
```

#### 并行处理（未来版本）

```bash
# 使用多GPU并行（规划中）
python cli/run_nb10.py --config config/config.yaml --mode full --gpus 0,1,2,3
```

---

### 3. 断点续传（Resume/Checkpoint）

**v1.1.1新功能**: 全自动断点续传支持，适用于长时间处理任务（CPU模式、大批量数据）

#### 为什么需要断点续传？

**典型场景**:
- ✅ CPU模式处理200例数据，每例3-5分钟，总计10-16小时
- ✅ 处理过程中电脑意外关机、断电、系统重启
- ✅ 手动中断处理（Ctrl+C）后希望从中断处继续
- ✅ 网络共享存储偶尔断开连接
- ✅ 分多次处理大数据集（避免长时间占用电脑）

**价值**:
- 🕐 节省时间：无需重新处理已完成的案例
- 🔒 安全可靠：每处理完一例立即保存，崩溃也不丢失进度
- 🎯 灵活控制：可随时中断，随时继续

---

#### 如何使用断点续传

**方式1: 默认启用（推荐，零配置）**

断点续传默认已启用，无需任何额外配置：

```bash
# 第一次运行（处理50例后中断）
python cli/run_nb10.py --config config/config.yaml --mode full

# 重新运行（自动跳过已完成的50例，从第51例继续）
python cli/run_nb10.py --config config/config.yaml --mode full
```

**自动行为**:
- ✅ 自动创建缓存文件: `output/.nb10_resume_cache.csv`
- ✅ 每处理完一例立即保存到缓存（成功或失败都记录）
- ✅ 重新运行时自动跳过成功案例
- ✅ 失败案例会自动重试（不跳过）

**屏幕提示示例**:
```
======================================================================
RESUME MODE DETECTED
======================================================================
  Previously processed: 50 cases
  Remaining to process: 150 cases
======================================================================
```

---

**方式2: 配置文件控制**

如果需要禁用断点续传（例如重新处理所有数据）：

```yaml
# config.yaml
processing:
  enable_resume: false  # 禁用断点续传
```

---

**方式3: 命令行控制（最灵活）**

```bash
# 正常使用断点续传（默认行为）
python cli/run_nb10.py --config config/config.yaml --mode full

# 清除缓存，强制重新处理所有案例
python cli/run_nb10.py --config config/config.yaml --mode full --clear-cache

# 本次运行禁用断点续传（不保存/不加载缓存）
python cli/run_nb10.py --config config/config.yaml --mode full --no-resume
```

**参数说明**:

| 参数 | 功能 | 使用场景 |
|------|------|----------|
| 无参数 | 使用断点续传（默认） | 正常使用 |
| `--clear-cache` | 清除缓存并重新开始 | 想重新处理所有数据 |
| `--no-resume` | 本次运行禁用断点续传 | 临时测试，不想保存缓存 |

---

#### 断点续传工作原理

**缓存文件**: `output/.nb10_resume_cache.csv`

**文件格式**:
```csv
patient_id,status,agatston_score,timestamp
patient_001,success,153.2,2025-10-17T14:30:45
patient_002,success,0.0,2025-10-17T14:35:12
patient_003,failed,,2025-10-17T14:38:00
patient_004,success,2356.7,2025-10-17T14:43:28
```

**处理逻辑**:
1. **启动时**: 加载缓存，提取所有 `status=success` 的 `patient_id`
2. **过滤**: 从待处理列表中移除这些ID
3. **处理**: 仅处理剩余案例
4. **保存**: 每完成一例，立即追加到缓存（增量写入，崩溃安全）

**失败案例处理**:
- ❌ 失败案例记录到缓存但 **不会被跳过**
- ✅ 重新运行时会 **自动重试** 失败案例
- 💡 这样确保数据完整性（失败可能是临时问题）

---

#### 实战示例

**场景1: 处理中断后继续**

```bash
# 第一次运行（处理到30/200时按Ctrl+C中断）
$ python cli/run_nb10.py --config config/config.yaml --mode full
[1/200] Processing: patient_001... ✓ Success
[2/200] Processing: patient_002... ✓ Success
...
[30/200] Processing: patient_030... ✓ Success
^C  # 用户按Ctrl+C中断

# 稍后继续（自动从patient_031开始）
$ python cli/run_nb10.py --config config/config.yaml --mode full
======================================================================
RESUME MODE DETECTED
======================================================================
  Previously processed: 30 cases
  Remaining to process: 170 cases
======================================================================
[1/170] Processing: patient_031... ✓ Success
...
```

---

**场景2: 系统崩溃后恢复**

```bash
# 处理过程中系统突然断电（已完成100/500例）
$ python cli/run_nb10.py --config config/config.yaml --mode full
[1/500] Processing: patient_001... ✓ Success
...
[100/500] Processing: patient_100... ✓ Success
# 系统突然断电

# 重启后继续（自动从patient_101开始）
$ python cli/run_nb10.py --config config/config.yaml --mode full
======================================================================
RESUME MODE DETECTED
======================================================================
  Previously processed: 100 cases
  Remaining to process: 400 cases
======================================================================
[1/400] Processing: patient_101... ✓ Success
...
```

---

**场景3: 清除缓存重新开始**

```bash
# 发现配置错误，需要重新处理所有数据
$ python cli/run_nb10.py --config config/config.yaml --mode full --clear-cache
Clearing resume cache...
✓ Cache cleared - will process all cases

[1/200] Processing: patient_001... ✓ Success
...
```

---

**场景4: CPU模式长时间处理**

```bash
# 场景：200例患者，CPU模式，预计耗时12-16小时
# 策略：分3次完成，每次4-5小时

# 第一天晚上运行（处理到65例后关机睡觉）
$ python cli/run_nb10.py --config config/config.yaml --mode full --device cpu
[1/200] Processing: patient_001... ✓ Success (~3-5 minutes)
...
[65/200] Processing: patient_065... ✓ Success
# 晚上11点关机

# 第二天继续（自动从patient_066开始）
$ python cli/run_nb10.py --config config/config.yaml --mode full --device cpu
======================================================================
RESUME MODE DETECTED
======================================================================
  Previously processed: 65 cases
  Remaining to process: 135 cases
======================================================================
[1/135] Processing: patient_066... ✓ Success
...
```

---

#### 缓存管理

**查看缓存内容**:
```bash
# 查看缓存文件
cat output/.nb10_resume_cache.csv

# 统计已处理案例数
cat output/.nb10_resume_cache.csv | grep "success" | wc -l

# 查看失败案例
cat output/.nb10_resume_cache.csv | grep "failed"
```

**手动删除缓存**:
```bash
# Linux/macOS
rm output/.nb10_resume_cache.csv

# Windows
del output\.nb10_resume_cache.csv
```

**缓存文件位置**:
- 默认位置: `output/.nb10_resume_cache.csv`
- 与 `output_dir` 配置项同目录
- 隐藏文件（`.`开头），不影响正常结果文件

---

#### 注意事项

**✅ 安全行为**:
- 断点续传不会修改任何已有结果文件
- 仅在处理全新案例时使用缓存
- 缓存文件损坏时自动忽略并从头开始

**⚠️ 注意**:
- 如果修改了 `data_dir`（切换数据集），建议使用 `--clear-cache`
- 如果修改了模型或配置参数，建议使用 `--clear-cache` 重新处理
- 缓存文件基于 `patient_id`（文件夹名），确保不要重命名患者文件夹

**❌ 不适用场景**:
- 处理时间很短（<10分钟），断点续传意义不大
- Pilot模式（仅10例），无需断点续传
- 使用GPU且数据量小（<100例），处理很快，无需断点续传

---

### 4. 结果过滤和筛选

#### 按状态筛选

```bash
# 仅查看成功案例
cat output/nb10_results_latest.csv | grep "success"

# 查看失败案例
cat output/nb10_results_latest.csv | grep "failed"
```

#### 按评分范围筛选

```python
import pandas as pd

# 读取结果
df = pd.read_csv('output/nb10_results_latest.csv')

# 筛选高风险病例 (>400)
high_risk = df[df['agatston_score'] > 400]
print(f"High risk cases: {len(high_risk)}")

# 统计
print(df['agatston_score'].describe())
```

---

## 输出结果

### 1. CSV结果文件

#### 文件位置

- **最新结果**: `output/nb10_results_latest.csv`
- **带时间戳**: `output/nb10_results_YYYYMMDD_HHMMSS.csv`

#### 字段说明

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `patient_id` | String | 患者ID（文件夹名） | `dicom_7084967` |
| `agatston_score` | Float | Agatston钙化评分 | `3505.0` |
| `calcium_volume_mm3` | Float | 钙化体积(mm³) | `1752.5` |
| `calcium_mass_mg` | Float | 钙化质量(mg) | `2103.6` |
| `num_slices` | Integer | 处理的切片数 | `67` |
| `has_calcification` | Boolean | 是否检测到钙化 | `True` |
| `status` | String | 处理状态 | `success` / `failed` |
| `error` | String | 错误信息（如有） | `No suitable series` |

#### 示例数据

```csv
patient_id,agatston_score,calcium_volume_mm3,calcium_mass_mg,num_slices,has_calcification,status,error
patient_001,153.2,76.6,91.9,65,True,success,
patient_002,0.0,0.0,0.0,70,False,success,
patient_003,,,,,failed,No suitable series found
patient_004,2356.7,1178.4,1414.1,68,True,success,
```

---

### 2. 日志文件

#### 日志位置

`logs/nb10_YYYYMMDD_HHMMSS.log`

#### 日志内容示例

```
2025-10-17 11:50:38 - nb10 - INFO - NB10 AI-CAC Tool v1.1.0
2025-10-14 11:50:38 - nb10 - INFO - Configuration loaded
2025-10-14 11:50:38 - nb10 - INFO - Device: NVIDIA GeForce RTX 2060 (6.0 GB)
2025-10-14 11:50:38 - nb10 - INFO - Found 100 DICOM folders
2025-10-14 11:50:38 - nb10 - INFO - [1/100] Processing: patient_001
2025-10-14 11:50:58 - nb10 - INFO -   ✓ Success - Agatston Score: 153.20
2025-10-14 11:50:58 - nb10 - INFO - [2/100] Processing: patient_002
...
2025-10-14 12:00:00 - nb10 - INFO - Inference Complete: Success: 98/100
```

---

### 3. 风险分层

根据Agatston评分进行风险分层：

| 评分范围 | 风险等级 | 临床意义 |
|----------|----------|----------|
| 0 | 零钙化 | 低风险 |
| 1-100 | 轻度钙化 | 低-中风险 |
| 101-400 | 中度钙化 | 中-高风险 |
| 401-1000 | 重度钙化 | 高风险 |
| >1000 | 极重度钙化 | 极高风险 |

---

## 性能优化

### 1. GPU优化

#### 显存优化

**问题**: GPU显存不足(OOM)

**解决方案**:

1. **关闭其他GPU程序**
   ```bash
   nvidia-smi  # 查看GPU占用
   # 关闭其他占用GPU的程序
   ```

2. **降低batch size**（已在代码中优化）
   ```python
   # core/ai_cac_inference_lib.py
   SLICE_BATCH_SIZE = 4  # 从16降到4
   ```

3. **使用混合精度**（未来版本）
   ```python
   # 规划中：FP16推理
   ```

---

### 2. CPU优化

#### 提升CPU性能

**多核利用**（未来版本）:
```yaml
performance:
  num_workers: 4  # DataLoader并行
  torch_threads: 8  # PyTorch线程数
```

**当前建议**:
- 使用性能更好的CPU (i7/i9, Ryzen 7/9)
- 增加系统RAM
- 或使用GPU模式

---

### 3. I/O优化

#### 使用SSD

**问题**: DICOM加载慢

**解决**: 将数据存储在SSD而非HDD
- HDD: ~100MB/s
- SATA SSD: ~500MB/s
- NVMe SSD: ~3000MB/s

#### 缓存优化

```yaml
paths:
  cache_dir: "/fast_ssd/cache"  # 使用快速SSD作为缓存
```

---

## 故障排除

### 常见错误

#### 1. `No suitable series found`

**原因**: DICOM数据不符合要求
- 层厚不在4-6mm范围
- 不是胸部CT
- 序列类型不支持

**解决**:
1. 检查DICOM元数据
2. 调整层厚过滤范围:
   ```yaml
   processing:
     slice_thickness_min: 3.0
     slice_thickness_max: 7.0
   ```

---

#### 2. `CUDA out of memory`

**原因**: GPU显存不足

**解决**: 参考 [性能优化 > GPU优化](#gpu优化)

---

#### 3. 处理速度慢

**GPU模式慢**:
- 检查是否使用CPU模式: `--device cuda`
- 检查GPU负载: `nvidia-smi`

**CPU模式慢**:
- 正常，CPU模式本身就慢(~10-20分钟/例)
- 建议使用GPU或升级硬件

---

### 获取帮助

**查看日志**:
```bash
tail -100 logs/nb10_*.log
```

**运行诊断**（如果提供）:
```bash
python scripts/diagnose.py
```

**联系支持**:
- GitHub Issues
- Email: support@your-org.com
- 文档: [FAQ.md](FAQ.md)

---

## 最佳实践

### 1. 数据管理

✅ **推荐**:
- 使用清晰的命名规则
- 保持目录结构一致
- 定期备份原始数据
- 将DICOM数据存储在快速存储（SSD）

❌ **避免**:
- 文件名包含特殊字符
- 混合不同扫描参数的数据
- 在系统盘存储大量数据

---

### 2. 工作流程

**典型工作流程**:

1. **数据准备**: 组织DICOM文件
2. **Pilot测试**: 处理5-10例验证
3. **完整处理**: Full模式处理所有数据
4. **结果验证**: 检查CSV和日志
5. **统计分析**: 使用Python/R分析结果
6. **报告生成**: 导出结果用于论文/报告

---

### 3. 质量控制

**建议检查**:
- 处理成功率 (>95%)
- 日志中的警告和错误
- 异常高/低的评分
- 失败案例的原因

**示例检查脚本**:
```python
import pandas as pd

df = pd.read_csv('output/nb10_results_latest.csv')

# 成功率
success_rate = (df['status'] == 'success').sum() / len(df)
print(f"Success rate: {success_rate:.1%}")

# 异常值检查
high_scores = df[df['agatston_score'] > 2000]
print(f"Very high scores (>2000): {len(high_scores)}")
```

---

## 附录

### A. 性能基准参考

| 环境 | 单例时间 | 10例时间 | 100例时间 |
|------|----------|----------|-----------|
| RTX 4090 (24GB) | ~15s | ~3min | ~25min |
| RTX 3060 (12GB) | ~25s | ~5min | ~42min |
| RTX 2060 (6GB) | ~35s | ~6min | ~58min |
| i9-13900K (CPU) | ~8min | ~80min | ~13h |
| i7-12700 (CPU) | ~12min | ~120min | ~20h |

---

### B. 文件大小参考

| 项目 | 大小 |
|------|------|
| AI-CAC模型 | 1.12 GB |
| PyTorch GPU版 | ~3.5 GB |
| PyTorch CPU版 | ~1.5 GB |
| 单个DICOM案例 | ~30-100 MB |
| 输出CSV (100例) | ~10 KB |

---

### C. 相关资源

**AI-CAC论文**:
- NEJM AI 2025: [doi.org/10.1056/AIoa2400937](https://doi.org/10.1056/AIoa2400937)

**官方GitHub**:
- https://github.com/Raffi-Hagopian/AI-CAC

**文档**:
- [安装指南](INSTALLATION_GUIDE.md)
- [配置指南](CONFIGURATION_GUIDE.md)
- [FAQ](FAQ.md)

---

**感谢使用NB10 AI-CAC工具！**

**文档版本**: 1.1.1
**最后更新**: 2025-10-17
