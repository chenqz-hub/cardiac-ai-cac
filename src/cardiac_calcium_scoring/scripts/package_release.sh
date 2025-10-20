#!/bin/bash
# NB10 AI-CAC Release Packaging Script
# Usage: ./scripts/package_release.sh [version]

set -e

VERSION=${1:-"1.1.0"}
RELEASE_NAME="nb10-ai-cac-full-v${VERSION}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="${PROJECT_ROOT}/dist"
PACKAGE_DIR="${DIST_DIR}/${RELEASE_NAME}"

echo "=========================================="
echo "NB10 AI-CAC Release Packaging"
echo "Version: ${VERSION}"
echo "=========================================="
echo ""

# 1. 清理旧构建
echo "[1/8] Cleaning old builds..."
rm -rf "${PACKAGE_DIR}"
mkdir -p "${PACKAGE_DIR}/nb10_windows"

# 2. 复制核心文件
echo "[2/8] Copying application files..."
cd "${PROJECT_ROOT}"
cp -r cli core config deployment docs scripts examples "${PACKAGE_DIR}/nb10_windows/"
cp README.md CHANGELOG.md PROJECT_STRUCTURE.md "${PACKAGE_DIR}/nb10_windows/"
cp PHASE1_STATUS.md "${PACKAGE_DIR}/nb10_windows/docs/"

# 3. 创建空目录
echo "[3/8] Creating output directories..."
mkdir -p "${PACKAGE_DIR}/nb10_windows/"{output,logs,data/cache,tests}
echo "# 输出目录" > "${PACKAGE_DIR}/nb10_windows/output/README.md"
echo "# 日志目录" > "${PACKAGE_DIR}/nb10_windows/logs/README.md"
echo "# 缓存目录" > "${PACKAGE_DIR}/nb10_windows/data/cache/README.md"
echo "# 测试目录" > "${PACKAGE_DIR}/nb10_windows/tests/README.md"

# 4. 复制模型文件（如果存在）
echo "[4/8] Checking model files..."
if [ -f "${PROJECT_ROOT}/models/va_non_gated_ai_cac_model.pth" ]; then
    mkdir -p "${PACKAGE_DIR}/nb10_windows/models"
    echo "  Copying model file (1.2GB)..."
    cp "${PROJECT_ROOT}/models/va_non_gated_ai_cac_model.pth" "${PACKAGE_DIR}/nb10_windows/models/"
    MODEL_SIZE=$(du -sh "${PACKAGE_DIR}/nb10_windows/models/va_non_gated_ai_cac_model.pth" | cut -f1)
    echo "  ✓ Model file included (${MODEL_SIZE})"
else
    mkdir -p "${PACKAGE_DIR}/nb10_windows/models"
    cat > "${PACKAGE_DIR}/nb10_windows/models/README.md" << 'EOF'
# AI-CAC 模型文件

## 下载模型

模型文件较大（约1.2GB），需要单独下载。

### 方法1: 自动下载（推荐）
```bash
cd nb10_windows
python deployment/download_models.py
```

### 方法2: 手动下载
1. 从以下地址下载模型文件：
   - Google Drive: [下载链接]
   - 百度网盘: [下载链接] 提取码: xxxx

2. 将下载的文件放置到此目录：
   ```
   nb10_windows/models/va_non_gated_ai_cac_model.pth
   ```

3. 验证文件大小约为 1.2GB

## 模型信息
- 文件名: va_non_gated_ai_cac_model.pth
- 大小: ~1.2GB
- SHA256: [待填充]
- 版本: v1.0
EOF
    echo "  ⚠ Model file not found - download instructions created"
fi

# 5. 生成Windows批处理文件
echo "[5/8] Generating Windows batch scripts..."

# install_gpu.bat
cat > "${PACKAGE_DIR}/install_gpu.bat" << 'EOF'
@echo off
chcp 65001 >nul
echo ==========================================
echo NB10 AI-CAC GPU版本依赖安装
echo ==========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/4] 检测到Python版本:
python --version
echo.

echo [2/4] 创建虚拟环境...
python -m venv venv
if errorlevel 1 (
    echo [错误] 虚拟环境创建失败
    pause
    exit /b 1
)
echo   ✓ 虚拟环境创建成功
echo.

echo [3/4] 升级pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
echo   ✓ pip升级完成
echo.

echo [4/4] 安装依赖包（这可能需要几分钟）...
echo   提示: 正在下载和安装PyTorch、MONAI等大型包...
pip install -r nb10_windows\deployment\requirements_gpu.txt
if errorlevel 1 (
    echo.
    echo [错误] 依赖安装失败
    echo 可能原因:
    echo   1. 网络连接问题
    echo   2. CUDA版本不兼容
    echo   3. 磁盘空间不足
    echo.
    echo 建议: 检查网络后重试，或尝试CPU版本 (install_cpu.bat)
    pause
    exit /b 1
)

echo.
echo ==========================================
echo ✓ 安装完成！
echo ==========================================
echo.
echo 下一步:
echo   1. 编辑配置文件:
echo      nb10_windows\config\config.yaml
echo.
echo   2. 配置DICOM数据路径:
echo      paths:
echo        data_dir: "D:/DICOM_Data"
echo        output_dir: "D:/NB10_Results"
echo.
echo   3. 启动程序:
echo      双击运行 run_nb10.bat
echo.
pause
EOF

# install_cpu.bat
cat > "${PACKAGE_DIR}/install_cpu.bat" << 'EOF'
@echo off
chcp 65001 >nul
echo ==========================================
echo NB10 AI-CAC CPU版本依赖安装
echo ==========================================
echo.
echo 注意: CPU模式运行较慢 (约50-100秒/患者)
echo 建议使用NVIDIA GPU以获得最佳性能 (10-15秒/患者)
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [1/4] 检测到Python版本:
python --version
echo.

echo [2/4] 创建虚拟环境...
python -m venv venv
if errorlevel 1 (
    echo [错误] 虚拟环境创建失败
    pause
    exit /b 1
)
echo   ✓ 虚拟环境创建成功
echo.

echo [3/4] 升级pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
echo   ✓ pip升级完成
echo.

echo [4/4] 安装依赖包（这可能需要几分钟）...
pip install -r nb10_windows\deployment\requirements_cpu.txt
if errorlevel 1 (
    echo.
    echo [错误] 依赖安装失败
    echo 可能原因:
    echo   1. 网络连接问题
    echo   2. 磁盘空间不足
    echo.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo ✓ 安装完成！
echo ==========================================
echo.
echo 性能提示:
echo   - CPU模式: 约50-100秒/患者
echo   - GPU模式: 约10-15秒/患者 (需要NVIDIA显卡)
echo.
echo 下一步:
echo   1. 编辑配置文件:
echo      nb10_windows\config\config.yaml
echo.
echo   2. 配置DICOM数据路径:
echo      paths:
echo        data_dir: "D:/DICOM_Data"
echo        output_dir: "D:/NB10_Results"
echo.
echo   3. 启动程序:
echo      双击运行 run_nb10.bat
echo.
pause
EOF

# run_nb10.bat
cat > "${PACKAGE_DIR}/run_nb10.bat" << 'EOF'
@echo off
chcp 65001 >nul
echo ==========================================
echo NB10 AI-CAC 启动器
echo ==========================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo [错误] 未找到虚拟环境
    echo.
    echo 请先运行以下命令之一:
    echo   - install_gpu.bat  (GPU版本，推荐)
    echo   - install_cpu.bat  (CPU版本)
    echo.
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查模型文件
if not exist "nb10_windows\models\va_non_gated_ai_cac_model.pth" (
    echo [错误] 未找到模型文件
    echo.
    echo 模型文件路径:
    echo   nb10_windows\models\va_non_gated_ai_cac_model.pth
    echo.
    echo 请下载模型文件并放置到上述路径
    echo 下载方法详见: nb10_windows\models\README.md
    echo.
    pause
    exit /b 1
)

echo ✓ 环境检查通过
echo.

REM 进入工作目录
cd nb10_windows

echo ==========================================
echo 使用说明
echo ==========================================
echo.
echo 命令格式:
echo   python cli\run_nb10.py [选项]
echo.
echo 常用选项:
echo   --data-dir PATH      DICOM数据目录
echo   --mode MODE          pilot (测试) 或 full (完整)
echo   --pilot-limit N      测试模式处理N个病例
echo   --output-dir PATH    结果输出目录
echo.
echo 示例:
echo   python cli\run_nb10.py --data-dir "D:\DICOM_Data" --mode pilot --pilot-limit 5
echo.
echo ==========================================
echo.

REM 显示帮助信息
python cli\run_nb10.py --help

echo.
echo 提示: 修改配置文件可以设置默认路径
echo   配置文件: config\config.yaml
echo.
echo 按任意键退出...
pause >nul
EOF

# 6. 生成发布文档
echo "[6/8] Generating release documents..."

# README.txt
cat > "${PACKAGE_DIR}/README.txt" << EOF
================================================================================
NB10 AI-CAC 冠脉钙化评分工具 v${VERSION} (完整版)
================================================================================

这是一个基于深度学习的冠状动脉钙化自动评分工具，适用于Windows环境。

【主要功能】
  ✓ 自动DICOM数据处理
  ✓ AI智能钙化识别
  ✓ Agatston评分计算
  ✓ 硬件自适应优化 (Phase 1)
  ✓ 安全监控系统 (Phase 2)
  ✓ 实时资源监控
  ✓ OOM保护机制

【硬件要求】
  推荐配置：
    - Windows 10/11 (64位)
    - NVIDIA GPU (RTX 2060及以上，6GB+ VRAM)
    - 8GB+ 系统内存
    - 10GB 磁盘空间

  最低配置：
    - Windows 10/11 (64位)
    - CPU模式（较慢，50-100秒/患者）
    - 4GB+ 系统内存
    - 10GB 磁盘空间

【快速开始】
  1. 解压到C盘（避免中文路径）
     推荐: C:\nb10-ai-cac-full-v${VERSION}\
     避免: C:\用户\文档\nb10\

  2. 安装Python（如未安装）
     下载: https://www.python.org/downloads/
     版本: Python 3.10 或更高
     重要: 安装时勾选 "Add Python to PATH"

  3. 安装依赖包
     GPU版本（推荐）: 双击运行 install_gpu.bat
     CPU版本:         双击运行 install_cpu.bat

  4. 配置数据路径
     编辑文件: nb10_windows\config\config.yaml
     修改以下路径:
       paths:
         data_dir: "D:/DICOM_Data"      # 您的DICOM数据路径
         output_dir: "D:/NB10_Results"  # 结果输出路径

  5. 下载模型文件（如未包含）
     查看: nb10_windows\models\README.md
     大小: 约1.2GB

  6. 运行程序
     双击运行: run_nb10.bat
     或命令行:
       cd nb10_windows
       python cli\run_nb10.py --data-dir "D:\DICOM_Data" --mode pilot --pilot-limit 5

【处理模式】
  pilot模式: 快速测试（默认处理1个病例）
    python cli\run_nb10.py --mode pilot --pilot-limit 5

  full模式: 处理所有病例
    python cli\run_nb10.py --mode full

【性能表现】
  GPU模式 (RTX 2060):
    - 处理速度: 10-15秒/患者
    - 内存占用: 2-3GB VRAM
    - Phase 1优化: +17.2% 性能提升

  CPU模式:
    - 处理速度: 50-100秒/患者
    - 内存占用: 2-4GB RAM

【输出结果】
  CSV文件包含:
    - Agatston评分
    - 钙化体积 (mm³)
    - 钙化质量 (mg)
    - 风险分层

  位置: output/nb10_results_latest.csv

【文档】
  用户手册:     nb10_windows/docs/USER_MANUAL.md
  安装指南:     nb10_windows/docs/INSTALLATION_GUIDE.md
  打包部署:     nb10_windows/docs/PACKAGING_DEPLOYMENT_GUIDE.md
  Phase 1报告:  nb10_windows/docs/PHASE1_FINAL_PERFORMANCE_REPORT.md
  Phase 2报告:  nb10_windows/docs/PHASE2_TEST_REPORT.md

【常见问题】
  Q: 提示"未找到Python"？
  A: 确保Python已安装并添加到PATH环境变量

  Q: 提示"未找到模型文件"？
  A: 下载模型文件到 nb10_windows\models\ 目录
     详见 nb10_windows\models\README.md

  Q: GPU不可用？
  A: 检查NVIDIA驱动是否安装，或使用CPU模式

  Q: 内存不足错误？
  A: Phase 2安全监控会自动保护，关闭其他程序释放内存

  Q: 处理速度慢？
  A: GPU模式比CPU模式快5-10倍，建议使用GPU

【技术支持】
  项目主页: [待填写]
  问题反馈: [待填写]
  邮箱: support@example.com

【版权声明】
  © 2025 Chen Doctor Team. All rights reserved.
  仅供医学研究使用，禁止商业用途。

【更新日志】
  详见 CHANGELOG.txt

================================================================================
祝您使用愉快！
================================================================================
EOF

# VERSION.txt
cat > "${PACKAGE_DIR}/VERSION.txt" << EOF
NB10 AI-CAC v${VERSION}
Build Date: $(date +%Y-%m-%d)
Git Commit: $(cd "${PROJECT_ROOT}" && git rev-parse --short HEAD 2>/dev/null || echo "unknown")

================================================================================
Features
================================================================================
✓ Phase 1: Hardware Adaptive Optimization
  - Automatic hardware detection
  - Multi-tier performance profiles (Minimal → Enterprise)
  - DataLoader optimization (num_workers, pin_memory)
  - Performance boost: +17.2% on RTX 2060

✓ Phase 2: Safety Monitoring System
  - Real-time RAM/VRAM monitoring
  - 4-level safety classification (SAFE/WARNING/CRITICAL/EMERGENCY)
  - OOM protection mechanism
  - Automatic GPU cache clearing
  - Comprehensive resource logging

✓ Core Features
  - DICOM batch processing
  - AI-based calcium detection
  - Agatston score calculation
  - Risk stratification
  - CSV report generation

================================================================================
Compatibility
================================================================================
Operating System:
  - Windows 10 (64-bit)
  - Windows 11 (64-bit)

Python:
  - Python 3.10+
  - Python 3.11 (recommended)
  - Python 3.12 (tested)

GPU Support:
  - CUDA 11.7+
  - NVIDIA GPU with 6GB+ VRAM
  - CPU fallback supported

Dependencies:
  - PyTorch 2.0+
  - MONAI 1.3+
  - pydicom
  - numpy, pandas, etc.

================================================================================
Performance
================================================================================
GPU Mode (RTX 2060):
  - Processing: 10-15s per patient
  - VRAM usage: 2-3GB
  - Optimization: +17.2% vs baseline

CPU Mode:
  - Processing: 50-100s per patient
  - RAM usage: 2-4GB

Safety Monitor:
  - Overhead: <1%
  - OOM protection: Active

================================================================================
Package Contents
================================================================================
nb10_windows/
  ├── cli/              Command-line interface
  ├── core/             Core inference modules
  ├── config/           Configuration files
  ├── models/           AI model files (1.2GB)
  ├── docs/             Documentation
  ├── deployment/       Deployment tools
  ├── scripts/          Utility scripts
  ├── output/           Results directory
  └── logs/             Log files directory

Batch Scripts:
  - install_gpu.bat     GPU version installer
  - install_cpu.bat     CPU version installer
  - run_nb10.bat        Application launcher

Documentation:
  - README.txt          Quick start guide
  - VERSION.txt         This file
  - CHANGELOG.txt       Version history

================================================================================
Build Information
================================================================================
Built on:  $(date +"%Y-%m-%d %H:%M:%S")
Platform:  $(uname -s) $(uname -m)
Builder:   Automated packaging script

Git Repository:
  Branch: $(cd "${PROJECT_ROOT}" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
  Commit: $(cd "${PROJECT_ROOT}" && git rev-parse HEAD 2>/dev/null || echo "unknown")
  Tag:    v${VERSION}

================================================================================
License
================================================================================
This software is provided for medical research purposes only.
Commercial use is prohibited without explicit permission.

© 2025 Chen Doctor Team. All rights reserved.

================================================================================
EOF

# CHANGELOG.txt
if [ -f "${PROJECT_ROOT}/CHANGELOG.md" ]; then
    cp "${PROJECT_ROOT}/CHANGELOG.md" "${PACKAGE_DIR}/CHANGELOG.txt"
else
    cat > "${PACKAGE_DIR}/CHANGELOG.txt" << EOF
# Changelog

## [${VERSION}] - $(date +%Y-%m-%d)

### Added
- Phase 1: Hardware Adaptive Optimization (+17.2% performance)
- Phase 2: Safety Monitoring System (OOM protection)
- Automatic hardware detection
- Multi-tier performance profiles
- Real-time resource monitoring
- Comprehensive documentation

### Changed
- Improved DataLoader configuration
- Enhanced GPU memory management
- Better error handling

### Fixed
- Memory leak in batch processing
- GPU cache accumulation

## [1.0.0] - Initial Release
EOF
fi

# 7. 清理开发文件
echo "[7/8] Cleaning development files..."
cd "${PACKAGE_DIR}/nb10_windows"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name ".DS_Store" -delete 2>/dev/null || true
find . -type f -name "*.log" -delete 2>/dev/null || true
rm -rf .git .gitignore .pytest_cache 2>/dev/null || true
cd - >/dev/null

# 8. 创建压缩包
echo "[8/8] Creating archive..."
cd "${DIST_DIR}"
if command -v zip >/dev/null 2>&1; then
    zip -r "${RELEASE_NAME}.zip" "${RELEASE_NAME}/" -q
    echo "  ✓ ZIP archive created"
else
    tar -czf "${RELEASE_NAME}.tar.gz" "${RELEASE_NAME}/"
    echo "  ✓ TAR.GZ archive created"
fi
cd - >/dev/null

# 9. 生成校验和
echo ""
echo "Generating checksums..."
cd "${DIST_DIR}"
if [ -f "${RELEASE_NAME}.zip" ]; then
    sha256sum "${RELEASE_NAME}.zip" > "${RELEASE_NAME}.zip.sha256"
    ARCHIVE_FILE="${RELEASE_NAME}.zip"
elif [ -f "${RELEASE_NAME}.tar.gz" ]; then
    sha256sum "${RELEASE_NAME}.tar.gz" > "${RELEASE_NAME}.tar.gz.sha256"
    ARCHIVE_FILE="${RELEASE_NAME}.tar.gz"
fi
cd - >/dev/null

# 10. 完成
echo ""
echo "=========================================="
echo "✓ Package created successfully!"
echo "=========================================="
echo ""
echo "Output:"
echo "  Directory: ${PACKAGE_DIR}/"
echo "  Archive:   ${DIST_DIR}/${ARCHIVE_FILE}"
echo "  Checksum:  ${DIST_DIR}/${ARCHIVE_FILE}.sha256"
echo ""

if [ -f "${DIST_DIR}/${ARCHIVE_FILE}" ]; then
    ARCHIVE_SIZE=$(du -sh "${DIST_DIR}/${ARCHIVE_FILE}" | cut -f1)
    echo "Archive size: ${ARCHIVE_SIZE}"
fi

if [ -d "${PACKAGE_DIR}/nb10_windows/models" ] && [ -f "${PACKAGE_DIR}/nb10_windows/models/va_non_gated_ai_cac_model.pth" ]; then
    echo "Model file:   Included (1.2GB)"
else
    echo "Model file:   NOT included (download required)"
fi

echo ""
echo "Next steps:"
echo "  1. Test the package on Windows workstation"
echo "  2. Verify model file is present (or downloadable)"
echo "  3. Run pilot test (5 cases)"
echo "  4. Distribute to hospital IT department"
echo ""
echo "Distribution methods:"
echo "  - USB drive: Copy ${ARCHIVE_FILE} to USB"
echo "  - Network: Upload to hospital intranet server"
echo "  - Cloud: Upload to Baidu Pan / Google Drive"
echo ""
