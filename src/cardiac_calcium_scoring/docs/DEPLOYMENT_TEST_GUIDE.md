# NB10 AI-CAC 轻量版 - Windows测试部署指南

**版本**: v1.0.0 (Lite Edition)
**目标**: Windows 11无GPU环境（医院场景模拟）
**生成日期**: 2025-10-15

---

## 📦 **打包文件信息**

### **轻量版打包（推荐）**

| 文件 | 大小 | 说明 |
|------|------|------|
| `nb10-ai-cac-lite-v1.0.0.zip` | **104KB** | 应用程序（不含模型和Python） |
| `nb10-ai-cac-lite-v1.0.0.zip.sha256` | 94B | 文件校验和 |
| **模型文件（单独）** | ~1.2GB | `va_non_gated_ai_cac_model.pth` |

### **完整版打包（备选）**

| 文件 | 大小 | 说明 |
|------|------|------|
| `nb10-ai-cac-v1.0.0.zip` | 1.1GB | 完整包（含模型，不含Python） |
| `nb10-ai-cac-v1.0.0.zip.sha256` | 89B | 文件校验和 |

**推荐使用轻量版**：
- ✅ 快速网络传输（104KB vs 1.1GB）
- ✅ 易于分发和更新
- ⚠️ 需要单独准备模型文件

---

## 🖥️ **Windows 11测试环境准备**

### **目标机器规格**
```
操作系统: Windows 11 (无GPU)
CPU: 任意现代CPU (4核心+推荐)
内存: 8GB+ 推荐
磁盘: 20GB可用空间
网络: 可选（离线安装模式）
```

---

## 📋 **部署步骤（医院场景模拟）**

### **步骤1: 准备文件（在Linux机器上）**

```bash
# 1. 复制轻量版到共享位置
cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/nb10_windows/dist

# 2. 准备传输文件列表
ls -lh nb10-ai-cac-lite-v1.0.0.zip*

# 3. 验证校验和
sha256sum -c nb10-ai-cac-lite-v1.0.0.zip.sha256

# 4. 准备模型文件
# 位置: tools/nb10_windows/models/va_non_gated_ai_cac_model.pth
ls -lh ../../models/va_non_gated_ai_cac_model.pth
```

---

### **步骤2: 验证文件完整性（重要！）**

#### 2.1 SHA256校验和说明

**什么是SHA256文件？**
- `.sha256`文件包含原始ZIP文件的数字指纹
- 用于验证文件在传输过程中是否被损坏或篡改
- 确保在Windows机器上得到的是完整、未损坏的文件

**如何使用SHA256验证？**

在Linux上（传输前验证）:
```bash
# 验证文件完整性
sha256sum -c nb10-ai-cac-lite-v1.0.0.zip.sha256

# 预期输出:
# nb10-ai-cac-lite-v1.0.0.zip: OK  ← 文件完整
```

在Windows上（传输后验证）:
```powershell
# 方法1: 使用PowerShell验证
# 1. 查看.sha256文件内容（记下校验和值）
type nb10-ai-cac-lite-v1.0.0.zip.sha256

# 2. 计算实际文件的校验和
certutil -hashfile nb10-ai-cac-lite-v1.0.0.zip SHA256

# 3. 手动对比两个值是否完全一致

# 方法2: 使用自动脚本（推荐）
# 我们已经在start_nb10.bat中集成了自动验证功能
```

**何时需要验证？**
- ✅ 网络传输后（防止传输错误）
- ✅ U盘拷贝后（防止读写错误）
- ✅ 长期存储后使用前（防止文件损坏）
- ⚠️ 如果校验失败，请重新下载/传输文件

---

### **步骤3: 传输到Windows机器**

**方法A: U盘传输（推荐用于离线环境）**
```
1. 插入U盘到Linux机器
2. 复制文件:
   - nb10-ai-cac-lite-v1.0.0.zip (104KB)
   - nb10-ai-cac-lite-v1.0.0.zip.sha256 (94B) ← 同时复制校验文件
   - va_non_gated_ai_cac_model.pth (1.2GB)
3. 安全弹出U盘
4. 插入U盘到Windows机器
5. 复制到: C:\nb10-test\
6. 验证文件完整性（见步骤2.1）
```

**方法B: 网络传输**
```
1. 使用FileZilla/WinSCP
2. 或通过共享文件夹
3. 或通过云盘（如果允许）
```

---

### **步骤4: Windows机器上快速启动（一键式）**

#### 4.1 使用一键启动脚本（推荐）

我们提供了`start_nb10.bat`一键启动脚本，自动完成所有检测和配置：

**功能特性**:
- ✅ 自动检测是否已安装（避免重复安装）
- ✅ 自动检测GPU可用性（选择CPU或GPU版本）
- ✅ 自动检测Python安装（提示如果缺失）
- ✅ 自动检测模型文件（提醒如果缺失）
- ✅ 自动激活虚拟环境
- ✅ 清晰的错误提示和用户交互

**使用方法**:
```cmd
# 进入解压后的目录
cd C:\nb10-test\nb10-ai-cac-lite-v1.0.0

# 双击运行或命令行运行
start_nb10.bat
```

**首次运行流程**:
```
=========================================
NB10 AI-CAC 冠脉钙化评分系统
一键启动脚本 v1.0.0
=========================================

[检测] 检查安装状态...
[信息] 未检测到安装，开始初始化安装...

[检测] 检查Python环境...
[成功] Python 3.10.11 已安装

[检测] 检查GPU可用性...
[信息] 未检测到NVIDIA GPU，将使用CPU模式

[检测] 检查模型文件...
[成功] 模型文件已找到

[安装] 开始安装依赖包（CPU模式）...
[进度] 创建虚拟环境...
[进度] 安装PyTorch (CPU版本)...
[进度] 安装其他依赖...
[成功] 依赖安装完成！

[启动] 激活虚拟环境并运行NB10...
按任意键继续...
```

**已安装后运行**:
```
=========================================
NB10 AI-CAC 冠脉钙化评分系统
一键启动脚本 v1.0.0
=========================================

[检测] 检查安装状态...
[成功] 已检测到安装

[检测] 检查模型文件...
[成功] 模型文件已找到

[启动] 激活虚拟环境并运行NB10...

========================================
NB10 AI-CAC 冠脉钙化积分分析工具
========================================
[菜单显示...]
```

#### 4.2 常见提示和处理

**提示1: Python未安装**
```
[错误] 未检测到Python
[提示] 请先安装Python 3.10:
        1. 访问: https://www.python.org/downloads/release/python-31011/
        2. 下载: Windows installer (64-bit)
        3. 安装时务必勾选 "Add Python to PATH"

按任意键退出...
```
→ 按照提示安装Python后重新运行

**提示2: 模型文件缺失**
```
[警告] 未找到模型文件
[路径] nb10_windows\models\va_non_gated_ai_cac_model.pth
[提示] 请将模型文件复制到上述路径
[大小] 约1.2GB

是否继续安装其他组件? (Y/N):
```
→ 选择Y继续安装，稍后补充模型文件

**提示3: GPU检测失败**
```
[信息] 未检测到NVIDIA GPU
[选择] 将使用CPU模式安装
[说明] CPU模式处理速度较慢（约50-100秒/例）
       如需GPU加速，请在有GPU的机器上重新安装

按任意键继续...
```
→ 正常，无GPU环境预期行为

---

### **步骤5: Windows机器上手动安装（高级用户）**

如果需要手动控制安装过程，可以按照以下步骤操作：

#### 3.1 解压应用程序

```cmd
# 1. 在Windows上打开命令提示符 (Win+R → cmd)
cd C:\nb10-test

# 2. 解压文件（使用Windows自带或7-Zip）
# 右键 → 解压到当前文件夹
# 或使用PowerShell:
Expand-Archive -Path nb10-ai-cac-lite-v1.0.0.zip -DestinationPath .
```

**目录结构应该是**:
```
C:\nb10-test\
├── nb10-ai-cac-lite-v1.0.0\
│   ├── nb10_windows\          ← 应用程序目录
│   ├── install_cpu.bat        ← CPU版本安装脚本
│   ├── install_gpu.bat        ← GPU版本安装脚本
│   ├── run_nb10.bat           ← 运行脚本
│   ├── README.txt             ← 使用说明
│   └── VERSION.txt            ← 版本信息
└── va_non_gated_ai_cac_model.pth  ← 模型文件（需要复制）
```

#### 3.2 放置模型文件

```cmd
# 复制模型文件到正确位置
copy va_non_gated_ai_cac_model.pth nb10-ai-cac-lite-v1.0.0\nb10_windows\models\

# 验证文件存在
dir nb10-ai-cac-lite-v1.0.0\nb10_windows\models\
```

---

### **步骤4: 安装Python和依赖**

#### 4.1 安装Python 3.10

**如果Windows机器上没有Python**:

1. 下载Python 3.10.11:
   - 官方: https://www.python.org/downloads/release/python-31011/
   - 选择: "Windows installer (64-bit)"

2. 运行安装程序:
   - ✅ **重要**: 勾选 "Add Python to PATH"
   - 选择 "Customize installation"
   - 勾选所有可选功能
   - 安装位置: `C:\Python310\` (推荐)

3. 验证安装:
   ```cmd
   python --version
   # 应该显示: Python 3.10.11
   ```

#### 4.2 安装依赖包（CPU模式）

```cmd
cd C:\nb10-test\nb10-ai-cac-lite-v1.0.0

# 双击运行安装脚本
install_cpu.bat

# 或在命令行运行
.\install_cpu.bat
```

**安装过程**（约5-10分钟）:
```
[1/5] 检测Python版本...
[2/5] 检查模型文件...
[3/5] 创建虚拟环境...
[4/5] 升级pip...
[5/5] 安装依赖包...
```

**预期输出**:
```
✓ 依赖安装完成！

下一步:
  1. 编辑配置文件: nb10_windows\config\config.yaml
  2. 运行程序: 双击 run_nb10.bat
```

---

### **步骤5: 配置数据路径**

#### 5.1 准备测试DICOM数据

```cmd
# 创建测试数据目录
mkdir D:\DICOM_Test_Data
mkdir D:\NB10_Results

# 复制5-10例DICOM数据到 D:\DICOM_Test_Data\
```

#### 5.2 编辑配置文件

```cmd
# 使用记事本打开配置文件
notepad nb10_windows\config\config.yaml
```

**修改以下内容**:
```yaml
paths:
  data_dir: "D:/DICOM_Test_Data"      # 测试数据路径
  output_dir: "D:/NB10_Results"       # 输出路径

processing:
  mode: "pilot"                        # 测试模式
  pilot_limit: 5                       # 只处理5例

hardware:
  device: "cpu"                        # 强制CPU模式（无GPU环境）
  num_workers: 2                       # CPU线程数
```

---

### **步骤6: 运行测试**

#### 6.1 启动程序

```cmd
cd C:\nb10-test\nb10-ai-cac-lite-v1.0.0

# 方法1: 双击运行
# 双击 run_nb10.bat

# 方法2: 命令行运行
.\run_nb10.bat
```

#### 6.2 运行测试（Pilot模式）

在NB10菜单中选择:
```
1. 测试模式 (处理5例)
```

**预期性能（CPU模式）**:
- 处理时间: **50-100秒/患者**
- 5例总时间: **约5-10分钟**

#### 6.3 查看结果

```cmd
# 打开输出目录
explorer D:\NB10_Results

# 检查输出文件
dir D:\NB10_Results
```

**应该看到**:
```
nb10_results_YYYYMMDD_HHMMSS.csv     ← 详细评分数据
summary_statistics.txt                ← 统计摘要
visualization\                        ← 可视化图表
  ├── agatston_distribution.png
  └── risk_stratification.png
```

---

## ✅ **验证检查清单**

### **部署阶段**

- [ ] Windows 11系统准备完毕
- [ ] 轻量版ZIP文件传输到Windows
- [ ] 模型文件传输到Windows
- [ ] 文件解压成功
- [ ] 模型文件放置到正确位置
- [ ] Python 3.10安装成功
- [ ] 依赖包安装成功（install_cpu.bat）

### **配置阶段**

- [ ] 测试DICOM数据准备（5-10例）
- [ ] config.yaml配置正确
- [ ] 数据路径存在且可访问
- [ ] 输出路径存在且可写入

### **测试阶段**

- [ ] run_nb10.bat成功启动
- [ ] Pilot模式（5例）运行成功
- [ ] 所有5例处理成功
- [ ] 输出CSV文件生成
- [ ] 统计报告生成
- [ ] 可视化图表生成
- [ ] 处理时间符合预期（50-100秒/例）

### **功能验证**

- [ ] Agatston评分准确
- [ ] 风险分层正确（低/中/高）
- [ ] 体积和质量评分计算正确
- [ ] 统计分析正确
- [ ] 可视化图表清晰

---

## 🐛 **常见问题排查**

### **问题1: 找不到Python**

**症状**:
```
[错误] 未检测到Python
```

**解决**:
1. 确认Python已安装: `python --version`
2. 如果未找到，重新安装Python并勾选"Add Python to PATH"
3. 或手动添加到PATH:
   ```cmd
   setx PATH "%PATH%;C:\Python310;C:\Python310\Scripts"
   ```

---

### **问题2: 模型文件未找到**

**症状**:
```
[错误] 未找到模型文件
模型文件路径: nb10_windows\models\va_non_gated_ai_cac_model.pth
```

**解决**:
1. 检查模型文件是否存在:
   ```cmd
   dir nb10_windows\models\va_non_gated_ai_cac_model.pth
   ```
2. 如果不存在，复制模型文件到该路径
3. 验证文件大小约为1.2GB

---

### **问题3: 依赖安装失败**

**症状**:
```
[错误] 依赖安装失败
```

**解决**:
1. 检查网络连接
2. 尝试使用国内镜像:
   ```cmd
   pip install -r nb10_windows\deployment\requirements_cpu.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```
3. 检查磁盘空间（需要约5GB）

---

### **问题4: CPU模式太慢**

**症状**:
- 每例处理时间 >100秒

**解决**:
1. 减少pilot_limit（只测试2-3例）
2. 关闭其他应用程序释放CPU
3. 调整config.yaml:
   ```yaml
   hardware:
     num_workers: 4  # 增加线程数
   ```

---

### **问题5: 内存不足**

**症状**:
```
MemoryError或OOM (Out of Memory)
```

**解决**:
1. 关闭其他应用程序
2. 重启Windows
3. 调整config.yaml:
   ```yaml
   processing:
     batch_size: 1  # 减少批处理大小
   ```

---

## 📊 **测试报告模板**

测试完成后，请填写以下报告：

```
========================================
NB10 AI-CAC 轻量版测试报告
========================================

【测试环境】
  操作系统: Windows 11 [版本号]
  CPU: [型号和核心数]
  内存: [大小]
  Python版本: 3.10.11
  包版本: nb10-ai-cac-lite-v1.0.0

【测试数据】
  DICOM案例数: 5例
  数据来源: [CHD/Normal/混合]
  数据大小: [约XXX MB]

【测试结果】
  ✓/✗ 安装成功
  ✓/✗ 配置正确
  ✓/✗ 运行成功

  处理成功: X/5例
  处理失败: X/5例

  平均处理时间: XXX秒/例
  总处理时间: XXX分钟

【性能评估】
  处理速度: [快/中/慢]
  CPU使用率: XX%
  内存使用: XXX MB

【功能验证】
  ✓/✗ Agatston评分正确
  ✓/✗ 风险分层合理
  ✓/✗ 输出文件完整
  ✓/✗ 可视化清晰

【问题记录】
  1. [问题描述]
  2. [问题描述]

【建议改进】
  1. [建议内容]
  2. [建议内容]

【整体评价】
  满意度: [★★★★★]
  临床可用性: [高/中/低]
  推荐部署: [是/否]

【测试人员】
  姓名: ________
  日期: 2025-10-15
========================================
```

---

## 📞 **技术支持**

如测试中遇到问题，请联系:
- GitHub Issues: [项目地址]
- Email: support@example.com
- 微信群: [邀请链接]

---

**文档版本**: V1.0
**最后更新**: 2025-10-15
**维护者**: 陈医生团队
