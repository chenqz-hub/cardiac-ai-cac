# Phase 2 安全监控系统实施指南
# Safety Monitor Implementation Guide

**版本**: v1.0
**日期**: 2025-10-14
**状态**: 核心模块已完成，集成进行中

---

## 📋 实施概览

根据[HARDWARE_ADAPTIVE_OPTIMIZATION_DESIGN.md](HARDWARE_ADAPTIVE_OPTIMIZATION_DESIGN.md)设计文档，Phase 2主要实现OOM保护和自动降级机制，确保系统在医院各种硬件环境下稳定运行。

---

## ✅ 已完成工作

### 1. 核心安全监控模块 (`core/safety_monitor.py`)

**文件**: [safety_monitor.py](../core/safety_monitor.py)

**功能**:
- ✅ RAM实时监控
- ✅ GPU VRAM实时监控
- ✅ 4级安全等级判断 (SAFE/WARNING/CRITICAL/EMERGENCY)
- ✅ 自动降级建议生成
- ✅ GPU缓存清理
- ✅ 单例模式全局访问

**关键类**:

```python
# 安全监控器
class SafetyMonitor:
    def check_status() -> ResourceStatus
        """检查当前资源状态"""

    def should_downgrade(status) -> bool
        """判断是否需要降级"""

    def suggest_downgrade_profile(current_num_workers) -> dict
        """生成降级配置建议"""

    def clear_gpu_cache()
        """清理GPU缓存"""

# 全局单例获取
monitor = get_monitor()
```

**安全阈值**:

| 资源 | WARNING | CRITICAL | EMERGENCY |
|------|---------|----------|-----------|
| RAM可用 | <20% | <10% | <5% |
| VRAM已用 | >80% | >90% | >95% |

**测试结果**:
```bash
$ python core/safety_monitor.py

当前资源状态:
  RAM: 3.22GB 可用 / 4.80GB 总量 (67.0%)
  VRAM: 6.00GB 可用 / 6.00GB 总量 (100.0%)

安全等级:
  RAM: safe
  VRAM: safe
  整体: safe

建议操作: CONTINUE
  详情: 资源充足 (RAM: 3.2GB, VRAM: 6.0GB)

✅ 测试通过
```

---

## 🔄 待完成工作（集成步骤）

### 步骤1: 集成到推理流程 (`ai_cac_inference_lib.py`)

**位置**: `run_inference_on_dicom_folder()`函数

**集成点**:

```python
def run_inference_on_dicom_folder(..., safety_monitor=None):
    # 1. 开始前检查资源
    if safety_monitor:
        status = safety_monitor.check_status()
        if status.overall_level == SafetyLevel.EMERGENCY:
            raise RuntimeError(f"资源严重不足，无法启动推理: {status.details}")

    # 2. 推理循环中监控
    for start_idx in range(0, num_slices, SLICE_BATCH_SIZE):
        # 每个batch前检查
        if safety_monitor and start_idx % 20 == 0:  # 每20个slice检查一次
            status = safety_monitor.check_status()
            if status.overall_level == SafetyLevel.CRITICAL:
                logger.warning(f"资源不足，清理GPU缓存")
                safety_monitor.clear_gpu_cache()

        # ... 推理代码 ...

    # 3. 结束后清理
    if safety_monitor:
        safety_monitor.clear_gpu_cache()
```

### 步骤2: 集成到CLI (`cli/run_nb10.py`)

**位置**: `run_inference_batch()`函数

**集成点**:

```python
from core.safety_monitor import get_monitor

# 初始化安全监控器
logger.info("Initializing safety monitor...")
safety_monitor = get_monitor(
    ram_warning=20.0,
    ram_critical=10.0,
    ram_emergency=5.0,
    vram_warning=80.0,
    vram_critical=90.0,
    vram_emergency=95.0,
    enable_auto_downgrade=True
)

# 检查初始状态
initial_status = safety_monitor.check_status()
safety_monitor.log_status(initial_status, prefix="  Initial: ")

# 传递给推理函数
for idx, folder_path in enumerate(dicom_folders):
    try:
        result = run_inference_on_dicom_folder(
            folder_path,
            model,
            config.device,
            performance_profile=performance_profile,
            safety_monitor=safety_monitor  # ← 传递监控器
        )

        # 定期检查状态（每10个患者）
        if (idx + 1) % 10 == 0:
            status = safety_monitor.check_status()
            safety_monitor.log_status(status, prefix=f"  After {idx+1} patients: ")

            # 如果需要降级
            if safety_monitor.should_downgrade(status):
                logger.warning(f"资源不足，建议降级配置")
                downgrade = safety_monitor.suggest_downgrade_profile(
                    performance_profile.num_workers
                )
                logger.warning(f"  {downgrade['reason']}")
                # 可选: 实际应用降级配置
                # performance_profile.num_workers = downgrade['num_workers']
                # performance_profile.pin_memory = downgrade['pin_memory']

    except RuntimeError as e:
        if "资源严重不足" in str(e):
            logger.error(f"资源不足，停止处理")
            break
        raise
```

### 步骤3: 添加配置文件支持 (`config/config.yaml`)

**新增配置段**:

```yaml
# 安全监控配置
safety_monitor:
  enabled: true

  # RAM阈值（可用百分比）
  ram_thresholds:
    warning: 20.0    # 可用<20%警告
    critical: 10.0   # 可用<10%危险
    emergency: 5.0   # 可用<5%紧急

  # VRAM阈值（已用百分比）
  vram_thresholds:
    warning: 80.0    # 已用>80%警告
    critical: 90.0   # 已用>90%危险
    emergency: 95.0  # 已用>95%紧急

  # 自动降级
  auto_downgrade:
    enabled: true
    log_interval: 10  # 每10个患者记录一次状态
```

---

## 🎯 安全机制工作流程

### 正常流程（资源充足）

```
开始推理
  ↓
初始检查 → ✅ SAFE
  ↓
推理患者1-10
  ↓
定期检查(10个患者) → ✅ SAFE
  ↓
继续推理...
  ↓
完成
```

### 警告流程（资源接近阈值）

```
推理中...
  ↓
定期检查 → ⚠️ WARNING
  ↓
记录警告日志
  ↓
清理GPU缓存
  ↓
继续推理（密切监控）
```

### 危险流程（资源不足需降级）

```
推理中...
  ↓
定期检查 → 🔴 CRITICAL
  ↓
建议降级配置
  ↓
应用降级: num_workers 2→1
  ↓
清理GPU缓存
  ↓
继续推理（降级配置）
```

### 紧急流程（资源严重不足）

```
推理开始前/中
  ↓
检查 → 🚨 EMERGENCY
  ↓
抛出异常
  ↓
停止处理，记录错误
  ↓
用户介入处理
```

---

## 🛡️ OOM保护机制

### 1. 预防性保护

- **资源检查**: 开始前检查是否有足够资源
- **动态监控**: 推理过程中持续监控
- **渐进式降级**: WARNING → CRITICAL → EMERGENCY逐级应对

### 2. 主动保护

- **GPU缓存清理**: 定期调用`torch.cuda.empty_cache()`
- **批次调整**: 根据VRAM使用情况调整SLICE_BATCH_SIZE
- **降级配置**: 自动减少num_workers

### 3. 被动保护

- **异常捕获**: 捕获OOM异常，尝试恢复
- **紧急停止**: EMERGENCY级别立即停止处理
- **错误报告**: 详细记录资源状态

---

## 💡 使用示例

### 示例1: 基础集成

```python
from core.safety_monitor import get_monitor
from core.ai_cac_inference_lib import run_inference_on_dicom_folder

# 创建监控器
monitor = get_monitor()

# 检查状态
status = monitor.check_status()
print(f"资源状态: {status.overall_level.value}")

# 推理时传入监控器
result = run_inference_on_dicom_folder(
    dicom_folder,
    model,
    device='cuda',
    safety_monitor=monitor
)
```

### 示例2: 自定义阈值

```python
# 为低RAM环境调整阈值
monitor = get_monitor(
    ram_warning=15.0,    # 降低到15%
    ram_critical=8.0,     # 降低到8%
    ram_emergency=3.0,    # 降低到3%
)
```

### 示例3: 手动降级

```python
# 检查是否需要降级
status = monitor.check_status()
if monitor.should_downgrade(status):
    downgrade = monitor.suggest_downgrade_profile(
        current_num_workers=2
    )
    print(f"建议: {downgrade['reason']}")
    print(f"新配置: num_workers={downgrade['num_workers']}")
```

---

## 📊 测试验证计划

### 单元测试

```bash
# 测试安全监控器
python core/safety_monitor.py

# 预期输出:
# ✅ RAM/VRAM检测正常
# ✅ 安全等级判断正确
# ✅ 降级建议合理
```

### 集成测试

```bash
# 测试小批量（10例）
python cli/run_nb10.py \
  --data-dir /path/to/data \
  --mode pilot \
  --pilot-limit 10

# 监控点:
# - 启动时资源检查
# - 推理中定期监控
# - 完成后资源释放
```

### 压力测试

```bash
# 测试大批量（199例CHD）
python cli/run_nb10.py \
  --data-dir /path/to/chd \
  --mode full

# 验证:
# - 长时间运行稳定性
# - 内存泄漏检测
# - 自动降级触发
```

---

## 🚀 部署检查清单

### 代码集成

- [x] `safety_monitor.py` 核心模块创建
- [ ] `ai_cac_inference_lib.py` 集成安全检查
- [ ] `run_nb10.py` 集成监控器初始化
- [ ] `config.yaml` 添加安全配置

### 测试验证

- [x] 单元测试通过
- [ ] 集成测试通过
- [ ] 压力测试通过
- [ ] 医院环境测试

### 文档完善

- [x] 实施指南文档
- [ ] 用户手册更新
- [ ] 故障排查指南
- [ ] API文档生成

---

## 📝 已知限制与改进方向

### 当前限制

1. **监控粒度**: 目前每10个患者检查一次，可能无法及时发现突发OOM
2. **降级策略**: 降级是永久的，不会在资源充足时恢复
3. **GPU温度**: 未实现温度监控（Phase 3功能）

### 改进方向

1. **动态监控频率**: 根据资源使用情况调整检查频率
2. **智能恢复**: 资源充足时自动恢复原配置
3. **多GPU支持**: 监控多个GPU的资源使用
4. **预测模型**: 根据历史数据预测OOM风险

---

## 🔗 相关文档

1. **设计文档**: [HARDWARE_ADAPTIVE_OPTIMIZATION_DESIGN.md](HARDWARE_ADAPTIVE_OPTIMIZATION_DESIGN.md)
2. **Phase 1总结**: [PHASE1_FINAL_PERFORMANCE_REPORT.md](PHASE1_FINAL_PERFORMANCE_REPORT.md)
3. **代码文件**: [safety_monitor.py](../core/safety_monitor.py)

---

**文档版本**: v1.0
**最后更新**: 2025-10-14
**作者**: NB10 Team + Claude Code
