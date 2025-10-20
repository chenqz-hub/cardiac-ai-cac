#!/bin/bash
# ============================================================================
# NB10 AI-CAC 工具 - Linux/WSL 启动脚本
# 版本: 1.1.0
# 说明: 所有功能通过此脚本统一管理，支持日志记录和错误追踪
# ============================================================================

set -e

# 初始化环境
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs/menu"
CONFIG_DIR="${SCRIPT_DIR}/config"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/nb10_menu_${TIMESTAMP}.log"

# 创建日志目录
mkdir -p "${LOG_DIR}"

# 日志记录函数
log() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "${LOG_FILE}"
}

# 显示标题
show_header() {
    local title="$1"
    echo ""
    echo "========================================================================"
    echo "                          $title"
    echo "========================================================================"
}

# 显示结果
show_result() {
    local exit_code="$1"
    local task="$2"
    echo "========================================================================"
    if [ "$exit_code" -eq 0 ]; then
        echo "  ✓ ${task}成功完成！"
        echo "    结果文件: output/nb10_results_latest.csv"
        echo "    日志文件: logs/nb10_*.log"
    else
        echo "  ✗ ${task}失败！"
        echo "    退出码: $exit_code"
        echo "    请查看日志文件: ${LOG_FILE}"
    fi
    echo "========================================================================"
}

# 检查Python环境
log "INFO" "NB10 AI-CAC Tool v1.1.0 启动"
log "INFO" "工作目录: ${SCRIPT_DIR}"
log "INFO" "日志文件: ${LOG_FILE}"

log "INFO" "检查Python环境..."
PYTHON_CMD="../../venv/bin/python"
if [ ! -f "$PYTHON_CMD" ]; then
    log "ERROR" "未找到虚拟环境Python: $PYTHON_CMD"
    echo "错误: 未找到虚拟环境，请确保已创建 venv"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
log "INFO" "Python版本: ${PYTHON_VERSION}"

# 解析命令行参数
if [ $# -eq 0 ] || [ "$1" = "menu" ]; then
    ACTION="menu"
elif [ "$1" = "test" ]; then
    ACTION="test"
elif [ "$1" = "chd" ]; then
    ACTION="chd"
elif [ "$1" = "normal" ]; then
    ACTION="normal"
elif [ "$1" = "analyze" ]; then
    ACTION="analyze"
elif [ "$1" = "config" ]; then
    ACTION="config"
elif [ "$1" = "logs" ]; then
    ACTION="logs"
elif [ "$1" = "help" ]; then
    ACTION="help"
else
    log "WARN" "未知命令: $1"
    echo "未知命令: $1"
    echo "使用 './nb10.sh help' 查看帮助"
    exit 1
fi

# ============================================================================
# 主菜单
# ============================================================================
if [ "$ACTION" = "menu" ]; then
    log "INFO" "显示主菜单"
    clear
    show_header "NB10 AI-CAC 冠状动脉钙化评分工具"
    echo "                       统一管理界面 v1.1.0"
    echo "========================================================================"
    echo ""
    echo "  【快速处理】"
    echo "  1. 快速测试 (Pilot模式 - 5例)              [./nb10.sh test]"
    echo "  2. 处理CHD组 (完整模式)                     [./nb10.sh chd]"
    echo "  3. 处理Normal组 (完整模式)                  [./nb10.sh normal]"
    echo ""
    echo "  【统计分析】"
    echo "  4. CHD vs Normal组对比分析                 [./nb10.sh analyze]"
    echo ""
    echo "  【系统管理】"
    echo "  5. 查看系统配置                            [./nb10.sh config]"
    echo "  6. 查看操作日志                            [./nb10.sh logs]"
    echo "  7. 查看帮助文档                            [./nb10.sh help]"
    echo ""
    echo "  【高级功能】"
    echo "  8. Python交互式菜单 (跨平台)"
    echo "  9. 自定义数据目录处理"
    echo ""
    echo "  0. 退出程序"
    echo ""
    echo "========================================================================"
    echo "  提示: 所有操作都会自动记录到日志文件"
    echo "  当前日志: ${LOG_FILE}"
    echo "========================================================================"
    echo ""

    read -p "请选择操作 (0-9): " choice
    log "INFO" "用户选择: $choice"

    case $choice in
        1) ACTION="test" ;;
        2) ACTION="chd" ;;
        3) ACTION="normal" ;;
        4) ACTION="analyze" ;;
        5) ACTION="config" ;;
        6) ACTION="logs" ;;
        7) ACTION="help" ;;
        8) ACTION="python_menu" ;;
        9) ACTION="custom_dir" ;;
        0) ACTION="exit" ;;
        *)
            log "WARN" "无效选择: $choice"
            echo "无效选择，请重新运行"
            exit 1
            ;;
    esac
fi

# ============================================================================
# 1. 快速测试
# ============================================================================
if [ "$ACTION" = "test" ]; then
    log "INFO" "执行: 快速测试 (Pilot模式)"
    clear
    show_header "快速测试 (Pilot模式)"
    echo ""
    echo "此模式将处理5例患者数据，用于快速验证系统功能。"
    echo "预计耗时: 约2-3分钟"
    echo ""
    read -p "按Enter继续..."
    echo ""
    log "INFO" "开始执行: $PYTHON_CMD cli/run_calcium_scoring.py --mode pilot --pilot-limit 5"
    echo "正在运行快速测试..."
    echo ""

    echo "" | $PYTHON_CMD cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 5 2>&1 | tee -a "${LOG_FILE}"
    EXIT_CODE=${PIPESTATUS[0]}

    log "INFO" "快速测试完成，退出码: ${EXIT_CODE}"
    echo ""
    show_result ${EXIT_CODE} "快速测试"
    read -p "按Enter返回..."
    exec "$0" menu
fi

# ============================================================================
# 2. 处理CHD组
# ============================================================================
if [ "$ACTION" = "chd" ]; then
    log "INFO" "执行: 处理CHD组"
    clear
    show_header "处理CHD组数据"
    echo ""
    echo "配置文件: config/config.yaml"
    echo "处理模式: 完整模式 (Full)"
    echo "预计耗时: 约30-60分钟"
    echo ""
    echo "警告: 处理过程中请勿关闭窗口！"
    echo ""
    read -p "按Enter继续..."
    echo ""
    log "INFO" "开始执行: $PYTHON_CMD cli/run_calcium_scoring.py --config config/config.yaml --mode full"
    echo "正在处理CHD组数据..."
    echo ""

    echo "" | $PYTHON_CMD cli/run_calcium_scoring.py --config config/config.yaml --mode full 2>&1 | tee -a "${LOG_FILE}"
    EXIT_CODE=${PIPESTATUS[0]}

    log "INFO" "CHD组处理完成，退出码: ${EXIT_CODE}"
    echo ""
    show_result ${EXIT_CODE} "CHD组处理"
    read -p "按Enter返回..."
    exec "$0" menu
fi

# ============================================================================
# 3. 处理Normal组
# ============================================================================
if [ "$ACTION" = "normal" ]; then
    log "INFO" "执行: 处理Normal组"
    clear
    show_header "处理Normal组数据"
    echo ""
    echo "配置文件: config/config_normal.yaml"
    echo "处理模式: 完整模式 (Full)"
    echo "预计耗时: 约30-60分钟"
    echo ""
    echo "警告: 处理过程中请勿关闭窗口！"
    echo ""
    read -p "按Enter继续..."
    echo ""
    log "INFO" "开始执行: $PYTHON_CMD cli/run_calcium_scoring.py --config config/config_normal.yaml --mode full"
    echo "正在处理Normal组数据..."
    echo ""

    echo "" | $PYTHON_CMD cli/run_calcium_scoring.py --config config/config_normal.yaml --mode full 2>&1 | tee -a "${LOG_FILE}"
    EXIT_CODE=${PIPESTATUS[0]}

    log "INFO" "Normal组处理完成，退出码: ${EXIT_CODE}"
    echo ""
    show_result ${EXIT_CODE} "Normal组处理"
    read -p "按Enter返回..."
    exec "$0" menu
fi

# ============================================================================
# 4. CHD vs Normal对比分析
# ============================================================================
if [ "$ACTION" = "analyze" ]; then
    log "INFO" "执行: CHD vs Normal对比分析"
    clear
    show_header "CHD vs Normal组对比分析"
    echo ""
    echo "默认路径:"
    echo "  CHD组: output/chd/nb10_results_latest.csv"
    echo "  Normal组: output/normal/nb10_results_latest.csv"
    echo ""

    if [ ! -f "output/chd/nb10_results_latest.csv" ]; then
        log "ERROR" "CHD组结果文件不存在"
        echo "错误: CHD组结果文件不存在"
        echo "请先运行 './nb10.sh chd' 处理CHD组数据"
        read -p "按Enter返回..."
        exec "$0" menu
    fi

    if [ ! -f "output/normal/nb10_results_latest.csv" ]; then
        log "ERROR" "Normal组结果文件不存在"
        echo "错误: Normal组结果文件不存在"
        echo "请先运行 './nb10.sh normal' 处理Normal组数据"
        read -p "按Enter返回..."
        exec "$0" menu
    fi

    read -p "按Enter继续..."
    echo ""
    log "INFO" "开始执行: python scripts/analyze_chd_vs_normal.py"
    echo "正在进行统计分析..."
    echo ""

    python scripts/analyze_chd_vs_normal.py output/chd/nb10_results_latest.csv output/normal/nb10_results_latest.csv 2>&1 | tee -a "${LOG_FILE}"
    EXIT_CODE=${PIPESTATUS[0]}

    log "INFO" "统计分析完成，退出码: ${EXIT_CODE}"
    echo ""
    show_result ${EXIT_CODE} "统计分析"
    read -p "按Enter返回..."
    exec "$0" menu
fi

# ============================================================================
# 5. 查看系统配置
# ============================================================================
if [ "$ACTION" = "config" ]; then
    log "INFO" "执行: 查看系统配置"
    clear
    show_header "系统配置信息"
    echo ""
    echo "【Python环境】"
    python --version 2>&1 | tee -a "${LOG_FILE}"
    echo ""
    echo "【GPU信息】"
    $PYTHON_CMD -c "import torch; print(f'CUDA可用: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"无\"}') if torch.cuda.is_available() else print('未检测到GPU')" 2>&1 | tee -a "${LOG_FILE}"
    echo ""
    echo "【配置文件】"
    echo "CHD组: config/config.yaml"
    echo "Normal组: config/config_normal.yaml"
    echo ""
    echo "【工作目录】"
    echo "${SCRIPT_DIR}"
    echo ""
    echo "【日志目录】"
    echo "${LOG_DIR}"
    echo ""
    log "INFO" "系统配置查看完成"
    read -p "按Enter返回..."
    exec "$0" menu
fi

# ============================================================================
# 6. 查看操作日志
# ============================================================================
if [ "$ACTION" = "logs" ]; then
    log "INFO" "执行: 查看操作日志"
    clear
    show_header "操作日志"
    echo ""
    echo "【最近的5个菜单日志】"
    echo ""
    ls -t "${LOG_DIR}"/nb10_menu_*.log 2>/dev/null | head -5 | nl
    echo ""
    echo "【最近的5个处理日志】"
    echo ""
    ls -t logs/nb10_*.log 2>/dev/null | head -5 | nl
    echo ""
    read -p "输入要查看的日志序号 (1-5) 或按Enter返回: " log_choice
    if [ -n "$log_choice" ]; then
        # 可以添加查看特定日志的逻辑
        log "INFO" "查看日志: 序号 ${log_choice}"
    fi
    read -p "按Enter返回..."
    exec "$0" menu
fi

# ============================================================================
# 7. 显示帮助
# ============================================================================
if [ "$ACTION" = "help" ]; then
    log "INFO" "显示帮助信息"
    clear
    show_header "NB10 使用帮助"
    echo ""
    echo "【命令行用法】"
    echo "  ./nb10.sh           - 启动交互式菜单"
    echo "  ./nb10.sh menu      - 启动交互式菜单"
    echo "  ./nb10.sh test      - 快速测试 (5例)"
    echo "  ./nb10.sh chd       - 处理CHD组"
    echo "  ./nb10.sh normal    - 处理Normal组"
    echo "  ./nb10.sh analyze   - 统计分析对比"
    echo "  ./nb10.sh config    - 查看系统配置"
    echo "  ./nb10.sh logs      - 查看操作日志"
    echo "  ./nb10.sh help      - 显示帮助"
    echo ""
    echo "【直接调用Python】"
    echo "  $PYTHON_CMD cli/run_calcium_scoring.py --help"
    echo "  echo \"\" | $PYTHON_CMD cli/run_calcium_scoring.py --mode pilot --pilot-limit 5"
    echo "  echo \"\" | $PYTHON_CMD cli/run_calcium_scoring.py --mode full"
    echo ""
    echo "【配置文件】"
    echo "  config/config.yaml        - CHD组配置"
    echo "  config/config_normal.yaml - Normal组配置"
    echo ""
    echo "【日志文件】"
    echo "  logs/menu/nb10_menu_*.log - 菜单操作日志"
    echo "  logs/nb10_*.log           - 数据处理日志"
    echo ""
    echo "【文档】"
    echo "  docs/USER_MANUAL.md       - 用户手册"
    echo "  SCRIPT_MANAGEMENT_GUIDE.md - 脚本管理指南"
    echo "  VSCODE_TERMINAL_GUIDE.md   - VS Code Terminal指南"
    echo ""
    log "INFO" "帮助信息显示完成"
    read -p "按Enter返回..."
    exec "$0" menu
fi

# ============================================================================
# 8. Python交互式菜单
# ============================================================================
if [ "$ACTION" = "python_menu" ]; then
    log "INFO" "执行: 启动Python交互式菜单"
    clear
    echo ""
    echo "正在启动Python交互式菜单..."
    echo ""
    log "INFO" "开始执行: $PYTHON_CMD menu.py"
    $PYTHON_CMD menu.py 2>&1 | tee -a "${LOG_FILE}"
    EXIT_CODE=${PIPESTATUS[0]}
    log "INFO" "Python菜单退出，退出码: ${EXIT_CODE}"
    exec "$0" menu
fi

# ============================================================================
# 9. 自定义数据目录
# ============================================================================
if [ "$ACTION" = "custom_dir" ]; then
    log "INFO" "执行: 自定义数据目录处理"
    clear
    show_header "自定义数据目录处理"
    echo ""
    echo "请输入数据目录的完整路径"
    echo "支持格式:"
    echo "  - Linux路径: /home/wuxia/data/DICOM"
    echo "  - WSL路径: /mnt/d/MedicalData/DICOM"
    echo ""
    read -p "数据目录: " data_dir
    log "INFO" "用户输入数据目录: ${data_dir}"

    if [ -z "$data_dir" ]; then
        log "WARN" "数据目录为空"
        echo "数据目录不能为空！"
        read -p "按Enter返回..."
        exec "$0" menu
    fi

    echo ""
    echo "处理模式:"
    echo "1. Pilot模式 (测试少量数据)"
    echo "2. Full模式 (处理全部数据)"
    echo ""
    read -p "选择模式 (1 或 2): " mode_choice
    log "INFO" "用户选择模式: ${mode_choice}"

    if [ "$mode_choice" = "1" ]; then
        mode="pilot"
        read -p "处理多少例? (默认10): " pilot_limit
        pilot_limit=${pilot_limit:-10}
        log "INFO" "Pilot模式，处理 ${pilot_limit} 例"
        extra_params="--pilot-limit ${pilot_limit}"
    else
        mode="full"
        log "INFO" "Full模式"
        extra_params=""
    fi

    echo ""
    echo "配置确认:"
    echo "  数据目录: ${data_dir}"
    echo "  处理模式: ${mode}"
    [ "$mode" = "pilot" ] && echo "  处理例数: ${pilot_limit}"
    echo ""
    read -p "按Enter继续..."
    echo ""
    log "INFO" "开始执行自定义数据处理"
    echo "正在处理数据..."
    echo ""

    echo "" | $PYTHON_CMD cli/run_calcium_scoring.py --config config/config.yaml --mode ${mode} --data-dir "${data_dir}" ${extra_params} 2>&1 | tee -a "${LOG_FILE}"
    EXIT_CODE=${PIPESTATUS[0]}

    log "INFO" "自定义数据处理完成，退出码: ${EXIT_CODE}"
    echo ""
    show_result ${EXIT_CODE} "数据处理"
    read -p "按Enter返回..."
    exec "$0" menu
fi

# ============================================================================
# 退出程序
# ============================================================================
if [ "$ACTION" = "exit" ]; then
    log "INFO" "用户退出程序"
    clear
    show_header "感谢使用 NB10 AI-CAC 工具"
    echo ""
    echo "如有问题，请查看:"
    echo "  - 操作日志: ${LOG_FILE}"
    echo "  - 处理日志: logs/nb10_*.log"
    echo "  - 用户手册: docs/USER_MANUAL.md"
    echo ""
    sleep 2
    exit 0
fi
