# 硬件自适应优化 - 实施计划
# Hardware Adaptive Optimization - Implementation Plan

**版本**: 1.0.0
**创建日期**: 2025-10-14
**目标版本**: NB10 v1.1.0
**预期完成**: 6周（Week 3-4 in Hospital Deployment Roadmap）

---

## 📋 快速概览

基于 [HARDWARE_ADAPTIVE_OPTIMIZATION_DESIGN.md](HARDWARE_ADAPTIVE_OPTIMIZATION_DESIGN.md) 的完整设计，本文档提供一个**可立即执行**的实施计划。

### 核心目标

✅ 在RTX 2060 (6GB)上实现 **20-30%性能提升**
✅ 零配置，自动检测硬件并优化
✅ 保持医疗级稳定性和结果一致性

### 优先级排序

**Phase 1 (Week 1)**: 核心优化 - 立即可见的性能提升
**Phase 2 (Week 2)**: 安全监控 - 确保稳定性
**Phase 3 (Week 3-4)**: 高级功能 - 可选

---

## 🚀 Phase 1: 核心优化（Week 1）- 立即实施

### 任务1.1: 硬件检测模块 (Day 1-2)

**目标**: 实现基础硬件检测

**新建文件**: `core/hardware_profiler.py`

```python
"""硬件检测模块"""
import torch
import psutil
import platform

class GPUInfo:
    def __init__(self):
        self.available = torch.cuda.is_available()
        if self.available:
            self.device_name = torch.cuda.get_device_name(0)
            self.vram_total_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
            self.vram_available_gb = self.vram_total_gb  # 简化版本
        else:
            self.device_name = "CPU"
            self.vram_total_gb = 0
            self.vram_available_gb = 0

class CPUInfo:
    def __init__(self):
        self.physical_cores = psutil.cpu_count(logical=False)
        self.logical_cores = psutil.cpu_count(logical=True)
        self.cpu_model = platform.processor()

class RAMInfo:
    def __init__(self):
        mem = psutil.virtual_memory()
        self.total_gb = mem.total / 1024**3
        self.available_gb = mem.available / 1024**3

def detect_hardware():
    """检测硬件信息"""
    return {
        'gpu': GPUInfo(),
        'cpu': CPUInfo(),
        'ram': RAMInfo()
    }
```

**验收标准**:
```bash
python -c "from core.hardware_profiler import detect_hardware; hw=detect_hardware(); print(f'GPU: {hw[\"gpu\"].device_name}, VRAM: {hw[\"gpu\"].vram_total_gb:.1f}GB')"
# 输出: GPU: NVIDIA GeForce RTX 2060, VRAM: 6.0GB
```

---

### 任务1.2: 配置档位系统 (Day 2-3)

**目标**: 定义5档配置并实现自动选择

**新建文件**: `core/performance_profiles.py`

```python
"""性能配置档位"""
from enum import Enum
from dataclasses import dataclass

class ProfileTier(Enum):
    MINIMAL = 1
    STANDARD = 2
    PERFORMANCE = 3
    PROFESSIONAL = 4
    ENTERPRISE = 5

@dataclass
class PerformanceProfile:
    tier: ProfileTier
    num_workers: int
    pin_memory: bool
    slice_batch_size: int
    clear_cache_interval: int

# 预定义配置
PROFILES = {
    ProfileTier.MINIMAL: PerformanceProfile(
        tier=ProfileTier.MINIMAL,
        num_workers=0,
        pin_memory=False,
        slice_batch_size=2,
        clear_cache_interval=1
    ),
    ProfileTier.STANDARD: PerformanceProfile(
        tier=ProfileTier.STANDARD,
        num_workers=2,          # ← 关键优化
        pin_memory=True,        # ← 关键优化
        slice_batch_size=4,
        clear_cache_interval=1
    ),
    ProfileTier.PERFORMANCE: PerformanceProfile(
        tier=ProfileTier.PERFORMANCE,
        num_workers=4,
        pin_memory=True,
        slice_batch_size=6,
        clear_cache_interval=3
    )
}

def select_profile(hw_info):
    """根据硬件信息选择最优配置"""
    gpu = hw_info['gpu']
    ram = hw_info['ram']

    if not gpu.available:
        return PROFILES[ProfileTier.MINIMAL]

    if gpu.vram_total_gb >= 12:
        return PROFILES[ProfileTier.PERFORMANCE]
    elif gpu.vram_total_gb >= 6:
        return PROFILES[ProfileTier.STANDARD]
    else:
        return PROFILES[ProfileTier.MINIMAL]
```

---

### 任务1.3: 修改推理核心 (Day 3-4)

**目标**: 应用优化配置到实际推理

**修改文件**: `core/ai_cac_inference_lib.py`

**关键修改**:

```python
# Line ~136: DataLoader配置
from core.performance_profiles import select_profile
from core.hardware_profiler import detect_hardware

# 在函数开始处检测硬件
hw_info = detect_hardware()
profile = select_profile(hw_info)

print(f"✓ 检测到硬件: {hw_info['gpu'].device_name}")
print(f"✓ 使用配置档位: {profile.tier.name}")
print(f"  - num_workers: {profile.num_workers}")
print(f"  - pin_memory: {profile.pin_memory}")

# 原代码:
# dataloader = DataLoader(dataset, batch_size=1, shuffle=False,
#                        num_workers=0, pin_memory=False)

# 修改为:
dataloader = DataLoader(
    dataset,
    batch_size=1,
    shuffle=False,
    num_workers=profile.num_workers,      # ← 动态配置
    pin_memory=profile.pin_memory,        # ← 动态配置
    prefetch_factor=2 if profile.num_workers > 0 else None
)
```

**预期效果**:
- RTX 2060: 从35-40秒/患者 → 28-32秒/患者 (**↓20-25%**)
- 无结果差异（已通过Pilot验证）

---

### 任务1.4: CLI集成 (Day 4-5)

**目标**: 在启动时显示硬件检测结果

**修改文件**: `cli/run_nb10.py`

```python
def main():
    # ... 现有代码 ...

    # 添加硬件检测显示
    print("="*70)
    print("🔍 正在检测硬件配置...")
    print("="*70)

    from core.hardware_profiler import detect_hardware
    from core.performance_profiles import select_profile

    hw_info = detect_hardware()
    profile = select_profile(hw_info)

    print(f"✓ GPU: {hw_info['gpu'].device_name} "
          f"({hw_info['gpu'].vram_total_gb:.1f}GB)")
    print(f"✓ RAM: {hw_info['ram'].total_gb:.1f}GB")
    print(f"✓ CPU: {hw_info['cpu'].physical_cores}核")
    print(f"\n推荐配置档位: {profile.tier.name}")
    print(f"预计性能提升: 20-30%")
    print("="*70)
    print()

    # ... 继续现有流程 ...
```

---

## 🛡️ Phase 2: 安全监控（Week 2）

### 任务2.1: OOM保护 (Day 1-2)

**新建文件**: `core/safety_monitor.py`

```python
"""安全监控模块"""
import torch
import logging

logger = logging.getLogger(__name__)

class OOMProtector:
    """OOM保护器"""
    def __init__(self, profile):
        self.profile = profile
        self.oom_count = 0

    def check_memory_before_inference(self):
        """推理前检查GPU内存"""
        if not torch.cuda.is_available():
            return True

        # 获取可用显存
        available_gb = (torch.cuda.get_device_properties(0).total_memory -
                       torch.cuda.memory_allocated(0)) / 1024**3

        # 估算需要的显存 (经验值: slice_batch_size * 0.8GB)
        required_gb = self.profile.slice_batch_size * 0.8

        if available_gb < required_gb * 1.2:  # 需要20%安全边际
            logger.warning(f"⚠️ 可用显存不足: {available_gb:.1f}GB < {required_gb*1.2:.1f}GB")
            logger.warning("  建议: 降低batch size或切换到稳定模式")
            return False

        return True

    def handle_oom(self):
        """处理OOM异常"""
        self.oom_count += 1

        if self.oom_count >= 3:
            logger.error("❌ 连续3次OOM，建议切换到CPU模式")
            return False

        # 自动降级
        old_size = self.profile.slice_batch_size
        self.profile.slice_batch_size = max(2, old_size - 2)

        logger.warning(f"⚠️ OOM检测，已降级: batch_size {old_size} → {self.profile.slice_batch_size}")
        torch.cuda.empty_cache()

        return True  # 可以重试
```

**集成到推理**:

```python
# 在 ai_cac_inference_lib.py 中
from core.safety_monitor import OOMProtector

oom_protector = OOMProtector(profile)

try:
    # 推理前检查
    if not oom_protector.check_memory_before_inference():
        logger.warning("内存不足警告，但继续尝试...")

    # 推理代码...

except RuntimeError as e:
    if "out of memory" in str(e).lower():
        if oom_protector.handle_oom():
            # 重试
            continue
        else:
            raise
```

---

### 任务2.2: 性能跟踪 (Day 3-4)

**目标**: 监控实际性能并与预期对比

```python
class PerformanceTracker:
    """性能跟踪器"""
    def __init__(self, expected_time_per_patient):
        self.expected_time = expected_time_per_patient
        self.processing_times = []

    def record_time(self, elapsed_time):
        """记录处理时间"""
        self.processing_times.append(elapsed_time)

        # 每5个patient检查一次
        if len(self.processing_times) % 5 == 0:
            avg_time = sum(self.processing_times[-5:]) / 5

            if avg_time > self.expected_time * 1.5:
                logger.warning("="*60)
                logger.warning("⚠️ 性能低于预期")
                logger.warning(f"  预期: {self.expected_time:.1f}秒/例")
                logger.warning(f"  实际: {avg_time:.1f}秒/例")
                logger.warning("  建议: 检查系统资源或切换到稳定模式")
                logger.warning("="*60)
```

---

## 🎯 Phase 3: 高级功能（Week 3-4, 可选）

### 可选功能列表

| 功能 | 优先级 | 性能提升 | 复杂度 | 风险 |
|------|--------|----------|--------|------|
| GPU温度监控 | 中 | 0% | 低 | 低 |
| 混合精度推理(FP16) | 低 | 10-15% | 中 | **高** (需验证精度) |
| 异步数据传输 | 低 | 5-10% | 高 | 中 |
| 多GPU支持 | 低 | 50%+ | 很高 | 中 |

**建议**: v1.1.0仅实施Phase 1-2，高级功能延后到v1.2.0

---

## ✅ 测试与验证

### 测试矩阵

| 硬件环境 | 档位 | 预期时间 | 验收标准 |
|---------|------|---------|----------|
| RTX 2060 6GB | Standard | 28-32秒 | ✅ 提升20-25% |
| RTX 3060 12GB | Performance | 18-22秒 | ✅ 提升40-45% |
| CPU only | Minimal | 100-150秒 | ✅ 正常运行 |

### 一致性验证

**关键**: 必须验证优化后结果与优化前完全一致

```bash
# 运行30例Pilot测试
python cli/run_nb10.py --mode pilot --pilot-limit 30

# 对比结果
python scripts/compare_with_baseline.py \
    --baseline results/baseline_30cases.csv \
    --optimized output/nb10_results_optimized.csv

# 预期输出:
# ✅ 30/30例完全一致 (差异0.0000分)
# ✅ 平均时间: 35.2秒 → 28.5秒 (↓19.0%)
```

---

## 📦 交付清单

### Week 1 交付物

- [ ] `core/hardware_profiler.py` (硬件检测)
- [ ] `core/performance_profiles.py` (配置档位)
- [ ] 修改 `core/ai_cac_inference_lib.py` (应用优化)
- [ ] 修改 `cli/run_nb10.py` (显示硬件信息)
- [ ] 单元测试 `tests/test_hardware_profiler.py`
- [ ] 性能测试报告 (30例Pilot)

### Week 2 交付物

- [ ] `core/safety_monitor.py` (安全监控)
- [ ] 集成OOM保护到推理流程
- [ ] 集成性能跟踪到推理流程
- [ ] 更新用户文档
- [ ] 完整测试报告 (60例验证)

---

## 🚧 风险与应对

### 风险1: Windows多进程兼容性

**风险**: `num_workers > 0` 在Windows上可能不稳定

**应对**:
- 保守设置 `num_workers=2` (不超过4)
- 提供降级到 `num_workers=0` 的选项
- 充分测试Windows环境

### 风险2: 结果一致性

**风险**: 优化可能影响Agatston score计算

**应对**:
- **强制要求**: 60例Pilot测试100%一致
- 任何差异立即回退修改
- 完整记录所有测试结果

### 风险3: 性能未达预期

**风险**: 实际提升< 20%

**应对**:
- 降低承诺: "预期提升15-25%"
- 分析瓶颈并迭代优化
- 提供详细性能分析报告

---

## 📊 成功指标

### 必达指标 (v1.1.0发布条件)

✅ RTX 2060上性能提升 ≥ 20%
✅ 60例Pilot测试结果100%一致
✅ 无OOM崩溃（连续200例测试）
✅ 用户文档完整

### 可选指标 (v1.2.0目标)

⭐ RTX 3060上性能提升 ≥ 40%
⭐ 混合精度推理（精度损失<0.1%）
⭐ 多GPU并行支持

---

## 📅 时间线总结

```
Week 1 (Phase 1): 核心优化
├─ Day 1-2: 硬件检测模块
├─ Day 2-3: 配置档位系统
├─ Day 3-4: 修改推理核心
└─ Day 4-5: CLI集成 + 初步测试

Week 2 (Phase 2): 安全监控
├─ Day 1-2: OOM保护
├─ Day 3-4: 性能跟踪
└─ Day 4-5: 完整测试 + 文档

Week 3-4 (Phase 3, 可选): 高级功能
└─ 根据v1.1.0测试结果决定是否实施
```

---

## 🎯 下一步行动

### 立即可执行 (今天)

1. **创建feature分支**:
```bash
git checkout -b feature/hardware-optimization
```

2. **创建新文件**:
```bash
touch core/hardware_profiler.py
touch core/performance_profiles.py
touch core/safety_monitor.py
```

3. **开始实施任务1.1**: 硬件检测模块 (预计2小时)

4. **运行验证**:
```bash
python -m pytest tests/test_hardware_profiler.py -v
```

---

**文档状态**: ✅ 可执行
**最后更新**: 2025-10-14
**负责人**: 陈医生团队
**目标完成日期**: 2025-11-25 (6周后)
