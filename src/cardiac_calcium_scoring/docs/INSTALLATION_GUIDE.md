# NB10 Windows Tool - 安装指南

**版本**: 1.1.0
**更新日期**: 2025-10-17
**适用系统**: Windows 10/11, Linux

---

## 📋 目录

1. [系统要求](#系统要求)
2. [安装方式](#安装方式)
3. [在线安装（推荐）](#在线安装推荐)
4. [离线安装](#离线安装)
5. [验证安装](#验证安装)
6. [常见问题](#常见问题)
7. [卸载](#卸载)

---

## 系统要求

### 硬件要求

**最低配置**:
- CPU: Intel i5 或同等性能CPU
- 内存: 16GB RAM
- 硬盘: 10GB可用空间
- GPU: 可选

**推荐配置**:
- CPU: Intel i7/i9 或 AMD Ryzen 7/9
- 内存: 32GB RAM
- 硬盘: 50GB SSD可用空间
- GPU: NVIDIA RTX 2060 (6GB) 或更高

**GPU要求（可选但强烈推荐）**:
- NVIDIA显卡，支持CUDA 12.x
- 最小显存: 6GB (RTX 2060, RTX 3050等)
- 推荐显存: 8GB+ (RTX 3060, RTX 4060等)

### 软件要求

**必需**:
- **操作系统**:
  - Windows 10/11 (64-bit)
  - Linux (Ubuntu 20.04+, 或其他发行版)
- **Python**: 3.10, 3.11, 或 3.12
- **磁盘空间**: 至少10GB（含模型和依赖）

**GPU版本额外要求**:
- **NVIDIA驱动**: 版本 ≥ 525.60.13 (Linux) 或 ≥ 528.33 (Windows)
- **CUDA**: 12.1 或 12.7 (随PyTorch自动安装)

---

## 安装方式

NB10工具提供两种安装方式：

1. **在线安装**（推荐）：需要网络连接，自动下载所有依赖
2. **离线安装**：适用于无法访问国际网络或需要离线部署的环境

---

## 在线安装（推荐）

### Step 1: 安装Python

#### Windows

1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载 Python 3.10, 3.11 或 3.12 Windows安装包
3. 运行安装程序：
   - ✅ 勾选 "Add Python to PATH"
   - ✅ 选择 "Install Now"
4. 验证安装：
   ```cmd
   python --version
   ```
   应显示: `Python 3.x.x`

#### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip

# 或使用pyenv管理多个Python版本
curl https://pyenv.run | bash
pyenv install 3.10.13
pyenv global 3.10.13
```

---

### Step 2: 获取NB10代码

#### 选项A: 从Git仓库克隆

```bash
# 克隆完整项目
git clone https://github.com/your-org/cardiac-ml-research.git
cd cardiac-ml-research/tools/nb10_windows

# 或仅克隆NB10工具（如果单独发布）
git clone https://github.com/your-org/nb10-windows.git
cd nb10-windows
```

#### 选项B: 下载ZIP包

1. 下载项目ZIP文件
2. 解压到目标目录
3. 进入 `tools/nb10_windows/` 目录

---

### Step 3: 创建虚拟环境

虚拟环境可以隔离项目依赖，避免与其他Python项目冲突。

#### Windows

```cmd
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 验证
python --version
where python
```

#### Linux

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 验证
python --version
which python
```

**激活成功标志**: 命令提示符前会显示 `(venv)`

---

### Step 4: 安装依赖

#### 选项A: GPU版本（推荐，如果有NVIDIA GPU）

```bash
# 验证GPU可用性
nvidia-smi

# 安装GPU版本依赖
pip install -r deployment/requirements_gpu.txt
```

**预计下载大小**: ~3.5GB
**预计安装时间**: 5-15分钟（取决于网络速度）

#### 选项B: CPU版本（如果没有GPU）

```bash
# 安装CPU版本依赖
pip install -r deployment/requirements_cpu.txt
```

**预计下载大小**: ~1.5GB
**预计安装时间**: 3-10分钟

**注意**: CPU版本推理速度较慢（~10-20分钟/例 vs ~30秒/例 GPU）

---

### Step 5: 下载AI-CAC模型

模型文件约1.12GB，需要单独下载。

#### 选项A: 使用下载脚本

```bash
python deployment/download_models.py
```

按提示确认下载。

#### 选项B: 手动下载

1. 访问 [AI-CAC Release](https://github.com/Raffi-Hagopian/AI-CAC/releases/tag/v1.0.0)
2. 下载 `va_non_gated_ai_cac_model.pth` (1.12GB)
3. 保存到 `models/` 目录:
   ```bash
   # 验证文件大小应为 ~1.2GB
   ls -lh models/va_non_gated_ai_cac_model.pth
   ```

#### 选项C: 使用gdown（如果可用）

```bash
pip install gdown
gdown 1uD12kphnWlJ5R6K-mDQnxS8LjYhPGSfm -O models/va_non_gated_ai_cac_model.pth
```

---

### Step 6: 配置NB10

```bash
# 复制配置模板
cp config/config.yaml.template config/config.yaml

# 编辑配置文件
nano config/config.yaml  # Linux
notepad config/config.yaml  # Windows
```

**最小必需配置**:

```yaml
paths:
  data_dir: "/path/to/your/dicom/data"  # DICOM数据目录
  model_path: "./models/va_non_gated_ai_cac_model.pth"
  output_dir: "./output"

processing:
  mode: "pilot"  # 或 "full"
  device: "cuda"  # 或 "cpu"
```

详细配置说明见 [配置指南](CONFIGURATION_GUIDE.md)

---

### Step 7: 验证安装

运行快速测试验证安装成功：

```bash
# 测试单个案例
python cli/run_nb10.py --config config/config.yaml --mode pilot --pilot-limit 1
```

**预期输出**:
```
======================================================================
NB10 AI-CAC Tool v1.0.0-beta
======================================================================

Loading configuration from: config/config.yaml
✓ Configuration loaded

[1/1] Processing: patient_001
  ✓ Success - Agatston Score: 123.45

Inference Complete:
  Success: 1/1

Results saved to: output/nb10_results_latest.csv
```

---

## 离线安装

适用于无法访问国际网络的环境。

> **✨ v1.1.0 新特性**: 现在支持嵌套目录结构，可自动检测 `deployment/offline_wheels/gpu/` 和 `deployment/offline_wheels/cpu/` 等子目录中的安装包。

### 准备离线安装包（在有网络的机器上）

#### Step 1: 下载wheel文件

```bash
# 创建wheels目录
mkdir -p deployment/offline_wheels

# GPU版本
pip download -r deployment/requirements_gpu.txt -d deployment/offline_wheels

# 或CPU版本
pip download -r deployment/requirements_cpu.txt -d deployment/offline_wheels
```

**下载大小**: GPU版本 ~3.5GB, CPU版本 ~1.5GB

#### Step 2: 下载模型文件

按照前面"Step 5: 下载AI-CAC模型"的说明下载模型到 `models/` 目录

#### Step 3: 打包项目

```bash
# Windows
tar -czf nb10-windows-offline.tar.gz .

# Linux
tar -czf nb10-windows-offline.tar.gz \
  --exclude=venv \
  --exclude=__pycache__ \
  --exclude=*.pyc \
  --exclude=output/* \
  --exclude=logs/*.log \
  .
```

**完整包大小**: ~5-7GB (含wheel文件和模型)

---

### 在离线机器上安装

#### Step 1: 传输安装包

通过U盘、网盘或其他方式将 `nb10-windows-offline.tar.gz` 传输到目标机器

#### Step 2: 解压

```bash
tar -xzf nb10-windows-offline.tar.gz
cd nb10-windows
```

#### Step 3: 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux
python3 -m venv venv
source venv/bin/activate
```

#### Step 4: 离线安装依赖

```bash
# GPU版本 - 自动检测以下位置（按优先级）：
# 1. deployment/offline_wheels/gpu/
# 2. deployment/offline_wheels/
# 3. offline_packages/gpu_wheels/
pip install --no-index --find-links=deployment/offline_wheels -r deployment/requirements_gpu.txt

# CPU版本 - 自动检测以下位置（按优先级）：
# 1. deployment/offline_wheels/cpu/
# 2. deployment/offline_wheels/
# 3. offline_packages/cpu_wheels/
pip install --no-index --find-links=deployment/offline_wheels -r deployment/requirements_cpu.txt
```

> **💡 提示**: v1.1.0 支持嵌套目录结构，安装脚本会自动查找最合适的wheel包位置。

#### Step 5: 配置和验证

按照在线安装的 Step 6 和 Step 7 进行配置和验证

---

## 验证安装

### 验证Python依赖

```bash
# 验证PyTorch
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
# 应输出: PyTorch: 2.2.0+cu121 或 2.2.0+cpu

# 验证MONAI
python -c "import monai; print(f'MONAI: {monai.__version__}')"
# 应输出: MONAI: 1.3.2

# 验证GPU（如果安装GPU版本）
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
# 应输出: CUDA available: True, GPU: NVIDIA GeForce RTX 2060
```

### 验证模型文件

```bash
# Windows
dir models\va_non_gated_ai_cac_model.pth

# Linux
ls -lh models/va_non_gated_ai_cac_model.pth

# 应显示文件大小约1.2GB
```

### 运行完整测试

```bash
# 运行自带测试脚本（如果提供）
python tests/test_installation.py

# 或运行Pilot模式
python cli/run_nb10.py --config config/config.yaml --mode pilot --pilot-limit 1
```

---

## 常见问题

### Q1: `ImportError: No module named 'torch'`

**原因**: PyTorch未安装或虚拟环境未激活

**解决**:
```bash
# 确认虚拟环境已激活（提示符前有 (venv)）
# Windows
venv\Scripts\activate

# Linux
source venv/bin/activate

# 重新安装
pip install -r deployment/requirements_gpu.txt
```

---

### Q2: `CUDA out of memory`

**原因**: GPU显存不足

**解决方法**:

**方法1**: 减少batch size (已在代码中优化为4，6GB GPU可用)

**方法2**: 使用CPU模式
```bash
python cli/run_nb10.py --config config/config.yaml --device cpu
```

**方法3**: 关闭其他占用GPU的程序
```bash
nvidia-smi  # 查看GPU占用
```

---

### Q3: `No module named 'einops'`

**原因**: 缺少einops依赖

**解决**:
```bash
pip install einops
```

---

### Q4: NumPy版本不兼容

**错误**: `A module that was compiled using NumPy 1.x cannot be run in NumPy 2.x`

**解决**:
```bash
pip install "numpy<2"
```

---

### Q5: Python 3.12缺少distutils

**错误**: `ModuleNotFoundError: No module named 'distutils'`

**解决**:
```bash
pip install setuptools
```

---

### Q6: 模型下载失败

**原因**: Google Drive访问受限或网络问题

**解决方法**:

**方法1**: 使用备用下载链接（如果提供）

**方法2**: 手动下载
1. 访问 https://github.com/Raffi-Hagopian/AI-CAC/releases
2. 下载 va_non_gated_ai_cac_model.pth
3. 放到 models/ 目录

**方法3**: 使用国内镜像（如果可用）

---

### Q7: pip安装速度慢

**解决**: 使用国内镜像

```bash
# 清华镜像
pip install -r deployment/requirements_gpu.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 阿里镜像
pip install -r deployment/requirements_gpu.txt -i https://mirrors.aliyun.com/pypi/simple/

# 或永久配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 卸载

### 完全卸载

```bash
# 1. 停用虚拟环境
deactivate

# 2. 删除虚拟环境
# Windows
rmdir /s venv

# Linux
rm -rf venv

# 3. 删除项目目录（可选）
cd ..
rm -rf nb10-windows

# 4. 清理pip缓存（可选）
pip cache purge
```

### 仅卸载依赖包

```bash
# 激活虚拟环境
source venv/bin/activate  # Linux
venv\Scripts\activate     # Windows

# 卸载所有依赖
pip uninstall -r deployment/requirements.txt -y
```

---

## 升级

### 从旧版本升级

```bash
# 1. 备份配置文件
cp config/config.yaml config/config.yaml.backup

# 2. 备份输出结果（如果需要）
cp -r output output_backup

# 3. 拉取最新代码
git pull origin main

# 4. 升级依赖
pip install --upgrade -r deployment/requirements_gpu.txt

# 5. 恢复配置文件
cp config/config.yaml.backup config/config.yaml

# 6. 验证
python cli/run_nb10.py --version
```

---

## 技术支持

**文档**:
- [主README](../README.md)
- [用户手册](USER_MANUAL.md)
- [研究思路](RESEARCH_RATIONALE.md)
- [快速开始](../快速开始.md)

**问题反馈**:
- GitHub Issues: https://github.com/your-org/nb10-windows/issues
- Email: support@your-org.com

**日志位置**:
- 安装日志: `logs/install.log`
- 运行日志: `logs/nb10_*.log`

---

**安装完成后，请参考 [用户手册](USER_MANUAL.md) 开始使用NB10工具！**

---

**文档版本**: 1.1.0
**最后更新**: 2025-10-17
**维护者**: NB10 Development Team
