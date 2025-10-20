# NB10 完全离线部署指南

**适用场景**: 医院环境无互联网连接，需要完全离线安装

**版本**: 1.1.0
**更新日期**: 2025-10-17

---

## 📋 目录

1. [概述](#概述)
2. [准备工作](#准备工作)
3. [步骤1: 下载离线包](#步骤1-下载离线包windows)
4. [步骤2: 打包分发](#步骤2-打包分发)
5. [步骤3: 医院部署](#步骤3-医院部署)
6. [验证和测试](#验证和测试)
7. [常见问题](#常见问题)

---

## 概述

### 完整离线部署包内容

```
nb10-ai-cac-offline-complete/
├── nb10_windows/                          # 应用代码 (~10MB)
│   ├── cli/
│   ├── core/
│   ├── deployment/
│   │   └── offline_wheels/
│   │       ├── cpu/                       # CPU离线包 (~1.5GB)
│   │       │   ├── torch-*.whl
│   │       │   ├── monai-*.whl
│   │       │   └── ... (~40个文件)
│   │       └── gpu/                       # GPU离线包 (~3.5GB)
│   │           ├── torch-*.whl
│   │           ├── monai-*.whl
│   │           └── ... (~40个文件)
│   └── models/
│       └── va_non_gated_ai_cac_model.pth  # AI模型 (~1.2GB)
└── start_nb10.bat                         # 启动脚本
```

**总大小**: ~6-7GB

---

## 准备工作

### 需要的机器

1. **准备机器** (有网络连接):
   - Windows 10/11
   - Python 3.10, 3.11, 或 3.12
   - 互联网连接
   - ~10GB 可用磁盘空间

2. **目标机器** (医院，无网络):
   - Windows 10/11
   - Python 3.10, 3.11, 或 3.12
   - 无需互联网连接

### 重要提醒

⚠️ **必须在 Windows 上准备离线包！**

- ✅ 在 Windows 上准备 → Windows 离线包
- ❌ 在 WSL/Linux 上准备 → Linux 离线包（无法在 Windows 使用）

---

## 步骤1: 下载离线包（Windows）

### 方法A: 使用自动脚本（推荐）

在有网络的 Windows 机器上：

```batch
REM 1. 解压 nb10-ai-cac-lite-v1.1.0.zip
REM 2. 进入目录
cd nb10-ai-cac-lite-v1.1.0\nb10_windows

REM 3. 运行离线包准备脚本
.\deployment\prepare_offline_windows.bat

REM 脚本会自动：
REM - 创建 offline_wheels/cpu/ 和 gpu/ 目录
REM - 下载所有依赖包（~5GB）
REM - 验证下载完整性
REM - 预计时间：30-60分钟
```

### 方法B: 手动下载

如果自动脚本失败，手动执行：

```batch
REM 1. 创建目录
mkdir deployment\offline_wheels\cpu
mkdir deployment\offline_wheels\gpu

REM 2. 下载CPU包（~1.5GB，15-30分钟）
pip download -r deployment\requirements_cpu.txt -d deployment\offline_wheels\cpu\

REM 3. 下载GPU包（~3.5GB，20-40分钟）
pip download -r deployment\requirements_gpu.txt -d deployment\offline_wheels\gpu\

REM 4. 验证
dir deployment\offline_wheels\cpu\*.whl
dir deployment\offline_wheels\gpu\*.whl
```

### 验证下载

```batch
REM 检查文件数量
dir deployment\offline_wheels\cpu\*.whl | find /c ".whl"
REM 应该显示：~40

dir deployment\offline_wheels\gpu\*.whl | find /c ".whl"
REM 应该显示：~40

REM 检查是否是 Windows 版本
dir deployment\offline_wheels\cpu\torch*.whl
REM 应该看到：torch-2.2.0+cpu-cp312-cp312-win_amd64.whl
REM           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
REM           确保是 win_amd64，不是 linux_x86_64
```

**关键检查点**：
- ✅ CPU 和 GPU 目录都有 ~40 个 `.whl` 文件
- ✅ 文件名包含 `win_amd64` 或 `win32`
- ❌ 如果看到 `linux_x86_64` 或 `manylinux` → 错误，需要在 Windows 重新下载

---

## 步骤2: 打包分发

### 下载AI模型

**重要**：模型文件不在离线包中，需要单独下载！

```batch
REM 方法1: 使用 gdown
pip install gdown
gdown 1uD12kphnWlJ5R6K-mDQnxS8LjYhPGSfm -O models\va_non_gated_ai_cac_model.pth

REM 方法2: 从 GitHub Release 下载
REM https://github.com/Raffi-Hagopian/AI-CAC/releases/tag/v1.0.0
REM 下载 va_non_gated_ai_cac_model.pth (~1.2GB)
REM 放到 models\ 目录
```

### 创建完整分发包

```batch
REM 1. 确认所有文件就绪
nb10_windows\
├── deployment\offline_wheels\cpu\    (✅ ~1.5GB, ~40个文件)
├── deployment\offline_wheels\gpu\    (✅ ~3.5GB, ~40个文件)
└── models\va_non_gated_ai_cac_model.pth  (✅ ~1.2GB)

REM 2. 打包整个目录
cd ..
powershell Compress-Archive -Path nb10-ai-cac-lite-v1.1.0 -DestinationPath nb10-ai-cac-offline-complete.zip

REM 或使用 7-Zip（如果已安装）
"C:\Program Files\7-Zip\7z.exe" a -tzip nb10-ai-cac-offline-complete.zip nb10-ai-cac-lite-v1.1.0
```

**最终包大小**：~6-7GB（压缩后可能 ~5-6GB）

---

## 步骤3: 医院部署

### 传输到医院

**传输方式**：
1. ✅ USB 硬盘（推荐，8GB以上）
2. ✅ 医院内网文件服务器
3. ✅ 企业微信/钉钉（文件传输）
4. ❌ 不推荐：邮件（太大）

### 在医院机器上安装

```batch
REM 1. 解压完整包
REM    右键点击 nb10-ai-cac-offline-complete.zip
REM    选择"解压到当前文件夹"

REM 2. 验证文件结构
cd nb10-ai-cac-lite-v1.1.0
dir /s /b models\*.pth
dir /s /b deployment\offline_wheels\cpu\*.whl
dir /s /b deployment\offline_wheels\gpu\*.whl

REM 3. 直接运行（无需网络）
.\start_nb10.bat

REM 安装脚本会自动检测离线包并使用
```

**安装过程**：
```
[5/5] Installing dependencies...

  [INFO] Using offline packages (no network required)
  [PATH] nb10_windows\deployment\offline_wheels\cpu

  Installing torch...
  Installing monai...
  ...
  [OK] Installation complete!
```

---

## 验证和测试

### 步骤1: 验证离线包正确性

在**准备机器**（有网络）上测试：

```batch
REM 1. 创建测试环境
cd nb10_windows
python -m venv test_venv

REM 2. 激活虚拟环境
test_venv\Scripts\activate.bat

REM 3. 测试离线安装（禁用网络访问）
pip install --no-index --find-links=deployment\offline_wheels\cpu -r deployment\requirements_cpu.txt

REM 4. 验证安装
python -c "import torch, monai, numpy, pandas; print('OK')"

REM 5. 清理测试环境
deactivate
rmdir /s /q test_venv
```

如果测试成功，说明离线包正确。

### 步骤2: 在目标机器测试

在**医院机器**（无网络）上：

```batch
REM 1. 确保无网络连接（可选，用于验证）
REM    控制面板 → 网络 → 禁用网络适配器

REM 2. 运行安装
.\start_nb10.bat

REM 3. 检查日志
REM    应该看到 "[INFO] Using offline packages (no network required)"
REM    不应该看到 "Downloading from PyPI"

REM 4. 测试推理
REM    按照提示配置数据目录
REM    运行 Pilot 模式测试 1-2 个病例
```

---

## 常见问题

### Q1: 下载失败 "Connection timed out"

**原因**: 网络不稳定或 PyPI 服务器临时不可用

**解决**:
```batch
REM 使用国内镜像加速
pip download -r deployment\requirements_cpu.txt -d deployment\offline_wheels\cpu\ -i https://pypi.tuna.tsinghua.edu.cn/simple

pip download -r deployment\requirements_gpu.txt -d deployment\offline_wheels\gpu\ -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: 安装时提示 "No matching distribution found"

**原因**: 离线包是 Linux 版本，不是 Windows 版本

**检查**:
```batch
dir deployment\offline_wheels\cpu\torch*.whl
REM 应该看到：win_amd64
REM 错误情况：linux_x86_64
```

**解决**:
```batch
REM 删除错误的包
del /q deployment\offline_wheels\cpu\*
del /q deployment\offline_wheels\gpu\*

REM 在 Windows 上重新下载
pip download -r deployment\requirements_cpu.txt -d deployment\offline_wheels\cpu\
pip download -r deployment\requirements_gpu.txt -d deployment\offline_wheels\gpu\
```

### Q3: 包太大，无法通过企业微信传输

**方案A**: 分卷压缩

```batch
REM 使用 7-Zip 分卷压缩（每个 1GB）
"C:\Program Files\7-Zip\7z.exe" a -v1g -tzip nb10-offline.zip nb10-ai-cac-lite-v1.1.0

REM 会生成：
REM   nb10-offline.zip.001  (1GB)
REM   nb10-offline.zip.002  (1GB)
REM   ...
REM   nb10-offline.zip.006  (~1GB)

REM 解压时：
"C:\Program Files\7-Zip\7z.exe" x nb10-offline.zip.001
```

**方案B**: 分开传输

1. 先传输 Lite 包（~140KB）
2. 医生在医院机器上运行 `prepare_offline_windows.bat`（如果有网络）
3. 如果完全无网络，分别传输：
   - 应用代码（~10MB）
   - CPU 离线包（~1.5GB）
   - GPU 离线包（~3.5GB）
   - AI 模型（~1.2GB）

### Q4: 如何更新离线包？

如果依赖版本更新：

```batch
REM 1. 清除旧包
del /q deployment\offline_wheels\cpu\*
del /q deployment\offline_wheels\gpu\*

REM 2. 更新 requirements 文件（如果有新版本）

REM 3. 重新下载
pip download -r deployment\requirements_cpu.txt -d deployment\offline_wheels\cpu\
pip download -r deployment\requirements_gpu.txt -d deployment\offline_wheels\gpu\

REM 4. 重新打包分发
```

### Q5: 医院只有 CPU，不需要 GPU 包

可以只准备 CPU 包：

```batch
REM 1. 只下载 CPU 包
pip download -r deployment\requirements_cpu.txt -d deployment\offline_wheels\cpu\

REM 2. 不创建或删除 GPU 目录
REM    安装脚本会自动跳过 GPU 包

REM 3. 打包时排除 GPU 目录
powershell Compress-Archive -Path nb10-ai-cac-lite-v1.1.0 -DestinationPath nb10-ai-cac-cpu-only.zip

REM 最终包大小：~2.5GB
```

---

## 最佳实践

### 准备阶段

1. ✅ 在 Windows 上准备离线包（不是 WSL/Linux）
2. ✅ 验证 wheel 文件平台：`win_amd64`
3. ✅ 测试离线安装成功
4. ✅ 包含 AI 模型文件
5. ✅ 创建 SHA256 校验和验证完整性

### 分发阶段

1. ✅ 使用可靠的传输方式（USB 硬盘优先）
2. ✅ 验证传输后文件完整性
3. ✅ 提供安装说明文档
4. ✅ 提供测试数据样本（可选）

### 部署阶段

1. ✅ 先在测试机器上验证
2. ✅ 确认 Python 版本匹配
3. ✅ 检查磁盘空间充足
4. ✅ 运行 Pilot 模式测试
5. ✅ 培训医生使用流程

---

## 文件清单

完整离线部署包应包含：

```
✅ nb10_windows/                          应用代码
✅ nb10_windows/deployment/offline_wheels/cpu/  CPU离线包（~40个.whl文件）
✅ nb10_windows/deployment/offline_wheels/gpu/  GPU离线包（~40个.whl文件）
✅ nb10_windows/models/va_non_gated_ai_cac_model.pth  AI模型
✅ start_nb10.bat                         启动脚本
✅ docs/                                  文档（可选）
✅ README.md                              使用说明（可选）
```

---

## 联系支持

如有问题：
- 📧 Email: support@example.com
- 📄 文档: docs/USER_MANUAL.md
- 📄 故障排查: deployment/offline_wheels/README.md

---

**版本**: 1.1.0
**最后更新**: 2025-10-17
**维护者**: NB10 Development Team
