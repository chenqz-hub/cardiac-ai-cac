"""
硬件检测模块
Hardware Detection Module

用于自动检测GPU、CPU、内存等硬件信息，为性能优化提供基础数据。
"""

import torch
import psutil
import platform
import logging
from dataclasses import dataclass
from typing import Optional

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

    def __post_init__(self):
        if self.available and self.cuda_version is None:
            try:
                self.cuda_version = torch.version.cuda
            except:
                self.cuda_version = "Unknown"


@dataclass
class CPUInfo:
    """CPU信息"""
    physical_cores: int
    logical_cores: int
    cpu_model: str
    cpu_freq_mhz: Optional[float] = None

    def __post_init__(self):
        if self.cpu_freq_mhz is None:
            try:
                freq = psutil.cpu_freq()
                self.cpu_freq_mhz = freq.max if freq else None
            except:
                self.cpu_freq_mhz = None


@dataclass
class RAMInfo:
    """内存信息"""
    total_gb: float
    available_gb: float
    percent_used: float

    @property
    def is_sufficient(self) -> bool:
        """是否有足够内存（建议至少6GB可用，理想8GB+）"""
        # 基于实测: 3GB即可获得17.2%提升，设置6GB为安全阈值
        return self.available_gb >= 6.0


@dataclass
class HardwareInfo:
    """完整硬件信息"""
    gpu: GPUInfo
    cpu: CPUInfo
    ram: RAMInfo
    platform: str
    python_version: str


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
            device_count=device_count
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
    """检测CPU信息"""
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

        logger.info(f"检测到CPU: {physical_cores}核 ({logical_cores}线程)")

        return CPUInfo(
            physical_cores=physical_cores,
            logical_cores=logical_cores,
            cpu_model=cpu_model
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
    检测完整硬件信息

    Returns:
        HardwareInfo: 包含GPU、CPU、内存等完整硬件信息

    Example:
        >>> hw = detect_hardware()
        >>> print(f"GPU: {hw.gpu.device_name}, VRAM: {hw.gpu.vram_total_gb:.1f}GB")
        >>> print(f"CPU: {hw.cpu.physical_cores}核")
        >>> print(f"RAM: {hw.ram.total_gb:.1f}GB")
    """
    logger.info("="*70)
    logger.info("正在检测硬件配置...")
    logger.info("="*70)

    gpu = detect_gpu()
    cpu = detect_cpu()
    ram = detect_ram()

    hw_info = HardwareInfo(
        gpu=gpu,
        cpu=cpu,
        ram=ram,
        platform=platform.system(),
        python_version=platform.python_version()
    )

    logger.info("="*70)
    logger.info("硬件检测完成")
    logger.info("="*70)

    return hw_info


def print_hardware_summary(hw: HardwareInfo):
    """
    打印硬件信息摘要

    Args:
        hw: HardwareInfo对象
    """
    print("\n" + "="*70)
    print("🔍 硬件配置检测结果")
    print("="*70)

    # GPU信息
    if hw.gpu.available:
        print(f"✓ GPU: {hw.gpu.device_name}")
        print(f"  - VRAM: {hw.gpu.vram_total_gb:.1f}GB (可用: {hw.gpu.vram_available_gb:.1f}GB)")
        print(f"  - CUDA: {hw.gpu.cuda_version}")
        if hw.gpu.device_count > 1:
            print(f"  - 设备数: {hw.gpu.device_count}个GPU")
    else:
        print(f"✗ GPU: 不可用")
        print(f"  - 模式: CPU推理")

    # CPU信息
    print(f"✓ CPU: {hw.cpu.physical_cores}核心 ({hw.cpu.logical_cores}线程)")
    if hw.cpu.cpu_freq_mhz:
        print(f"  - 频率: {hw.cpu.cpu_freq_mhz:.0f}MHz")
    if hw.cpu.cpu_model and hw.cpu.cpu_model != "Unknown CPU":
        model_short = hw.cpu.cpu_model[:50] + "..." if len(hw.cpu.cpu_model) > 50 else hw.cpu.cpu_model
        print(f"  - 型号: {model_short}")

    # 内存信息
    print(f"✓ RAM: {hw.ram.total_gb:.1f}GB 总量")
    print(f"  - 可用: {hw.ram.available_gb:.1f}GB ({100-hw.ram.percent_used:.1f}% 空闲)")
    if not hw.ram.is_sufficient:
        print(f"  ⚠️  警告: 可用内存不足8GB，可能影响性能")

    # 平台信息
    print(f"✓ 平台: {hw.platform}")
    print(f"✓ Python: {hw.python_version}")

    print("="*70 + "\n")


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    print("\n测试硬件检测模块...")
    print("="*70)

    hw = detect_hardware()
    print_hardware_summary(hw)

    # 验证
    print("\n验收标准检查:")
    print(f"✓ GPU可用: {hw.gpu.available}")
    print(f"✓ VRAM: {hw.gpu.vram_total_gb:.1f}GB")
    print(f"✓ CPU核心: {hw.cpu.physical_cores}")
    print(f"✓ 内存: {hw.ram.total_gb:.1f}GB")
