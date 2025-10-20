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

if exist "nb10_windows\venv\Scripts\activate.bat" (
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
        set "INSTALL_SCRIPT=install_cpu.bat"
    ) else (
        echo [成功] 检测到NVIDIA GPU，将使用GPU模式
        echo [说明] GPU模式处理速度快（约20-30秒/例）
        set "GPU_MODE=gpu"
        set "INSTALL_SCRIPT=install_gpu.bat"
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

if not exist "nb10_windows\venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境未找到
    echo [说明] 安装可能未完成或失败
    echo [建议] 请删除venv目录后重新运行此脚本
    echo.
    pause
    exit /b 1
)

REM 激活虚拟环境并调用run_nb10.bat
call nb10_windows\venv\Scripts\activate.bat

REM 检查虚拟环境是否成功激活
python -c "import sys; sys.exit(0 if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 1)" 2>nul
if errorlevel 1 (
    echo [警告] 虚拟环境激活可能失败，尝试直接运行...
)

REM 切换到nb10_windows目录
cd nb10_windows

REM 调用实际的运行脚本
if exist "venv\Scripts\python.exe" (
    REM 直接使用虚拟环境的Python
    venv\Scripts\python.exe cli\run_nb10.py
) else (
    echo [错误] 虚拟环境中的Python未找到
    echo [路径] nb10_windows\venv\Scripts\python.exe
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
