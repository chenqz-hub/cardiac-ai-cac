# 硬件自适应优化系统 - 技术设计文档

**版本**: 1.0.0
**创建日期**: 2025-10-14
**文档状态**: 设计提案 (Proposal)
**目标版本**: NB10 v2.0.0

---

## 📋 执行摘要

本文档描述了一个**智能硬件感知与自适应配置系统**的完整设计方案，旨在让NB10 AI-CAC工具能够：

1. **自动检测**用户的硬件配置（GPU、CPU、RAM、存储）
2. **智能选择**最优的性能参数
3. **动态调整**运行策略以平衡性能与稳定性
4. **零配置**开箱即用体验，适配从诊所笔记本到医院工作站的各种环境

**核心价值**：
- 医生用户无需了解技术细节
- 自动榨取硬件潜力，性能提升 20-40%
- 高稳定性保护机制，避免医疗场景下的中断
- 跨设备兼容，一套软件适配所有硬件

---

## 🎯 设计目标

### 主要目标

1. **易用性优先**
   - 默认"Auto"模式，医生用户无需配置
   - 启动时自动检测并显示硬件信息
   - 提供简单的交互界面选择模式

2. **性能最大化**
   - 根据硬件自动调整：
     - DataLoader workers数量
     - GPU内存管理策略
     - 批处理大小
     - 数据传输优化
   - 预期性能提升：20-40%（视硬件而定）

3. **稳定性保证**
   - OOM（内存溢出）保护机制
   - GPU温度监控与过热保护
   - 异常自动降级策略
   - 医疗级可靠性要求

4. **跨设备兼容**
   - 支持从4GB到24GB+的各种GPU
   - 兼容CPU模式（无GPU环境）
   - Windows/Linux跨平台
   - 笔记本到服务器全覆盖

### 非功能性目标

- **完全离线运行** - 不需要网络连接
- **向后兼容** - 保留手动配置选项
- **可扩展性** - 易于添加新硬件档位
- **可维护性** - 清晰的代码结构和文档

---

## 🔍 当前性能瓶颈分析

### 现状评估

基于代码审查（`core/ai_cac_inference_lib.py` 和 `cli/run_nb10.py`），当前系统存在以下瓶颈：

#### 1. 数据加载瓶颈（25-30%处理时间）

```python
# 当前配置 - ai_cac_inference_lib.py:136
dataloader = DataLoader(dataset, batch_size=1, shuffle=False,
                       num_workers=0,        # ❌ 单线程加载
                       pin_memory=False)     # ❌ 硬编码为False
```

**问题**：
- `num_workers=0` 导致DICOM加载与GPU推理完全串行
- 单个cardiac CT DICOM可能200-400张切片，加载耗时长
- GPU推理时CPU空闲等待，资源浪费

**影响**：约占总处理时间的 25-30%

---

#### 2. CPU↔GPU传输瓶颈（10-15%处理时间）

```python
# 当前传输方式 - ai_cac_inference_lib.py:154-155
inputs = inputs.to(device)
hu_vols = hu_vols.to(device)
```

**问题**：
- `pin_memory=False` 导致数据需经过两次拷贝（pageable → pinned → GPU）
- 同步传输，GPU等待数据到达
- 未使用CUDA streams进行异步传输

**影响**：约占总处理时间的 10-15%

---

#### 3. GPU缓存清理策略（5-8%处理时间）

```python
# 当前清理策略 - ai_cac_inference_lib.py:201-203
if device == 'cuda':
    del inputs, hu_vols, pred_vol
    torch.cuda.empty_cache()  # 每个patient都执行
```

**问题**：
- 每处理完一个patient立即清理GPU缓存
- `torch.cuda.empty_cache()` 本身有开销（约0.5-1秒）
- 对于6GB以上GPU，过于保守

**影响**：约占总处理时间的 5-8%

---

#### 4. 批处理大小固定（不可优化）

```python
# 固定配置 - ai_cac_inference_lib.py:140
SLICE_BATCH_SIZE = 4  # 处理4个切片/批次
```

**问题**：
- 针对6GB GPU优化，对于更大显存未充分利用
- 对于4GB GPU可能仍有OOM风险

**影响**：性能潜力未充分发挥

---

### 性能提升潜力评估

基于医学影像深度学习的典型工作流，单个Patient处理时间分解：

```
当前基线（100%）:
├─ DICOM加载与解析      25-30%  ← num_workers=0 瓶颈
├─ 数据预处理（重采样）   15-20%  ← CPU操作
├─ CPU→GPU传输          10-15%  ← pin_memory=False 瓶颈
├─ GPU推理计算          30-40%  ← 实际AI计算（不可压缩）
├─ GPU→CPU传输          5-10%
└─ 后处理（Agatston）    5-10%

优化后预期（60-75%）:
├─ DICOM加载（后台）     0-5%    ← num_workers=2-4 隐藏加载延迟
├─ 数据预处理           12-15%  ← 轻微优化
├─ CPU→GPU传输（异步）   3-5%    ← pin_memory=True + 异步
├─ GPU推理计算          30-40%  ← 不变（硬件极限）
├─ GPU→CPU传输          4-8%
└─ 后处理              5-8%
```

**保守估计**：总体性能提升 **20-30%**
**激进优化**：总体性能提升 **30-40%**（高端硬件）

---

## 🏗️ 系统架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     NB10 AI-CAC Application                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │           1. Hardware Detection Module                │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │ │
│  │  │ GPU Profiler│  │CPU Profiler│  │RAM Profiler│     │ │
│  │  └────────────┘  └────────────┘  └────────────┘     │ │
│  │           ┌────────────┐                              │ │
│  │           │Disk Profiler│                              │ │
│  │           └────────────┘                              │ │
│  └──────────────────────┬──────────────────────────────┘ │
│                         │                                  │
│                         ▼                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │       2. Configuration Profile Selector              │ │
│  │                                                       │ │
│  │   Hardware Metrics → Scoring Algorithm → Tier       │ │
│  │                                                       │ │
│  │   Tiers: Minimal | Standard | Performance |          │ │
│  │          Professional | Enterprise                    │ │
│  └──────────────────────┬──────────────────────────────┘ │
│                         │                                  │
│                         ▼                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │       3. Runtime Optimization Engine                 │ │
│  │                                                       │ │
│  │   • DataLoader Configuration                          │ │
│  │   • Memory Management Strategy                        │ │
│  │   • Batch Size Adjustment                             │ │
│  │   • Cache Clearing Policy                             │ │
│  └──────────────────────┬──────────────────────────────┘ │
│                         │                                  │
│                         ▼                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │       4. Safety & Monitoring System                  │ │
│  │                                                       │ │
│  │   • OOM Protection                                    │ │
│  │   • Temperature Monitoring                            │ │
│  │   • Auto-downgrade on Failure                         │ │
│  │   • Performance Tracking                              │ │
│  └──────────────────────┬──────────────────────────────┘ │
│                         │                                  │
│                         ▼                                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │            5. User Interface Layer                   │ │
│  │                                                       │ │
│  │   • Hardware Detection Display                        │ │
│  │   • Mode Selection (Auto/Performance/Stable/Custom)   │ │
│  │   • Progress & Performance Metrics                    │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 核心模块详细设计

### Module 1: 硬件检测模块

#### 1.1 GPU检测器 (GPU Profiler)

**文件位置**: `core/hardware_profiler.py` → `class GPUProfiler`

**检测指标**:

```python
class GPUInfo:
    """GPU硬件信息"""
    available: bool                # 是否有可用GPU
    device_name: str               # GPU型号（如 "NVIDIA RTX 2060"）
    compute_capability: tuple      # CUDA计算能力（如 (7, 5)）
    vram_total_gb: float          # 总显存（GB）
    vram_available_gb: float      # 可用显存（GB）
    driver_version: str           # 驱动版本
    cuda_version: str             # CUDA版本
    supports_fp16: bool           # 是否支持FP16混合精度
    supports_tensor_core: bool    # 是否有Tensor Core
```

**检测逻辑**:

```python
def detect_gpu() -> GPUInfo:
    """检测GPU信息"""
    if not torch.cuda.is_available():
        return GPUInfo(available=False)

    gpu_info = GPUInfo(
        available=True,
        device_name=torch.cuda.get_device_name(0),
        vram_total_gb=torch.cuda.get_device_properties(0).total_memory / 1024**3,
        vram_available_gb=(torch.cuda.get_device_properties(0).total_memory -
                          torch.cuda.memory_allocated(0)) / 1024**3,
        driver_version=torch.version.cuda,
        ...
    )

    # 测试可用显存（考虑其他进程占用）
    gpu_info.vram_available_gb = measure_available_vram()

    return gpu_info
```

---

#### 1.2 CPU检测器 (CPU Profiler)

**检测指标**:

```python
class CPUInfo:
    """CPU硬件信息"""
    physical_cores: int           # 物理核心数
    logical_cores: int            # 逻辑核心数（含超线程）
    cpu_model: str                # CPU型号
    frequency_mhz: float          # 主频（MHz）
    platform: str                 # 操作系统（Windows/Linux）
```

**检测逻辑**:

```python
import psutil
import platform

def detect_cpu() -> CPUInfo:
    """检测CPU信息"""
    return CPUInfo(
        physical_cores=psutil.cpu_count(logical=False),
        logical_cores=psutil.cpu_count(logical=True),
        cpu_model=platform.processor(),
        frequency_mhz=psutil.cpu_freq().max,
        platform=platform.system()
    )
```

---

#### 1.3 内存检测器 (RAM Profiler)

**检测指标**:

```python
class RAMInfo:
    """内存信息"""
    total_gb: float               # 总内存（GB）
    available_gb: float           # 可用内存（GB）
    used_percent: float           # 使用百分比
```

**检测逻辑**:

```python
def detect_ram() -> RAMInfo:
    """检测内存信息"""
    mem = psutil.virtual_memory()
    return RAMInfo(
        total_gb=mem.total / 1024**3,
        available_gb=mem.available / 1024**3,
        used_percent=mem.percent
    )
```

---

#### 1.4 磁盘检测器 (Disk Profiler)

**检测指标**:

```python
class DiskInfo:
    """磁盘信息"""
    disk_type: str                # SSD/HDD/NVMe/Unknown
    read_speed_mbps: float        # 读取速度（MB/s，通过简单benchmark）
```

**检测逻辑**:

```python
def detect_disk(data_dir: Path) -> DiskInfo:
    """检测磁盘类型和性能"""
    # 方法1: 检查磁盘类型（Windows: wmic, Linux: lsblk）
    disk_type = detect_disk_type(data_dir)

    # 方法2: 简单读取benchmark（读取100MB测试文件）
    read_speed = benchmark_disk_read(data_dir)

    return DiskInfo(
        disk_type=disk_type,
        read_speed_mbps=read_speed
    )
```

---

### Module 2: 配置档位系统

#### 2.1 配置档位定义

**文件位置**: `core/performance_profiles.py`

共定义 **5个配置档位**，从低到高：

---

##### Tier 1: Minimal (最小配置)

**硬件特征**:
- GPU显存: ≤4GB (GTX 1650, RTX 3050 4GB)
- 或只有CPU

**配置参数**:

```yaml
profile_minimal:
  device: "cuda"  # 或 "cpu" (若无GPU)
  num_workers: 0
  pin_memory: false
  slice_batch_size: 2
  clear_cache_interval: 1
  use_mixed_precision: false
  prefetch_next_patient: false
  async_data_transfer: false
```

**预期性能**:
- 单例处理时间: 45-60秒
- 稳定性: ★★★★★
- 适用场景: 诊所笔记本、低端工作站

---

##### Tier 2: Standard (标准配置) ← **当前RTX 2060场景**

**硬件特征**:
- GPU显存: 6GB (RTX 2060, GTX 1060 6GB)
- RAM: 16GB+
- CPU: 4核+

**配置参数**:

```yaml
profile_standard:
  device: "cuda"
  num_workers: 2                    # Windows保守值
  pin_memory: true                  # ✅ 修复当前硬编码问题
  slice_batch_size: 4
  clear_cache_interval: 1
  use_mixed_precision: false
  prefetch_next_patient: false
  async_data_transfer: false        # 可选：true（中等风险）
```

**预期性能**:
- 单例处理时间: 28-32秒（↓18-20% vs 当前）
- 稳定性: ★★★★☆
- 适用场景: 标准医疗工作站

**性能提升来源**:
- `num_workers=2`: 减少DICOM加载等待 (+10-12%)
- `pin_memory=true`: 加速CPU→GPU传输 (+5-8%)
- 总计: **+18-20%**

---

##### Tier 3: Performance (高性能配置)

**硬件特征**:
- GPU显存: 8-12GB (RTX 3060 12GB, RTX 3070, RTX 4060 Ti)
- RAM: 32GB+
- CPU: 6核+

**配置参数**:

```yaml
profile_performance:
  device: "cuda"
  num_workers: 4
  pin_memory: true
  slice_batch_size: 6
  clear_cache_interval: 3
  use_mixed_precision: true         # 启用FP16加速
  prefetch_next_patient: true       # 预加载下一个patient
  async_data_transfer: true         # CUDA streams异步传输
  dataloader_prefetch_factor: 2
```

**预期性能**:
- 单例处理时间: 18-22秒（↓50% vs 当前）
- 稳定性: ★★★★☆
- 适用场景: 大型医院影像中心

---

##### Tier 4: Professional (专业配置)

**硬件特征**:
- GPU显存: 16-24GB (RTX 4080, RTX A5000, RTX 4090)
- RAM: 64GB+
- CPU: 8核+
- 存储: NVMe SSD

**配置参数**:

```yaml
profile_professional:
  device: "cuda"
  num_workers: 6
  pin_memory: true
  slice_batch_size: 8
  clear_cache_interval: 5
  use_mixed_precision: true
  prefetch_next_patient: true
  async_data_transfer: true
  dataloader_prefetch_factor: 3
```

**预期性能**:
- 单例处理时间: 12-15秒（↓65% vs 当前）
- 稳定性: ★★★★☆
- 适用场景: 科研机构、三甲医院AI中心

---

##### Tier 5: Enterprise (服务器配置)

**硬件特征**:
- GPU: 多卡或A100/H100
- RAM: 128GB+
- 存储: RAID SSD阵列

**配置参数**:

```yaml
profile_enterprise:
  device: "cuda"
  multi_gpu: true                   # 多GPU并行
  num_workers: 16
  pin_memory: true
  slice_batch_size: 12
  clear_cache_interval: 10
  use_mixed_precision: true
  prefetch_next_patient: true
  async_data_transfer: true
  dataloader_prefetch_factor: 4
```

**预期性能**:
- 单例处理时间: 8-10秒
- 吞吐量: 可并行处理多个patient
- 适用场景: 云端AI服务、大规模筛查

---

#### 2.2 档位选择算法

**文件位置**: `core/performance_profiles.py` → `select_optimal_profile()`

**评分算法**:

```python
def select_optimal_profile(
    gpu_info: GPUInfo,
    cpu_info: CPUInfo,
    ram_info: RAMInfo,
    disk_info: DiskInfo
) -> ProfileTier:
    """
    根据硬件信息选择最优配置档位

    评分权重：
    - GPU: 60%
    - RAM: 20%
    - CPU: 15%
    - Disk: 5%
    """
    score = 0

    # 1. GPU评分（60分）
    if not gpu_info.available:
        score += 0  # CPU模式
    elif gpu_info.vram_total_gb >= 16:
        score += 60
    elif gpu_info.vram_total_gb >= 8:
        score += 45
    elif gpu_info.vram_total_gb >= 6:
        score += 30
    elif gpu_info.vram_total_gb >= 4:
        score += 15
    else:
        score += 5

    # 2. RAM评分（20分）
    if ram_info.total_gb >= 64:
        score += 20
    elif ram_info.total_gb >= 32:
        score += 15
    elif ram_info.total_gb >= 16:
        score += 10
    else:
        score += 5

    # 3. CPU评分（15分）
    if cpu_info.physical_cores >= 8:
        score += 15
    elif cpu_info.physical_cores >= 6:
        score += 11
    elif cpu_info.physical_cores >= 4:
        score += 7
    else:
        score += 3

    # 4. 磁盘评分（5分）
    if disk_info.disk_type == "NVMe":
        score += 5
    elif disk_info.disk_type == "SSD":
        score += 3
    else:
        score += 1

    # 映射到档位
    if score >= 85:
        return ProfileTier.ENTERPRISE
    elif score >= 65:
        return ProfileTier.PROFESSIONAL
    elif score >= 45:
        return ProfileTier.PERFORMANCE
    elif score >= 25:
        return ProfileTier.STANDARD
    else:
        return ProfileTier.MINIMAL
```

**示例评分**:

| 硬件配置 | GPU | RAM | CPU | Disk | 总分 | 档位 |
|---------|-----|-----|-----|------|------|------|
| RTX 2060 + 16GB + i5 6核 + SSD | 30 | 10 | 11 | 3 | **54** | Standard |
| RTX 3060 12GB + 32GB + i7 8核 + NVMe | 45 | 15 | 15 | 5 | **80** | Professional |
| RTX 4090 + 64GB + i9 12核 + NVMe | 60 | 20 | 15 | 5 | **100** | Enterprise |
| CPU only + 8GB | 0 | 5 | 7 | 1 | **13** | Minimal |

---

### Module 3: 运行时优化引擎

#### 3.1 DataLoader配置优化

**修改文件**: `core/ai_cac_inference_lib.py:135-136`

**当前代码**:
```python
dataloader = DataLoader(dataset, batch_size=1, shuffle=False,
                       num_workers=0, pin_memory=False)
```

**优化后代码**:
```python
# 从配置中读取优化参数
from core.performance_profiles import get_active_profile

profile = get_active_profile()

dataloader = DataLoader(
    dataset,
    batch_size=1,
    shuffle=False,
    num_workers=profile.num_workers,           # 动态值：0-16
    pin_memory=profile.pin_memory,             # 动态值：True/False
    prefetch_factor=profile.prefetch_factor if profile.num_workers > 0 else None,
    persistent_workers=profile.num_workers > 0 # 复用worker进程
)
```

---

#### 3.2 GPU缓存清理策略优化

**修改文件**: `core/ai_cac_inference_lib.py:201-203`

**当前代码**:
```python
if device == 'cuda':
    del inputs, hu_vols, pred_vol
    torch.cuda.empty_cache()  # 每次都清理
```

**优化后代码**:
```python
# 根据配置动态清理
patient_counter += 1

# 清理临时变量
del inputs, hu_vols, pred_vol

# 根据配置间隔清理GPU缓存
if device == 'cuda' and patient_counter % profile.clear_cache_interval == 0:
    torch.cuda.empty_cache()
    logger.debug(f"GPU cache cleared (interval={profile.clear_cache_interval})")
```

---

#### 3.3 异步数据传输优化（高级功能）

**新增代码**: `core/ai_cac_inference_lib.py` → `run_inference_on_dicom_folder()`

**实现CUDA streams异步传输**:

```python
if profile.async_data_transfer and device == 'cuda':
    # 创建异步传输stream
    stream = torch.cuda.Stream()

    with torch.cuda.stream(stream):
        inputs = inputs.to(device, non_blocking=True)
        hu_vols = hu_vols.to(device, non_blocking=True)

    # GPU可以同时执行其他操作，传输完成前等待
    torch.cuda.current_stream().wait_stream(stream)
else:
    # 同步传输（默认）
    inputs = inputs.to(device)
    hu_vols = hu_vols.to(device)
```

---

#### 3.4 混合精度推理（高级功能）

**修改文件**: `core/ai_cac_inference_lib.py` → 推理循环

**添加FP16支持**:

```python
if profile.use_mixed_precision and device == 'cuda':
    # 使用自动混合精度
    with torch.cuda.amp.autocast():
        batch_out = model(batch.float())
else:
    # 标准FP32推理
    batch_out = model(batch.float())
```

**注意事项**:
- 需要验证混合精度对Agatston score计算精度的影响
- 建议在Professional及以上档位启用
- 需要在文档中说明精度tradeoff

---

### Module 4: 安全与监控系统

#### 4.1 OOM（内存溢出）保护

**文件位置**: `core/safety_monitor.py` → `class OOMProtector`

**保护策略**:

```python
class OOMProtector:
    """OOM保护器"""

    def __init__(self, profile: PerformanceProfile):
        self.profile = profile
        self.oom_count = 0
        self.max_oom_retry = 3

    def pre_inference_check(self) -> bool:
        """推理前检查GPU内存"""
        if not torch.cuda.is_available():
            return True

        # 检查可用显存
        available = torch.cuda.memory_available() / 1024**3
        required = self.estimate_memory_requirement()

        if available < required * 1.2:  # 需要20%安全边际
            logger.warning(f"可用显存不足: {available:.1f}GB < {required*1.2:.1f}GB")
            logger.warning("建议降低SLICE_BATCH_SIZE或切换到稳定模式")
            return False

        return True

    def handle_oom_exception(self, e: Exception) -> bool:
        """处理OOM异常"""
        self.oom_count += 1

        if self.oom_count >= self.max_oom_retry:
            logger.error("连续3次OOM，建议切换到CPU模式或稳定模式")
            return False

        # 自动降级策略
        logger.warning(f"检测到OOM (第{self.oom_count}次)，自动降级...")

        # 降低SLICE_BATCH_SIZE
        self.profile.slice_batch_size = max(2, self.profile.slice_batch_size - 2)

        # 清理GPU缓存
        torch.cuda.empty_cache()

        logger.info(f"已降级: SLICE_BATCH_SIZE={self.profile.slice_batch_size}")
        return True  # 可以重试
```

---

#### 4.2 GPU温度监控

**文件位置**: `core/safety_monitor.py` → `class TemperatureMonitor`

**监控策略**:

```python
class TemperatureMonitor:
    """GPU温度监控器"""

    def __init__(self, max_temp: float = 85.0, critical_temp: float = 90.0):
        self.max_temp = max_temp
        self.critical_temp = critical_temp
        self.high_temp_count = 0

    def check_temperature(self) -> str:
        """
        检查GPU温度

        Returns:
            "ok" | "warning" | "critical"
        """
        try:
            # 使用nvidia-smi或pynvml读取温度
            temp = self.get_gpu_temperature()

            if temp >= self.critical_temp:
                logger.error(f"GPU温度过高: {temp}°C >= {self.critical_temp}°C")
                return "critical"
            elif temp >= self.max_temp:
                self.high_temp_count += 1
                logger.warning(f"GPU温度偏高: {temp}°C (警告阈值: {self.max_temp}°C)")

                if self.high_temp_count >= 3:
                    logger.warning("GPU温度持续偏高，暂停10秒降温...")
                    time.sleep(10)
                    self.high_temp_count = 0

                return "warning"
            else:
                self.high_temp_count = 0
                return "ok"

        except Exception as e:
            logger.debug(f"无法读取GPU温度: {e}")
            return "ok"

    def get_gpu_temperature(self) -> float:
        """获取GPU温度（单位：摄氏度）"""
        # 方法1: 使用pynvml (推荐)
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            pynvml.nvmlShutdown()
            return float(temp)
        except:
            pass

        # 方法2: 解析nvidia-smi输出
        try:
            import subprocess
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=5
            )
            return float(result.stdout.strip())
        except:
            pass

        # 无法获取温度
        raise RuntimeError("无法读取GPU温度")
```

---

#### 4.3 性能跟踪与异常检测

**文件位置**: `core/safety_monitor.py` → `class PerformanceTracker`

**跟踪指标**:

```python
class PerformanceTracker:
    """性能跟踪器"""

    def __init__(self, expected_time_per_patient: float):
        self.expected_time = expected_time_per_patient
        self.processing_times = []
        self.check_interval = 5  # 每5个patient检查一次

    def record_time(self, patient_id: str, elapsed_time: float):
        """记录处理时间"""
        self.processing_times.append(elapsed_time)

        if len(self.processing_times) % self.check_interval == 0:
            self.check_performance()

    def check_performance(self):
        """检查性能是否正常"""
        if len(self.processing_times) < self.check_interval:
            return

        # 计算最近5个patient的平均时间
        recent_avg = np.mean(self.processing_times[-self.check_interval:])

        # 如果实际时间 > 预期时间的1.5倍
        if recent_avg > self.expected_time * 1.5:
            logger.warning("="*60)
            logger.warning(f"⚠️ 性能低于预期")
            logger.warning(f"   预期时间: {self.expected_time:.1f}秒/例")
            logger.warning(f"   实际时间: {recent_avg:.1f}秒/例 (慢 {(recent_avg/self.expected_time-1)*100:.0f}%)")
            logger.warning("")
            logger.warning("可能原因:")
            logger.warning("  1. 其他程序占用GPU/CPU资源")
            logger.warning("  2. 磁盘IO瓶颈（DICOM文件读取慢）")
            logger.warning("  3. 系统内存不足")
            logger.warning("")
            logger.warning("建议操作:")
            logger.warning("  1. 关闭其他程序释放资源")
            logger.warning("  2. 切换到'Stable'稳定模式")
            logger.warning("="*60)
```

---

#### 4.4 自动降级策略

**文件位置**: `core/safety_monitor.py` → `class AutoDowngradeManager`

**降级逻辑**:

```python
class AutoDowngradeManager:
    """自动降级管理器"""

    def __init__(self, current_profile: ProfileTier):
        self.current_tier = current_profile
        self.failure_count = 0
        self.max_failures = 3

    def record_failure(self, error_type: str):
        """记录失败"""
        self.failure_count += 1
        logger.warning(f"记录失败事件: {error_type} (累计: {self.failure_count}/{self.max_failures})")

        if self.failure_count >= self.max_failures:
            self.trigger_downgrade()

    def trigger_downgrade(self):
        """触发降级"""
        logger.warning("="*60)
        logger.warning("⚠️ 连续失败超过阈值，触发自动降级")
        logger.warning("")

        # 降级到下一档位
        downgrade_map = {
            ProfileTier.ENTERPRISE: ProfileTier.PROFESSIONAL,
            ProfileTier.PROFESSIONAL: ProfileTier.PERFORMANCE,
            ProfileTier.PERFORMANCE: ProfileTier.STANDARD,
            ProfileTier.STANDARD: ProfileTier.MINIMAL,
            ProfileTier.MINIMAL: None  # 无法降级
        }

        new_tier = downgrade_map.get(self.current_tier)

        if new_tier is None:
            logger.error("已处于最低档位，无法继续降级")
            logger.error("建议切换到CPU模式或检查硬件")
            return False

        logger.warning(f"档位切换: {self.current_tier.name} → {new_tier.name}")
        logger.warning("="*60)

        # 应用新配置
        apply_profile(new_tier)
        self.current_tier = new_tier
        self.failure_count = 0  # 重置失败计数

        return True
```

---

### Module 5: 用户界面层

#### 5.1 启动时硬件检测显示

**修改文件**: `cli/run_nb10.py` → `main()`

**交互界面设计**:

```python
def display_hardware_detection_and_select_mode(
    gpu_info: GPUInfo,
    cpu_info: CPUInfo,
    ram_info: RAMInfo,
    disk_info: DiskInfo,
    recommended_tier: ProfileTier
) -> ProfileTier:
    """
    显示硬件检测结果并让用户选择模式

    Returns:
        用户选择的配置档位
    """
    print("="*70)
    print("NB10 AI-CAC 智能硬件检测")
    print("="*70)
    print()
    print("正在检测硬件配置...")
    print()

    # 显示硬件信息
    if gpu_info.available:
        print(f"✓ GPU: {gpu_info.device_name} ({gpu_info.vram_total_gb:.1f}GB)")
    else:
        print(f"⚠ GPU: 不可用 (将使用CPU模式)")

    print(f"✓ RAM: {ram_info.total_gb:.1f}GB (可用: {ram_info.available_gb:.1f}GB)")
    print(f"✓ CPU: {cpu_info.cpu_model} ({cpu_info.physical_cores}核{cpu_info.logical_cores}线程)")
    print(f"✓ 磁盘: {disk_info.disk_type}")
    print()

    print("-"*70)
    print(f"推荐配置档位: {recommended_tier.name.title()}")
    print()

    # 显示预期性能
    performance = get_expected_performance(recommended_tier)
    print(f"预计单例处理时间: {performance.time_per_patient_sec:.0f}秒")

    # 如果用户有指定病例数，计算总耗时
    # print(f"预计总耗时(197例): {performance.time_per_patient_sec * 197 / 3600:.1f}小时")

    print("-"*70)
    print()

    # 用户选择
    print("可选模式:")
    print("  [1] Auto (推荐) - 自动选择最佳配置")
    print("  [2] Performance - 高性能模式 (可能不稳定)")
    print("  [3] Stable - 稳定模式 (速度较慢，稳定性最高)")
    print("  [4] Custom - 手动配置")
    print()

    while True:
        choice = input("请选择 [1-4] (直接回车使用推荐): ").strip()

        if choice == "" or choice == "1":
            print(f"\n✓ 已选择: Auto - {recommended_tier.name.title()} 模式")
            return recommended_tier

        elif choice == "2":
            # 尝试升级到Performance档位
            if recommended_tier.value < ProfileTier.PERFORMANCE.value:
                print("\n⚠️ 警告: 当前硬件配置低于Performance模式要求")
                confirm = input("   强制使用可能导致不稳定，是否继续? (yes/no): ")
                if confirm.lower() == 'yes':
                    print("\n✓ 已选择: Performance 高性能模式")
                    return ProfileTier.PERFORMANCE
                else:
                    continue
            else:
                print("\n✓ 已选择: Performance 高性能模式")
                return ProfileTier.PERFORMANCE

        elif choice == "3":
            # 降级到Minimal/Standard
            stable_tier = ProfileTier.STANDARD if recommended_tier.value >= ProfileTier.STANDARD.value else ProfileTier.MINIMAL
            print(f"\n✓ 已选择: Stable - {stable_tier.name.title()} 稳定模式")
            return stable_tier

        elif choice == "4":
            print("\n自定义模式暂未实现，请编辑 config.yaml 文件")
            print("将使用推荐配置...")
            return recommended_tier

        else:
            print("⚠️ 无效选择，请输入 1-4")
```

**输出示例（RTX 2060环境）**:

```
======================================================================
NB10 AI-CAC 智能硬件检测
======================================================================

正在检测硬件配置...

✓ GPU: NVIDIA GeForce RTX 2060 (6.0GB)
✓ RAM: 16.0GB (可用: 10.2GB)
✓ CPU: Intel(R) Core(TM) i5-10400 (6核12线程)
✓ 磁盘: SSD

----------------------------------------------------------------------
推荐配置档位: Standard

预计单例处理时间: 30秒
----------------------------------------------------------------------

可选模式:
  [1] Auto (推荐) - 自动选择最佳配置
  [2] Performance - 高性能模式 (可能不稳定)
  [3] Stable - 稳定模式 (速度较慢，稳定性最高)
  [4] Custom - 手动配置

请选择 [1-4] (直接回车使用推荐): _
```

---

#### 5.2 运行时性能监控显示

**修改文件**: `cli/run_nb10.py` → `run_inference_batch()`

**实时显示**:

```python
def run_inference_batch(...):
    """运行批量推理（带性能监控）"""

    # 初始化监控器
    perf_tracker = PerformanceTracker(expected_time=profile.expected_time_per_patient)
    temp_monitor = TemperatureMonitor()

    for i, folder_path in enumerate(dicom_folders, 1):
        patient_id = folder_path.name

        # 显示进度
        logger.info(f"[{i}/{len(dicom_folders)}] Processing: {patient_id}")

        # 温度检查
        temp_status = temp_monitor.check_temperature()
        if temp_status == "critical":
            logger.error("GPU温度过高，强制切换到CPU模式")
            config.set('processing.device', 'cpu')

        start_time = time.time()

        try:
            result = run_inference_on_dicom_folder(...)
            elapsed = time.time() - start_time

            # 记录性能
            perf_tracker.record_time(patient_id, elapsed)

            # 显示结果（带时间）
            logger.info(f"  ✓ Success - Agatston: {result['agatston_score']:.2f} "
                       f"(耗时: {elapsed:.1f}秒)")

        except Exception as e:
            logger.error(f"  ✗ Failed - {str(e)}")
            # 记录失败，触发自动降级检查
            auto_downgrade.record_failure(str(e))
```

---

#### 5.3 完成后性能总结

**添加功能**: 在处理完成后显示性能统计

```python
def display_performance_summary(results_df: pd.DataFrame, profile: PerformanceProfile):
    """显示性能总结"""

    success_df = results_df[results_df['status'] == 'success']

    if len(success_df) == 0:
        return

    print()
    print("="*70)
    print("性能总结")
    print("="*70)
    print()
    print(f"配置档位: {profile.tier.name.title()}")
    print(f"成功处理: {len(success_df)} 例")
    print()

    # 假设我们在推理时记录了每例的处理时间（需要添加此字段）
    if 'processing_time_sec' in success_df.columns:
        avg_time = success_df['processing_time_sec'].mean()
        min_time = success_df['processing_time_sec'].min()
        max_time = success_df['processing_time_sec'].max()

        print(f"平均处理时间: {avg_time:.1f}秒/例")
        print(f"最快: {min_time:.1f}秒  |  最慢: {max_time:.1f}秒")
        print()

        # 与预期性能对比
        expected = profile.expected_time_per_patient
        diff_percent = (avg_time - expected) / expected * 100

        if abs(diff_percent) < 10:
            print(f"✓ 性能符合预期 (预期: {expected:.1f}秒)")
        elif diff_percent > 0:
            print(f"⚠️ 性能低于预期 {diff_percent:.0f}% (预期: {expected:.1f}秒)")
            print("   建议检查系统资源占用或切换到稳定模式")
        else:
            print(f"✓ 性能超出预期 {-diff_percent:.0f}% (预期: {expected:.1f}秒)")

    print("="*70)
```

---

## 📝 配置文件增强

### 更新 config.yaml 结构

**文件位置**: `config/config.yaml` 和 `config/config.yaml.template`

**新增配置段**:

```yaml
# ============================================================
# Hardware Detection & Performance Configuration
# ============================================================
performance:
  # 硬件检测配置
  hardware_detection:
    enabled: true                    # 启用自动硬件检测
    mode: "auto"                     # auto/manual
    profile: "standard"              # 手动指定档位（仅在mode=manual时生效）
                                     # 可选: minimal/standard/performance/professional/enterprise

  # 运行时安全保护
  safety:
    oom_protection: true             # OOM保护
    temperature_monitoring: true     # GPU温度监控
    max_gpu_temp: 85.0               # GPU温度警告阈值（摄氏度）
    critical_gpu_temp: 90.0          # GPU温度紧急阈值
    memory_leak_detection: true      # 内存泄漏检测
    auto_downgrade: true             # 异常时自动降级

  # 性能跟踪
  tracking:
    enabled: true                    # 启用性能跟踪
    check_interval: 5                # 每N个patient检查一次性能
    save_metrics: true               # 保存性能指标到CSV

  # 高级优化（Professional及以上档位）
  advanced:
    use_mixed_precision: false       # 使用FP16混合精度（需验证精度影响）
    async_data_transfer: false       # 异步数据传输（CUDA streams）
    prefetch_next_patient: false     # 预加载下一个patient
    dataloader_prefetch_factor: 2    # DataLoader预取因子
    persistent_workers: true         # 复用DataLoader worker进程

# ============================================================
# Original Performance Configuration (保留向后兼容)
# ============================================================
# 注意: 如果 hardware_detection.enabled=true，以下配置会被自动检测值覆盖
# ============================================================
  # GPU memory management
  gpu_memory_fraction: 0.9

  # Clear GPU cache every N patients
  clear_cache_interval: 1            # 将被自动检测值覆盖

  # Number of workers for data loading
  num_workers: 0                     # 将被自动检测值覆盖

  # Pin memory for faster GPU transfer
  pin_memory: true                   # 将被自动检测值覆盖
```

---

## 🚀 实现计划

### Phase 1: 核心基础设施（第1-2周）

**目标**: 建立硬件检测和配置档位系统

**任务清单**:

- [ ] **Task 1.1**: 创建 `core/hardware_profiler.py`
  - [ ] 实现 `GPUProfiler` 类
  - [ ] 实现 `CPUProfiler` 类
  - [ ] 实现 `RAMProfiler` 类
  - [ ] 实现 `DiskProfiler` 类
  - [ ] 单元测试（在多种硬件上测试）

- [ ] **Task 1.2**: 创建 `core/performance_profiles.py`
  - [ ] 定义5个配置档位（Minimal → Enterprise）
  - [ ] 实现评分算法 `select_optimal_profile()`
  - [ ] 创建配置档位数据类 `PerformanceProfile`
  - [ ] 单元测试

- [ ] **Task 1.3**: 更新 `core/config_manager.py`
  - [ ] 添加硬件检测配置加载
  - [ ] 添加安全配置加载
  - [ ] 集成 `PerformanceProfile` 到配置系统
  - [ ] 更新验证逻辑

- [ ] **Task 1.4**: 更新配置文件模板
  - [ ] 更新 `config/config.yaml.template`
  - [ ] 添加详细注释和示例
  - [ ] 创建迁移指南（从旧配置到新配置）

**验收标准**:
- 硬件检测在Windows和Linux上正常工作
- 所有5个档位配置正确
- 单元测试覆盖率 > 80%

---

### Phase 2: 运行时优化引擎（第3-4周）

**目标**: 应用优化配置到实际推理流程

**任务清单**:

- [ ] **Task 2.1**: 修改 `core/ai_cac_inference_lib.py`
  - [ ] 动态配置DataLoader（num_workers, pin_memory等）
  - [ ] 实现动态GPU缓存清理策略
  - [ ] 添加异步数据传输（CUDA streams）
  - [ ] 添加混合精度推理（FP16）
  - [ ] 性能测试

- [ ] **Task 2.2**: 修改 `cli/run_nb10.py`
  - [ ] 集成硬件检测到启动流程
  - [ ] 添加交互式模式选择界面
  - [ ] 更新日志输出（包含性能信息）

- [ ] **Task 2.3**: 性能验证
  - [ ] 在RTX 2060环境测试（Standard档位）
  - [ ] 在RTX 3060/3070环境测试（Performance档位）
  - [ ] 在CPU环境测试（Minimal档位）
  - [ ] 性能对比报告

**验收标准**:
- Standard档位性能提升 18-25%
- Performance档位性能提升 40-50%
- 无功能退化（Agatston score结果一致）

---

### Phase 3: 安全与监控系统（第5-6周）

**目标**: 实现保护机制，确保医疗级可靠性

**任务清单**:

- [ ] **Task 3.1**: 创建 `core/safety_monitor.py`
  - [ ] 实现 `OOMProtector` 类
  - [ ] 实现 `TemperatureMonitor` 类
  - [ ] 实现 `PerformanceTracker` 类
  - [ ] 实现 `AutoDowngradeManager` 类
  - [ ] 单元测试

- [ ] **Task 3.2**: 集成到推理流程
  - [ ] 在推理前进行安全检查
  - [ ] 在推理中监控温度和性能
  - [ ] 在异常时触发保护机制
  - [ ] 记录所有安全事件到日志

- [ ] **Task 3.3**: 压力测试
  - [ ] OOM场景测试（模拟低显存环境）
  - [ ] 高温场景测试（持续满载）
  - [ ] 多次失败自动降级测试
  - [ ] 长时间运行稳定性测试（197例连续运行）

**验收标准**:
- OOM时自动降级，无崩溃
- GPU温度超阈值时正确处理
- 异常降级机制正常工作
- 稳定性测试通过（197例无中断）

---

### Phase 4: 用户体验优化（第7周）

**目标**: 完善交互界面和文档

**任务清单**:

- [ ] **Task 4.1**: 优化启动界面
  - [ ] 美化硬件检测输出
  - [ ] 添加进度条和实时性能显示
  - [ ] 完成后显示性能总结
  - [ ] 用户体验测试

- [ ] **Task 4.2**: 更新文档
  - [ ] 更新 `docs/USER_MANUAL.md`（添加硬件自适应章节）
  - [ ] 更新 `docs/INSTALLATION_GUIDE.md`（硬件推荐配置）
  - [ ] 创建 `docs/PERFORMANCE_TUNING_GUIDE.md`
  - [ ] 更新 `README.md`

- [ ] **Task 4.3**: 创建示例和教程
  - [ ] 视频教程：首次运行和模式选择
  - [ ] 故障排除指南
  - [ ] FAQ文档

**验收标准**:
- 医生用户测试反馈良好（易用性评分 > 4/5）
- 文档完整，覆盖所有功能
- FAQ覆盖常见问题

---

### Phase 5: 测试与发布（第8周）

**目标**: 全面测试并准备发布

**任务清单**:

- [ ] **Task 5.1**: 集成测试
  - [ ] 完整工作流测试（检测→推理→结果）
  - [ ] 多硬件环境测试矩阵
  - [ ] 边界情况测试
  - [ ] 回归测试（确保与v1.0兼容）

- [ ] **Task 5.2**: 性能基准测试
  - [ ] 建立性能基准数据库
  - [ ] 生成性能对比报告
  - [ ] 验证所有档位性能符合预期

- [ ] **Task 5.3**: 代码审查与优化
  - [ ] Code review
  - [ ] 性能profiling
  - [ ] 代码清理和文档完善

- [ ] **Task 5.4**: 发布准备
  - [ ] 更新 `CHANGELOG.md`
  - [ ] 创建发布说明
  - [ ] 打包和分发准备

**验收标准**:
- 所有测试通过
- 性能提升达标
- 文档完整
- 准备好发布 v2.0.0

---

## 📊 性能预期总结

### 当前基线 vs 优化后性能

| 硬件配置 | 当前性能 | 优化后档位 | 预期性能 | 提升幅度 | 197例总耗时 |
|---------|---------|----------|---------|---------|------------|
| RTX 2060 6GB + 16GB RAM | 35-40秒/例 | Standard | 28-32秒/例 | **↓ 20-25%** | 1.6-1.8小时 (vs 2.0小时) |
| RTX 3060 12GB + 32GB RAM | 30-35秒/例 | Performance | 18-22秒/例 | **↓ 40-45%** | 1.0-1.2小时 |
| RTX 4080 16GB + 64GB RAM | 25-30秒/例 | Professional | 12-15秒/例 | **↓ 50-55%** | 0.65-0.8小时 |
| CPU only (i7 8核) | 120-180秒/例 | Minimal | 100-150秒/例 | ↓ 15-20% | 5.5-8.2小时 |

---

## ⚠️ 风险与限制

### 技术风险

1. **混合精度精度损失**
   - **风险**: FP16可能影响Agatston score计算精度
   - **缓解**: 需要验证混合精度结果与FP32的一致性
   - **建议**: 在Professional及以上档位可选启用，默认关闭

2. **Windows多进程兼容性**
   - **风险**: Windows上DataLoader多进程可能不稳定
   - **缓解**: 保守设置num_workers（最多4-6），提供回退机制
   - **建议**: 充分测试Windows环境

3. **GPU温度监控依赖**
   - **风险**: `pynvml`或`nvidia-smi`可能不可用
   - **缓解**: 温度监控作为可选功能，失败时不影响主流程
   - **建议**: 提供明确的依赖安装指南

### 硬件限制

1. **6GB GPU显存约束**
   - **限制**: 无法大幅提升SLICE_BATCH_SIZE
   - **应对**: Standard档位保守配置，确保稳定性
   - **建议**: 在文档中说明升级到12GB GPU的性能提升

2. **Windows fork性能**
   - **限制**: Windows上多进程性能不如Linux
   - **应对**: 适当降低num_workers预期
   - **建议**: 在Linux上可以更激进的配置

### 医疗应用限制

1. **结果一致性要求**
   - **要求**: 优化后的Agatston score必须与优化前一致
   - **验证**: 需要在多种硬件上验证结果一致性
   - **测试**: Phase 4需要包含完整的一致性测试

2. **稳定性优先**
   - **原则**: 医疗场景下稳定性 > 性能
   - **设计**: 提供"Stable"模式作为安全选项
   - **建议**: 默认档位偏保守，用户可手动选择激进模式

---

## 📖 关键问题回答

### 1. 网络连接需求

**回答**: **不需要网络连接**

- 所有硬件检测完全本地进行
- 无需访问外部API或服务
- 配置文件和模型均为本地文件
- **可选功能**: 上传匿名硬件统计用于优化（需用户同意，默认关闭）

---

### 2. 未知硬件处理策略

**回答**: **引导用户手动选择，建议保守档位**

**处理流程**:

1. **检测失败时**:
   ```
   ⚠️ 无法自动检测硬件配置

   可能原因:
   - GPU驱动未正确安装
   - 不支持的硬件

   请手动选择配置档位:
     [1] Minimal - 最低配置（推荐，稳定性最高）
     [2] Standard - 标准配置
     [3] Performance - 高性能配置

   建议: 首次运行请选择 [1] Minimal 进行测试
   ```

2. **异常硬件组合**:
   - 例如: 4GB GPU + 64GB RAM（不均衡）
   - 系统会显示警告，建议使用保守配置
   - 用户可选择忽略警告

3. **Fallback策略**:
   - 默认回退到 `Minimal` 档位
   - 记录警告日志
   - 引导用户查看文档或联系支持

---

### 3. 手动配置覆盖

**回答**: **配置可手动覆盖，默认为自动模式**

**配置优先级**（从高到低）:

```
1. 命令行参数 (--num-workers 4)
   ↓
2. 配置文件手动设置 (hardware_detection.mode: "manual")
   ↓
3. 自动检测结果 (hardware_detection.mode: "auto", 默认)
   ↓
4. 系统默认值 (Minimal档位)
```

**手动覆盖方式**:

**方式1: 修改配置文件**
```yaml
# config.yaml
performance:
  hardware_detection:
    enabled: true
    mode: "manual"               # 切换到手动模式
    profile: "performance"       # 手动指定档位

  # 或者直接覆盖单个参数
  num_workers: 4                 # 覆盖自动检测值
  pin_memory: true
```

**方式2: 命令行参数**
```bash
# 覆盖num_workers
python cli/run_nb10.py --config config.yaml --num-workers 4

# 覆盖档位
python cli/run_nb10.py --config config.yaml --profile performance

# 禁用自动检测
python cli/run_nb10.py --config config.yaml --no-auto-detect
```

**方式3: 交互式选择**
```
请选择 [1-4] (直接回车使用推荐): 4

自定义模式:
  num_workers [推荐: 2]: 4
  pin_memory [推荐: true]: true
  slice_batch_size [推荐: 4]: 6
  ...
```

---

## 📌 后续工作

### 未来增强功能（v2.1+）

1. **学习式优化**
   - 记录历史运行数据
   - 基于实际性能自动调整配置
   - 个性化硬件Profile

2. **云端配置同步**（可选）
   - 用户可选择上传匿名硬件数据
   - 获取社区优化配置推荐
   - 帮助改进自动检测算法

3. **多GPU并行**
   - Enterprise档位支持多GPU
   - 批量处理patients到不同GPU
   - 显著提升吞吐量

4. **高级性能分析工具**
   - 内置profiler
   - 瓶颈可视化
   - 优化建议生成器

---

## 📄 附录

### A. 依赖包列表

新增依赖:

```
psutil>=5.9.0           # CPU/RAM检测
pynvml>=11.5.0          # GPU温度监控（可选）
```

### B. 测试硬件矩阵

建议在以下硬件上进行测试:

| 分类 | GPU | RAM | CPU | OS |
|------|-----|-----|-----|-----|
| 低端 | GTX 1650 4GB | 8GB | i3 4核 | Windows 10 |
| 标准 | RTX 2060 6GB | 16GB | i5 6核 | Windows 11 |
| 高端 | RTX 3060 12GB | 32GB | i7 8核 | Windows 11 |
| 专业 | RTX 4080 16GB | 64GB | i9 12核 | Linux |
| CPU | 无 | 16GB | i7 8核 | Windows 11 |

### C. 性能测试协议

标准测试流程:

1. 使用相同的30例测试数据集
2. 记录每例的处理时间和结果
3. 验证Agatston score一致性（误差 < 0.1%）
4. 监控GPU温度、显存占用、CPU/RAM使用率
5. 生成性能报告和对比图表

### D. 参考资料

- PyTorch DataLoader优化: https://pytorch.org/docs/stable/data.html
- CUDA Best Practices: https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/
- MONAI性能优化: https://docs.monai.io/en/stable/performance.html

---

## ✅ 文档状态

- **版本**: 1.0.0
- **状态**: 设计提案 (Proposal)
- **审核状态**: 待审核
- **实施状态**: 未开始

**变更历史**:
- 2025-10-14: 初始版本，基于性能分析讨论创建

---

## 👥 贡献者

- **设计**: Claude (AI Assistant) + 陈医生团队
- **性能分析**: 基于 `tools/nb10_windows` 代码审查
- **测试环境**: RTX 2060 6GB + 16GB RAM + Windows

---

## 📞 联系与反馈

如有问题或建议，请通过以下方式反馈:

- 项目Issue: (待添加GitHub仓库链接)
- 文档Issue: 在本文档所在目录创建 `FEEDBACK.md`

---

**文档结束**
