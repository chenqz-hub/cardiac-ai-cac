# VS Code Terminal 使用指南 - NB10开发

> **💡 快速开始**: 如果您想直接运行应用程序，请查看：
> - [HOW_TO_RUN.md](../HOW_TO_RUN.md) - 如何运行应用（3种方法）
> - [MENU_GUIDE.md](../MENU_GUIDE.md) - 菜单系统完整指南
> - [VSCODE_QUICK_START.md](../VSCODE_QUICK_START.md) - VS Code快速入门

## 🎯 核心答案

**VS Code Terminal 和 Windows CMD映射WSL 不完全一样！**

关键区别：
- **VS Code Terminal**: 可以选择运行环境（WSL或Windows）
- **Windows CMD + pushd**: 始终在Windows环境中运行

---

## 📊 三种方式详细对比

### 对比表格

| 特性 | ① VS Code WSL Terminal | ② VS Code CMD Terminal | ③ Windows CMD + pushd |
|------|----------------------|----------------------|---------------------|
| **运行环境** | Linux (WSL) | Windows | Windows |
| **Shell类型** | bash/zsh | cmd.exe | cmd.exe |
| **当前目录显示** | `/home/wuxia/...` | `Z:\` | `Z:\` |
| **路径格式** | Linux格式 | Windows格式 | Windows格式 |
| **执行脚本** | `./nb10.bat` | `nb10.bat` | `nb10.bat` |
| **Python venv** | `source venv/bin/activate` | `venv\Scripts\activate.bat` | `venv\Scripts\activate.bat` |
| **文件权限** | Linux权限系统 | Windows权限 | Windows权限 |
| **性能** | 原生Linux速度 | 跨系统略慢 | 跨系统略慢 |
| **推荐程度** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

---

## 🔍 详细说明

### ① VS Code WSL Terminal（最推荐）⭐⭐⭐⭐⭐

#### 特点：
- ✅ **运行在真正的Linux环境中**
- ✅ 完整的Linux命令支持
- ✅ 原生性能，无跨系统开销
- ✅ 文件权限完全一致
- ✅ 最适合开发WSL项目

#### 如何使用：

**方法1: 打开WSL目录**
```bash
# 在VS Code中
File → Open Folder → 输入路径：
\\wsl.localhost\Ubuntu\home\wuxia\projects\family_management_hub\members\wife\medical_research\cardiac-ml-research

# VS Code会自动识别并使用WSL环境
```

**方法2: 使用WSL扩展**
1. 安装 "Remote - WSL" 扩展
2. 左下角点击绿色图标
3. 选择 "Connect to WSL"
4. 然后打开项目文件夹

**方法3: 命令行启动**
```bash
# 在WSL终端中
cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/nb10_windows
code .
```

#### 使用示例：

```bash
# VS Code WSL Terminal 显示：
wuxia@hostname:/home/wuxia/projects/.../tools/nb10_windows$

# 执行命令（Linux方式）
ls -la
./nb10.bat test
source venv/bin/activate
python cli/run_nb10.py --mode pilot
```

**优点**：
- ✅ 真正的Linux环境
- ✅ 所有Linux工具可用（grep, sed, awk等）
- ✅ 性能最佳
- ✅ 文件权限正确

**缺点**：
- ⚠️ 需要安装WSL扩展
- ⚠️ 第一次连接可能需要几秒钟

---

### ② VS Code CMD Terminal

#### 特点：
- 运行在Windows环境中
- 访问WSL文件需要映射驱动器
- 使用Windows命令

#### 如何使用：

**步骤1**: 打开CMD Terminal
- Terminal → New Terminal
- 选择 "Command Prompt"

**步骤2**: 映射WSL目录
```cmd
pushd \\wsl.localhost\Ubuntu\home\wuxia\projects\family_management_hub\members\wife\medical_research\cardiac-ml-research\tools\nb10_windows
```

#### 使用示例：

```cmd
# VS Code CMD Terminal 显示：
Z:\nb10_windows>

# 执行命令（Windows方式）
dir
nb10.bat test
venv\Scripts\activate.bat
python cli\run_nb10.py --mode pilot
```

**优点**：
- ✅ 不需要额外扩展
- ✅ 熟悉的Windows命令

**缺点**：
- ⚠️ 跨系统访问，性能略慢
- ⚠️ 文件权限可能不一致
- ⚠️ Linux命令不可用

---

### ③ Windows CMD + pushd（独立终端）

#### 特点：
- 独立的CMD窗口
- 不在VS Code中运行

#### 使用示例：

```cmd
# 打开独立的CMD窗口
C:\Users\YourName> pushd \\wsl.localhost\Ubuntu\home\wuxia\...

Z:\nb10_windows> nb10.bat test
```

**优点**：
- ✅ 独立窗口，不占用VS Code
- ✅ 简单直接

**缺点**：
- ⚠️ 需要切换窗口
- ⚠️ 不能利用VS Code集成

---

## 🎯 推荐方案：使用VS Code WSL Terminal

### 完整设置步骤

#### 步骤1: 安装WSL扩展

1. 打开VS Code
2. 按 `Ctrl+Shift+X` 打开扩展市场
3. 搜索 "Remote - WSL"
4. 点击 "Install"

#### 步骤2: 在WSL中打开项目

**方法A: 从WSL终端启动（推荐）**

```bash
# 在WSL Ubuntu终端中
cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research
code .
```

VS Code会自动：
- 连接到WSL
- 在Linux环境中打开项目
- Terminal自动使用bash

**方法B: 从VS Code连接**

1. 点击左下角绿色图标（><）
2. 选择 "Connect to WSL"
3. File → Open Folder
4. 输入：`/home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research`

#### 步骤3: 使用Terminal

```bash
# Terminal会自动显示为WSL bash
wuxia@hostname:~/projects/.../cardiac-ml-research$

# 进入工作目录
cd tools/cardiac_calcium_scoring

# 使用Linux命令（三种方式）
# 方式1: Bash菜单
bash calcium_scoring.sh test

# 方式2: Python菜单
../../venv/bin/python menu.py

# 方式3: 直接命令
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --mode pilot --pilot-limit 5
```

> **💡 提示**: 详细的运行方式说明请参考 [MENU_GUIDE.md](../MENU_GUIDE.md)

---

## 💡 实用技巧

### 技巧1: 设置默认Terminal为WSL

在VS Code中：

1. `Ctrl+Shift+P` 打开命令面板
2. 输入 "Terminal: Select Default Profile"
3. 选择 "Ubuntu (WSL)"

现在每次打开Terminal都会自动使用WSL bash！

---

### 技巧2: 在VS Code中切换Terminal类型

在Terminal面板右上角，点击下拉菜单：
- "Ubuntu (WSL)" - Linux环境 ⭐推荐
- "Command Prompt" - Windows CMD
- "PowerShell" - Windows PowerShell

---

### 技巧3: 同时使用多个Terminal

```bash
# Terminal 1: WSL bash
cd tools/nb10_windows
./nb10.bat test

# Terminal 2: WSL bash
cd tools/nb10_windows
tail -f logs/nb10_*.log

# 点击 "+" 创建新Terminal
# 点击 "Split Terminal" 分屏显示
```

---

### 技巧4: VS Code任务配置

创建 `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "NB10 Quick Test",
            "type": "shell",
            "command": "cd tools/nb10_windows && ./nb10.bat test",
            "problemMatcher": [],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "options": {
                "shell": {
                    "executable": "bash",
                    "args": ["-c"]
                }
            }
        },
        {
            "label": "NB10 Process CHD",
            "type": "shell",
            "command": "cd tools/nb10_windows && ./nb10.bat chd",
            "problemMatcher": []
        }
    ]
}
```

然后：
- `Ctrl+Shift+B` 运行默认任务
- Terminal → Run Task → 选择任务

---

## 🔄 对比使用场景

### 场景1: 快速测试

**VS Code WSL Terminal** (最佳):
```bash
cd tools/nb10_windows
./nb10.bat test
```

**VS Code CMD Terminal**:
```cmd
pushd \\wsl.localhost\Ubuntu\home\wuxia\...\tools\nb10_windows
nb10.bat test
```

**结论**: WSL Terminal更简洁

---

### 场景2: Python开发调试

**VS Code WSL Terminal** (最佳):
```bash
cd tools/nb10_windows
source venv/bin/activate
python cli/run_nb10.py --mode pilot --pilot-limit 5
```

**VS Code CMD Terminal**:
```cmd
pushd \\wsl.localhost\Ubuntu\...\tools\nb10_windows
venv\Scripts\activate.bat
python cli\run_nb10.py --mode pilot --pilot-limit 5
```

**结论**: WSL Terminal路径更清晰

---

### 场景3: 查看日志

**VS Code WSL Terminal** (最佳):
```bash
cd tools/nb10_windows
tail -f logs/nb10_*.log
grep "ERROR" logs/*.log
```

**VS Code CMD Terminal**:
```cmd
Z:\nb10_windows> type logs\nb10_*.log
Z:\nb10_windows> findstr "ERROR" logs\*.log
```

**结论**: WSL Terminal有更强大的Linux工具

---

## ⚠️ 注意事项

### 1. 路径格式差异

**WSL Terminal (Linux)**:
```bash
/home/wuxia/projects/...
./nb10.bat
../venv/bin/activate
```

**CMD Terminal (Windows)**:
```cmd
Z:\
nb10.bat
..\venv\Scripts\activate.bat
```

### 2. 文件权限

**WSL Terminal**:
- 使用Linux权限（rwx）
- `chmod +x script.sh` 有效

**CMD Terminal**:
- 使用Windows权限
- `chmod` 命令不存在

### 3. 环境变量

**WSL Terminal**:
- Linux环境变量（$HOME, $PATH等）
- `.bashrc`, `.profile` 生效

**CMD Terminal**:
- Windows环境变量（%USERPROFILE%, %PATH%等）
- Linux环境变量不可用

---

## 🎯 最佳实践建议

### ✅ 推荐：VS Code WSL Terminal

**原因**：
1. ✅ 真正的Linux环境
2. ✅ 性能最佳
3. ✅ 文件权限一致
4. ✅ 所有Linux工具可用
5. ✅ 与开发环境完全一致

**设置方法**：
```bash
# 在WSL终端中打开项目
cd /home/wuxia/projects/.../cardiac-ml-research
code .

# 或在VS Code中
# 左下角点击 >< → Connect to WSL
# 然后打开项目文件夹
```

### ⚠️ 不推荐：VS Code CMD Terminal

**原因**：
- 跨系统访问，性能略慢
- 路径转换麻烦
- Linux工具不可用
- 文件权限可能不一致

**何时使用**：
- 需要运行Windows特有的命令
- 不想安装WSL扩展（不推荐）

---

## 📋 快速参考

### VS Code WSL Terminal（推荐）

```bash
# 打开项目
cd /home/wuxia/projects/.../cardiac-ml-research
code .

# 在VS Code Terminal中
cd tools/nb10_windows
./nb10.bat test
source venv/bin/activate
python cli/run_nb10.py --mode pilot
```

### VS Code CMD Terminal

```cmd
# 在Terminal中
pushd \\wsl.localhost\Ubuntu\home\wuxia\...\tools\nb10_windows
nb10.bat test
venv\Scripts\activate.bat
python cli\run_nb10.py --mode pilot
```

---

## 🎓 总结

### 核心要点

1. **VS Code Terminal ≠ Windows CMD**
   - VS Code Terminal可以选择WSL或CMD
   - Windows CMD始终是Windows环境

2. **最佳选择：VS Code WSL Terminal**
   - 真正的Linux环境
   - 性能最佳
   - 开发体验最好

3. **设置很简单**
   - 安装"Remote - WSL"扩展
   - 从WSL中用`code .`打开项目
   - Terminal自动使用WSL bash

4. **与Windows CMD + pushd的区别**
   - VS Code WSL: 运行在Linux中
   - CMD + pushd: 运行在Windows中，访问WSL文件

---

**推荐配置**: 使用VS Code + Remote WSL扩展，获得最佳开发体验！

**相关文档**:
- [HOW_TO_RUN.md](../HOW_TO_RUN.md) - 如何运行应用（3种方法）⭐
- [MENU_GUIDE.md](../MENU_GUIDE.md) - 菜单系统完整指南 ⭐
- [VSCODE_QUICK_START.md](../VSCODE_QUICK_START.md) - VS Code快速入门 ⭐
- [SCRIPT_MANAGEMENT_GUIDE.md](SCRIPT_MANAGEMENT_GUIDE.md) - 脚本管理指南
- [WINDOWS_ACCESS_GUIDE.md](WINDOWS_ACCESS_GUIDE.md) - Windows访问WSL指南
- [scripts/README.md](../scripts/README.md) - 打包脚本说明
