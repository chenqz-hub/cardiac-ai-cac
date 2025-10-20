# NB10 AI-CAC Windows应用打包与部署指南

**版本**: v2.0.0-beta
**更新日期**: 2025-10-14
**目标环境**: 医院Windows工作站

---

## 目录

1. [打包方案对比](#打包方案对比)
2. [推荐方案：标准Python包](#方案1-标准python包推荐)
3. [备选方案：独立可执行文件](#方案2-独立可执行文件pyinstaller)
4. [企业方案：Docker容器](#方案3-docker容器企业级)
5. [部署检查清单](#部署检查清单)
6. [医院环境适配](#医院环境适配)

---

## 打包方案对比

| 方案 | 优点 | 缺点 | 推荐场景 |
|-----|------|------|---------|
| **标准Python包** | 体积小、易更新、灵活配置 | 需要Python环境 | ✅ 推荐（有IT支持） |
| **独立可执行文件** | 无需Python、一键运行 | 体积大（~2GB）、不灵活 | 零IT支持的小医院 |
| **Docker容器** | 隔离环境、易管理 | 需要Docker、Windows配置复杂 | 企业级部署 |
| **离线安装包** | 无需网络、快速部署 | 需手动更新依赖 | 内网环境 |

---

## 方案1: 标准Python包（推荐）

### 适用场景
- ✅ 医院有基础IT支持
- ✅ 工作站可以安装Python
- ✅ 需要灵活配置和更新
- ✅ 多台工作站部署

### 打包内容结构

```
nb10-ai-cac-v2.0.0-beta/
├── nb10_windows/                  # 应用主目录
│   ├── cli/                       # 命令行工具
│   ├── core/                      # 核心模块
│   ├── config/                    # 配置文件
│   ├── models/                    # AI模型（1.2GB）
│   │   └── va_non_gated_ai_cac_model.pth
│   ├── docs/                      # 文档
│   ├── deployment/                # 部署工具
│   │   ├── requirements.txt       # Python依赖
│   │   ├── requirements_gpu.txt   # GPU版本依赖
│   │   ├── requirements_cpu.txt   # CPU版本依赖
│   │   └── offline_wheels/        # 离线依赖包（可选）
│   ├── scripts/                   # 工具脚本
│   ├── output/                    # 输出目录（空）
│   ├── logs/                      # 日志目录（空）
│   └── data/                      # 数据目录（空）
├── install_gpu.bat                # GPU版本一键安装脚本
├── install_cpu.bat                # CPU版本一键安装脚本
├── run_nb10.bat                   # Windows快捷启动脚本
├── README.txt                     # 快速开始指南
├── LICENSE.txt                    # 许可证
└── CHANGELOG.txt                  # 版本更新日志
```

### 创建打包脚本

让我为您创建一键打包脚本：

```bash
# 自动打包脚本（在Linux/WSL上运行）
./scripts/package_release.sh
```

### 部署步骤（医院端）

#### 步骤1: 解压安装包
```cmd
# 解压到C盘（避免中文路径）
C:\nb10-ai-cac-v2.0.0-beta\
```

#### 步骤2: 安装Python（如未安装）
```
1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.10+ (推荐3.12)
3. 安装时勾选 "Add Python to PATH"
```

#### 步骤3: 安装依赖
```cmd
# GPU版本（推荐，需要NVIDIA显卡）
cd C:\nb10-ai-cac-v2.0.0-beta
install_gpu.bat

# CPU版本（无GPU时使用）
install_cpu.bat
```

#### 步骤4: 配置路径
编辑 `nb10_windows/config/config.yaml`:
```yaml
paths:
  data_dir: "D:/DICOM_Data"  # 修改为实际DICOM数据路径
  output_dir: "D:/NB10_Results"  # 修改为结果输出路径
```

#### 步骤5: 运行测试
```cmd
# 双击运行
run_nb10.bat

# 或手动运行
cd nb10_windows
python cli/run_nb10.py --data-dir "D:/DICOM_Data" --mode pilot --pilot-limit 5
```

### 优势总结
- ✅ 体积小（依赖另行下载）
- ✅ 易于更新（替换代码即可）
- ✅ 配置灵活
- ✅ 性能最优

---

## 方案2: 独立可执行文件（PyInstaller）

### 适用场景
- ✅ 无IT支持的小诊所
- ✅ 工作站无法安装Python
- ✅ 需要"开箱即用"
- ⚠️ 接受较大体积（~2GB）

### 打包步骤

```bash
# 在开发环境运行
cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/nb10_windows

# 安装PyInstaller
pip install pyinstaller

# 生成可执行文件
pyinstaller --onefile \
  --name nb10_ai_cac \
  --icon=assets/icon.ico \
  --add-data "models:models" \
  --add-data "config:config" \
  --hidden-import torch \
  --hidden-import monai \
  --hidden-import pydicom \
  cli/run_nb10.py
```

### 打包内容
```
nb10-ai-cac-standalone-v2.0.0/
├── nb10_ai_cac.exe           # 主程序（~2GB）
├── config/                    # 配置文件目录
│   └── config.yaml
├── output/                    # 输出目录
├── logs/                      # 日志目录
├── README.txt                 # 使用说明
└── 快速启动.bat               # 启动脚本
```

### 使用方式（医院端）
```cmd
# 双击运行
快速启动.bat

# 或命令行
nb10_ai_cac.exe --data-dir "D:/DICOM_Data" --mode pilot --pilot-limit 5
```

### 优势总结
- ✅ 无需安装Python
- ✅ 一键运行
- ✅ 适合非技术人员
- ⚠️ 体积大（~2GB）
- ⚠️ 更新需要重新打包

---

## 方案3: Docker容器（企业级）

### 适用场景
- ✅ 大型医院信息中心
- ✅ 需要统一管理多个工作站
- ✅ 有Docker经验的IT团队
- ⚠️ Windows Docker配置较复杂

### Dockerfile示例

```dockerfile
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

WORKDIR /app

# 安装依赖
COPY deployment/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用
COPY nb10_windows/ /app/nb10_windows/

# 暴露输出目录
VOLUME ["/data", "/output"]

# 启动命令
ENTRYPOINT ["python", "/app/nb10_windows/cli/run_nb10.py"]
CMD ["--help"]
```

### 使用方式
```bash
# 构建镜像
docker build -t nb10-ai-cac:v2.0.0 .

# 运行
docker run --gpus all \
  -v D:/DICOM_Data:/data \
  -v D:/NB10_Results:/output \
  nb10-ai-cac:v2.0.0 \
  --data-dir /data --output-dir /output --mode pilot
```

---

## 打包准备清单

### 1. 清理开发文件
```bash
cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/nb10_windows

# 清理缓存
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name ".DS_Store" -delete

# 清理输出目录
rm -rf output/*.csv
rm -rf logs/*.log
rm -rf data/cache/*

# 保留README文件
```

### 2. 准备发布文件

#### README.txt（快速开始指南）
```text
================================================================================
NB10 AI-CAC 冠脉钙化评分工具 v2.0.0-beta
================================================================================

这是一个基于AI的冠状动脉钙化评分工具，适用于Windows环境。

【硬件要求】
  推荐配置：
    - NVIDIA GPU (RTX 2060及以上，6GB+ VRAM)
    - 8GB+ RAM
    - Windows 10/11 64位

  最低配置：
    - CPU模式（较慢）
    - 4GB+ RAM
    - Windows 10/11 64位

【快速开始】
  1. 解压到C盘（避免中文路径）
  2. 双击运行 install_gpu.bat (GPU版本) 或 install_cpu.bat (CPU版本)
  3. 编辑 nb10_windows/config/config.yaml 配置数据路径
  4. 双击运行 run_nb10.bat

【命令行用法】
  cd nb10_windows
  python cli/run_nb10.py --data-dir <DICOM路径> --mode pilot --pilot-limit 5

【技术支持】
  文档: nb10_windows/docs/
  邮箱: support@example.com

【版权声明】
  (C) 2025 Chen Doctor Team. All rights reserved.
  仅供医学研究使用。
```

#### install_gpu.bat
```batch
@echo off
echo ========================================
echo NB10 AI-CAC GPU版本依赖安装
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 检测到Python版本:
python --version

echo.
echo [2/3] 创建虚拟环境...
python -m venv venv

echo.
echo [3/3] 安装依赖包（这可能需要几分钟）...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r nb10_windows\deployment\requirements_gpu.txt

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo 下一步:
echo   1. 编辑 nb10_windows\config\config.yaml 配置数据路径
echo   2. 双击运行 run_nb10.bat 启动程序
echo.
pause
```

#### install_cpu.bat
```batch
@echo off
echo ========================================
echo NB10 AI-CAC CPU版本依赖安装
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 检测到Python版本:
python --version

echo.
echo [2/3] 创建虚拟环境...
python -m venv venv

echo.
echo [3/3] 安装依赖包（这可能需要几分钟）...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r nb10_windows\deployment\requirements_cpu.txt

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo 注意: CPU模式运行较慢（约50-100秒/患者）
echo 建议使用NVIDIA GPU以获得最佳性能（10-15秒/患者）
echo.
echo 下一步:
echo   1. 编辑 nb10_windows\config\config.yaml 配置数据路径
echo   2. 双击运行 run_nb10.bat 启动程序
echo.
pause
```

#### run_nb10.bat
```batch
@echo off
echo ========================================
echo NB10 AI-CAC 启动器
echo ========================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\python.exe" (
    echo [错误] 未找到虚拟环境
    echo 请先运行 install_gpu.bat 或 install_cpu.bat
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查模型文件
if not exist "nb10_windows\models\va_non_gated_ai_cac_model.pth" (
    echo [警告] 未找到模型文件
    echo 请确保 nb10_windows\models\va_non_gated_ai_cac_model.pth 存在
    pause
    exit /b 1
)

echo [启动] NB10 AI-CAC 工具...
echo.
echo 使用说明:
echo   --data-dir: DICOM数据目录
echo   --mode: pilot (测试模式) 或 full (完整模式)
echo   --pilot-limit: 测试病例数
echo.
echo 示例:
echo   python cli\run_nb10.py --data-dir "D:\DICOM_Data" --mode pilot --pilot-limit 5
echo.
echo ========================================
echo.

cd nb10_windows
python cli\run_nb10.py --help

echo.
echo 按任意键退出...
pause >nul
```

### 3. 生成版本信息

#### VERSION.txt
```text
NB10 AI-CAC v2.0.0-beta
Build Date: 2025-10-14
Git Commit: 3211282

Features:
- ✅ Phase 1: Hardware Adaptive Optimization (17.2% performance boost)
- ✅ Phase 2: Safety Monitoring System (OOM protection)
- ✅ Automatic hardware detection
- ✅ Multi-tier performance profiles
- ✅ Real-time resource monitoring
- ✅ Comprehensive logging

Compatibility:
- Windows 10/11 (64-bit)
- Python 3.10+
- CUDA 11.7+ (GPU version)
- CPU fallback supported
```

---

## 自动打包脚本

让我创建一个一键打包脚本：

### scripts/package_release.sh

```bash
#!/bin/bash
# NB10 AI-CAC Release Packaging Script
# Usage: ./scripts/package_release.sh [version]

set -e

VERSION=${1:-"2.0.0-beta"}
RELEASE_NAME="nb10-ai-cac-v${VERSION}"
PACKAGE_DIR="./dist/${RELEASE_NAME}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "NB10 AI-CAC Release Packaging"
echo "Version: ${VERSION}"
echo "=========================================="
echo ""

# 1. 清理旧构建
echo "[1/6] Cleaning old builds..."
rm -rf dist/${RELEASE_NAME}
mkdir -p ${PACKAGE_DIR}

# 2. 复制核心文件
echo "[2/6] Copying application files..."
cp -r cli core config deployment docs scripts examples tests ${PACKAGE_DIR}/nb10_windows/
cp README.md CHANGELOG.md PROJECT_STRUCTURE.md ${PACKAGE_DIR}/nb10_windows/
cp PHASE1_STATUS.md ${PACKAGE_DIR}/nb10_windows/docs/

# 3. 创建空目录
echo "[3/6] Creating output directories..."
mkdir -p ${PACKAGE_DIR}/nb10_windows/{output,logs,data/cache}
echo "输出目录" > ${PACKAGE_DIR}/nb10_windows/output/README.md
echo "日志目录" > ${PACKAGE_DIR}/nb10_windows/logs/README.md

# 4. 复制模型文件（如果存在）
echo "[4/6] Copying model files..."
if [ -f "models/va_non_gated_ai_cac_model.pth" ]; then
    mkdir -p ${PACKAGE_DIR}/nb10_windows/models
    cp models/va_non_gated_ai_cac_model.pth ${PACKAGE_DIR}/nb10_windows/models/
    echo "✓ Model file included (1.2GB)"
else
    mkdir -p ${PACKAGE_DIR}/nb10_windows/models
    echo "模型文件下载说明见 deployment/download_models.py" > ${PACKAGE_DIR}/nb10_windows/models/README.md
    echo "⚠ Model file not found - download required"
fi

# 5. 生成Windows批处理文件
echo "[5/6] Generating Windows scripts..."

# install_gpu.bat (见上文)
cat > ${PACKAGE_DIR}/install_gpu.bat << 'EOF'
@echo off
REM [内容见上文install_gpu.bat]
EOF

# install_cpu.bat (见上文)
cat > ${PACKAGE_DIR}/install_cpu.bat << 'EOF'
@echo off
REM [内容见上文install_cpu.bat]
EOF

# run_nb10.bat (见上文)
cat > ${PACKAGE_DIR}/run_nb10.bat << 'EOF'
@echo off
REM [内容见上文run_nb10.bat]
EOF

# 6. 生成发布文档
echo "[6/6] Generating release documents..."

# README.txt (见上文)
cat > ${PACKAGE_DIR}/README.txt << 'EOF'
[内容见上文README.txt]
EOF

# VERSION.txt
cat > ${PACKAGE_DIR}/VERSION.txt << EOF
NB10 AI-CAC v${VERSION}
Build Date: $(date +%Y-%m-%d)
Git Commit: $(git rev-parse --short HEAD)

[内容见上文VERSION.txt]
EOF

# CHANGELOG.txt
cp CHANGELOG.md ${PACKAGE_DIR}/CHANGELOG.txt

# 7. 清理开发文件
echo ""
echo "Cleaning development files..."
cd ${PACKAGE_DIR}/nb10_windows
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
find . -type f -name ".DS_Store" -delete
cd -

# 8. 创建压缩包
echo ""
echo "Creating archive..."
cd dist
zip -r ${RELEASE_NAME}.zip ${RELEASE_NAME}/ -q
cd -

# 9. 生成校验和
echo ""
echo "Generating checksums..."
cd dist
sha256sum ${RELEASE_NAME}.zip > ${RELEASE_NAME}.zip.sha256
cd -

# 10. 完成
echo ""
echo "=========================================="
echo "✓ Package created successfully!"
echo "=========================================="
echo ""
echo "Output:"
echo "  Package: dist/${RELEASE_NAME}/"
echo "  Archive: dist/${RELEASE_NAME}.zip"
echo "  SHA256:  dist/${RELEASE_NAME}.zip.sha256"
echo ""
du -sh dist/${RELEASE_NAME}.zip
echo ""
echo "Next steps:"
echo "  1. Test the package on Windows"
echo "  2. Upload to distribution server"
echo "  3. Update download links in documentation"
echo ""
```

---

## 部署检查清单

### 打包前检查
- [ ] 所有代码已提交到Git
- [ ] 版本号已更新（VERSION.txt, CHANGELOG.md）
- [ ] 模型文件已准备（1.2GB）
- [ ] 文档已更新（README, 用户手册）
- [ ] 依赖列表已确认（requirements*.txt）
- [ ] 测试通过（至少5例pilot测试）
- [ ] 清理了开发文件（__pycache__, *.pyc）

### 医院部署前检查
- [ ] 确认硬件配置（GPU型号、RAM大小）
- [ ] 确认Python版本（3.10+）
- [ ] 确认CUDA版本（11.7+，如使用GPU）
- [ ] 准备测试DICOM数据（5-10例）
- [ ] 确认网络环境（在线/离线安装）
- [ ] 准备安装文档和培训材料

### 首次运行检查
- [ ] 虚拟环境创建成功
- [ ] 依赖包安装完整
- [ ] 模型文件加载成功
- [ ] GPU检测正常（如有）
- [ ] 配置文件路径正确
- [ ] 测试数据处理成功
- [ ] 输出CSV格式正确
- [ ] 日志记录正常

---

## 医院环境适配

### 常见问题处理

#### 1. 无网络环境（内网）
**解决方案**: 离线依赖包
```bash
# 在有网络的机器上预下载
pip download -r deployment/requirements_gpu.txt -d offline_wheels/

# 在目标机器上离线安装
pip install --no-index --find-links=offline_wheels/ -r deployment/requirements_gpu.txt
```

#### 2. 无GPU环境
**解决方案**: CPU模式
```yaml
# config/config.yaml
processing:
  device: "cpu"  # 改为cpu模式

performance:
  num_workers: 2  # CPU可以增加worker数
```

#### 3. 低内存环境（<8GB RAM）
**解决方案**: 已自动适配
- Phase 1硬件自适应优化会自动检测
- Phase 2安全监控会实时保护
- 建议关闭其他程序以释放内存

#### 4. 中文路径问题
**解决方案**:
```
✓ 推荐: C:\nb10-ai-cac\
✗ 避免: C:\用户\文档\nb10\
```

#### 5. 权限问题
**解决方案**:
- 以管理员身份运行安装脚本
- 或安装到用户目录（无需管理员权限）

---

## 更新和维护

### 版本更新流程
1. 替换 `nb10_windows/` 目录（保留config/config.yaml）
2. 运行 `pip install -r deployment/requirements.txt` 更新依赖
3. 查看 CHANGELOG.txt 了解新功能
4. 运行测试验证

### 配置迁移
```bash
# 备份配置
copy nb10_windows\config\config.yaml config_backup.yaml

# 更新后恢复
copy config_backup.yaml nb10_windows\config\config.yaml
```

---

## 总结建议

### 推荐方案
对于大多数医院环境，我们推荐：

**方案1（标准Python包） + 离线依赖包**

原因：
1. ✅ 体积适中（~1.5GB含模型）
2. ✅ 灵活配置，易于更新
3. ✅ 性能最优
4. ✅ 适配Phase 1/2所有优化
5. ✅ 支持在线/离线安装

### 打包命令
```bash
# 在项目根目录运行
cd /home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research/tools/nb10_windows

# 执行打包
chmod +x scripts/package_release.sh
./scripts/package_release.sh 2.0.0-beta

# 输出
dist/nb10-ai-cac-v2.0.0-beta.zip  (~1.5GB)
```

### 分发方式
1. **U盘拷贝**: 直接拷贝ZIP文件到医院
2. **网络下载**: 上传到医院内网服务器
3. **百度网盘**: 提供下载链接和提取码

---

**文档维护**: Chen Doctor Team
**技术支持**: support@example.com
**最后更新**: 2025-10-14
