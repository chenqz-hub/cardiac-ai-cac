@echo off
chcp 65001 >nul
REM ====================================================================
REM Week 7 离线部署包打包脚本 (Windows版)
REM ====================================================================
REM 功能: 创建医院环境离线部署包
REM 版本: v1.0.0 (Week 7)
REM 创建日期: 2025-10-18
REM ====================================================================

echo ========================================
echo   冠脉钙化评分系统 - Week 7离线部署包
echo   版本: v2.0.0-alpha
echo   创建时间: %date% %time%
echo ========================================
echo.

REM ====================================================================
REM 1. 环境检查
REM ====================================================================
echo [1/7] 检查环境...

REM 检查当前目录
if not exist "calcium_scoring.bat" (
    if not exist "calcium_scoring.sh" (
        echo [错误] 请在 tools/cardiac_calcium_scoring 目录下运行此脚本
        pause
        exit /b 1
    )
)

REM 检查Python虚拟环境
if not exist "..\..\venv" (
    echo [错误] 未找到虚拟环境 ..\..\venv
    echo 请先运行: python -m venv ..\..\venv
    pause
    exit /b 1
)

REM 检查AI-CAC模型
if not exist "models\va_non_gated_ai_cac_model.pth" (
    echo [错误] AI-CAC模型文件缺失
    echo 请确认模型文件位于: models\va_non_gated_ai_cac_model.pth
    pause
    exit /b 1
)

echo [成功] AI-CAC模型已就绪
echo.

REM ====================================================================
REM 2. 创建发布目录
REM ====================================================================
echo [2/7] 创建发布目录...

set RELEASE_NAME=cardiac_calcium_scoring_v2.0.0_week7_%date:~0,4%%date:~5,2%%date:~8,2%
set RELEASE_DIR=releases\%RELEASE_NAME%

REM 清理旧的发布目录(如果存在)
if exist "%RELEASE_DIR%" (
    echo 清理旧的发布目录...
    rmdir /s /q "%RELEASE_DIR%"
)

mkdir "%RELEASE_DIR%"
echo [成功] 创建发布目录: %RELEASE_DIR%
echo.

REM ====================================================================
REM 3. 打包依赖包
REM ====================================================================
echo [3/7] 下载Python依赖包 (离线安装用)...
echo.
echo 注意: 此步骤需要10-30分钟，请耐心等待...
echo.

mkdir "%RELEASE_DIR%\dependencies"

REM 激活虚拟环境并下载依赖
call ..\..\venv\Scripts\activate.bat

echo 下载依赖包到 %RELEASE_DIR%\dependencies ...
pip download -r deployment\requirements.txt -d "%RELEASE_DIR%\dependencies" --no-cache-dir

if errorlevel 1 (
    echo [错误] 依赖包下载失败
    pause
    exit /b 1
)

echo.
echo [成功] 依赖包下载完成
echo.

REM ====================================================================
REM 4. 复制核心文件
REM ====================================================================
echo [4/7] 复制核心文件...

xcopy /E /I /Q cli "%RELEASE_DIR%\cli"
xcopy /E /I /Q core "%RELEASE_DIR%\core"
xcopy /E /I /Q config "%RELEASE_DIR%\config"
xcopy /E /I /Q models "%RELEASE_DIR%\models"
xcopy /E /I /Q deployment "%RELEASE_DIR%\deployment"

REM 创建输出和日志目录
mkdir "%RELEASE_DIR%\output"
mkdir "%RELEASE_DIR%\logs"

REM 复制启动脚本
copy calcium_scoring.bat "%RELEASE_DIR%\" >nul
copy calcium_scoring.sh "%RELEASE_DIR%\" >nul
copy start_calcium_scoring.bat "%RELEASE_DIR%\" >nul
if exist menu.py copy menu.py "%RELEASE_DIR%\" >nul

REM 复制README和配置
if exist README.md (
    copy README.md "%RELEASE_DIR%\" >nul
) else (
    echo # 冠脉钙化评分系统 v2.0.0 > "%RELEASE_DIR%\README.md"
)
copy deployment\requirements.txt "%RELEASE_DIR%\" >nul

echo [成功] 核心文件复制完成
echo.

REM ====================================================================
REM 5. 复制部署文档
REM ====================================================================
echo [5/7] 复制部署文档...

mkdir "%RELEASE_DIR%\docs"

if exist "..\..\docs\deployment\DEPLOYMENT_GUIDE.md" copy "..\..\docs\deployment\DEPLOYMENT_GUIDE.md" "%RELEASE_DIR%\docs\" >nul
if exist "..\..\docs\deployment\USER_MANUAL.md" copy "..\..\docs\deployment\USER_MANUAL.md" "%RELEASE_DIR%\docs\" >nul
if exist "..\..\docs\deployment\TECHNICAL_SPECS.md" copy "..\..\docs\deployment\TECHNICAL_SPECS.md" "%RELEASE_DIR%\docs\" >nul
if exist "..\..\docs\deployment\FAQ.md" copy "..\..\docs\deployment\FAQ.md" "%RELEASE_DIR%\docs\" >nul
if exist "..\..\WEEK6_PROGRESS.md" copy "..\..\WEEK6_PROGRESS.md" "%RELEASE_DIR%\docs\" >nul

echo [成功] 部署文档复制完成
echo.

REM ====================================================================
REM 6. 创建安装脚本
REM ====================================================================
echo [6/7] 创建离线安装脚本...

REM Windows安装脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo echo ========================================
echo echo 冠脉钙化评分系统 - 离线安装
echo echo 版本: v2.0.0-alpha
echo echo ========================================
echo echo.
echo.
echo python --version ^>nul 2^>^&1
echo if errorlevel 1 ^(
echo     echo [错误] 未找到Python，请先安装Python 3.10+
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo [1/4] 创建虚拟环境...
echo python -m venv venv
echo.
echo echo [2/4] 激活虚拟环境...
echo call venv\Scripts\activate.bat
echo.
echo echo [3/4] 安装依赖包 ^(离线模式^)...
echo pip install --no-index --find-links=dependencies -r requirements.txt
echo.
echo echo [4/4] 验证安装...
echo python -c "import torch; import nibabel; print('成功')"
echo.
echo echo ========================================
echo echo 安装完成！
echo echo.
echo echo 使用说明:
echo echo   双击 start_calcium_scoring.bat 启动
echo echo.
echo echo 文档位置: docs\
echo echo ========================================
echo pause
) > "%RELEASE_DIR%\install_offline.bat"

echo [成功] 安装脚本创建完成
echo.

REM ====================================================================
REM 7. 创建README
REM ====================================================================
echo [7/7] 生成部署说明...

(
echo # 冠脉钙化评分系统 v2.0.0 - 离线部署包
echo.
echo ## 快速开始 ^(Windows系统^)
echo.
echo ### 1. 安装
echo ```cmd
echo 双击运行: install_offline.bat
echo ```
echo.
echo ### 2. 启动
echo ```cmd
echo 双击运行: start_calcium_scoring.bat
echo ```
echo.
echo ## 系统要求
echo.
echo ### 最低配置
echo - **操作系统**: Windows 10/11
echo - **Python**: 3.10+
echo - **内存**: 8GB RAM
echo - **处理器**: 2核心 CPU
echo - **磁盘空间**: 10GB可用空间
echo.
echo ### 推荐配置
echo - **操作系统**: Windows 10/11 Pro
echo - **Python**: 3.10+
echo - **内存**: 16GB+ RAM
echo - **处理器**: 8核心+ CPU
echo - **GPU**: NVIDIA RTX 2060 或更高
echo - **磁盘空间**: 20GB可用空间
echo.
echo ## Week 6测试结果
echo.
echo - **总测试**: 196/197例成功 ^(99.5%%^)
echo - **CHD组**: 100/101成功 - 平均评分356.6
echo - **Normal组**: 96/96成功 - 平均评分6.3
echo - **性能**: GPU 15秒/患者, CPU 305秒/患者
echo.
echo 详见: docs\WEEK6_PROGRESS.md
echo.
echo ## 文档
echo.
echo - **DEPLOYMENT_GUIDE.md** - IT管理员部署指南
echo - **USER_MANUAL.md** - 医生/技术员用户手册
echo - **TECHNICAL_SPECS.md** - 技术规格文档
echo - **FAQ.md** - 常见问题解答
echo.
echo ## 版本信息
echo.
echo - **版本**: v2.0.0-alpha ^(Week 7离线部署版^)
echo - **发布日期**: 2025-10-18
echo - **验证状态**: 生产就绪 ^(196例完整测试通过^)
) > "%RELEASE_DIR%\README_DEPLOYMENT.md"

echo [成功] 部署说明生成完成
echo.

REM ====================================================================
REM 8. 生成发布报告
REM ====================================================================
echo 生成发布报告...

(
echo ====================================================================
echo 冠脉钙化评分系统 v2.0.0-alpha - Week 7离线部署包
echo ====================================================================
echo 发布日期: %date% %time%
echo 发布类型: Week 7医院试点部署包
echo.
echo 版本信息
echo --------
echo - 版本号: v2.0.0-alpha
echo - 代码名称: cardiac_calcium_scoring
echo - 验证状态: 生产就绪 ^(99.5%%成功率, 196/197例^)
echo.
echo 包内容
echo ------
echo 1. 核心程序
echo    - CLI命令行界面
echo    - 核心模块
echo    - AI-CAC模型 ^(~450MB^)
echo    - 配置文件
echo.
echo 2. Python依赖包 ^(离线安装^)
echo    - 见 dependencies\ 目录
echo.
echo 3. 完整文档
echo    - DEPLOYMENT_GUIDE.md ^(IT管理员部署指南^)
echo    - USER_MANUAL.md ^(用户手册^)
echo    - TECHNICAL_SPECS.md ^(技术规格^)
echo    - FAQ.md ^(常见问题^)
echo    - WEEK6_PROGRESS.md ^(Week 6测试报告^)
echo.
echo 性能指标 ^(Week 6测试^)
echo ---------------------
echo - 测试规模: 196/197例成功 ^(99.5%%^)
echo - CHD组: 100/101成功, 平均评分356.6
echo - Normal组: 96/96成功, 平均评分6.3
echo - GPU性能: 15秒/患者 ^(RTX 2060^)
echo - CPU性能: 305秒/患者 ^(8核CPU^)
echo.
echo 系统要求
echo --------
echo 最低配置:
echo - Python 3.10+
echo - 8GB RAM
echo - 2核心 CPU
echo - 10GB磁盘空间
echo.
echo 推荐配置:
echo - Python 3.10+
echo - 16GB+ RAM
echo - 8核心+ CPU
echo - NVIDIA GPU ^(可选^)
echo - 20GB磁盘空间
echo.
echo 安装步骤
echo --------
echo 1. 解压发布包
echo 2. 运行 install_offline.bat
echo 3. 双击 start_calcium_scoring.bat
echo.
echo 技术支持
echo --------
echo - 完整文档: 见 docs\ 目录
echo - 运行日志: 见 logs\ 目录
echo - FAQ: docs\FAQ.md
echo.
echo ====================================================================
echo Generated with Claude Code
echo ====================================================================
) > "releases\%RELEASE_NAME%_release_notes.txt"

echo [成功] 发布报告生成完成
echo.

REM ====================================================================
REM 完成
REM ====================================================================
echo ========================================
echo   打包完成！
echo ========================================
echo.
echo 发布包位置:
echo   - releases\%RELEASE_NAME%\
echo.
echo 发布说明:
echo   - releases\%RELEASE_NAME%_release_notes.txt
echo.
echo 下一步:
echo   1. 测试发布包: cd releases\%RELEASE_NAME%
echo   2. 运行安装: install_offline.bat
echo   3. 准备医院试点部署
echo.
echo 注意: 如需压缩为ZIP，请手动压缩 releases\%RELEASE_NAME% 文件夹
echo.
pause
