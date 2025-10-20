# NB10 在 Linux/WSL 环境下的使用指南

## ⚠️ 重要提示

**`.bat` 文件是 Windows 批处理文件，不能在 Linux/WSL bash 中直接执行！**

在 VS Code 的 WSL Terminal 中，请使用 `.sh` 文件或直接调用 Python。

---

## 🎯 在 WSL/Linux 环境下的正确使用方法

### 方法1: 使用 Shell 脚本（推荐）⭐⭐⭐⭐⭐

```bash
cd /home/wuxia/projects/.../tools/nb10_windows

# 使用 Linux shell 脚本
./nb10.sh              # 显示交互式菜单
./nb10.sh test         # 快速测试 (5例)
./nb10.sh chd          # 处理CHD组
./nb10.sh normal       # 处理Normal组
./nb10.sh analyze      # 统计分析
./nb10.sh config       # 查看配置
./nb10.sh help         # 显示帮助
```

**特点**：
- ✅ 功能完整的菜单系统
- ✅ 自动日志记录
- ✅ 中文界面
- ✅ 与 `nb10.bat` 功能完全相同

---

### 方法2: 直接调用 Python（最灵活）⭐⭐⭐⭐⭐

```bash
cd /home/wuxia/projects/.../tools/nb10_windows

# 激活虚拟环境
source venv/bin/activate

# 快速测试
python cli/run_nb10.py --mode pilot --pilot-limit 5

# 完整处理
python cli/run_nb10.py --mode full

# 自定义数据目录
python cli/run_nb10.py --data-dir /path/to/data --mode pilot

# 查看所有选项
python cli/run_nb10.py --help
```

**特点**：
- ✅ 最大灵活性
- ✅ 可精确控制所有参数
- ✅ 适合脚本化和自动化
- ✅ 跨平台兼容

---

### 方法3: 使用 Python 菜单

```bash
cd /home/wuxia/projects/.../tools/nb10_windows
python menu.py
```

**特点**：
- ✅ 跨平台交互式菜单
- ✅ Python 编写，兼容性好

---

## 📋 快速参考

### 常用命令速查

```bash
# 进入工作目录
cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/nb10_windows

# === Shell 脚本方式 ===
./nb10.sh test         # 快速测试5例
./nb10.sh chd          # 处理CHD组
./nb10.sh normal       # 处理Normal组
./nb10.sh analyze      # CHD vs Normal 对比分析

# === Python 直调方式 ===
source venv/bin/activate
python cli/run_nb10.py --mode pilot --pilot-limit 5
python cli/run_nb10.py --config config/config.yaml --mode full
python cli/run_nb10.py --data-dir /mnt/d/Data --mode pilot
```

---

## ⚠️ 错误和解决方案

### 错误1: `./nb10.bat: 权限不够`

**原因**: `.bat` 文件是 Windows 文件，不能在 Linux 中执行

**解决**: 使用 `./nb10.sh` 代替

```bash
❌ 错误: ./nb10.bat
✅ 正确: ./nb10.sh
```

---

### 错误2: `@echo: not found`

**原因**: 尝试用 `sh` 命令执行 Windows `.bat` 文件

**解决**: 使用 shell 脚本或 Python

```bash
❌ 错误: sh ./nb10.bat
✅ 正确: ./nb10.sh
✅ 正确: python cli/run_nb10.py
```

---

### 错误3: `permission denied`

**原因**: 脚本没有执行权限

**解决**: 添加执行权限

```bash
chmod +x nb10.sh
./nb10.sh
```

---

## 🔄 .bat vs .sh 对照表

| Windows (.bat) | Linux/WSL (.sh) | Python (直调) |
|---------------|-----------------|---------------|
| `nb10.bat` | `./nb10.sh` | `python menu.py` |
| `nb10.bat test` | `./nb10.sh test` | `python cli/run_nb10.py --mode pilot` |
| `nb10.bat chd` | `./nb10.sh chd` | `python cli/run_nb10.py --mode full` |
| `nb10.bat help` | `./nb10.sh help` | `python cli/run_nb10.py --help` |

---

## 💡 VS Code WSL Terminal 最佳实践

### 您的环境

```
Windows 电脑
  ↓
VS Code (Windows)
  ↓
Remote-WSL 扩展
  ↓
WSL Terminal (Linux bash)
  ← 您在这里！
```

### 推荐使用方式

```bash
# 您已经在 Linux 环境中，所以应该：

✅ 使用 Linux 命令:
   cd /home/wuxia/...
   ls -la
   ./nb10.sh test

✅ 使用 Linux 路径:
   /home/wuxia/projects/...

✅ 使用 Linux shell 脚本:
   ./nb10.sh

❌ 不要使用 Windows 命令:
   dir          # 应该用 ls
   pushd        # 不需要，已经在 Linux 中
   nb10.bat     # 应该用 nb10.sh
```

---

## 🚀 完整工作流程示例

### 场景1: 快速测试

```bash
# 1. 进入工作目录
cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/nb10_windows

# 2. 运行快速测试
./nb10.sh test

# 或直接调用 Python
source venv/bin/activate
python cli/run_nb10.py --mode pilot --pilot-limit 5
```

### 场景2: 处理完整数据集

```bash
cd /home/wuxia/projects/.../tools/nb10_windows

# 方式1: 使用菜单
./nb10.sh chd

# 方式2: 直接调用
source venv/bin/activate
python cli/run_nb10.py --config config/config.yaml --mode full
```

### 场景3: 自定义数据处理

```bash
cd /home/wuxia/projects/.../tools/nb10_windows
source venv/bin/activate

python cli/run_nb10.py \
  --data-dir /mnt/d/MedicalData/DICOM \
  --output-dir /mnt/d/Results \
  --mode pilot \
  --pilot-limit 10
```

---

## 📚 相关文档

- [SCRIPT_MANAGEMENT_GUIDE.md](SCRIPT_MANAGEMENT_GUIDE.md) - 脚本管理和调用指南
- [VSCODE_TERMINAL_GUIDE.md](VSCODE_TERMINAL_GUIDE.md) - VS Code Terminal 使用指南
- [WINDOWS_ACCESS_GUIDE.md](WINDOWS_ACCESS_GUIDE.md) - Windows 访问 WSL 指南
- [docs/USER_MANUAL.md](docs/USER_MANUAL.md) - 用户手册

---

## 🎯 总结

### 在 VS Code WSL Terminal 中：

**推荐使用**（按优先级）：

1. ⭐⭐⭐⭐⭐ **Shell 脚本**: `./nb10.sh test`
   - 功能完整
   - 使用简单
   - 自动日志

2. ⭐⭐⭐⭐⭐ **Python 直调**: `python cli/run_nb10.py --mode pilot`
   - 最灵活
   - 精确控制
   - 适合自动化

3. ⭐⭐⭐⭐ **Python 菜单**: `python menu.py`
   - 跨平台
   - 交互式

**不要使用**：

- ❌ `./nb10.bat` - Windows 批处理文件，不能在 Linux 中运行
- ❌ `sh ./nb10.bat` - 会出错
- ❌ Windows CMD 命令 (pushd, dir等) - 您已在 Linux 环境中

---

**记住**: 在 VS Code WSL Terminal 中，您已经在完整的 Linux 环境中了，使用 Linux 的方式即可！

**文档版本**: v1.0
**更新日期**: 2025-10-16
