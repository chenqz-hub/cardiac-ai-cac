"""
NB10 AI-CAC 安全监控模块
Safety Monitor Module

功能:
1. 内存监控与OOM保护
2. GPU显存监控
3. 自动降级机制
4. 异常检测与恢复

作者: NB10 Team + Claude Code
日期: 2025-10-14
"""

import psutil
import torch
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """安全等级"""
    SAFE = "safe"           # 安全：资源充足
    WARNING = "warning"     # 警告：接近阈值
    CRITICAL = "critical"   # 危险：需要降级
    EMERGENCY = "emergency" # 紧急：立即停止


@dataclass
class ResourceStatus:
    """资源状态"""
    # RAM状态
    ram_total_gb: float
    ram_available_gb: float
    ram_percent_used: float
    ram_level: SafetyLevel

    # GPU VRAM状态
    vram_total_gb: float
    vram_allocated_gb: float
    vram_reserved_gb: float
    vram_free_gb: float
    vram_percent_used: float
    vram_level: SafetyLevel

    # 整体安全等级
    overall_level: SafetyLevel

    # 建议操作
    action_needed: str
    details: str


class SafetyMonitor:
    """
    安全监控器

    职责:
    1. 实时监控RAM和VRAM使用情况
    2. 检测OOM风险
    3. 建议降级操作
    """

    def __init__(
        self,
        # RAM阈值（可用内存百分比）
        ram_warning_threshold: float = 20.0,    # 可用<20%警告
        ram_critical_threshold: float = 10.0,   # 可用<10%危险
        ram_emergency_threshold: float = 5.0,   # 可用<5%紧急

        # VRAM阈值（已用内存百分比）
        vram_warning_threshold: float = 80.0,   # 已用>80%警告
        vram_critical_threshold: float = 90.0,  # 已用>90%危险
        vram_emergency_threshold: float = 95.0, # 已用>95%紧急

        # 是否启用自动降级
        enable_auto_downgrade: bool = True,
    ):
        """
        初始化安全监控器

        Args:
            ram_warning_threshold: RAM警告阈值（可用百分比）
            ram_critical_threshold: RAM危险阈值
            ram_emergency_threshold: RAM紧急阈值
            vram_warning_threshold: VRAM警告阈值（已用百分比）
            vram_critical_threshold: VRAM危险阈值
            vram_emergency_threshold: VRAM紧急阈值
            enable_auto_downgrade: 是否启用自动降级
        """
        self.ram_warning = ram_warning_threshold
        self.ram_critical = ram_critical_threshold
        self.ram_emergency = ram_emergency_threshold

        self.vram_warning = vram_warning_threshold
        self.vram_critical = vram_critical_threshold
        self.vram_emergency = vram_emergency_threshold

        self.enable_auto_downgrade = enable_auto_downgrade

        # 检查CUDA可用性
        self.cuda_available = torch.cuda.is_available()

        logger.info(f"SafetyMonitor initialized")
        logger.info(f"  RAM thresholds: {self.ram_warning}%/{self.ram_critical}%/{self.ram_emergency}%")
        logger.info(f"  VRAM thresholds: {self.vram_warning}%/{self.vram_critical}%/{self.vram_emergency}%")
        logger.info(f"  Auto-downgrade: {enable_auto_downgrade}")

    def check_ram_status(self) -> Tuple[float, float, float, SafetyLevel]:
        """
        检查RAM状态

        Returns:
            (total_gb, available_gb, percent_available, level)
        """
        mem = psutil.virtual_memory()
        total_gb = mem.total / (1024 ** 3)
        available_gb = mem.available / (1024 ** 3)
        percent_available = (mem.available / mem.total) * 100

        # 判断安全等级
        if percent_available < self.ram_emergency:
            level = SafetyLevel.EMERGENCY
        elif percent_available < self.ram_critical:
            level = SafetyLevel.CRITICAL
        elif percent_available < self.ram_warning:
            level = SafetyLevel.WARNING
        else:
            level = SafetyLevel.SAFE

        return total_gb, available_gb, percent_available, level

    def check_vram_status(self) -> Tuple[float, float, float, float, float, SafetyLevel]:
        """
        检查GPU VRAM状态

        Returns:
            (total_gb, allocated_gb, reserved_gb, free_gb, percent_used, level)
        """
        if not self.cuda_available:
            return 0.0, 0.0, 0.0, 0.0, 0.0, SafetyLevel.SAFE

        # 获取VRAM信息
        total_bytes = torch.cuda.get_device_properties(0).total_memory
        allocated_bytes = torch.cuda.memory_allocated(0)
        reserved_bytes = torch.cuda.memory_reserved(0)

        total_gb = total_bytes / (1024 ** 3)
        allocated_gb = allocated_bytes / (1024 ** 3)
        reserved_gb = reserved_bytes / (1024 ** 3)
        free_gb = (total_bytes - reserved_bytes) / (1024 ** 3)
        percent_used = (reserved_bytes / total_bytes) * 100

        # 判断安全等级
        if percent_used > self.vram_emergency:
            level = SafetyLevel.EMERGENCY
        elif percent_used > self.vram_critical:
            level = SafetyLevel.CRITICAL
        elif percent_used > self.vram_warning:
            level = SafetyLevel.WARNING
        else:
            level = SafetyLevel.SAFE

        return total_gb, allocated_gb, reserved_gb, free_gb, percent_used, level

    def check_status(self) -> ResourceStatus:
        """
        检查整体资源状态

        Returns:
            ResourceStatus对象
        """
        # 检查RAM
        ram_total, ram_avail, ram_percent_avail, ram_level = self.check_ram_status()
        ram_percent_used = 100 - ram_percent_avail

        # 检查VRAM
        vram_total, vram_alloc, vram_reserved, vram_free, vram_percent_used, vram_level = self.check_vram_status()

        # 确定整体安全等级（取最危险的）
        levels = [ram_level, vram_level]
        if SafetyLevel.EMERGENCY in levels:
            overall = SafetyLevel.EMERGENCY
        elif SafetyLevel.CRITICAL in levels:
            overall = SafetyLevel.CRITICAL
        elif SafetyLevel.WARNING in levels:
            overall = SafetyLevel.WARNING
        else:
            overall = SafetyLevel.SAFE

        # 确定建议操作
        action, details = self._determine_action(ram_level, vram_level, ram_avail, vram_free)

        return ResourceStatus(
            ram_total_gb=ram_total,
            ram_available_gb=ram_avail,
            ram_percent_used=ram_percent_used,
            ram_level=ram_level,

            vram_total_gb=vram_total,
            vram_allocated_gb=vram_alloc,
            vram_reserved_gb=vram_reserved,
            vram_free_gb=vram_free,
            vram_percent_used=vram_percent_used,
            vram_level=vram_level,

            overall_level=overall,
            action_needed=action,
            details=details
        )

    def _determine_action(
        self,
        ram_level: SafetyLevel,
        vram_level: SafetyLevel,
        ram_avail: float,
        vram_free: float
    ) -> Tuple[str, str]:
        """
        确定建议操作

        Returns:
            (action, details)
        """
        # 紧急情况：立即停止
        if ram_level == SafetyLevel.EMERGENCY or vram_level == SafetyLevel.EMERGENCY:
            return "STOP", f"资源严重不足 (RAM: {ram_avail:.1f}GB, VRAM: {vram_free:.1f}GB)，建议立即停止"

        # 危险情况：降级配置
        if ram_level == SafetyLevel.CRITICAL or vram_level == SafetyLevel.CRITICAL:
            details = []
            if ram_level == SafetyLevel.CRITICAL:
                details.append(f"RAM不足({ram_avail:.1f}GB)")
            if vram_level == SafetyLevel.CRITICAL:
                details.append(f"VRAM不足({vram_free:.1f}GB)")
            return "DOWNGRADE", f"{', '.join(details)}，建议降级配置"

        # 警告情况：监控
        if ram_level == SafetyLevel.WARNING or vram_level == SafetyLevel.WARNING:
            return "MONITOR", f"资源接近阈值 (RAM: {ram_avail:.1f}GB, VRAM: {vram_free:.1f}GB)，继续监控"

        # 安全
        return "CONTINUE", f"资源充足 (RAM: {ram_avail:.1f}GB, VRAM: {vram_free:.1f}GB)"

    def log_status(self, status: ResourceStatus, prefix: str = ""):
        """
        记录资源状态到日志

        Args:
            status: 资源状态
            prefix: 日志前缀
        """
        level_emoji = {
            SafetyLevel.SAFE: "✅",
            SafetyLevel.WARNING: "⚠️",
            SafetyLevel.CRITICAL: "🔴",
            SafetyLevel.EMERGENCY: "🚨"
        }

        emoji = level_emoji.get(status.overall_level, "❓")

        logger.info(f"{prefix}{emoji} Resource Status: {status.overall_level.value.upper()}")
        logger.info(f"{prefix}  RAM: {status.ram_available_gb:.1f}GB available ({100-status.ram_percent_used:.1f}%) - {status.ram_level.value}")
        logger.info(f"{prefix}  VRAM: {status.vram_free_gb:.1f}GB free ({100-status.vram_percent_used:.1f}%) - {status.vram_level.value}")
        logger.info(f"{prefix}  Action: {status.action_needed} - {status.details}")

    def should_downgrade(self, status: ResourceStatus) -> bool:
        """
        判断是否需要降级

        Args:
            status: 资源状态

        Returns:
            True if需要降级
        """
        if not self.enable_auto_downgrade:
            return False

        return status.action_needed in ["DOWNGRADE", "STOP"]

    def suggest_downgrade_profile(self, current_num_workers: int) -> Dict[str, Any]:
        """
        建议降级配置

        Args:
            current_num_workers: 当前num_workers

        Returns:
            降级后的配置建议
        """
        status = self.check_status()

        # 紧急情况：最小配置
        if status.overall_level == SafetyLevel.EMERGENCY:
            return {
                "num_workers": 0,
                "pin_memory": False,
                "prefetch_factor": None,
                "reason": "EMERGENCY: 资源严重不足，切换到最小配置"
            }

        # 危险情况：降低num_workers
        if status.overall_level == SafetyLevel.CRITICAL:
            new_workers = max(0, current_num_workers - 1)
            return {
                "num_workers": new_workers,
                "pin_memory": True if new_workers > 0 else False,
                "prefetch_factor": 2 if new_workers > 0 else None,
                "reason": f"CRITICAL: 降低num_workers {current_num_workers} → {new_workers}"
            }

        # 无需降级
        return {
            "num_workers": current_num_workers,
            "pin_memory": True,
            "prefetch_factor": 2,
            "reason": "资源充足，保持当前配置"
        }

    def clear_gpu_cache(self):
        """清理GPU缓存"""
        if self.cuda_available:
            torch.cuda.empty_cache()
            logger.info("GPU cache cleared")


# 全局单例
_monitor_instance: Optional[SafetyMonitor] = None


def get_monitor(
    ram_warning: float = 20.0,
    ram_critical: float = 10.0,
    ram_emergency: float = 5.0,
    vram_warning: float = 80.0,
    vram_critical: float = 90.0,
    vram_emergency: float = 95.0,
    enable_auto_downgrade: bool = True,
) -> SafetyMonitor:
    """
    获取全局SafetyMonitor实例

    Returns:
        SafetyMonitor单例
    """
    global _monitor_instance

    if _monitor_instance is None:
        _monitor_instance = SafetyMonitor(
            ram_warning_threshold=ram_warning,
            ram_critical_threshold=ram_critical,
            ram_emergency_threshold=ram_emergency,
            vram_warning_threshold=vram_warning,
            vram_critical_threshold=vram_critical,
            vram_emergency_threshold=vram_emergency,
            enable_auto_downgrade=enable_auto_downgrade,
        )

    return _monitor_instance


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

    print("=" * 70)
    print("NB10 Safety Monitor 测试")
    print("=" * 70)

    # 创建监控器
    monitor = get_monitor()

    # 检查状态
    status = monitor.check_status()

    # 打印状态
    print(f"\n当前资源状态:")
    print(f"  RAM: {status.ram_available_gb:.2f}GB 可用 / {status.ram_total_gb:.2f}GB 总量 ({100-status.ram_percent_used:.1f}%)")
    print(f"  VRAM: {status.vram_free_gb:.2f}GB 可用 / {status.vram_total_gb:.2f}GB 总量 ({100-status.vram_percent_used:.1f}%)")
    print(f"\n安全等级:")
    print(f"  RAM: {status.ram_level.value}")
    print(f"  VRAM: {status.vram_level.value}")
    print(f"  整体: {status.overall_level.value}")
    print(f"\n建议操作: {status.action_needed}")
    print(f"  详情: {status.details}")

    # 测试降级建议
    print(f"\n降级建议测试 (当前num_workers=2):")
    suggestion = monitor.suggest_downgrade_profile(current_num_workers=2)
    print(f"  建议num_workers: {suggestion['num_workers']}")
    print(f"  建议pin_memory: {suggestion['pin_memory']}")
    print(f"  原因: {suggestion['reason']}")

    # 记录到日志
    print("\n日志输出:")
    monitor.log_status(status, prefix="  ")

    print("\n" + "=" * 70)
    print("✅ 测试完成")
    print("=" * 70)
