"""
硬件检测模块 - 共享版本
Hardware Detection Module - Shared Version

支持多环境：Windows/Linux/Colab
用于自动检测GPU、CPU、内存等硬件信息，为性能优化提供基础数据。

提升自: tools/nb10_windows/core/hardware_profiler.py
扩展: 增加CPU缓存检测、Colab环境支持、更详细的CPU信息
"""

import torch
import psutil
import platform
import logging
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class GPUInfo:
    """GPU信息"""
    available: bool
    device_name: str
    vram_total_gb: float
    vram_available_gb: float
    cuda_version: Optional[str] = None
    device_count: int = 0
    compute_capability: Optional[tuple] = None  # 新增：计算能力

    def __post_init__(self):
        if self.available and self.cuda_version is None:
            try:
                self.cuda_version = torch.version.cuda
            except:
                self.cuda_version = "Unknown"


@dataclass
class CPUInfo:
    """CPU信息（增强版，医院CPU优化关键）"""
    physical_cores: int
    logical_cores: int
    cpu_model: str
    cpu_freq_mhz: Optional[float] = None
    cpu_freq_min_mhz: Optional[float] = None  # 新增：最低频率
    cpu_freq_max_mhz: Optional[float] = None  # 新增：最高频率
    cache_size_mb: Optional[float] = None     # 新增：缓存大小（重要）
    architecture: Optional[str] = None         # 新增：架构（x86_64/aarch64）

    def __post_init__(self):
        # 检测CPU频率
        if self.cpu_freq_mhz is None:
            try:
                freq = psutil.cpu_freq()
                if freq:
                    self.cpu_freq_mhz = freq.current
                    self.cpu_freq_min_mhz = freq.min
                    self.cpu_freq_max_mhz = freq.max
            except:
                pass

        # 检测架构
        if self.architecture is None:
            self.architecture = platform.machine()

    @property
    def is_high_performance(self) -> bool:
        """是否高性能CPU（8核+）"""
        return self.physical_cores >= 8

    @property
    def recommended_workers(self) -> int:
        """推荐的DataLoader worker数"""
        # 医院CPU优化关键参数
        if self.physical_cores <= 2:
            return 0  # Minimal档位：单线程
        elif self.physical_cores <= 4:
            return 2  # Standard档位低端
        elif self.physical_cores <= 8:
            return 4  # Standard档位标准
        elif self.physical_cores <= 16:
            return 8  # Performance档位
        else:
            return 16  # Professional档位


@dataclass
class RAMInfo:
    """内存信息"""
    total_gb: float
    available_gb: float
    percent_used: float

    @property
    def is_sufficient(self) -> bool:
        """是否有足够内存（建议至少6GB可用，理想8GB+）"""
        # 基于NB10实测: 3GB即可获得17.2%提升，设置6GB为安全阈值
        return self.available_gb >= 6.0

    @property
    def recommended_batch_size(self) -> int:
        """推荐的batch size"""
        # 基于可用内存推荐batch size（医院CPU优化关键）
        if self.available_gb < 4:
            return 1
        elif self.available_gb < 8:
            return 2
        elif self.available_gb < 16:
            return 4
        else:
            return 8


@dataclass
class EnvironmentInfo:
    """环境信息（新增模块）"""
    runtime_type: str  # 'windows' / 'linux' / 'colab' / 'wsl'
    is_colab: bool
    is_wsl: bool
    os_name: str
    os_version: str

    @property
    def is_hospital_environment(self) -> bool:
        """是否可能是医院环境（Windows且非Colab）"""
        return self.runtime_type == 'windows' and not self.is_colab


@dataclass
class HardwareInfo:
    """完整硬件信息"""
    gpu: GPUInfo
    cpu: CPUInfo
    ram: RAMInfo
    environment: EnvironmentInfo  # 新增
    platform: str
    python_version: str

    @property
    def recommended_device(self) -> str:
        """推荐的计算设备"""
        return "cuda" if self.gpu.available else "cpu"

    @property
    def performance_tier(self) -> str:
        """
        性能档位（5档）
        Minimal → Standard → Performance → Professional → Enterprise
        """
        if self.gpu.available:
            if self.gpu.vram_total_gb >= 16:
                return "Enterprise"
            elif self.gpu.vram_total_gb >= 6:
                return "Professional"
            else:
                return "Performance"
        else:
            # 纯CPU档位（医院环境关键）
            if self.cpu.physical_cores >= 16 and self.ram.total_gb >= 32:
                return "Performance"
            elif self.cpu.physical_cores >= 8 and self.ram.total_gb >= 16:
                return "Standard"
            else:
                return "Minimal"


def detect_environment() -> EnvironmentInfo:
    """
    检测运行环境（新增函数）

    支持检测:
    - Google Colab
    - WSL (Windows Subsystem for Linux)
    - 原生Windows
    - 原生Linux
    """
    os_name = platform.system()
    os_version = platform.release()

    # 检测Colab
    is_colab = False
    try:
        import google.colab
        is_colab = True
    except:
        pass

    # 检测WSL
    is_wsl = False
    if os_name == "Linux":
        try:
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
                is_wsl = 'microsoft' in version_info or 'wsl' in version_info
        except:
            pass

    # 确定运行时类型
    if is_colab:
        runtime_type = 'colab'
    elif is_wsl:
        runtime_type = 'wsl'
    elif os_name == "Windows":
        runtime_type = 'windows'
    elif os_name == "Linux":
        runtime_type = 'linux'
    elif os_name == "Darwin":
        runtime_type = 'macos'
    else:
        runtime_type = 'unknown'

    logger.info(f"检测到运行环境: {runtime_type}")

    return EnvironmentInfo(
        runtime_type=runtime_type,
        is_colab=is_colab,
        is_wsl=is_wsl,
        os_name=os_name,
        os_version=os_version
    )


def detect_gpu() -> GPUInfo:
    """检测GPU信息"""
    if not torch.cuda.is_available():
        logger.info("CUDA不可用，将使用CPU模式")
        return GPUInfo(
            available=False,
            device_name="CPU",
            vram_total_gb=0.0,
            vram_available_gb=0.0,
            device_count=0
        )

    try:
        device_count = torch.cuda.device_count()
        device_name = torch.cuda.get_device_name(0)
        props = torch.cuda.get_device_properties(0)
        vram_total_gb = props.total_memory / 1024**3

        # 计算能力（用于判断GPU性能）
        compute_capability = (props.major, props.minor)

        # 计算可用显存
        torch.cuda.empty_cache()
        vram_allocated = torch.cuda.memory_allocated(0) / 1024**3
        vram_available_gb = vram_total_gb - vram_allocated

        logger.info(f"检测到GPU: {device_name} ({vram_total_gb:.1f}GB VRAM)")

        return GPUInfo(
            available=True,
            device_name=device_name,
            vram_total_gb=vram_total_gb,
            vram_available_gb=vram_available_gb,
            device_count=device_count,
            compute_capability=compute_capability
        )

    except Exception as e:
        logger.warning(f"GPU检测失败: {e}")
        return GPUInfo(
            available=False,
            device_name="CPU",
            vram_total_gb=0.0,
            vram_available_gb=0.0,
            device_count=0
        )


def detect_cpu() -> CPUInfo:
    """检测CPU信息（增强版）"""
    try:
        physical_cores = psutil.cpu_count(logical=False) or 1
        logical_cores = psutil.cpu_count(logical=True) or 1

        # 获取CPU型号
        cpu_model = platform.processor()
        if not cpu_model or cpu_model.strip() == "":
            # 备用方法
            import subprocess
            try:
                if platform.system() == "Windows":
                    result = subprocess.run(
                        ["wmic", "cpu", "get", "name"],
                        capture_output=True,
                        text=True
                    )
                    lines = result.stdout.strip().split('\n')
                    cpu_model = lines[1].strip() if len(lines) > 1 else "Unknown CPU"
                elif platform.system() == "Linux":
                    with open('/proc/cpuinfo', 'r') as f:
                        for line in f:
                            if 'model name' in line:
                                cpu_model = line.split(':')[1].strip()
                                break
                else:
                    cpu_model = "Unknown CPU"
            except:
                cpu_model = "Unknown CPU"

        # 尝试获取CPU缓存大小（Linux）
        cache_size_mb = None
        try:
            if platform.system() == "Linux":
                cache_info = Path("/sys/devices/system/cpu/cpu0/cache")
                if cache_info.exists():
                    # 读取L3缓存（最大缓存层级）
                    for cache_dir in sorted(cache_info.glob("index*"), reverse=True):
                        size_file = cache_dir / "size"
                        if size_file.exists():
                            size_str = size_file.read_text().strip()
                            # 解析如 "8192K" → 8.0MB
                            if 'K' in size_str:
                                cache_size_mb = int(size_str.replace('K', '')) / 1024
                                break
        except:
            pass

        logger.info(f"检测到CPU: {physical_cores}核 ({logical_cores}线程)")

        return CPUInfo(
            physical_cores=physical_cores,
            logical_cores=logical_cores,
            cpu_model=cpu_model,
            cache_size_mb=cache_size_mb
        )

    except Exception as e:
        logger.warning(f"CPU检测失败: {e}")
        return CPUInfo(
            physical_cores=1,
            logical_cores=1,
            cpu_model="Unknown CPU"
        )


def detect_ram() -> RAMInfo:
    """检测内存信息"""
    try:
        mem = psutil.virtual_memory()
        total_gb = mem.total / 1024**3
        available_gb = mem.available / 1024**3
        percent_used = mem.percent

        logger.info(f"检测到内存: {total_gb:.1f}GB 总量, {available_gb:.1f}GB 可用 ({100-percent_used:.1f}% 空闲)")

        return RAMInfo(
            total_gb=total_gb,
            available_gb=available_gb,
            percent_used=percent_used
        )

    except Exception as e:
        logger.warning(f"内存检测失败: {e}")
        return RAMInfo(
            total_gb=0.0,
            available_gb=0.0,
            percent_used=100.0
        )


def detect_hardware() -> HardwareInfo:
    """
    检测完整硬件信息（增强版）

    Returns:
        HardwareInfo: 包含GPU、CPU、内存、环境等完整信息

    Example:
        >>> hw = detect_hardware()
        >>> print(f"环境: {hw.environment.runtime_type}")
        >>> print(f"GPU: {hw.gpu.device_name}, VRAM: {hw.gpu.vram_total_gb:.1f}GB")
        >>> print(f"CPU: {hw.cpu.physical_cores}核")
        >>> print(f"RAM: {hw.ram.total_gb:.1f}GB")
        >>> print(f"性能档位: {hw.performance_tier}")
        >>> print(f"推荐设备: {hw.recommended_device}")
    """
    logger.info("="*70)
    logger.info("正在检测硬件配置...")
    logger.info("="*70)

    environment = detect_environment()
    gpu = detect_gpu()
    cpu = detect_cpu()
    ram = detect_ram()

    hw_info = HardwareInfo(
        gpu=gpu,
        cpu=cpu,
        ram=ram,
        environment=environment,
        platform=platform.system(),
        python_version=platform.python_version()
    )

    logger.info("="*70)
    logger.info(f"硬件检测完成 - 性能档位: {hw_info.performance_tier}")
    logger.info("="*70)

    return hw_info


def print_hardware_summary(hw: HardwareInfo):
    """
    打印硬件信息摘要（增强版）

    Args:
        hw: HardwareInfo对象
    """
    print("\n" + "="*70)
    print("🔍 硬件配置检测结果")
    print("="*70)

    # 环境信息（新增）
    print(f"🌍 运行环境: {hw.environment.runtime_type.upper()}")
    if hw.environment.is_colab:
        print(f"  - Google Colab 环境")
    elif hw.environment.is_wsl:
        print(f"  - WSL (Windows Subsystem for Linux)")
    elif hw.environment.is_hospital_environment:
        print(f"  - 医院环境 (Windows)")
    print(f"  - 系统: {hw.environment.os_name} {hw.environment.os_version}")

    # GPU信息
    if hw.gpu.available:
        print(f"✓ GPU: {hw.gpu.device_name}")
        print(f"  - VRAM: {hw.gpu.vram_total_gb:.1f}GB (可用: {hw.gpu.vram_available_gb:.1f}GB)")
        print(f"  - CUDA: {hw.gpu.cuda_version}")
        if hw.gpu.compute_capability:
            print(f"  - 计算能力: {hw.gpu.compute_capability[0]}.{hw.gpu.compute_capability[1]}")
        if hw.gpu.device_count > 1:
            print(f"  - 设备数: {hw.gpu.device_count}个GPU")
    else:
        print(f"✗ GPU: 不可用")
        print(f"  - 模式: CPU推理")

    # CPU信息（增强）
    print(f"✓ CPU: {hw.cpu.physical_cores}核心 ({hw.cpu.logical_cores}线程)")
    if hw.cpu.cpu_freq_max_mhz:
        print(f"  - 频率: {hw.cpu.cpu_freq_mhz:.0f}MHz (最高: {hw.cpu.cpu_freq_max_mhz:.0f}MHz)")
    elif hw.cpu.cpu_freq_mhz:
        print(f"  - 频率: {hw.cpu.cpu_freq_mhz:.0f}MHz")
    if hw.cpu.cache_size_mb:
        print(f"  - 缓存: {hw.cpu.cache_size_mb:.1f}MB")
    if hw.cpu.architecture:
        print(f"  - 架构: {hw.cpu.architecture}")
    if hw.cpu.cpu_model and hw.cpu.cpu_model != "Unknown CPU":
        model_short = hw.cpu.cpu_model[:50] + "..." if len(hw.cpu.cpu_model) > 50 else hw.cpu.cpu_model
        print(f"  - 型号: {model_short}")

    # 内存信息
    print(f"✓ RAM: {hw.ram.total_gb:.1f}GB 总量")
    print(f"  - 可用: {hw.ram.available_gb:.1f}GB ({100-hw.ram.percent_used:.1f}% 空闲)")
    if not hw.ram.is_sufficient:
        print(f"  ⚠️  警告: 可用内存不足6GB，可能影响性能")

    # 平台信息
    print(f"✓ 平台: {hw.platform}")
    print(f"✓ Python: {hw.python_version}")

    # 性能档位和推荐配置（新增）
    print("\n" + "-"*70)
    print("📊 性能分析与推荐")
    print("-"*70)
    print(f"性能档位: {hw.performance_tier}")
    print(f"推荐设备: {hw.recommended_device.upper()}")
    print(f"推荐 DataLoader workers: {hw.cpu.recommended_workers}")
    print(f"推荐 Batch Size: {hw.ram.recommended_batch_size}")

    # 医院环境特别提示
    if hw.environment.is_hospital_environment and not hw.gpu.available:
        print("\n⚕️  医院环境 CPU 模式优化建议:")
        if hw.cpu.physical_cores >= 8:
            print("  ✓ CPU性能良好 (8核+)，预计处理速度: <60秒/患者")
        else:
            print("  ⚠️  CPU核心数较少，建议使用8核+配置以获得最佳性能")

    print("="*70 + "\n")


def get_optimal_config(hw: HardwareInfo) -> Dict[str, Any]:
    """
    根据硬件信息返回最优配置（新增函数，医院环境关键）

    Args:
        hw: 硬件信息

    Returns:
        包含最优配置的字典
    """
    config = {
        'device': hw.recommended_device,
        'num_workers': hw.cpu.recommended_workers,
        'batch_size': hw.ram.recommended_batch_size,
        'pin_memory': hw.gpu.available,  # GPU时启用pin_memory
        'prefetch_factor': 2 if hw.cpu.recommended_workers > 0 else None,
        'performance_tier': hw.performance_tier,
    }

    # CPU优化（医院环境）
    if not hw.gpu.available:
        config['cpu_optimization'] = {
            'torch_threads': hw.cpu.physical_cores,  # PyTorch线程数
            'mkl_threads': hw.cpu.physical_cores,    # MKL线程数（Intel CPU加速）
            'omp_threads': hw.cpu.physical_cores,    # OpenMP线程数
        }

    return config


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    print("\n测试硬件检测模块（共享版）...")
    print("="*70)

    hw = detect_hardware()
    print_hardware_summary(hw)

    # 获取最优配置
    print("\n最优配置:")
    print("="*70)
    optimal_config = get_optimal_config(hw)
    for key, value in optimal_config.items():
        print(f"{key}: {value}")

    # 验收标准
    print("\n验收标准检查:")
    print(f"✓ 环境检测: {hw.environment.runtime_type}")
    print(f"✓ GPU可用: {hw.gpu.available}")
    print(f"✓ VRAM: {hw.gpu.vram_total_gb:.1f}GB")
    print(f"✓ CPU核心: {hw.cpu.physical_cores}")
    print(f"✓ 内存: {hw.ram.total_gb:.1f}GB")
    print(f"✓ 性能档位: {hw.performance_tier}")
    print(f"✓ 推荐workers: {hw.cpu.recommended_workers}")
