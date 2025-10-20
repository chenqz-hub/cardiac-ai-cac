@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================================
:: NB10 AI-CAC 工具 - 统一启动入口
:: 版本: 1.1.0
:: 说明: 所有功能通过此脚本统一管理，支持日志记录和错误追踪
:: ============================================================================

:: 初始化环境
set "SCRIPT_DIR=%~dp0"
set "LOG_DIR=%SCRIPT_DIR%logs\menu"
set "CONFIG_DIR=%SCRIPT_DIR%config"
set "TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"
set "LOG_FILE=%LOG_DIR%\nb10_menu_%TIMESTAMP%.log"

:: 创建日志目录
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: 记录启动日志
call :log "INFO" "NB10 AI-CAC Tool v1.1.0 启动"
call :log "INFO" "工作目录: %SCRIPT_DIR%"
call :log "INFO" "日志文件: %LOG_FILE%"

:: 检查Python环境
call :log "INFO" "检查Python环境..."
python --version >nul 2>&1
if errorlevel 1 (
    call :log "ERROR" "未找到Python环境"
    call :show_error "未找到Python" "请确保已安装Python 3.10并添加到系统PATH"
    exit /b 1
)

:: 获取Python版本
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
call :log "INFO" "Python版本: %PYTHON_VERSION%"

:: 解析命令行参数
if "%~1"=="" goto MAIN_MENU
if /i "%~1"=="menu" goto MAIN_MENU
if /i "%~1"=="test" goto QUICK_TEST
if /i "%~1"=="chd" goto PROCESS_CHD
if /i "%~1"=="normal" goto PROCESS_NORMAL
if /i "%~1"=="analyze" goto COMPARE_ANALYSIS
if /i "%~1"=="config" goto VIEW_CONFIG
if /i "%~1"=="logs" goto VIEW_LOGS
if /i "%~1"=="help" goto SHOW_HELP

:: 未知命令
call :log "WARN" "未知命令: %~1"
echo 未知命令: %~1
echo 使用 'nb10 help' 查看帮助
pause
exit /b 1

:: ============================================================================
:: 主菜单
:: ============================================================================
:MAIN_MENU
call :log "INFO" "显示主菜单"
cls
echo.
echo ========================================================================
echo                 NB10 AI-CAC 冠状动脉钙化评分工具
echo                       统一管理界面 v1.1.0
echo ========================================================================
echo.
echo  【快速处理】
echo  1. 快速测试 (Pilot模式 - 5例)              [nb10 test]
echo  2. 处理CHD组 (完整模式)                     [nb10 chd]
echo  3. 处理Normal组 (完整模式)                  [nb10 normal]
echo.
echo  【统计分析】
echo  4. CHD vs Normal组对比分析                 [nb10 analyze]
echo.
echo  【系统管理】
echo  5. 查看系统配置                            [nb10 config]
echo  6. 查看操作日志                            [nb10 logs]
echo  7. 查看帮助文档                            [nb10 help]
echo.
echo  【高级功能】
echo  8. Python交互式菜单 (跨平台)
echo  9. 自定义数据目录处理
echo.
echo  0. 退出程序
echo.
echo ========================================================================
echo  提示: 所有操作都会自动记录到日志文件
echo  当前日志: logs\menu\nb10_menu_%TIMESTAMP%.log
echo ========================================================================
echo.

set /p choice="请选择操作 (0-9): "
call :log "INFO" "用户选择: %choice%"

if "%choice%"=="1" goto QUICK_TEST
if "%choice%"=="2" goto PROCESS_CHD
if "%choice%"=="3" goto PROCESS_NORMAL
if "%choice%"=="4" goto COMPARE_ANALYSIS
if "%choice%"=="5" goto VIEW_CONFIG
if "%choice%"=="6" goto VIEW_LOGS
if "%choice%"=="7" goto SHOW_HELP
if "%choice%"=="8" goto PYTHON_MENU
if "%choice%"=="9" goto CUSTOM_DIR
if "%choice%"=="0" goto EXIT
goto INVALID_CHOICE

:: ============================================================================
:: 1. 快速测试
:: ============================================================================
:QUICK_TEST
call :log "INFO" "执行: 快速测试 (Pilot模式)"
cls
call :show_header "快速测试 (Pilot模式)"
echo.
echo 此模式将处理5例患者数据，用于快速验证系统功能。
echo 预计耗时: 约2-3分钟
echo.
pause
echo.
call :log "INFO" "开始执行: python cli\run_nb10.py --mode pilot --pilot-limit 5"
echo 正在运行快速测试...
echo.
python cli\run_nb10.py --config config\config.yaml --mode pilot --pilot-limit 5 2>&1 | call :tee_log
set EXIT_CODE=!errorlevel!
call :log "INFO" "快速测试完成，退出码: !EXIT_CODE!"
echo.
call :show_result !EXIT_CODE! "快速测试"
pause
goto MAIN_MENU

:: ============================================================================
:: 2. 处理CHD组
:: ============================================================================
:PROCESS_CHD
call :log "INFO" "执行: 处理CHD组"
cls
call :show_header "处理CHD组数据"
echo.
echo 配置文件: config\config.yaml
echo 处理模式: 完整模式 (Full)
echo 预计耗时: 约30-60分钟
echo.
echo 警告: 处理过程中请勿关闭窗口！
echo.
pause
echo.
call :log "INFO" "开始执行: python cli\run_nb10.py --config config\config.yaml --mode full"
echo 正在处理CHD组数据...
echo.
python cli\run_nb10.py --config config\config.yaml --mode full 2>&1 | call :tee_log
set EXIT_CODE=!errorlevel!
call :log "INFO" "CHD组处理完成，退出码: !EXIT_CODE!"
echo.
call :show_result !EXIT_CODE! "CHD组处理"
pause
goto MAIN_MENU

:: ============================================================================
:: 3. 处理Normal组
:: ============================================================================
:PROCESS_NORMAL
call :log "INFO" "执行: 处理Normal组"
cls
call :show_header "处理Normal组数据"
echo.
echo 配置文件: config\config_normal.yaml
echo 处理模式: 完整模式 (Full)
echo 预计耗时: 约30-60分钟
echo.
echo 警告: 处理过程中请勿关闭窗口！
echo.
pause
echo.
call :log "INFO" "开始执行: python cli\run_nb10.py --config config\config_normal.yaml --mode full"
echo 正在处理Normal组数据...
echo.
python cli\run_nb10.py --config config\config_normal.yaml --mode full 2>&1 | call :tee_log
set EXIT_CODE=!errorlevel!
call :log "INFO" "Normal组处理完成，退出码: !EXIT_CODE!"
echo.
call :show_result !EXIT_CODE! "Normal组处理"
pause
goto MAIN_MENU

:: ============================================================================
:: 4. CHD vs Normal对比分析
:: ============================================================================
:COMPARE_ANALYSIS
call :log "INFO" "执行: CHD vs Normal对比分析"
cls
call :show_header "CHD vs Normal组对比分析"
echo.
echo 默认路径:
echo   CHD组: output\chd\nb10_results_latest.csv
echo   Normal组: output\normal\nb10_results_latest.csv
echo.
if not exist "output\chd\nb10_results_latest.csv" (
    call :log "ERROR" "CHD组结果文件不存在"
    call :show_error "CHD组结果文件不存在" "请先运行 'nb10 chd' 处理CHD组数据"
    pause
    goto MAIN_MENU
)
if not exist "output\normal\nb10_results_latest.csv" (
    call :log "ERROR" "Normal组结果文件不存在"
    call :show_error "Normal组结果文件不存在" "请先运行 'nb10 normal' 处理Normal组数据"
    pause
    goto MAIN_MENU
)
pause
echo.
call :log "INFO" "开始执行: python scripts\analyze_chd_vs_normal.py"
echo 正在进行统计分析...
echo.
python scripts\analyze_chd_vs_normal.py output\chd\nb10_results_latest.csv output\normal\nb10_results_latest.csv 2>&1 | call :tee_log
set EXIT_CODE=!errorlevel!
call :log "INFO" "统计分析完成，退出码: !EXIT_CODE!"
echo.
call :show_result !EXIT_CODE! "统计分析"
pause
goto MAIN_MENU

:: ============================================================================
:: 5. 查看系统配置
:: ============================================================================
:VIEW_CONFIG
call :log "INFO" "执行: 查看系统配置"
cls
call :show_header "系统配置信息"
echo.
echo 【Python环境】
python --version 2>&1 | call :tee_log
echo.
echo 【GPU信息】
python -c "import torch; print(f'CUDA可用: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"无\"}') if torch.cuda.is_available() else print('未检测到GPU')" 2>&1 | call :tee_log
echo.
echo 【配置文件】
echo CHD组: config\config.yaml
echo Normal组: config\config_normal.yaml
echo.
echo 【工作目录】
echo %SCRIPT_DIR%
echo.
echo 【日志目录】
echo %LOG_DIR%
echo.
call :log "INFO" "系统配置查看完成"
pause
goto MAIN_MENU

:: ============================================================================
:: 6. 查看操作日志
:: ============================================================================
:VIEW_LOGS
call :log "INFO" "执行: 查看操作日志"
cls
call :show_header "操作日志"
echo.
echo 【最近的5个菜单日志】
echo.
dir /b /o-d "%LOG_DIR%\nb10_menu_*.log" 2>nul | findstr /n "^" | findstr "^[1-5]:"
echo.
echo 【最近的5个处理日志】
echo.
dir /b /o-d "logs\nb10_*.log" 2>nul | findstr /n "^" | findstr "^[1-5]:"
echo.
set /p log_choice="输入要查看的日志序号 (1-5) 或按Enter返回: "
if "%log_choice%"=="" (
    call :log "INFO" "取消查看日志"
    goto MAIN_MENU
)
:: 这里可以添加查看特定日志的逻辑
call :log "INFO" "查看日志: 序号 %log_choice%"
pause
goto MAIN_MENU

:: ============================================================================
:: 7. 显示帮助
:: ============================================================================
:SHOW_HELP
call :log "INFO" "显示帮助信息"
cls
call :show_header "NB10 使用帮助"
echo.
echo 【命令行用法】
echo   nb10           - 启动交互式菜单
echo   nb10 menu      - 启动交互式菜单
echo   nb10 test      - 快速测试 (5例)
echo   nb10 chd       - 处理CHD组
echo   nb10 normal    - 处理Normal组
echo   nb10 analyze   - 统计分析对比
echo   nb10 config    - 查看系统配置
echo   nb10 logs      - 查看操作日志
echo   nb10 help      - 显示帮助
echo.
echo 【配置文件】
echo   config\config.yaml        - CHD组配置
echo   config\config_normal.yaml - Normal组配置
echo.
echo 【日志文件】
echo   logs\menu\nb10_menu_*.log - 菜单操作日志
echo   logs\nb10_*.log           - 数据处理日志
echo.
echo 【文档】
echo   Windows使用指南.md        - 完整使用指南
echo   docs\USER_MANUAL.md       - 用户手册
echo   docs\QUICK_REFERENCE_DATA_DIR.md - 快速参考
echo.
call :log "INFO" "帮助信息显示完成"
pause
goto MAIN_MENU

:: ============================================================================
:: 8. Python交互式菜单
:: ============================================================================
:PYTHON_MENU
call :log "INFO" "执行: 启动Python交互式菜单"
cls
echo.
echo 正在启动Python交互式菜单...
echo.
call :log "INFO" "开始执行: python menu.py"
python menu.py 2>&1 | call :tee_log
set EXIT_CODE=!errorlevel!
call :log "INFO" "Python菜单退出，退出码: !EXIT_CODE!"
goto MAIN_MENU

:: ============================================================================
:: 9. 自定义数据目录
:: ============================================================================
:CUSTOM_DIR
call :log "INFO" "执行: 自定义数据目录处理"
cls
call :show_header "自定义数据目录处理"
echo.
echo 请输入数据目录的完整路径
echo 支持格式:
echo   - Windows路径: D:\MedicalData\DICOM
echo   - WSL路径: /mnt/d/MedicalData/DICOM
echo.
set /p data_dir="数据目录: "
call :log "INFO" "用户输入数据目录: %data_dir%"
if "%data_dir%"=="" (
    call :log "WARN" "数据目录为空"
    echo 数据目录不能为空！
    pause
    goto MAIN_MENU
)
echo.
echo 处理模式:
echo 1. Pilot模式 (测试少量数据)
echo 2. Full模式 (处理全部数据)
echo.
set /p mode_choice="选择模式 (1 或 2): "
call :log "INFO" "用户选择模式: %mode_choice%"
if "%mode_choice%"=="1" (
    set mode=pilot
    set /p pilot_limit="处理多少例? (默认10): "
    if "!pilot_limit!"=="" set pilot_limit=10
    call :log "INFO" "Pilot模式，处理 !pilot_limit! 例"
    set extra_params=--pilot-limit !pilot_limit!
) else (
    set mode=full
    call :log "INFO" "Full模式"
    set extra_params=
)
echo.
echo 配置确认:
echo   数据目录: %data_dir%
echo   处理模式: %mode%
if "%mode%"=="pilot" echo   处理例数: !pilot_limit!
echo.
pause
echo.
call :log "INFO" "开始执行自定义数据处理"
echo 正在处理数据...
echo.
python cli\run_nb10.py --config config\config.yaml --mode %mode% --data-dir "%data_dir%" %extra_params% 2>&1 | call :tee_log
set EXIT_CODE=!errorlevel!
call :log "INFO" "自定义数据处理完成，退出码: !EXIT_CODE!"
echo.
call :show_result !EXIT_CODE! "数据处理"
pause
goto MAIN_MENU

:: ============================================================================
:: 无效选择
:: ============================================================================
:INVALID_CHOICE
call :log "WARN" "无效选择: %choice%"
echo.
echo 无效选择，请重新输入！
timeout /t 2 >nul
goto MAIN_MENU

:: ============================================================================
:: 退出程序
:: ============================================================================
:EXIT
call :log "INFO" "用户退出程序"
cls
call :show_header "感谢使用 NB10 AI-CAC 工具"
echo.
echo 如有问题，请查看:
echo   - 操作日志: %LOG_FILE%
echo   - 处理日志: logs\nb10_*.log
echo   - 用户手册: docs\USER_MANUAL.md
echo.
timeout /t 3
exit /b 0

:: ============================================================================
:: 辅助函数
:: ============================================================================

:: 日志记录函数
:log
set "LEVEL=%~1"
set "MESSAGE=%~2"
set "LOG_TIME=%date% %time:~0,8%"
echo [%LOG_TIME%] [%LEVEL%] %MESSAGE% >> "%LOG_FILE%"
goto :eof

:: 同时输出到屏幕和日志
:tee_log
for /f "delims=" %%i in ('more') do (
    echo %%i
    echo [%date% %time:~0,8%] [OUTPUT] %%i >> "%LOG_FILE%"
)
goto :eof

:: 显示标题
:show_header
echo.
echo ========================================================================
echo                          %~1
echo ========================================================================
goto :eof

:: 显示结果
:show_result
set "CODE=%~1"
set "TASK=%~2"
echo ========================================================================
if "%CODE%"=="0" (
    echo  ✓ %TASK%成功完成！
    echo    结果文件: output\nb10_results_latest.csv
    echo    日志文件: logs\nb10_*.log
) else (
    echo  ✗ %TASK%失败！
    echo    退出码: %CODE%
    echo    请查看日志文件: %LOG_FILE%
)
echo ========================================================================
goto :eof

:: 显示错误
:show_error
set "ERROR_TITLE=%~1"
set "ERROR_MSG=%~2"
echo.
echo ========================================================================
echo  ✗ 错误: %ERROR_TITLE%
echo ========================================================================
echo.
echo %ERROR_MSG%
echo.
goto :eof
