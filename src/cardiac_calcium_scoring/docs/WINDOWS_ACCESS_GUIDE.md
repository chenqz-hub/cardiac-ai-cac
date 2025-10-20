# Windows CMD 访问 WSL NB10 目录指南

## 📋 问题

如何在 Windows CMD 下访问 WSL 目录：
```
\\wsl.localhost\Ubuntu\home\wuxia\projects\family_management_hub\members\wife\medical_research\cardiac-ml-research\tools
```

---

## 🎯 推荐方案（按使用频率排序）

### ⭐⭐⭐ 方案1: 使用快捷批处理文件（最方便）

**适用场景**: 日常频繁访问

#### 步骤1: 创建批处理文件

在桌面或任意位置创建文件 `goto_nb10.bat`:

```batch
@echo off
echo 正在进入 NB10 目录...
pushd \\wsl.localhost\Ubuntu\home\wuxia\projects\family_management_hub\members\wife\medical_research\cardiac-ml-research\tools\nb10_windows
if errorlevel 1 (
    echo [错误] 无法访问WSL目录，请确保Ubuntu正在运行
    pause
    exit /b 1
)
echo [成功] 已进入 NB10 目录: %CD%
cmd
```

#### 步骤2: 使用

- **双击运行**: 直接双击 `goto_nb10.bat`
- **命令行运行**: `C:\Users\YourName\goto_nb10.bat`
- **创建桌面快捷方式**: 右键 → 发送到 → 桌面快捷方式

**优点**:
- ✅ 一键直达
- ✅ 自动检测错误
- ✅ 可放在桌面或开始菜单
- ✅ 最适合日常使用

---

### ⭐⭐⭐ 方案2: 使用 pushd 命令（推荐）

**适用场景**: 临时访问，不想创建文件

#### 命令:

```cmd
pushd \\wsl.localhost\Ubuntu\home\wuxia\projects\family_management_hub\members\wife\medical_research\cardiac-ml-research\tools
```

#### 说明:

- `pushd` 会自动创建临时驱动器映射（如 Z:）
- 可以像普通目录一样使用 `cd`、`dir` 等命令
- 使用 `popd` 返回原目录并清理映射

#### 示例操作:

```cmd
C:\Users\YourName> pushd \\wsl.localhost\Ubuntu\home\wuxia\projects\family_management_hub\members\wife\medical_research\cardiac-ml-research\tools

Z:\> dir
Z:\> cd nb10_windows
Z:\nb10_windows> dir
Z:\nb10_windows> start_nb10.bat

REM 完成后返回原目录
Z:\nb10_windows> popd
C:\Users\YourName>
```

**优点**:
- ✅ 临时访问很方便
- ✅ 自动创建/清理驱动器映射
- ✅ 标准Windows命令

---

### ⭐⭐ 方案3: 映射网络驱动器（适合长期使用）

**适用场景**: 需要频繁访问，希望有固定驱动器号

#### 创建映射:

```cmd
net use W: \\wsl.localhost\Ubuntu\home\wuxia\projects\family_management_hub\members\wife\medical_research\cardiac-ml-research\tools
```

#### 使用:

```cmd
W:
cd \nb10_windows
dir
```

#### 删除映射:

```cmd
net use W: /delete
```

**优点**:
- ✅ 创建固定的驱动器号
- ✅ 可以在文件资源管理器中看到
- ✅ 适合长期使用

**缺点**:
- ⚠️ 重启Windows后需要重新创建
- ⚠️ 需要手动管理映射

#### 设置开机自动映射（可选）:

创建 `C:\Users\YourName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\map_wsl.bat`:

```batch
@echo off
net use W: \\wsl.localhost\Ubuntu\home\wuxia\projects\family_management_hub\members\wife\medical_research\cardiac-ml-research\tools /persistent:no
```

---

### ⭐ 方案4: 使用 wsl 命令（适合执行脚本）

**适用场景**: 从Windows CMD执行Linux脚本

#### 方法A: 进入WSL并切换目录

```cmd
wsl
cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/nb10_windows
ls
```

#### 方法B: 直接执行命令

```cmd
wsl -e bash -c "cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/nb10_windows && ls -la"
```

#### 方法C: 执行批处理脚本

```cmd
wsl -e bash -c "cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/nb10_windows && ./nb10.bat test"
```

**优点**:
- ✅ 保持Linux环境特性
- ✅ 适合执行Linux脚本
- ✅ 不需要处理路径转换

**缺点**:
- ⚠️ 在Linux环境中运行，不是Windows环境
- ⚠️ 路径使用Linux格式

---

## 🔧 故障排除

### 问题1: "找不到网络路径"

**原因**: WSL未启动或路径不正确

**解决方案**:
1. 打开 Ubuntu 终端确保 WSL 正在运行
2. 检查路径是否正确
3. 尝试使用旧版路径格式：
   ```cmd
   pushd \\wsl$\Ubuntu\home\wuxia\...
   ```

---

### 问题2: "CMD不支持UNC路径"

**原因**: `cd` 命令不支持 UNC 路径

**解决方案**: 使用 `pushd` 而不是 `cd`

❌ 错误:
```cmd
cd \\wsl.localhost\Ubuntu\home\wuxia\...
```

✅ 正确:
```cmd
pushd \\wsl.localhost\Ubuntu\home\wuxia\...
```

---

### 问题3: 路径中有空格导致错误

**解决方案**: 使用双引号包围路径

```cmd
pushd "\\wsl.localhost\Ubuntu\home\wuxia\projects\family management hub\..."
```

---

### 问题4: 权限被拒绝

**原因**: WSL文件权限问题

**解决方案**:
1. 在WSL中检查文件权限：
   ```bash
   ls -la /home/wuxia/projects/.../tools
   ```

2. 如需修改权限：
   ```bash
   chmod 755 /home/wuxia/projects/.../tools
   ```

---

## 📝 实用技巧

### 技巧1: 创建右键菜单快捷方式

在注册表中添加右键菜单项（高级用户）：

```reg
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\Directory\Background\shell\OpenNB10]
@="在此处打开 NB10 CMD"

[HKEY_CLASSES_ROOT\Directory\Background\shell\OpenNB10\command]
@="cmd.exe /k pushd \"\\\\wsl.localhost\\Ubuntu\\home\\wuxia\\projects\\family_management_hub\\members\\wife\\medical_research\\cardiac-ml-research\\tools\\nb10_windows\""
```

---

### 技巧2: 创建PowerShell别名（PowerShell用户）

在PowerShell配置文件中添加：

```powershell
# 查看配置文件位置
$PROFILE

# 编辑配置文件，添加：
function goto-nb10 {
    Set-Location "\\wsl.localhost\Ubuntu\home\wuxia\projects\family_management_hub\members\wife\medical_research\cardiac-ml-research\tools\nb10_windows"
}

# 使用
goto-nb10
```

---

### 技巧3: 在文件资源管理器中快速访问

1. 打开文件资源管理器
2. 在地址栏输入：
   ```
   \\wsl.localhost\Ubuntu\home\wuxia\projects\family_management_hub\members\wife\medical_research\cardiac-ml-research\tools
   ```
3. 将当前位置添加到"快速访问"：右键 → 固定到快速访问

---

## 🎯 最佳实践推荐

根据不同使用场景选择合适的方法：

| 场景 | 推荐方法 | 原因 |
|------|---------|------|
| **日常开发** | 快捷批处理文件 | 一键直达，最方便 |
| **临时访问** | `pushd` 命令 | 快速简单，无需文件 |
| **长期使用** | 映射网络驱动器 | 固定驱动器号，便于记忆 |
| **执行脚本** | `wsl` 命令 | 保持Linux环境 |
| **文件管理** | 文件资源管理器 | 图形化界面 |

---

## 📌 快速参考

### 您的具体路径:

**WSL Linux路径**:
```
/home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools
```

**Windows UNC路径**:
```
\\wsl.localhost\Ubuntu\home\wuxia\projects\family_management_hub\members\wife\medical_research\cardiac-ml-research\tools
```

### 最快速的访问方式（推荐）:

**方法1**: 创建桌面快捷批处理文件
```batch
@echo off
pushd \\wsl.localhost\Ubuntu\home\wuxia\projects\family_management_hub\members\wife\medical_research\cardiac-ml-research\tools\nb10_windows
cmd
```

**方法2**: 直接使用 pushd
```cmd
pushd \\wsl.localhost\Ubuntu\home\wuxia\projects\family_management_hub\members\wife\medical_research\cardiac-ml-research\tools
```

---

## 🚀 进阶: 创建完整的启动脚本

创建 `C:\Users\YourName\Desktop\NB10开发环境.bat`:

```batch
@echo off
REM =========================================
REM NB10 开发环境快速启动脚本
REM =========================================

echo.
echo ========================================
echo NB10 AI-CAC 开发环境
echo ========================================
echo.
echo 正在进入 WSL 工作目录...
echo.

REM 进入WSL目录
pushd \\wsl.localhost\Ubuntu\home\wuxia\projects\family_management_hub\members\wife\medical_research\cardiac-ml-research\tools\nb10_windows

if errorlevel 1 (
    echo [错误] 无法访问 WSL 目录
    echo.
    echo 请确保:
    echo   1. Ubuntu WSL 已启动
    echo   2. 路径正确
    echo.
    pause
    exit /b 1
)

echo [成功] 已进入工作目录
echo 当前位置: %CD%
echo.
echo ========================================
echo 可用操作:
echo ========================================
echo   1. 运行 NB10 菜单: nb10.bat
echo   2. 快速测试: nb10.bat test
echo   3. 查看文件: dir
echo   4. 返回: popd
echo ========================================
echo.

REM 保持CMD窗口打开
cmd /k "echo 提示: 输入 'nb10.bat' 查看菜单，或 'popd' 返回"
```

**使用方式**: 双击桌面上的 `NB10开发环境.bat` 即可

---

**文档版本**: v1.0
**更新日期**: 2025-10-16
**适用系统**: Windows 10/11 + WSL2
