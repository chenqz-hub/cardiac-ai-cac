# Examples Directory

本目录包含NB10工具的示例配置、脚本和测试数据。

---

## 📁 目录内容

```
examples/
├── example_config.yaml            # 完整配置示例
├── example_batch.bat              # Windows批处理示例
├── example_script.py              # Python脚本示例
├── sample_data/                   # 示例DICOM数据
│   ├── chd/
│   │   ├── sample_001/
│   │   ├── sample_002/
│   │   └── sample_003/
│   └── normal/
│       ├── sample_004/
│       └── sample_005/
└── README.md                      # 本文件
```

---

## 🚀 快速开始示例

### 1. 使用示例配置

```bash
# 复制示例配置
copy examples\example_config.yaml config\config.yaml

# 编辑配置（修改路径）
notepad config\config.yaml

# 验证配置
python scripts\validate_config.py config\config.yaml
```

### 2. 运行示例数据

```bash
# Pilot模式（5例示例数据）
python cli\run_nb10.py --data-dir examples\sample_data --mode pilot

# 预期输出
# - output/ai_cac_scores_YYYYMMDD.csv
# - output/statistical_analysis/
# - output/figures/
```

### 3. 使用批处理脚本

```batch
@echo off
REM 双击运行或命令行执行
examples\example_batch.bat
```

---

## 📋 example_config.yaml

完整配置文件示例，包含所有可配置选项的说明。

**关键配置**：

```yaml
# 路径配置（需要根据实际情况修改）
paths:
  data_dir: "D:/cardiac_data/dicom_original"
  model_path: "./models/va_non_gated_ai_cac_model.pth"
  output_dir: "D:/cardiac_data/results"

# 处理配置
processing:
  mode: "pilot"        # "pilot" 或 "full"
  device: "cuda"       # "cuda" 或 "cpu"
  pilot_limit: 10

# 性能配置
performance:
  gpu_memory_fraction: 0.9
  clear_cache_interval: 5  # RTX 2060建议5，更大显存可以10
```

---

## 📜 example_batch.bat

Windows批处理脚本示例，简化命令行操作。

**功能**：
- 自动激活虚拟环境
- 运行NB10工具
- 显示结果摘要
- 错误处理

**使用方式**：
```batch
# 直接运行
examples\example_batch.bat

# 或自定义参数
examples\example_batch.bat --mode full --device cpu
```

**脚本内容**：
```batch
@echo off
echo ====================================
echo NB10 AI-CAC Processing Tool
echo ====================================

REM 激活虚拟环境
call venv\Scripts\activate

REM 运行工具
python cli\run_nb10.py --mode pilot

REM 显示结果
echo.
echo ====================================
echo Processing Complete!
echo Check output directory for results
echo ====================================

pause
```

---

## 🐍 example_script.py

Python脚本示例，展示如何编程调用NB10功能。

**功能**：
- 加载配置
- 扫描数据
- 运行推理
- 生成报告

**使用方式**：
```bash
python examples\example_script.py
```

**代码框架**：
```python
from core.config_manager import ConfigManager
from core.ai_cac_inference_lib import create_model, run_inference
from core.statistics import generate_statistical_report

# 1. 加载配置
config = ConfigManager('config/config.yaml')

# 2. 加载模型
model = create_model(
    device=config.device,
    checkpoint_path=config.model_path
)

# 3. 运行推理
results = run_inference(
    model=model,
    data_dir=config.data_dir,
    mode=config.mode
)

# 4. 生成报告
generate_statistical_report(
    results=results,
    output_dir=config.output_dir
)

print("✅ Processing complete!")
```

---

## 📊 示例数据（sample_data/）

### 数据来源

从完整数据集中提取5-10例代表性病例：

| 病例 | 组别 | Agatston评分 | 切片数 | 特点 |
|------|------|-------------|--------|------|
| sample_001 | CHD | 0 | 46 | 零钙化（软斑块） |
| sample_002 | CHD | 153 | 60 | 轻度钙化 |
| sample_003 | CHD | 794 | 72 | 重度钙化 |
| sample_004 | Normal | 0 | 58 | 正常零钙化 |
| sample_005 | Normal | 25 | 63 | 正常轻度钙化 |

### 数据特点

- **已脱敏**：移除患者识别信息
- **小体积**：每例约5-10MB
- **代表性**：覆盖不同钙化程度
- **验证用**：用于快速测试工具功能

### 使用示例数据

```bash
# 方式1：命令行指定
python cli\run_nb10.py --data-dir examples\sample_data

# 方式2：修改配置文件
# config/config.yaml:
#   paths:
#     data_dir: "./examples/sample_data"
```

### 预期结果

运行示例数据应得到：

```
Processing Results:
- Total Cases: 5
- Success: 5 (100%)
- Failed: 0
- Average Score: 194.4 ± 320.2
- Processing Time: ~2-3 minutes (GPU)
```

---

## 🎓 学习路径

### 新手（第一次使用）

1. **阅读主README**：[../README.md](../README.md)
2. **查看示例配置**：`example_config.yaml`
3. **运行示例数据**：
   ```bash
   python cli\run_nb10.py --data-dir examples\sample_data
   ```
4. **查看结果**：`output/ai_cac_scores_*.csv`
5. **阅读使用手册**：[../docs/user_manual.md](../docs/user_manual.md)

### 进阶（准备处理自己的数据）

1. **准备数据**：参考[../data/README.md](../data/README.md)
2. **配置路径**：修改`config/config.yaml`
3. **先运行Pilot**：测试10例
4. **验证结果**：检查输出是否正确
5. **运行Full模式**：处理全部数据

### 高级（定制和扩展）

1. **阅读代码**：`core/ai_cac_inference_lib.py`
2. **编写脚本**：参考`example_script.py`
3. **集成分析**：添加自定义统计分析
4. **批量处理**：编写自动化脚本

---

## 📖 相关文档

- [主README](../README.md) - 项目总览
- [安装指南](../docs/installation_guide.md) - 详细安装步骤
- [使用手册](../docs/user_manual.md) - 完整使用说明
- [配置说明](../docs/configuration.md) - 配置项详解
- [API文档](../docs/api_documentation.md) - 编程接口

---

## ⚠️ 注意事项

1. **示例数据限制**：
   - 仅用于功能验证
   - 不适合性能测试
   - 不能用于实际研究

2. **配置文件**：
   - 示例配置需要根据实际情况修改
   - 特别是路径部分
   - 建议复制后修改，不要直接使用

3. **脚本定制**：
   - 示例脚本仅供参考
   - 根据实际需求修改
   - 注意错误处理

---

**最后更新**: 2025-10-14
