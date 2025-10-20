"""
Runtime Environment Detector
运行环境检测模块

自动识别运行环境：Colab/Windows/Linux/WSL/macOS
支持Google Drive挂载（Colab环境）
"""

import os
import platform
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class RuntimeEnvironment:
    """运行环境信息"""
    runtime_type: str  # 'colab' / 'windows' / 'linux' / 'wsl' / 'macos' / 'unknown'
    is_colab: bool
    is_wsl: bool
    is_jupyter: bool
    os_name: str
    os_version: str
    python_version: str
    working_directory: Path
    home_directory: Path
    google_drive_mounted: bool = False
    google_drive_path: Optional[Path] = None

    @property
    def is_hospital_environment(self) -> bool:
        """是否可能是医院环境（Windows且非Colab）"""
        return self.runtime_type == 'windows' and not self.is_colab

    @property
    def is_cloud_environment(self) -> bool:
        """是否云环境"""
        return self.is_colab

    @property
    def supports_gpu(self) -> bool:
        """环境是否可能支持GPU（需要进一步硬件检测确认）"""
        # Colab通常有GPU，WSL/Windows/Linux可能有
        return True  # 实际GPU可用性由hardware.detector检测

    @property
    def recommended_install_method(self) -> str:
        """推荐的软件安装方式"""
        if self.is_colab:
            return "pip_online"  # Colab总是在线
        elif self.runtime_type in ['windows', 'wsl']:
            return "offline_package"  # 医院环境推荐离线包
        else:
            return "pip_mirror"  # Linux推荐镜像源


def detect_colab() -> bool:
    """
    检测是否运行在Google Colab

    Returns:
        True if running in Colab
    """
    try:
        import google.colab
        return True
    except ImportError:
        return False


def detect_jupyter() -> bool:
    """
    检测是否运行在Jupyter环境

    Returns:
        True if running in Jupyter/IPython
    """
    try:
        # 检查IPython
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython is None:
            return False

        # 检查是否在notebook环境
        if 'IPKernelApp' in ipython.config:
            return True

        # 检查ZMQInteractiveShell（Jupyter notebook/lab）
        shell_type = type(ipython).__name__
        if 'ZMQInteractiveShell' in shell_type:
            return True

        return False
    except ImportError:
        return False


def detect_wsl() -> bool:
    """
    检测是否运行在WSL (Windows Subsystem for Linux)

    Returns:
        True if running in WSL
    """
    if platform.system() != "Linux":
        return False

    try:
        # 方法1: 检查 /proc/version
        with open('/proc/version', 'r') as f:
            version_info = f.read().lower()
            if 'microsoft' in version_info or 'wsl' in version_info:
                return True

        # 方法2: 检查 /proc/sys/kernel/osrelease
        osrelease_path = Path('/proc/sys/kernel/osrelease')
        if osrelease_path.exists():
            osrelease = osrelease_path.read_text().lower()
            if 'microsoft' in osrelease or 'wsl' in osrelease:
                return True

        return False
    except Exception as e:
        logger.debug(f"WSL检测失败: {e}")
        return False


def detect_google_drive() -> tuple[bool, Optional[Path]]:
    """
    检测Google Drive是否挂载（Colab环境）

    Returns:
        (is_mounted, mount_path)
    """
    # Colab默认挂载路径
    default_mount_path = Path('/content/drive')

    if default_mount_path.exists():
        my_drive = default_mount_path / 'MyDrive'
        if my_drive.exists():
            return True, default_mount_path

    # 检查其他可能的挂载路径
    alternative_paths = [
        Path('/content/gdrive'),
        Path('/gdrive'),
        Path('/drive'),
    ]

    for path in alternative_paths:
        if path.exists():
            return True, path

    return False, None


def mount_google_drive(force: bool = False) -> tuple[bool, Optional[Path]]:
    """
    挂载Google Drive（仅Colab环境）

    Args:
        force: 强制重新挂载

    Returns:
        (success, mount_path)
    """
    # 检查是否在Colab
    if not detect_colab():
        logger.warning("非Colab环境，无法挂载Google Drive")
        return False, None

    # 检查是否已挂载
    is_mounted, mount_path = detect_google_drive()
    if is_mounted and not force:
        logger.info(f"Google Drive已挂载: {mount_path}")
        return True, mount_path

    # 尝试挂载
    try:
        from google.colab import drive
        mount_point = '/content/drive'
        drive.mount(mount_point, force_remount=force)

        # 验证挂载
        mount_path = Path(mount_point)
        if mount_path.exists():
            logger.info(f"Google Drive挂载成功: {mount_path}")
            return True, mount_path
        else:
            logger.error("Google Drive挂载失败")
            return False, None

    except Exception as e:
        logger.error(f"Google Drive挂载异常: {e}")
        return False, None


def detect_runtime() -> RuntimeEnvironment:
    """
    检测完整运行环境

    Returns:
        RuntimeEnvironment object
    """
    logger.info("="*70)
    logger.info("正在检测运行环境...")
    logger.info("="*70)

    # 基本信息
    os_name = platform.system()
    os_version = platform.release()
    python_version = platform.python_version()
    working_dir = Path.cwd()
    home_dir = Path.home()

    # 检测特殊环境
    is_colab = detect_colab()
    is_jupyter = detect_jupyter()
    is_wsl = detect_wsl()

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

    # Colab环境：检测Google Drive
    google_drive_mounted = False
    google_drive_path = None
    if is_colab:
        google_drive_mounted, google_drive_path = detect_google_drive()

    env = RuntimeEnvironment(
        runtime_type=runtime_type,
        is_colab=is_colab,
        is_wsl=is_wsl,
        is_jupyter=is_jupyter,
        os_name=os_name,
        os_version=os_version,
        python_version=python_version,
        working_directory=working_dir,
        home_directory=home_dir,
        google_drive_mounted=google_drive_mounted,
        google_drive_path=google_drive_path
    )

    logger.info("="*70)
    logger.info(f"运行环境检测完成: {runtime_type.upper()}")
    logger.info("="*70)

    return env


def print_environment_summary(env: RuntimeEnvironment):
    """
    打印运行环境摘要

    Args:
        env: RuntimeEnvironment object
    """
    print("\n" + "="*70)
    print("🌍 运行环境检测结果")
    print("="*70)

    # 基本信息
    print(f"运行时类型: {env.runtime_type.upper()}")
    print(f"操作系统: {env.os_name} {env.os_version}")
    print(f"Python版本: {env.python_version}")

    # 环境标志
    flags = []
    if env.is_colab:
        flags.append("Google Colab")
    if env.is_wsl:
        flags.append("WSL")
    if env.is_jupyter:
        flags.append("Jupyter")
    if env.is_hospital_environment:
        flags.append("医院环境")
    if env.is_cloud_environment:
        flags.append("云环境")

    if flags:
        print(f"环境特征: {', '.join(flags)}")

    # 路径信息
    print(f"\n📂 路径信息:")
    print(f"  工作目录: {env.working_directory}")
    print(f"  用户主目录: {env.home_directory}")

    # Google Drive（Colab）
    if env.is_colab:
        if env.google_drive_mounted:
            print(f"  Google Drive: ✓ 已挂载 ({env.google_drive_path})")
        else:
            print(f"  Google Drive: ✗ 未挂载")

    # 部署建议
    print(f"\n📦 推荐安装方式: {env.recommended_install_method}")
    if env.is_hospital_environment:
        print(f"  建议: 使用完整离线包（医院隔离网络）")
    elif env.is_colab:
        print(f"  建议: pip在线安装（Colab联网环境）")

    print("="*70 + "\n")


def get_data_directory_recommendations(env: RuntimeEnvironment) -> Dict[str, Path]:
    """
    根据环境推荐数据目录路径

    Args:
        env: RuntimeEnvironment object

    Returns:
        推荐的目录路径字典
    """
    recommendations = {}

    if env.is_colab:
        # Colab环境
        if env.google_drive_mounted:
            # 优先使用Google Drive
            base = env.google_drive_path / 'MyDrive' / 'cardiac-ml-research'
            recommendations['data_dir'] = base / 'data' / 'dicom_original'
            recommendations['output_dir'] = base / 'output'
            recommendations['cache_dir'] = base / 'data' / 'cache'
        else:
            # 使用/content（临时，断连即丢失）
            base = Path('/content/cardiac-ml-research')
            recommendations['data_dir'] = base / 'data' / 'dicom_original'
            recommendations['output_dir'] = base / 'output'
            recommendations['cache_dir'] = base / 'data' / 'cache'
            recommendations['warning'] = "Colab临时存储，建议挂载Google Drive"

    elif env.runtime_type in ['windows', 'wsl']:
        # Windows/WSL环境（医院）
        base = env.working_directory
        recommendations['data_dir'] = base / 'data' / 'dicom_original'
        recommendations['output_dir'] = base / 'output'
        recommendations['cache_dir'] = base / 'data' / 'cache'
        recommendations['log_dir'] = base / 'logs'

    else:
        # Linux/macOS
        base = env.working_directory
        recommendations['data_dir'] = base / 'data' / 'dicom_original'
        recommendations['output_dir'] = base / 'output'
        recommendations['cache_dir'] = base / 'data' / 'cache'
        recommendations['log_dir'] = base / 'logs'

    return recommendations


def setup_environment_for_tool(tool_name: str = "nb10") -> Dict[str, Any]:
    """
    为特定工具设置环境（一键初始化）

    Args:
        tool_name: 工具名称

    Returns:
        环境设置结果字典
    """
    env = detect_runtime()

    result = {
        'environment': env,
        'recommendations': get_data_directory_recommendations(env),
        'tool_name': tool_name,
    }

    # Colab环境特殊处理
    if env.is_colab:
        if not env.google_drive_mounted:
            print("检测到Colab环境但Google Drive未挂载")
            print("是否挂载Google Drive？(y/n): ", end='')
            # 注意：在实际Colab中需要用户交互
            result['google_drive_mount_required'] = True

    return result


if __name__ == "__main__":
    # 测试环境检测
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    print("\n测试运行环境检测模块...")
    print("="*70)

    env = detect_runtime()
    print_environment_summary(env)

    # 推荐目录
    print("\n推荐的数据目录:")
    print("="*70)
    recommendations = get_data_directory_recommendations(env)
    for key, value in recommendations.items():
        print(f"{key}: {value}")

    # 验收标准
    print("\n验收标准检查:")
    print(f"✓ 运行时类型: {env.runtime_type}")
    print(f"✓ Colab检测: {env.is_colab}")
    print(f"✓ WSL检测: {env.is_wsl}")
    print(f"✓ Jupyter检测: {env.is_jupyter}")
    print(f"✓ 医院环境识别: {env.is_hospital_environment}")
    print(f"✓ 推荐安装方式: {env.recommended_install_method}")

    if env.is_colab:
        print(f"✓ Google Drive挂载: {env.google_drive_mounted}")
