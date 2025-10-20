#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NB10 AI-CAC 冠状动脉钙化评分工具 - 交互式菜单系统
支持Windows和Linux/WSL环境
版本: 1.0.0
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

# 颜色代码（ANSI）
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def clear_screen():
    """清屏"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')


def pause(message="按Enter键继续..."):
    """暂停并等待用户输入"""
    input(f"\n{message}")


def print_header(title):
    """打印标题"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_section(title):
    """打印章节标题"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}【{title}】{Colors.ENDC}")


def print_success(message):
    """打印成功消息"""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")


def print_error(message):
    """打印错误消息"""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")


def print_warning(message):
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")


def run_command(command, shell=False):
    """运行命令并显示输出"""
    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=True, capture_output=False, text=True)
        else:
            result = subprocess.run(command, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print_error(f"命令执行失败: {e}")
        return False


def main_menu():
    """主菜单"""
    while True:
        clear_screen()
        print_header("NB10 AI-CAC 冠状动脉钙化评分工具 v1.0.0")

        print_section("快速处理")
        print("  1. 快速测试 (Pilot模式 - 处理5例)")
        print("  2. 处理CHD组 (完整模式)")
        print("  3. 处理Normal组 (完整模式)")
        print("  4. 自定义数据目录处理")

        print_section("统计分析")
        print("  5. CHD vs Normal组对比分析")
        print("  6. 查看最新处理结果")

        print_section("配置管理")
        print("  7. 编辑CHD组配置文件")
        print("  8. 编辑Normal组配置文件")
        print("  9. 查看系统配置")

        print_section("工具与帮助")
        print("  A. 查看用户手册")
        print("  B. 查看快速参考卡")
        print("  C. 检查硬件配置")
        print("  D. 查看日志文件")

        print(f"\n  {Colors.RED}0. 退出程序{Colors.ENDC}")
        print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

        choice = input("请选择操作 (0-9/A-D): ").strip().upper()

        if choice == '1':
            pilot_test()
        elif choice == '2':
            process_chd()
        elif choice == '3':
            process_normal()
        elif choice == '4':
            custom_dir_process()
        elif choice == '5':
            compare_analysis()
        elif choice == '6':
            view_results()
        elif choice == '7':
            edit_config('config/config.yaml', 'CHD组')
        elif choice == '8':
            edit_config('config/config_normal.yaml', 'Normal组')
        elif choice == '9':
            view_system_config()
        elif choice == 'A':
            view_manual()
        elif choice == 'B':
            view_quickref()
        elif choice == 'C':
            check_hardware()
        elif choice == 'D':
            view_logs()
        elif choice == '0':
            exit_program()
        else:
            print_error("无效选择，请重新输入！")
            pause()


def pilot_test():
    """快速测试"""
    clear_screen()
    print_header("快速测试 (Pilot模式)")

    print("此模式将处理5例患者数据，用于快速验证系统功能。")
    print("预计耗时: 约2-3分钟\n")
    pause("按Enter键开始测试...")

    print("\n正在运行快速测试...\n")
    success = run_command('echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 5')

    print("\n" + "="*80)
    if success:
        print_success("快速测试完成！")
    else:
        print_error("快速测试失败！请查看错误信息。")
    print("="*80)

    print("\n结果文件: output/nb10_results_latest.csv")
    print("日志文件: logs/nb10_*.log")
    pause()


def process_chd():
    """处理CHD组"""
    clear_screen()
    print_header("处理CHD组数据")

    print("数据目录: 从config.yaml读取")
    print("处理模式: 完整模式 (Full)")
    print("预计耗时: 约30-60分钟 (取决于数据量和硬件)\n")
    print_warning("处理过程中请勿关闭窗口！")

    pause("按Enter键开始处理...")

    print("\n正在处理CHD组数据...\n")
    success = run_command('echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode full')

    print("\n" + "="*80)
    if success:
        print_success("CHD组处理完成！")
    else:
        print_error("CHD组处理失败！请查看错误信息。")
    print("="*80)

    print("\n结果文件: output/nb10_results_latest.csv")
    print("日志文件: logs/nb10_*.log")
    pause()


def process_normal():
    """处理Normal组"""
    clear_screen()
    print_header("处理Normal组数据")

    print("数据目录: 从config_normal.yaml读取")
    print("处理模式: 完整模式 (Full)")
    print("预计耗时: 约30-60分钟 (取决于数据量和硬件)\n")
    print_warning("处理过程中请勿关闭窗口！")

    pause("按Enter键开始处理...")

    print("\n正在处理Normal组数据...\n")
    success = run_command('echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config_normal.yaml --mode full')

    print("\n" + "="*80)
    if success:
        print_success("Normal组处理完成！")
    else:
        print_error("Normal组处理失败！请查看错误信息。")
    print("="*80)

    print("\n结果文件: output/nb10_results_latest.csv")
    print("日志文件: logs/nb10_*.log")
    pause()


def custom_dir_process():
    """自定义数据目录处理"""
    clear_screen()
    print_header("自定义数据目录处理")

    print("请输入数据目录的完整路径。")
    print("支持格式:")
    print("  - Windows路径: D:\\MedicalData\\DICOM\\patient_data")
    print("  - WSL路径: /mnt/d/MedicalData/DICOM/patient_data\n")

    data_dir = input("数据目录路径: ").strip()
    if not data_dir:
        print_error("路径不能为空！")
        pause()
        return

    print("\n请选择处理模式:")
    print("1. Pilot模式 (测试少量数据)")
    print("2. Full模式 (处理全部数据)")

    mode_choice = input("\n选择模式 (1 或 2): ").strip()

    if mode_choice == '1':
        mode = 'pilot'
        pilot_limit = input("处理多少例? (默认10): ").strip()
        pilot_limit = pilot_limit if pilot_limit else '10'
        extra_params = f"--pilot-limit {pilot_limit}"
    else:
        mode = 'full'
        extra_params = ''
        pilot_limit = None

    print("\n配置确认:")
    print(f"  数据目录: {data_dir}")
    print(f"  处理模式: {mode}")
    if mode == 'pilot':
        print(f"  处理例数: {pilot_limit}")

    pause("\n按Enter键开始处理...")

    print("\n正在处理数据...\n")
    cmd = f'echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode {mode} --data-dir "{data_dir}" {extra_params}'
    success = run_command(cmd)

    print("\n" + "="*80)
    if success:
        print_success("处理完成！")
    else:
        print_error("处理失败！请查看错误信息。")
    print("="*80)

    print("\n结果文件: output/nb10_results_latest.csv")
    pause()


def compare_analysis():
    """CHD vs Normal组对比分析"""
    clear_screen()
    print_header("CHD vs Normal组对比分析")

    print("请确保已经处理完CHD组和Normal组的数据。\n")
    print("默认路径:")
    print("  CHD组结果: output/chd/nb10_results_latest.csv")
    print("  Normal组结果: output/normal/nb10_results_latest.csv\n")

    print("是否使用默认路径?")
    print("1. 是，使用默认路径")
    print("2. 否，手动指定路径")

    choice = input("\n选择 (1 或 2): ").strip()

    if choice == '1':
        chd_file = 'output/chd/nb10_results_latest.csv'
        normal_file = 'output/normal/nb10_results_latest.csv'
    else:
        chd_file = input("CHD组CSV文件路径: ").strip()
        normal_file = input("Normal组CSV文件路径: ").strip()

    if not os.path.exists(chd_file):
        print_error(f"CHD组文件不存在: {chd_file}")
        pause()
        return

    if not os.path.exists(normal_file):
        print_error(f"Normal组文件不存在: {normal_file}")
        pause()
        return

    print("\n正在进行统计分析...\n")
    success = run_command(f'python scripts/analyze_chd_vs_normal.py "{chd_file}" "{normal_file}"')

    print("\n" + "="*80)
    if success:
        print_success("分析完成！")
    else:
        print_error("分析失败！")
    print("="*80)
    pause()


def view_results():
    """查看最新处理结果"""
    clear_screen()
    print_header("查看最新处理结果")

    print("选择要查看的结果文件:")
    print("1. 最新结果 (output/nb10_results_latest.csv)")
    print("2. CHD组结果 (output/chd/nb10_results_latest.csv)")
    print("3. Normal组结果 (output/normal/nb10_results_latest.csv)")
    print("4. 返回主菜单")

    choice = input("\n选择 (1-4): ").strip()

    file_map = {
        '1': 'output/nb10_results_latest.csv',
        '2': 'output/chd/nb10_results_latest.csv',
        '3': 'output/normal/nb10_results_latest.csv'
    }

    if choice == '4':
        return

    result_file = file_map.get(choice)
    if not result_file:
        print_error("无效选择！")
        pause()
        return

    if not os.path.exists(result_file):
        print_error(f"文件不存在: {result_file}")
        print("请先运行相应的数据处理。")
        pause()
        return

    print(f"\n正在打开: {result_file}\n")

    if platform.system() == 'Windows':
        os.startfile(result_file)
    elif platform.system() == 'Darwin':  # macOS
        subprocess.run(['open', result_file])
    else:  # Linux
        subprocess.run(['xdg-open', result_file])

    print_success("文件已在默认程序中打开。")
    pause()


def edit_config(config_file, group_name):
    """编辑配置文件"""
    clear_screen()
    print_header(f"编辑{group_name}配置文件")

    if not os.path.exists(config_file):
        print_error(f"配置文件不存在: {config_file}")
        pause()
        return

    print(f"正在打开配置文件: {config_file}\n")

    editor = os.environ.get('EDITOR', 'notepad' if platform.system() == 'Windows' else 'nano')
    subprocess.run([editor, config_file])

    print("\n配置文件已关闭。")
    pause()


def view_system_config():
    """查看系统配置"""
    clear_screen()
    print_header("系统配置信息")

    print_section("Python版本")
    run_command("../../venv/bin/python --version")

    print_section("GPU信息")
    gpu_check = """
import torch
if torch.cuda.is_available():
    print(f"CUDA可用: True")
    print(f"GPU数量: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
else:
    print("CUDA可用: False (未检测到GPU)")
"""
    run_command(f'../../venv/bin/python -c "{gpu_check}"')

    print_section("项目路径")
    print(f"当前目录: {os.getcwd()}")

    print_section("配置文件")
    print("CHD组配置: config/config.yaml")
    print("Normal组配置: config/config_normal.yaml")

    print_section("输出目录")
    if os.path.exists('output'):
        print("output目录: 存在")
        try:
            files = os.listdir('output')
            for f in files[:10]:  # 显示前10个
                print(f"  - {f}")
        except:
            pass
    else:
        print("output目录: 不存在")

    print("\n" + "="*80)
    pause()


def view_manual():
    """查看用户手册"""
    clear_screen()
    print_header("用户手册")

    manual_file = 'docs/USER_MANUAL.md'
    if os.path.exists(manual_file):
        print("正在打开用户手册...\n")
        if platform.system() == 'Windows':
            os.startfile(manual_file)
        elif platform.system() == 'Darwin':
            subprocess.run(['open', manual_file])
        else:
            subprocess.run(['xdg-open', manual_file])
        print_success("用户手册已在默认编辑器中打开。")
    else:
        print_error(f"找不到用户手册文件: {manual_file}")

    pause()


def view_quickref():
    """查看快速参考卡"""
    clear_screen()
    print_header("快速参考卡")

    quickref_file = 'docs/QUICK_REFERENCE_DATA_DIR.md'
    if os.path.exists(quickref_file):
        print("正在打开快速参考卡...\n")
        if platform.system() == 'Windows':
            os.startfile(quickref_file)
        elif platform.system() == 'Darwin':
            subprocess.run(['open', quickref_file])
        else:
            subprocess.run(['xdg-open', quickref_file])
        print_success("快速参考卡已在默认编辑器中打开。")
    else:
        print_error(f"找不到快速参考卡文件: {quickref_file}")

    pause()


def check_hardware():
    """检查硬件配置"""
    clear_screen()
    print_header("硬件配置检查")

    print("正在检查硬件配置...\n")

    hardware_check = """
import torch
import psutil

print(f"【CPU】")
print(f"CPU核心数: {psutil.cpu_count(logical=False)}核 ({psutil.cpu_count()}线程)")
print(f"CPU使用率: {psutil.cpu_percent()}%")

print(f"\\n【内存】")
vm = psutil.virtual_memory()
print(f"总内存: {vm.total/1024**3:.1f}GB")
print(f"可用内存: {vm.available/1024**3:.1f}GB")
print(f"使用率: {vm.percent}%")

print(f"\\n【GPU】")
if torch.cuda.is_available():
    print(f"CUDA可用: True")
    for i in range(torch.cuda.device_count()):
        props = torch.cuda.get_device_properties(i)
        print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
        print(f"  显存: {props.total_memory/1024**3:.1f}GB")
else:
    print("CUDA可用: False (未检测到GPU)")
"""

    run_command(f'../../venv/bin/python -c "{hardware_check}"')

    print("\n" + "="*80)
    pause()


def view_logs():
    """查看日志文件"""
    clear_screen()
    print_header("查看日志文件")

    log_dir = Path('logs')
    if not log_dir.exists():
        print_error("logs目录不存在")
        pause()
        return

    log_files = sorted(log_dir.glob('nb10_*.log'), key=os.path.getmtime, reverse=True)[:5]

    if not log_files:
        print_error("没有找到日志文件")
        pause()
        return

    print("最近的5个日志文件:\n")
    for i, log_file in enumerate(log_files, 1):
        print(f"{i}. {log_file.name}")

    choice = input("\n输入要查看的日志序号 (1-5) 或按Enter返回: ").strip()

    if not choice:
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(log_files):
            log_file = log_files[idx]
            print(f"\n正在打开日志文件: {log_file.name}\n")

            editor = os.environ.get('EDITOR', 'notepad' if platform.system() == 'Windows' else 'less')
            subprocess.run([editor, str(log_file)])
        else:
            print_error("无效的序号！")
            pause()
    except ValueError:
        print_error("请输入有效的数字！")
        pause()


def exit_program():
    """退出程序"""
    clear_screen()
    print_header("感谢使用 NB10 AI-CAC 冠状动脉钙化评分工具")

    print("如有问题，请参考:")
    print("  - 用户手册: docs/USER_MANUAL.md")
    print("  - 快速参考: docs/QUICK_REFERENCE_DATA_DIR.md")
    print("  - GitHub: https://github.com/Raffi-Hagopian/AI-CAC")
    print()

    sys.exit(0)


if __name__ == '__main__':
    try:
        # 在Windows下启用ANSI颜色支持
        if platform.system() == 'Windows':
            os.system('color')

        main_menu()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断。")
        sys.exit(0)
    except Exception as e:
        print_error(f"程序发生错误: {e}")
        pause()
        sys.exit(1)
