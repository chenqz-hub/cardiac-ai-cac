# NB10 一键启动功能使用指南

**版本**: v1.0.0
**更新日期**: 2025-10-15
**适用场景**: Windows医院部署

---

## 📋 概述

本次更新为NB10 Windows轻量版添加了完整的一键启动功能，大幅简化医院端的部署和使用流程。

### 核心改进

1. **start_nb10.bat** - 一键启动脚本（新增）
2. **SHA256校验说明** - 文件完整性验证指南
3. **智能环境检测** - 自动化安装和配置
4. **增强错误处理** - 清晰的提示和引导

---

## 🚀 一键启动脚本 (start_nb10.bat)

### 功能特性

| 功能 | 说明 |
|------|------|
| **安装状态检测** | 自动识别是否已安装，避免重复安装 |
| **GPU自动检测** | 检测NVIDIA GPU，自动选择CPU/GPU模式 |
| **Python检测** | 检查Python安装，缺失时提供详细安装指引 |
| **模型文件检测** | 自动查找模型文件，缺失时提醒用户 |
| **虚拟环境激活** | 自动激活Python虚拟环境 |
| **错误处理** | 每步都有pause，错误信息清晰明确 |

### 使用方法

#### 首次使用（未安装）

```cmd
# 1. 解压轻量版ZIP文件到C:\nb10-test\
# 2. 确保Python 3.10已安装
# 3. 双击运行 start_nb10.bat

C:\nb10-test\nb10-ai-cac-lite-v1.0.0\start_nb10.bat
```

**脚本会自动执行**:
1. 检测到未安装
2. 检测Python版本
3. 检测GPU可用性 → 选择install_cpu.bat或install_gpu.bat
4. 检查模型文件 → 提示是否继续安装
5. 自动运行安装脚本
6. 激活虚拟环境
7. 启动NB10主程序

#### 已安装后使用

```cmd
# 直接双击运行 start_nb10.bat
```

**脚本会自动执行**:
1. 检测到已安装
2. 检查模型文件
3. 激活虚拟环境
4. 启动NB10主程序

---

## 🔐 SHA256文件完整性验证

### 什么是SHA256？

- `.sha256`文件包含ZIP文件的数字指纹
- 用于验证文件在传输过程中未被损坏或篡改
- 医院场景特别重要（U盘传输、网络下载）

### 如何验证？

#### Linux端（传输前）

```bash
# 在打包目录执行
cd /path/to/dist/

# 验证文件完整性
sha256sum -c nb10-ai-cac-lite-v1.0.0.zip.sha256

# 预期输出:
# nb10-ai-cac-lite-v1.0.0.zip: OK  ✅
```

#### Windows端（传输后）

**方法1: 使用PowerShell（推荐）**

```powershell
# 1. 查看预期校验和
type nb10-ai-cac-lite-v1.0.0.zip.sha256

# 输出示例:
# 0d21eb123b245be5783775e7728144b9c1a5228a74384798568eb5979e3c89d6

# 2. 计算实际文件的校验和
certutil -hashfile nb10-ai-cac-lite-v1.0.0.zip SHA256

# 输出示例:
# SHA256 的 nb10-ai-cac-lite-v1.0.0.zip 哈希:
# 0d21eb123b245be5783775e7728144b9c1a5228a74384798568eb5979e3c89d6

# 3. 手动对比两个值是否一致
# ✅ 一致 = 文件完整
# ❌ 不一致 = 文件损坏，需重新传输
```

**方法2: 使用文件资源管理器**

1. 右键点击ZIP文件 → 属性
2. 切换到"数字签名"或"哈希值"选项卡（需第三方工具）
3. 对比SHA256值

### 何时需要验证？

- ✅ **必须验证**: 网络传输后、U盘拷贝后
- ✅ **推荐验证**: 长期存储后首次使用
- ⚠️ **校验失败**: 立即停止使用，重新下载/传输

---

## 📊 典型使用场景

### 场景1: 医院IT部门首次部署

**环境**: 无GPU Windows 11工作站

```
步骤1: 文件传输
  - 使用U盘复制 nb10-ai-cac-lite-v1.0.0.zip 和 .sha256
  - 复制模型文件 va_non_gated_ai_cac_model.pth

步骤2: 验证文件
  - 使用certutil验证ZIP文件SHA256

步骤3: 解压安装
  - 解压ZIP到 C:\nb10-ai-cac\
  - 复制模型到 nb10_windows\models\

步骤4: 一键启动
  - 双击 start_nb10.bat
  - 脚本检测到无GPU → 自动使用CPU模式
  - 自动安装依赖包（约5-10分钟）
  - 自动启动程序

预期时间: 15-20分钟完成首次部署
```

### 场景2: 已安装环境日常使用

**环境**: 已部署GPU工作站

```
步骤1: 准备DICOM数据
  - 复制患者数据到 D:\DICOM_Data\

步骤2: 一键启动
  - 双击 start_nb10.bat
  - 脚本检测到已安装 → 直接启动

步骤3: 运行分析
  - 程序自动显示菜单
  - 选择"测试模式"或"完整模式"

预期时间: <30秒启动程序
```

### 场景3: 更新模型文件

**环境**: 需要更新AI模型

```
步骤1: 备份旧模型
  - 重命名 va_non_gated_ai_cac_model.pth 为 .pth.bak

步骤2: 复制新模型
  - 下载新模型文件
  - 复制到 nb10_windows\models\

步骤3: 验证
  - 双击 start_nb10.bat
  - 脚本自动检测新模型 → 提示"模型文件已找到"

步骤4: 测试
  - 运行Pilot模式测试2-3例
  - 验证新模型正常工作

预期时间: 5分钟完成模型更新
```

---

## 🐛 常见问题和解决方案

### 问题1: Python未安装

**现象**:
```
[错误] 未检测到Python
[提示] 请先安装Python 3.10:
        1. 访问: https://www.python.org/downloads/release/python-31011/
        2. 下载: Windows installer (64-bit)
        3. 安装时务必勾选 "Add Python to PATH"

按任意键退出...
```

**解决**:
1. 访问提示的网址下载Python
2. 运行安装程序
3. ⚠️ **重要**: 勾选"Add Python to PATH"
4. 安装完成后重新运行start_nb10.bat

---

### 问题2: 模型文件缺失

**现象**:
```
[警告] 未找到模型文件
[路径] nb10_windows\models\va_non_gated_ai_cac_model.pth
[提示] 请将模型文件复制到上述路径
[大小] 约1.2GB

是否继续安装其他组件? (Y/N):
```

**解决**:
- 选择 **Y**: 继续安装依赖，稍后手动添加模型
- 选择 **N**: 中止安装，先下载模型再重新运行

**推荐流程**:
1. 选择Y继续安装依赖（节省时间）
2. 同时下载模型文件
3. 下载完成后复制到指定路径
4. 重新运行start_nb10.bat验证

---

### 问题3: GPU检测失败（有GPU但未检测到）

**现象**:
```
[信息] 未检测到NVIDIA GPU，将使用CPU模式
[说明] CPU模式处理速度较慢（约50-100秒/例）
```

**可能原因**:
1. NVIDIA驱动未安装
2. nvidia-smi命令不在PATH中
3. GPU不是NVIDIA品牌（AMD/Intel）

**解决**:
1. 检查NVIDIA驱动: 运行`nvidia-smi`
2. 如果是AMD/Intel显卡 → 正常，使用CPU模式
3. 如果需要GPU加速 → 安装NVIDIA驱动后重新运行

---

### 问题4: 虚拟环境激活失败

**现象**:
```
[警告] 虚拟环境激活可能失败，尝试直接运行...
```

**影响**: 通常不影响运行（脚本会直接调用venv中的python.exe）

**如果确实失败**:
```
[错误] 虚拟环境中的Python未找到
[路径] nb10_windows\venv\Scripts\python.exe
[建议] 请重新安装
```

**解决**:
```cmd
# 删除虚拟环境
rd /s /q nb10_windows\venv

# 重新运行start_nb10.bat
start_nb10.bat
```

---

### 问题5: SHA256校验失败

**现象**:
```
# Linux验证
sha256sum -c nb10-ai-cac-lite-v1.0.0.zip.sha256
# 输出:
nb10-ai-cac-lite-v1.0.0.zip: FAILED  ❌
```

或

```
# Windows验证
# certutil输出的值与.sha256文件内容不一致
```

**原因**:
- 文件在传输过程中损坏
- 下载不完整
- U盘读写错误
- 网络传输错误

**解决**:
1. ⚠️ **立即停止使用该文件**
2. 重新下载或重新拷贝
3. 重新验证SHA256
4. 确认通过后再使用

---

## 📁 文件结构说明

### 解压后目录结构

```
nb10-ai-cac-lite-v1.0.0/
├── start_nb10.bat          ← ⭐ 一键启动（推荐）
├── install_cpu.bat         ← CPU模式手动安装
├── install_gpu.bat         ← GPU模式手动安装
├── run_nb10.bat            ← 手动运行（需先安装）
├── README.txt              ← 快速入门指南
├── VERSION.txt             ← 版本信息
├── CHANGELOG.txt           ← 更新日志
└── nb10_windows/           ← 应用程序主目录
    ├── cli/                ← 命令行接口
    ├── core/               ← 核心算法
    ├── config/             ← 配置文件
    │   └── config.yaml     ← ⚠️ 需配置数据路径
    ├── models/             ← 模型文件目录
    │   ├── README.md       ← 模型下载说明
    │   ├── DOWNLOAD_MODEL.txt
    │   └── va_non_gated_ai_cac_model.pth  ← ⚠️ 需单独下载
    ├── deployment/         ← 部署配置
    │   ├── requirements_cpu.txt
    │   └── requirements_gpu.txt
    ├── docs/               ← 用户文档
    │   ├── USER_MANUAL.md
    │   ├── INSTALLATION_GUIDE.md
    │   └── DEPLOYMENT_TEST_GUIDE.md
    ├── output/             ← 分析结果输出
    ├── logs/               ← 运行日志
    └── venv/               ← Python虚拟环境（安装后创建）
```

---

## 🎯 最佳实践建议

### 部署阶段

1. **文件传输**
   - ✅ 同时复制ZIP和SHA256文件
   - ✅ 传输后立即验证SHA256
   - ✅ 提前准备好模型文件

2. **Python安装**
   - ✅ 使用Python 3.10.11（推荐）
   - ✅ 务必勾选"Add Python to PATH"
   - ✅ 安装后重启命令提示符

3. **首次部署**
   - ✅ 使用start_nb10.bat一键安装
   - ✅ 安装过程中不要关闭窗口
   - ✅ 遇到选择提示仔细阅读

### 使用阶段

1. **日常启动**
   - ✅ 始终使用start_nb10.bat启动
   - ✅ 启动前确保数据路径配置正确
   - ✅ 首次运行建议Pilot模式测试

2. **数据配置**
   ```yaml
   # nb10_windows/config/config.yaml
   paths:
     data_dir: "D:/DICOM_Data"      # 修改为实际路径
     output_dir: "D:/NB10_Results"  # 修改为实际路径

   processing:
     mode: "pilot"                   # 测试模式
     pilot_limit: 5                  # 先测试5例

   hardware:
     device: "cpu"                   # CPU模式（无GPU）
     num_workers: 2                  # 根据CPU核心数调整
   ```

3. **性能优化**
   - GPU模式: 10-15秒/例（推荐）
   - CPU模式: 50-100秒/例（可用）
   - 批量处理: 使用Full模式
   - 小规模测试: 使用Pilot模式

---

## 📞 技术支持

### 遇到问题？

1. **查看日志**
   ```cmd
   # 查看最新日志
   type nb10_windows\logs\nb10_latest.log
   ```

2. **检查配置**
   ```cmd
   # 编辑配置文件
   notepad nb10_windows\config\config.yaml
   ```

3. **重新安装**
   ```cmd
   # 删除虚拟环境
   rd /s /q nb10_windows\venv

   # 重新运行一键启动
   start_nb10.bat
   ```

4. **联系支持**
   - GitHub Issues: [项目地址]
   - 邮箱: support@example.com
   - 医院IT部门

---

## 📝 版本历史

### v1.0.0 (2025-10-15)

**新增功能**:
- ⭐ start_nb10.bat 一键启动脚本
- 🔐 SHA256文件完整性验证说明
- 📖 ONE_CLICK_STARTUP_GUIDE.md 使用指南

**改进**:
- 自动检测安装状态
- 自动检测GPU可用性
- 自动检测Python和模型文件
- 增强错误提示和用户引导

**包信息**:
- 轻量版大小: 108KB
- SHA256: `0d21eb123b245be5783775e7728144b9c1a5228a74384798568eb5979e3c89d6`
- 模型文件: 需单独下载（1.2GB）

---

## 🎓 附录: Windows批处理脚本说明

### start_nb10.bat 技术细节

**核心功能模块**:

1. **安装状态检测** (Lines 460-469)
   ```batch
   if exist "nb10_windows\venv\Scripts\activate.bat" (
       set "INSTALL_STATUS=installed"
   ) else (
       set "INSTALL_STATUS=not_installed"
   )
   ```

2. **GPU检测** (Lines 495-512)
   ```batch
   nvidia-smi >nul 2>&1
   if errorlevel 1 (
       set "INSTALL_SCRIPT=install_cpu.bat"
   ) else (
       set "INSTALL_SCRIPT=install_gpu.bat"
   )
   ```

3. **模型文件检测** (Lines 517-541)
   ```batch
   if exist "%MODEL_PATH%" (
       set "MODEL_STATUS=found"
   ) else (
       set "MODEL_STATUS=not_found"
   )
   ```

4. **条件安装** (Lines 546-566)
   ```batch
   if "%INSTALL_STATUS%"=="not_installed" (
       call %INSTALL_SCRIPT%
   )
   ```

5. **虚拟环境激活** (Lines 599-623)
   ```batch
   call nb10_windows\venv\Scripts\activate.bat
   venv\Scripts\python.exe cli\run_nb10.py
   ```

**错误处理策略**:
- 每个关键步骤都有错误检测
- 错误信息包含原因和解决方案
- 适当使用`pause`等待用户确认
- 非零退出码传递错误状态

---

**文档版本**: V1.0
**维护者**: 陈医生团队
**最后更新**: 2025-10-15
**适用版本**: nb10-ai-cac-lite-v1.0.0及以上
