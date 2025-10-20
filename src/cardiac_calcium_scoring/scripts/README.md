# NB10 打包脚本使用指南

## 📦 可用的打包脚本

### 1. `package_release_lite_en.sh` ⭐ **推荐**
**用途**: 生成轻量版安装包(不含模型文件)
**语言**: 英文界面
**大小**: ~300KB
**默认版本**: v1.1.0

**特点**:
- ✅ 不包含1.2GB的模型文件,适合网络分发
- ✅ 所有批处理文件使用英文,避免编码问题
- ✅ 自动生成模型下载说明
- ✅ 包含一键启动脚本 `start_nb10.bat`
- ✅ 包含环境检测工具 `check_environment.bat`

**使用方法**:
```bash
cd tools/nb10_windows
./scripts/package_release_lite_en.sh          # 使用默认版本 v1.1.0
./scripts/package_release_lite_en.sh 1.2.0    # 指定版本号
```

**生成的文件**:
```
dist/
├── nb10-ai-cac-lite-v1.1.0/           # 解压目录
├── nb10-ai-cac-lite-v1.1.0.zip        # 安装包 (~300KB)
└── nb10-ai-cac-lite-v1.1.0.zip.sha256 # 校验文件
```

**适用场景**:
- 🌐 通过网络分发给用户
- 💾 U盘拷贝到医院工作站
- 📧 邮件发送
- ☁️ 云盘共享

---

### 2. `package_release.sh`
**用途**: 生成完整版安装包(包含模型文件)
**语言**: 中文界面
**大小**: ~1.2GB
**默认版本**: v1.1.0

**特点**:
- ✅ 包含完整的1.2GB模型文件
- ✅ 开箱即用,无需额外下载
- ⚠️ 文件较大,不适合网络传输

**使用方法**:
```bash
cd tools/nb10_windows
./scripts/package_release.sh              # 使用默认版本 v1.1.0
./scripts/package_release.sh 1.2.0        # 指定版本号
```

**生成的文件**:
```
dist/
├── nb10-ai-cac-full-v1.1.0/           # 解压目录
├── nb10-ai-cac-full-v1.1.0.zip        # 安装包 (~1.2GB)
└── nb10-ai-cac-full-v1.1.0.zip.sha256 # 校验文件
```

**适用场景**:
- 🏥 内网部署(医院内部服务器)
- 💿 光盘或大容量U盘分发
- 🧪 内部测试和验证
- 📦 一次性完整交付

---

### 3. `package_release_lite.sh` ⚠️ **已废弃**
**状态**: 已标记为废弃
**原因**: 中文批处理文件存在编码问题

**问题**:
- ❌ Windows批处理文件包含中文字符
- ❌ 不同地区的Windows系统可能出现乱码
- ❌ chcp 65001命令并不总是有效

**替代方案**:
使用 `package_release_lite_en.sh` (英文版本)

---

## 📋 版本规范

### 当前统一版本: v1.1.0

所有脚本已统一使用语义化版本号:
- `package_release_lite_en.sh`: v1.1.0 (默认)
- `package_release.sh`: v1.1.0 (默认)

### 版本命名规则:
```
v主版本.次版本.修订版本
  │      │      └─── 修复bug
  │      └────────── 添加新功能(向后兼容)
  └───────────────── 重大更新(可能不兼容)
```

**示例**:
- v1.1.0 → 添加了新功能
- v1.1.1 → 修复了bug
- v2.0.0 → 重大架构更新

---

## 🚀 推荐工作流程

### 发布流程:

#### 1. **日常开发和测试** (使用完整版)
```bash
# 生成包含模型的完整版,用于内部测试
./scripts/package_release.sh 1.1.0-beta
```

#### 2. **正式发布** (使用轻量版)
```bash
# 生成轻量版,用于分发
./scripts/package_release_lite_en.sh 1.1.0

# 查看生成的文件
ls -lh dist/nb10-ai-cac-lite-v1.1.0.zip
```

#### 3. **分发给用户**
```bash
# 轻量版安装包 (~300KB)
dist/nb10-ai-cac-lite-v1.1.0.zip

# 单独提供模型文件 (~1.2GB)
tools/nb10_windows/models/va_non_gated_ai_cac_model.pth
```

#### 4. **用户侧安装**
用户收到两个文件:
1. `nb10-ai-cac-lite-v1.1.0.zip` (解压到C盘)
2. `va_non_gated_ai_cac_model.pth` (放到 `nb10_windows/models/`)

然后运行 `start_nb10.bat` 即可自动安装和启动。

---

## 📂 dist目录结构

清理后的dist目录结构:
```
dist/
├── archive/                           # 归档旧版本
│   ├── nb10-ai-cac-v1.0.0.zip        # 旧版本完整包
│   └── nb10-ai-cac-v1.0.0.zip.sha256
├── nb10-ai-cac-lite-v1.1.0.zip       # 最新轻量版
├── nb10-ai-cac-lite-v1.1.0.zip.sha256
├── README.md                          # dist目录说明
├── RELEASE_NOTES.md                   # 发布说明
└── PACKAGE_VERIFICATION.txt           # 验证说明
```

**注意**:
- 解压后的目录不会保留在dist中(节省磁盘空间)
- 旧版本会自动归档到 `archive/` 目录

---

## 🔍 验证打包结果

### 检查包内容:
```bash
# 查看zip文件内容
unzip -l dist/nb10-ai-cac-lite-v1.1.0.zip | head -50

# 验证文件完整性
sha256sum -c dist/nb10-ai-cac-lite-v1.1.0.zip.sha256
```

### 测试安装流程:
```bash
# 解压到临时目录
cd /tmp
unzip ~/path/to/nb10-ai-cac-lite-v1.1.0.zip
cd nb10-ai-cac-lite-v1.1.0

# 在Windows系统上测试:
# 1. 双击 start_nb10.bat
# 2. 检查是否提示下载模型文件
# 3. 验证环境检测是否正常
```

---

## 🐛 常见问题

### Q1: 打包后的zip文件在Windows上显示乱码?
**A**: 使用 `package_release_lite_en.sh` (英文版),所有文本都是英文,不会有编码问题。

### Q2: 如何同时生成完整版和轻量版?
**A**:
```bash
# 先生成完整版(包含模型)
./scripts/package_release.sh 1.1.0

# 再生成轻量版(不含模型)
./scripts/package_release_lite_en.sh 1.1.0
```

### Q3: 模型文件太大,如何分发?
**A**:
- 轻量版: 通过网络/邮件发送 (~300KB)
- 模型文件: 通过医院内网服务器或大容量U盘单独提供 (~1.2GB)

### Q4: 用户如何知道模型文件放在哪里?
**A**: 轻量版包含详细的模型下载说明:
- `nb10_windows/models/README.md`
- `nb10_windows/models/DOWNLOAD_MODEL.txt`
- `start_nb10.bat` 会自动检测并提示

---

## 📝 更新日志

### v1.1.0 (2025-10-16)
- ✅ 统一版本号为 v1.1.0
- ✅ 完整版重命名为 `nb10-ai-cac-full-v*`
- ✅ 轻量版使用版本号命名 `nb10-ai-cac-lite-v*`
- ✅ 标记中文版脚本为废弃
- ✅ 清理dist目录,节省1.5GB空间
- ✅ 归档旧版本到 `archive/` 目录

### v1.0.22 (2025-10-15)
- 轻量英文版修复安装验证逻辑

### v1.0.0 (2025-10-14)
- 初始版本

---

## 📞 技术支持

如有问题,请联系开发团队或查看项目文档:
- 用户手册: `../docs/USER_MANUAL.md`
- 安装指南: `../docs/INSTALLATION_GUIDE.md`
- 打包部署指南: `../docs/PACKAGING_DEPLOYMENT_GUIDE.md`
