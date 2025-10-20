#!/bin/bash
# NB10 AI-CAC Lite Release Packaging Script (WITHOUT Model)
# Usage: ./scripts/package_release_lite.sh [version]
#
# ⚠️  DEPRECATED: This script is DEPRECATED due to Chinese encoding issues
# ⚠️  Please use: package_release_lite_en.sh instead (English version)
#
# This script contains Chinese characters in batch files which may cause
# encoding issues on Windows systems with different locales.

echo "=========================================="
echo "⚠️  WARNING: This script is DEPRECATED"
echo "=========================================="
echo ""
echo "Reason: Chinese character encoding issues on Windows"
echo "Alternative: Use package_release_lite_en.sh (English version)"
echo ""
echo "Press Ctrl+C to cancel, or wait 10 seconds to continue anyway..."
sleep 10

set -e

VERSION=${1:-"1.0.0"}
RELEASE_NAME="nb10-ai-cac-lite-v${VERSION}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="${PROJECT_ROOT}/dist"
PACKAGE_DIR="${DIST_DIR}/${RELEASE_NAME}"

echo "=========================================="
echo "NB10 AI-CAC LITE Release Packaging"
echo "Version: ${VERSION}"
echo "NOTE: Model file NOT included (separate download)"
echo "=========================================="
echo ""

# 1. 清理旧构建
echo "[1/8] Cleaning old builds..."
rm -rf "${PACKAGE_DIR}"
mkdir -p "${PACKAGE_DIR}/nb10_windows"

# 2. 复制核心文件
echo "[2/8] Copying application files..."
cd "${PROJECT_ROOT}"

# 复制核心代码目录
cp -r cli core config deployment scripts examples "${PACKAGE_DIR}/nb10_windows/"

# 复制基础文档（不含phase详细报告）
mkdir -p "${PACKAGE_DIR}/nb10_windows/docs"
cp docs/USER_MANUAL.md "${PACKAGE_DIR}/nb10_windows/docs/" 2>/dev/null || true
cp docs/INSTALLATION_GUIDE.md "${PACKAGE_DIR}/nb10_windows/docs/" 2>/dev/null || true
cp docs/PACKAGING_DEPLOYMENT_GUIDE.md "${PACKAGE_DIR}/nb10_windows/docs/" 2>/dev/null || true

# 复制项目文档（只复制核心文档，排除临时文件）
cp README.md "${PACKAGE_DIR}/nb10_windows/"
cp CHANGELOG.md "${PACKAGE_DIR}/nb10_windows/" 2>/dev/null || echo "# Changelog" > "${PACKAGE_DIR}/nb10_windows/CHANGELOG.md"

# 清理根目录临时文件（在复制后立即清理）
echo "  - Cleaning temporary files from nb10_windows root..."
cd "${PACKAGE_DIR}/nb10_windows"
# 删除开发和调试用的临时脚本
rm -f compare_psm_vs_nonpsm.py
rm -f integrate_multimodal_data.py
rm -f investigate_failed_merges.py
rm -f trace_unmatched_patients.py
rm -f menu.py
# 删除阶段性文档和计划文档
rm -f DOCUMENT_CLEANUP_PLAN.md
rm -f *_PROGRESS.md
rm -f *_SUMMARY*.md
rm -f *_REPORT*.md
rm -f *_STATUS*.md
rm -f *_LOG*.md
rm -f QUICK_*.md
rm -f SESSION_*.md
rm -f NEXT_*.md
rm -f FINAL_*.md
rm -f COLAB_*.md
rm -f SOLUTION_*.md
rm -f VALIDATION_*.md
rm -f README_FIRST.txt
cd "${PROJECT_ROOT}"

# 3. 创建空目录
echo "[3/8] Creating output directories..."
mkdir -p "${PACKAGE_DIR}/nb10_windows/"{output,logs,data/cache,tests,models}
echo "# 输出目录" > "${PACKAGE_DIR}/nb10_windows/output/README.md"
echo "# 日志目录" > "${PACKAGE_DIR}/nb10_windows/logs/README.md"
echo "# 缓存目录" > "${PACKAGE_DIR}/nb10_windows/data/cache/README.md"
echo "# 测试目录" > "${PACKAGE_DIR}/nb10_windows/tests/README.md"

# 4. 创建模型下载说明（重要！）
echo "[4/8] Creating model download instructions..."
cat > "${PACKAGE_DIR}/nb10_windows/models/README.md" << 'EOF'
# AI-CAC 模型文件下载说明

⚠️ **重要**: 此轻量版本不包含模型文件，需要单独下载。

## 模型信息

- **文件名**: `va_non_gated_ai_cac_model.pth`
- **大小**: 约 1.2GB
- **放置位置**: 此目录 (`models/`)

## 下载方法

### 方法1: 从医院IT部门获取

如果您是通过医院IT部门获得此软件，请向IT部门索取模型文件。
IT部门应该有单独的模型文件备份。

### 方法2: 百度网盘下载

```
链接: [待填写]
提取码: [待填写]
```

下载后将文件放置到此目录。

### 方法3: Google Drive下载

```
链接: [待填写]
```

### 方法4: 医院内网服务器

如果医院已部署内网服务器，请从以下路径复制：
```
\\hospital-server\shared\nb10-models\va_non_gated_ai_cac_model.pth
```

## 安装步骤

1. 下载模型文件 `va_non_gated_ai_cac_model.pth`
2. 确认文件大小约为 1.2GB
3. 将文件复制到此目录:
   ```
   nb10_windows\models\va_non_gated_ai_cac_model.pth
   ```
4. 验证文件路径正确
5. 运行程序测试

## 验证

运行以下命令验证模型文件是否正确放置：

```cmd
cd nb10_windows
python -c "import os; print('✓ 模型文件存在' if os.path.exists('models/va_non_gated_ai_cac_model.pth') else '✗ 模型文件不存在')"
```

## 技术支持

如果下载遇到问题，请联系:
- 邮箱: support@example.com
- 医院IT部门
EOF

cat > "${PACKAGE_DIR}/nb10_windows/models/DOWNLOAD_MODEL.txt" << 'EOF'
================================================================================
模型文件下载说明
================================================================================

⚠️ 此轻量版本不包含AI模型文件，需要单独下载！

模型文件:
  文件名: va_non_gated_ai_cac_model.pth
  大小:   约1.2GB
  位置:   放置到此文件夹 (models/)

下载途径:
  1. 从医院IT部门获取
  2. 百度网盘: [链接待填写]
  3. Google Drive: [链接待填写]
  4. 医院内网服务器

安装后目录结构:
  models/
  ├── va_non_gated_ai_cac_model.pth  ← 下载的模型文件
  ├── README.md                       ← 详细说明
  └── DOWNLOAD_MODEL.txt              ← 本文件

详细说明请查看 README.md

================================================================================
EOF

# 5. 生成Windows批处理文件
echo "[5/8] Generating Windows batch scripts..."

# 创建scripts目录用于存放辅助批处理文件
mkdir -p "${PACKAGE_DIR}/scripts"

# install_gpu.bat (修改版，增加模型检查) - 放到scripts目录
cat > "${PACKAGE_DIR}/scripts/install_gpu.bat" << 'EOF'
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

echo [1/5] 检测到Python版本:
python --version
echo.

echo [2/5] 检查模型文件...
if not exist "nb10_windows\models\va_non_gated_ai_cac_model.pth" (
    echo.
    echo ⚠️  警告: 未找到模型文件
    echo.
    echo 模型文件路径:
    echo   nb10_windows\models\va_non_gated_ai_cac_model.pth
    echo.
    echo 请先下载模型文件（约1.2GB）
    echo 下载说明: nb10_windows\models\README.md
    echo.
    echo 您可以:
    echo   1. 现在中止安装，先下载模型文件
    echo   2. 继续安装依赖，稍后再下载模型
    echo.
    choice /C 12 /M "请选择"
    if errorlevel 2 (
        echo.
        echo 继续安装依赖...
    ) else (
        echo.
        echo 安装已中止。请下载模型文件后重新运行。
        pause
        exit /b 0
    )
) else (
    echo   ✓ 模型文件存在
)
echo.

echo [3/5] 创建虚拟环境...
python -m venv venv
if errorlevel 1 (
    echo [错误] 虚拟环境创建失败
    pause
    exit /b 1
)
echo   ✓ 虚拟环境创建成功
echo.

echo [4/5] 升级pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
echo   ✓ pip升级完成
echo.

echo [5/5] 安装依赖包（这可能需要几分钟）...
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
echo ✓ 依赖安装完成！
echo ==========================================
echo.

REM 再次检查模型文件
if not exist "nb10_windows\models\va_non_gated_ai_cac_model.pth" (
    echo ⚠️  提醒: 模型文件仍未就绪
    echo.
    echo 下一步必做:
    echo   1. 下载模型文件 (约1.2GB)
    echo      详见: nb10_windows\models\README.md
    echo.
    echo   2. 将模型文件放置到:
    echo      nb10_windows\models\va_non_gated_ai_cac_model.pth
    echo.
    echo   3. 编辑配置文件:
    echo      nb10_windows\config\config.yaml
    echo.
    echo   4. 运行程序:
    echo      双击 run_nb10.bat
    echo.
) else (
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
)
pause
EOF

# install_cpu.bat (类似修改) - 放到scripts目录
cat > "${PACKAGE_DIR}/scripts/install_cpu.bat" << 'EOF'
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

echo [1/5] 检测到Python版本:
python --version
echo.

echo [2/5] 检查模型文件...
if not exist "nb10_windows\models\va_non_gated_ai_cac_model.pth" (
    echo.
    echo ⚠️  警告: 未找到模型文件
    echo.
    echo 请先下载模型文件（约1.2GB）
    echo 下载说明: nb10_windows\models\README.md
    echo.
    echo 您可以:
    echo   1. 现在中止安装，先下载模型文件
    echo   2. 继续安装依赖，稍后再下载模型
    echo.
    choice /C 12 /M "请选择"
    if errorlevel 2 (
        echo 继续安装依赖...
    ) else (
        echo 安装已中止。
        pause
        exit /b 0
    )
) else (
    echo   ✓ 模型文件存在
)
echo.

echo [3/5] 创建虚拟环境...
python -m venv venv
echo   ✓ 完成
echo.

echo [4/5] 升级pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
echo   ✓ 完成
echo.

echo [5/5] 安装依赖包...
pip install -r nb10_windows\deployment\requirements_cpu.txt
if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo ==========================================
echo ✓ 依赖安装完成！
echo ==========================================
echo.

if not exist "nb10_windows\models\va_non_gated_ai_cac_model.pth" (
    echo ⚠️  提醒: 请下载模型文件
    echo 详见: nb10_windows\models\README.md
    echo.
)

echo 下一步:
echo   1. 下载模型文件（如未下载）
echo   2. 编辑配置文件: nb10_windows\config\config.yaml
echo   3. 运行程序: 双击 run_nb10.bat
echo.
pause
EOF

# run_nb10.bat - 放到scripts目录
cat > "${PACKAGE_DIR}/scripts/run_nb10.bat" << 'EOF'
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
echo.
echo 示例:
echo   python cli\run_nb10.py --data-dir "D:\DICOM_Data" --mode pilot --pilot-limit 5
echo.
echo ==========================================
echo.

REM 显示帮助信息
python cli\run_nb10.py --help

echo.
echo 按任意键退出...
pause >nul
EOF

# start_nb10.bat (一键启动脚本)
cat > "${PACKAGE_DIR}/start_nb10.bat" << 'EOF'
@echo off
REM =========================================
REM NB10 AI-CAC 一键启动脚本
REM 版本: v1.0.0
REM 功能: 自动检测环境并安装/运行NB10
REM =========================================

setlocal enabledelayedexpansion

REM 设置控制台编码为UTF-8
chcp 65001 >nul 2>&1

echo =========================================
echo NB10 AI-CAC 冠脉钙化评分系统
echo 一键启动脚本 v1.0.0
echo =========================================
echo.

REM =========================================
REM 步骤1: 检查安装状态
REM =========================================
echo [检测] 检查安装状态...

if exist "venv\Scripts\activate.bat" (
    echo [成功] 已检测到安装
    set "INSTALL_STATUS=installed"
) else (
    echo [信息] 未检测到安装，开始初始化安装...
    set "INSTALL_STATUS=not_installed"
)
echo.

REM =========================================
REM 步骤2: 检查Python环境
REM =========================================
echo [检测] 检查Python环境...

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python
    echo [提示] 请先安装Python 3.10:
    echo         1. 访问: https://www.python.org/downloads/release/python-31011/
    echo         2. 下载: Windows installer ^(64-bit^)
    echo         3. 安装时务必勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [成功] Python %PYTHON_VERSION% 已安装
echo.

REM =========================================
REM 步骤3: 检查GPU可用性（仅在未安装时）
REM =========================================
if "%INSTALL_STATUS%"=="not_installed" (
    echo [检测] 检查GPU可用性...

    REM 尝试运行nvidia-smi检测GPU
    nvidia-smi >nul 2>&1
    if errorlevel 1 (
        echo [信息] 未检测到NVIDIA GPU，将使用CPU模式
        echo [说明] CPU模式处理速度较慢（约50-100秒/例）
        set "GPU_MODE=cpu"
        set "INSTALL_SCRIPT=scripts\install_cpu.bat"
    ) else (
        echo [成功] 检测到NVIDIA GPU，将使用GPU模式
        echo [说明] GPU模式处理速度快（约20-30秒/例）
        set "GPU_MODE=gpu"
        set "INSTALL_SCRIPT=scripts\install_gpu.bat"
    )
    echo.
)

REM =========================================
REM 步骤4: 检查模型文件
REM =========================================
echo [检测] 检查模型文件...

set "MODEL_PATH=nb10_windows\models\va_non_gated_ai_cac_model.pth"
if exist "%MODEL_PATH%" (
    echo [成功] 模型文件已找到
    set "MODEL_STATUS=found"
) else (
    echo [警告] 未找到模型文件
    echo [路径] %MODEL_PATH%
    echo [提示] 请将模型文件复制到上述路径
    echo [大小] 约1.2GB
    echo.
    set "MODEL_STATUS=not_found"

    if "%INSTALL_STATUS%"=="not_installed" (
        echo 是否继续安装其他组件? ^(Y/N^):
        set /p CONTINUE_INSTALL=
        if /i "!CONTINUE_INSTALL!" neq "Y" (
            echo [取消] 用户取消安装
            pause
            exit /b 0
        )
    )
)
echo.

REM =========================================
REM 步骤5: 执行安装（如果需要）
REM =========================================
if "%INSTALL_STATUS%"=="not_installed" (
    echo [安装] 开始安装依赖包（%GPU_MODE%模式）...
    echo.

    call %INSTALL_SCRIPT%
    if errorlevel 1 (
        echo.
        echo [错误] 安装失败，请检查错误信息
        echo [日志] 可能原因:
        echo         - 网络连接问题
        echo         - 磁盘空间不足
        echo         - Python版本不兼容
        echo.
        pause
        exit /b 1
    )

    echo.
    echo [成功] 依赖安装完成！
    echo.
)

REM =========================================
REM 步骤6: 再次检查模型文件（安装后）
REM =========================================
if "%MODEL_STATUS%"=="not_found" (
    if exist "%MODEL_PATH%" (
        echo [成功] 模型文件已找到（安装后检测）
    ) else (
        echo [警告] 模型文件仍未找到
        echo [提示] 程序可以启动，但运行分析时会失败
        echo [建议] 请在运行分析前复制模型文件到:
        echo         %MODEL_PATH%
        echo.
        pause
    )
)

REM =========================================
REM 步骤7: 激活虚拟环境并启动
REM =========================================
echo [启动] 激活虚拟环境并运行NB10...
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境未找到
    echo [说明] 安装可能未完成或失败
    echo [建议] 请删除venv目录后重新运行此脚本
    echo.
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查虚拟环境是否成功激活
python -c "import sys; sys.exit(0 if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 1)" 2>nul
if errorlevel 1 (
    echo [警告] 虚拟环境激活可能失败，尝试直接运行...
)

REM 切换到nb10_windows目录
cd nb10_windows

REM 调用实际的运行脚本 (使用相对于根目录的venv路径)
if exist "..\venv\Scripts\python.exe" (
    REM 直接使用虚拟环境的Python
    ..\venv\Scripts\python.exe cli\run_nb10.py
) else (
    echo [错误] 虚拟环境中的Python未找到
    echo [路径] venv\Scripts\python.exe
    echo [建议] 请重新安装
    echo.
    cd ..
    pause
    exit /b 1
)

REM 运行完成后返回上级目录
cd ..

echo.
echo [完成] NB10已退出
pause
EOF

# 6. 生成发布文档
echo "[6/8] Generating release documents..."

# README.txt (修改版，强调模型单独下载)
cat > "${PACKAGE_DIR}/README.txt" << EOF
================================================================================
NB10 AI-CAC 冠脉钙化评分工具 v${VERSION} (轻量版)
================================================================================

⚠️  注意: 此为轻量版本，模型文件需单独下载（约1.2GB）

【主要功能】
  ✓ 自动DICOM数据处理
  ✓ AI智能钙化识别
  ✓ Agatston评分计算
  ✓ 硬件自适应优化 (Phase 1: +17.2% 性能)
  ✓ 安全监控系统 (Phase 2: OOM保护)

【硬件要求】
  推荐配置：
    - Windows 10/11 (64位)
    - NVIDIA GPU (RTX 2060+, 6GB+ VRAM)
    - 8GB+ 系统内存
    - 10GB 磁盘空间

  最低配置：
    - Windows 10/11 (64位)
    - CPU模式（较慢，50-100秒/患者）
    - 4GB+ 系统内存
    - 10GB 磁盘空间

【快速开始 - 一键启动（推荐）】
  ⭐ 双击运行: start_nb10.bat
     自动完成: 环境检测 → 自动安装 → 直接运行

  这是您唯一需要的操作！其他批处理文件都在 scripts\ 目录中，
  由 start_nb10.bat 自动调用，无需手动执行。

【目录结构】
  nb10-ai-cac-lite-v${VERSION}/
  ├── start_nb10.bat          ← 【推荐】一键启动（唯一需要的脚本）
  ├── README.txt              ← 本文件
  ├── VERSION.txt             ← 版本信息
  ├── CHANGELOG.txt           ← 更新日志
  ├── scripts/                ← 辅助脚本目录（由start_nb10.bat自动调用）
  │   ├── install_gpu.bat     ← GPU版本安装脚本
  │   ├── install_cpu.bat     ← CPU版本安装脚本
  │   └── run_nb10.bat        ← 手动运行脚本
  └── nb10_windows/           ← 主程序目录
      ├── cli/                ← 命令行工具
      ├── core/               ← 核心代码
      ├── config/             ← 配置文件
      ├── models/             ← 模型文件目录（需下载模型）
      └── docs/               ← 文档

【详细安装步骤】
  1. 解压到C盘（避免中文路径）
     推荐: C:\nb10-ai-cac-lite-v${VERSION}\

  2. ⚠️ 下载模型文件（重要！）
     详见: nb10_windows\models\README.md
     大小: 约1.2GB
     放置: nb10_windows\models\va_non_gated_ai_cac_model.pth

  3. 安装Python（如未安装）
     下载: https://www.python.org/downloads/
     版本: Python 3.10 或更高
     重要: 安装时勾选 "Add Python to PATH"

  4. 🚀 一键启动
     双击运行: start_nb10.bat
     程序会自动：
       ✓ 检测Python环境
       ✓ 检测GPU/CPU
       ✓ 检查模型文件
       ✓ 安装依赖包
       ✓ 启动程序

  5. 配置数据路径（首次运行后）
     编辑文件: nb10_windows\config\config.yaml
     修改以下路径:
       paths:
         data_dir: "D:/DICOM_Data"
         output_dir: "D:/NB10_Results"

【高级用户 - 手动安装】
  如果您需要手动控制安装过程：

  1. 手动安装依赖包
     GPU版本: 双击 scripts\install_gpu.bat
     CPU版本: 双击 scripts\install_cpu.bat

  2. 手动运行程序
     双击 scripts\run_nb10.bat

【轻量版说明】
  - 软件包大小: 约300MB（不含模型）
  - 模型文件: 需单独下载，约1.2GB
  - 优势: 快速分发，网络传输友好
  - 注意: 首次使用前必须下载模型文件

【性能表现】
  GPU模式 (RTX 2060): 10-15秒/患者
  CPU模式: 50-100秒/患者

【文档】
  用户手册: nb10_windows/docs/USER_MANUAL.md
  安装指南: nb10_windows/docs/INSTALLATION_GUIDE.md
  打包部署: nb10_windows/docs/PACKAGING_DEPLOYMENT_GUIDE.md

【技术支持】
  邮箱: support@example.com

【版权声明】
  © 2025 Chen Doctor Team. All rights reserved.
  仅供医学研究使用，禁止商业用途。

================================================================================
EOF

# VERSION.txt
cat > "${PACKAGE_DIR}/VERSION.txt" << EOF
NB10 AI-CAC v${VERSION} (Lite Edition)
Build Date: $(date +%Y-%m-%d)
Git Commit: $(cd "${PROJECT_ROOT}" && git rev-parse --short HEAD 2>/dev/null || echo "unknown")
Package Type: LITE (Model NOT included)

================================================================================
Features
================================================================================
✓ Phase 1: Hardware Adaptive Optimization (+17.2% performance)
✓ Phase 2: Safety Monitoring System (OOM protection)
✓ Automatic hardware detection
✓ Multi-tier performance profiles
✓ Real-time resource monitoring

================================================================================
Package Information
================================================================================
Package Type: Lite Edition
Package Size: ~300MB (without model)
Model File: SEPARATE DOWNLOAD REQUIRED
  - File: va_non_gated_ai_cac_model.pth
  - Size: ~1.2GB
  - Location: nb10_windows/models/
  - Download: See nb10_windows/models/README.md

================================================================================
Compatibility
================================================================================
Operating System: Windows 10/11 (64-bit)
Python: 3.10+
GPU: CUDA 11.7+ (optional, recommended)
CPU: Supported (slower)

================================================================================
Build Information
================================================================================
Built on: $(date +"%Y-%m-%d %H:%M:%S")
Platform: $(uname -s) $(uname -m)
Git Branch: $(cd "${PROJECT_ROOT}" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
Git Commit: $(cd "${PROJECT_ROOT}" && git rev-parse HEAD 2>/dev/null || echo "unknown")

================================================================================
EOF

# CHANGELOG.txt
cat > "${PACKAGE_DIR}/CHANGELOG.txt" << EOF
# Changelog

## [${VERSION}] - $(date +%Y-%m-%d)

### Added
- Phase 1: Hardware Adaptive Optimization (+17.2% performance)
- Phase 2: Safety Monitoring System (OOM protection)
- Automatic hardware detection
- Multi-tier performance profiles
- Real-time resource monitoring

### Package Info
- **Lite Edition**: Model file NOT included
- Model file requires separate download (~1.2GB)
- Reduced package size for faster distribution

### Documentation
- Complete user manual
- Installation guide
- Packaging and deployment guide

### Fixed
- Memory management improvements
- GPU cache optimization
- Error handling enhancements

================================================================================
EOF

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
    ARCHIVE_FILE="${RELEASE_NAME}.zip"
    echo "  ✓ ZIP archive created"
else
    tar -czf "${RELEASE_NAME}.tar.gz" "${RELEASE_NAME}/"
    ARCHIVE_FILE="${RELEASE_NAME}.tar.gz"
    echo "  ✓ TAR.GZ archive created"
fi
cd - >/dev/null

# 9. 生成校验和
echo ""
echo "Generating checksums..."
cd "${DIST_DIR}"
sha256sum "${ARCHIVE_FILE}" > "${ARCHIVE_FILE}.sha256"
cd - >/dev/null

# 10. 完成
echo ""
echo "=========================================="
echo "✓ LITE Package created successfully!"
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

echo "Model file:   NOT included (separate download required)"
echo ""
echo "⚠️  IMPORTANT:"
echo "  Users must download model file separately (~1.2GB)"
echo "  Download instructions: nb10_windows/models/README.md"
echo ""
echo "Next steps:"
echo "  1. Prepare model file for separate distribution"
echo "  2. Update model download links in:"
echo "     - nb10_windows/models/README.md"
echo "     - nb10_windows/models/DOWNLOAD_MODEL.txt"
echo "  3. Test the lite package on Windows"
echo "  4. Distribute both:"
echo "     - ${ARCHIVE_FILE} (app, ~300MB)"
echo "     - va_non_gated_ai_cac_model.pth (model, ~1.2GB)"
echo ""
