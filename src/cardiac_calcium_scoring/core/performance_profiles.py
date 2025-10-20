"""
性能配置档位系统
Performance Profile System

根据硬件配置自动选择最优的DataLoader和推理参数。
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ProfileTier(Enum):
    """配置档位等级"""
    MINIMAL = 1      # 最低配置 (CPU或<4GB VRAM)
    STANDARD = 2     # 标准配置 (6GB VRAM, RTX 2060类)
    PERFORMANCE = 3  # 性能配置 (8-12GB VRAM, RTX 3060类)
    PROFESSIONAL = 4 # 专业配置 (16-24GB VRAM, RTX 4080类)
    ENTERPRISE = 5   # 企业配置 (多GPU或>24GB VRAM)


@dataclass
class PerformanceProfile:
    """性能配置参数"""
    # 档位信息
    tier: ProfileTier
    tier_name: str
    description: str

    # DataLoader优化参数
    num_workers: int          # 数据加载线程数
    pin_memory: bool          # 是否使用pinned memory
    prefetch_factor: Optional[int]  # 预取因子

    # 推理批处理参数
    slice_batch_size: int     # 切片批大小

    # 缓存管理参数
    clear_cache_interval: int # 多少个patient清理一次缓存
    enable_auto_cache: bool   # 是否启用自动缓存管理

    # 预期性能
    expected_speedup: str     # 预期性能提升
    expected_time_per_patient: float  # 预期处理时间(秒/患者)

    def __str__(self):
        return (f"档位: {self.tier_name}\n"
                f"  - num_workers: {self.num_workers}\n"
                f"  - pin_memory: {self.pin_memory}\n"
                f"  - slice_batch_size: {self.slice_batch_size}\n"
                f"  - 预期提升: {self.expected_speedup}")


# 预定义配置档位
PROFILES = {
    ProfileTier.MINIMAL: PerformanceProfile(
        tier=ProfileTier.MINIMAL,
        tier_name="Minimal",
        description="CPU mode or GPU VRAM<4GB",
        num_workers=2,              # v1.1.3: CPU多线程优化（从0→2）
        pin_memory=False,           # CPU不需要pin_memory
        prefetch_factor=2,          # v1.1.3: 新增预取优化
        slice_batch_size=8,         # v1.1.3: CPU可用更大batch（从2→8）
        clear_cache_interval=1,
        enable_auto_cache=True,
        expected_speedup="↑ 30-40% (v1.1.3优化)",  # v1.1.3: 预期提升
        expected_time_per_patient=10.5  # 15秒 * 0.70 ≈ 10.5秒
    ),

    ProfileTier.STANDARD: PerformanceProfile(
        tier=ProfileTier.STANDARD,
        tier_name="Standard",
        description="6GB VRAM (RTX 2060/3050/4050)",
        num_workers=2,              # ← 默认启用（RAM不足时自动降为0）
        pin_memory=True,            # ← 默认启用（RAM不足时自动禁用）
        prefetch_factor=2,
        slice_batch_size=4,
        clear_cache_interval=1,
        enable_auto_cache=True,
        expected_speedup="↑ 20-30%",
        expected_time_per_patient=11.0  # 15秒 * 0.73 ≈ 11秒
    ),

    ProfileTier.PERFORMANCE: PerformanceProfile(
        tier=ProfileTier.PERFORMANCE,
        tier_name="Performance",
        description="8-12GB VRAM (RTX 3060/4060)",
        num_workers=4,
        pin_memory=True,
        prefetch_factor=2,
        slice_batch_size=6,
        clear_cache_interval=3,
        enable_auto_cache=True,
        expected_speedup="↑ 35-45%",
        expected_time_per_patient=9.0   # 15秒 * 0.60 ≈ 9秒
    ),

    ProfileTier.PROFESSIONAL: PerformanceProfile(
        tier=ProfileTier.PROFESSIONAL,
        tier_name="Professional",
        description="16-24GB VRAM (RTX 4080/A5000)",
        num_workers=6,
        pin_memory=True,
        prefetch_factor=3,
        slice_batch_size=8,
        clear_cache_interval=5,
        enable_auto_cache=True,
        expected_speedup="↑ 50-60%",
        expected_time_per_patient=7.0   # 15秒 * 0.47 ≈ 7秒
    ),

    ProfileTier.ENTERPRISE: PerformanceProfile(
        tier=ProfileTier.ENTERPRISE,
        tier_name="Enterprise",
        description="Multi-GPU or >24GB VRAM (A6000/H100)",
        num_workers=8,
        pin_memory=True,
        prefetch_factor=4,
        slice_batch_size=12,
        clear_cache_interval=10,
        enable_auto_cache=True,
        expected_speedup="↑ 70-80%+",
        expected_time_per_patient=5.0   # 15秒 * 0.33 ≈ 5秒
    ),
}


def select_profile_by_hardware(hw_info) -> PerformanceProfile:
    """
    根据硬件信息自动选择最优配置档位

    Args:
        hw_info: HardwareInfo对象 (来自hardware_profiler)

    Returns:
        PerformanceProfile: 最优配置档位

    档位选择规则:
    - MINIMAL: CPU模式 或 GPU VRAM < 4GB
    - STANDARD: 4-7GB VRAM (RTX 2060, 3050)
    - PERFORMANCE: 8-12GB VRAM (RTX 3060, 4060)
    - PROFESSIONAL: 13-24GB VRAM (RTX 4080, A5000)
    - ENTERPRISE: 多GPU 或 >24GB VRAM
    """
    gpu = hw_info.gpu
    cpu = hw_info.cpu
    ram = hw_info.ram

    # 规则1: 无GPU或VRAM不足 → MINIMAL
    if not gpu.available or gpu.vram_total_gb < 4.0:
        logger.info("选择档位: MINIMAL (CPU模式或VRAM不足)")
        return PROFILES[ProfileTier.MINIMAL]

    # 规则2: 多GPU → ENTERPRISE
    if gpu.device_count > 1:
        logger.info(f"选择档位: ENTERPRISE (检测到{gpu.device_count}个GPU)")
        return PROFILES[ProfileTier.ENTERPRISE]

    # 规则3: 根据VRAM大小选择
    vram = gpu.vram_total_gb

    if vram >= 24:
        tier = ProfileTier.ENTERPRISE
    elif vram >= 13:
        tier = ProfileTier.PROFESSIONAL
    elif vram >= 8:
        tier = ProfileTier.PERFORMANCE
    elif vram >= 4:
        tier = ProfileTier.STANDARD
    else:
        tier = ProfileTier.MINIMAL

    profile = PROFILES[tier]

    # 内存检查: 如果可用RAM不足，降级num_workers和pin_memory
    # 原因: 测试发现pin_memory在低RAM环境(<8GB)下会产生负面影响 (-3.2%)
    # 详见: docs/PHASE1_PERFORMANCE_TEST_REPORT.md
    if not ram.is_sufficient:  # <8GB可用
        logger.warning(f"可用内存不足({ram.available_gb:.1f}GB)，禁用pin_memory和降低num_workers")
        # 创建修改后的profile副本
        profile = PerformanceProfile(
            tier=profile.tier,
            tier_name=profile.tier_name,
            description=profile.description,
            num_workers=max(0, profile.num_workers - 2),  # 降级
            pin_memory=False,  # ← 禁用pin_memory（低RAM下会导致性能下降）
            prefetch_factor=profile.prefetch_factor,
            slice_batch_size=profile.slice_batch_size,
            clear_cache_interval=profile.clear_cache_interval,
            enable_auto_cache=profile.enable_auto_cache,
            expected_speedup="基线 (内存不足，已禁用优化)",
            expected_time_per_patient=15.0  # 回退到基线性能
        )

    logger.info(f"选择档位: {profile.tier_name}")
    logger.info(f"  VRAM: {vram:.1f}GB, CPU: {cpu.physical_cores}核, RAM: {ram.total_gb:.1f}GB")
    logger.info(f"  预期性能提升: {profile.expected_speedup}")

    return profile


def print_profile_summary(profile: PerformanceProfile):
    """
    打印配置档位摘要

    Args:
        profile: PerformanceProfile对象
    """
    print("\n" + "="*70)
    print(f"⚙️  性能配置档位: {profile.tier_name}")
    print("="*70)
    print(f"说明: {profile.description}")
    print()
    print("DataLoader优化:")
    print(f"  - num_workers: {profile.num_workers} (数据加载线程)")
    print(f"  - pin_memory: {profile.pin_memory} (GPU内存锁定)")
    if profile.prefetch_factor:
        print(f"  - prefetch_factor: {profile.prefetch_factor} (预取批次)")
    print()
    print("推理参数:")
    print(f"  - slice_batch_size: {profile.slice_batch_size}")
    print(f"  - clear_cache_interval: {profile.clear_cache_interval}")
    print()
    print("预期性能:")
    print(f"  - 性能提升: {profile.expected_speedup}")
    print(f"  - 处理时间: ~{profile.expected_time_per_patient:.0f}秒/患者")
    print("="*70 + "\n")


def get_profile_comparison_table():
    """返回所有档位的对比表格（用于文档）"""
    header = f"{'档位':<12} {'VRAM':<8} {'Workers':<8} {'Pin':<5} {'Batch':<6} {'预期提升':<12} {'时间':<10}"
    separator = "="*75

    rows = [separator, header, separator]

    for tier in ProfileTier:
        p = PROFILES[tier]
        row = (f"{p.tier_name:<12} "
               f"{p.description[:7]:<8} "
               f"{p.num_workers:<8} "
               f"{'是' if p.pin_memory else '否':<5} "
               f"{p.slice_batch_size:<6} "
               f"{p.expected_speedup:<12} "
               f"{p.expected_time_per_patient:.0f}秒")
        rows.append(row)

    rows.append(separator)
    return "\n".join(rows)


if __name__ == "__main__":
    # 测试代码
    print("\n测试性能配置档位系统...")
    print("="*70)

    # 显示所有档位对比
    print("\n📊 性能档位对比表:")
    print(get_profile_comparison_table())

    # 模拟硬件检测并选择档位
    print("\n\n🔍 模拟硬件检测和档位选择:")
    print("-"*70)

    from hardware_profiler import detect_hardware

    try:
        hw = detect_hardware()
        profile = select_profile_by_hardware(hw)
        print_profile_summary(profile)

        print("✅ 验收标准检查:")
        print(f"  - 档位选择: {profile.tier_name}")
        print(f"  - num_workers: {profile.num_workers}")
        print(f"  - pin_memory: {profile.pin_memory}")
        print(f"  - 预期提升: {profile.expected_speedup}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
