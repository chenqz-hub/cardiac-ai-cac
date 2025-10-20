# Tests Directory

本目录包含NB10工具的测试代码和测试数据。

---

## 🧪 测试类型

### 1. 单元测试（Unit Tests）

测试单个函数和模块：

```
tests/
├── test_inference.py          # AI-CAC推理功能测试
├── test_config.py             # 配置管理测试
├── test_data_loader.py        # 数据加载测试
├── test_statistics.py         # 统计分析测试
└── test_utils.py              # 工具函数测试
```

运行方式：
```bash
# 运行所有单元测试
python -m pytest tests/

# 运行单个测试文件
python -m pytest tests/test_inference.py

# 详细输出
python -m pytest tests/ -v
```

### 2. 集成测试（Integration Tests）

测试完整流程：

```
tests/
└── test_pipeline.py           # 完整处理流程测试
```

运行方式：
```bash
python -m pytest tests/test_pipeline.py
```

### 3. 一致性测试（Consistency Tests）

对比Colab和Windows版本结果：

```
tests/
├── compare_with_colab.py      # Colab结果对比脚本
└── results_comparison/        # 对比结果存放
    ├── colab_results.csv
    ├── windows_results.csv
    └── comparison_report.md
```

运行方式：
```bash
python tests/compare_with_colab.py \
  --colab results_comparison/colab_results.csv \
  --windows results_comparison/windows_results.csv
```

---

## 📊 测试数据

### test_data/

包含少量测试用DICOM数据：

```
test_data/
├── case_001/                  # 正常病例（零钙化）
│   ├── IM-0001.dcm
│   ├── IM-0002.dcm
│   └── ...
├── case_002/                  # 轻度钙化
│   └── ...
└── case_003/                  # 重度钙化
    └── ...
```

**数据来源**：
- 从完整数据集中提取3-5例
- 覆盖不同钙化程度
- 已脱敏处理

**用途**：
- 快速验证推理功能
- 测试数据加载
- 性能基准测试

---

## 🎯 关键测试场景

### 测试1：推理一致性

**目标**：确保Windows版本和Colab版本结果一致

```python
# tests/test_inference.py

def test_inference_consistency():
    """Test that Windows and Colab produce identical results"""
    # Given same DICOM data and model
    # When running inference
    # Then Agatston scores should match (within floating point tolerance)

    assert abs(windows_score - colab_score) < 0.01
```

**验收标准**：
- 相同输入产生相同输出
- 误差 < 0.01（浮点精度）
- 10例测试全部通过

### 测试2：边界条件

**目标**：处理异常输入

```python
def test_edge_cases():
    # Test zero calcium case
    # Test single slice case
    # Test missing DICOM tags
    # Test corrupted files
```

**验收标准**：
- 异常输入不崩溃
- 错误信息清晰
- 自动降级处理

### 测试3：性能基准

**目标**：验证性能符合预期

```python
def test_performance_benchmark():
    # Test GPU mode speed
    # Test CPU mode speed
    # Test memory usage
```

**验收标准**：
- GPU: < 1s/slice (RTX 2060)
- CPU: < 20s/slice
- 内存: < 8GB

---

## 📋 测试覆盖率

### 当前覆盖率目标

- **核心推理代码**: 90%+
- **配置管理**: 80%+
- **数据加载**: 85%+
- **统计分析**: 80%+
- **整体**: 75%+

### 查看覆盖率

```bash
# 运行测试并生成覆盖率报告
python -m pytest --cov=core --cov=cli --cov-report=html tests/

# 查看HTML报告
# Windows: start htmlcov/index.html
```

---

## 🔧 测试工具

### pytest

主要测试框架：

```bash
# 安装
pip install pytest pytest-cov

# 运行测试
pytest tests/

# 生成覆盖率报告
pytest --cov=core tests/
```

### pytest-benchmark

性能测试：

```bash
# 安装
pip install pytest-benchmark

# 运行性能测试
pytest tests/test_performance.py --benchmark-only
```

---

## 🚀 测试工作流

### 开发阶段

1. **编写功能代码**
2. **编写对应测试**
3. **运行测试确认通过**
4. **提交代码**

```bash
# 快速测试
python -m pytest tests/ -x  # 遇到第一个失败停止

# 详细测试
python -m pytest tests/ -v --tb=short
```

### 发布前

1. **运行完整测试套件**
2. **检查覆盖率**
3. **运行一致性测试**
4. **性能基准测试**
5. **在CPU/GPU环境测试**

```bash
# 完整测试流程
./scripts/run_all_tests.sh
```

### 持续集成（CI）

计划集成到GitHub Actions：

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest tests/
```

---

## 📊 一致性测试详解

### 对比Colab结果

**步骤**：

1. **准备Colab结果**：
   ```bash
   # 从Google Drive下载
   # 放置到 tests/results_comparison/colab_results.csv
   ```

2. **运行Windows版本**：
   ```bash
   python cli/run_nb10.py --mode pilot --output tests/results_comparison/
   ```

3. **对比结果**：
   ```bash
   python tests/compare_with_colab.py
   ```

**对比维度**：
- Agatston积分（逐个病例）
- 统计量（均值、标准差、P值）
- 风险分层分布

**验收标准**：
- 单例误差 < 0.5%
- 统计量误差 < 1%
- P值一致（相同显著性）

### 报告格式

```markdown
# Consistency Test Report

## Summary
- Total Cases: 10
- Matched Cases: 10 (100%)
- Average Difference: 0.08%
- Max Difference: 0.3%
- Status: ✅ PASS

## Detailed Comparison
| Patient ID | Colab | Windows | Diff | Diff% |
|------------|-------|---------|------|-------|
| case_001   | 153.0 | 153.1   | 0.1  | 0.07% |
| ...        | ...   | ...     | ...  | ...   |

## Statistical Comparison
| Metric | Colab | Windows | Diff |
|--------|-------|---------|------|
| Mean   | 358.8 | 358.9   | 0.1  |
| SD     | 658.3 | 658.4   | 0.1  |
| P-val  | 4.97e-17 | 4.96e-17 | OK |
```

---

## ⚠️ 注意事项

1. **测试数据隐私**：
   - 测试数据已脱敏
   - 不包含真实患者信息
   - 仅用于技术验证

2. **测试环境**：
   - CPU和GPU环境分别测试
   - Python 3.10专用测试
   - Windows 10/11验证

3. **持续更新**：
   - 新功能必须有测试
   - 修复bug需要回归测试
   - 定期更新测试数据

4. **性能测试**：
   - 性能测试在独立环境运行
   - 避免后台进程干扰
   - 多次运行取平均值

---

## 📖 相关文档

- [开发指南](../docs/development_guide.md)
- [贡献指南](../docs/contributing.md)
- [测试最佳实践](../docs/testing_best_practices.md)

---

**最后更新**: 2025-10-14
