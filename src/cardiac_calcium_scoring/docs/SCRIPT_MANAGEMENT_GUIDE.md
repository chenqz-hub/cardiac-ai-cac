# NB10脚本管理和调用指南

## 📚 目录
1. [问题现状](#问题现状)
2. [脚本差异分析](#脚本差异分析)
3. [最佳实践方案](#最佳实践方案)
4. [开发环境使用](#开发环境使用)
5. [生产环境部署](#生产环境部署)
6. [脚本维护策略](#脚本维护策略)

---

## 问题现状

### 当前发现的问题

您观察到的问题非常准确:

1. **nb10_windows根目录** 有中文批处理文件:
   - `start_nb10.bat` (中文界面)
   - `nb10.bat` (中文界面，功能丰富的菜单系统)

2. **打包脚本生成的** 批处理文件是英文:
   - `scripts/package_release_lite_en.sh` 生成的 `start_nb10.bat` (英文界面)

3. **结果**: 存在**两套不同的脚本**,可能导致维护问题

---

## 脚本差异分析

### 📊 对比表格

| 特性 | 开发版 (根目录) | 发布版 (打包脚本生成) |
|------|----------------|---------------------|
| **位置** | `tools/nb10_windows/` | `dist/nb10-ai-cac-lite-v*/` |
| **语言** | 中文 | 英文 |
| **功能** | 丰富(菜单系统) | 简化(一键启动) |
| **目标用户** | 开发者/研究人员 | 医院用户 |
| **路径结构** | 项目根目录 | 打包后结构 |

### 🔍 详细对比

#### 1. **开发版 `nb10.bat`** (根目录)

**特点**:
```batch
✓ 中文界面，适合中文用户
✓ 功能丰富的菜单系统:
  - 快速测试
  - 处理CHD组
  - 处理Normal组
  - 统计分析
  - 查看配置
  - 查看日志
✓ 多种运行模式
✓ 详细的日志记录
✓ 交互式操作
```

**调用方式**:
```bash
# 开发环境 (WSL/Linux)
cd tools/nb10_windows
./nb10.bat            # 显示菜单
./nb10.bat test       # 快速测试
./nb10.bat chd        # 处理CHD组
```

**路径假设**:
- venv在 `nb10_windows/venv/` (相对于nb10.bat所在目录的子目录)
- Python脚本在 `cli/run_nb10.py`

---

#### 2. **开发版 `start_nb10.bat`** (根目录)

**特点**:
```batch
✓ 中文界面
✓ 一键启动脚本
✓ 自动检测和安装
✓ 路径结构: nb10_windows/venv/
```

**调用方式**:
```bash
# 从项目根目录调用
cd /path/to/project/root
./start_nb10.bat
```

**路径假设**:
- venv在 `nb10_windows/venv/` (子目录)
- 脚本在 `nb10_windows/cli/run_nb10.py`

---

#### 3. **发布版 `start_nb10.bat`** (打包生成)

**特点**:
```batch
✓ 英文界面，避免编码问题
✓ 一键启动脚本
✓ 自动检测和安装
✓ 路径结构: venv/ (同级目录)
```

**调用方式**:
```bash
# 用户解压后
cd C:\nb10-ai-cac-lite-v1.1.0
start_nb10.bat
```

**路径假设**:
- venv在 `venv/` (同级目录)
- 脚本在 `nb10_windows/cli/run_nb10.py`

---

## 最佳实践方案

### 🎯 推荐方案: **双环境脚本策略**

**核心思想**: 不同环境使用不同脚本,通过目录结构和命名区分

```
project_root/
├── tools/nb10_windows/          # 开发环境
│   ├── nb10.bat                 # 开发者菜单 (中文,功能丰富)
│   ├── start_dev.bat            # 开发环境启动脚本 (推荐重命名)
│   ├── venv/                    # 开发环境虚拟环境
│   └── cli/run_nb10.py
│
└── dist/                        # 发布环境
    └── nb10-ai-cac-lite-v1.1.0/
        ├── start_nb10.bat       # 生产环境启动脚本 (英文)
        ├── venv/                # 生产环境虚拟环境
        └── nb10_windows/
            └── cli/run_nb10.py
```

---

## 开发环境使用

### 🛠️ 方案1: 使用开发版菜单系统 (推荐)

**适用**: 日常开发、数据处理、研究分析

```bash
# 1. 在WSL/Linux环境下
cd /home/wuxia/projects/.../tools/nb10_windows

# 2. 使用功能丰富的菜单
./nb10.bat              # 显示菜单
./nb10.bat test         # 快速测试5例
./nb10.bat chd          # 处理CHD组
./nb10.bat normal       # 处理Normal组
./nb10.bat analyze      # 统计分析
```

**特点**:
- ✅ 功能完整,支持多种操作
- ✅ 中文界面,便于理解
- ✅ 自动日志记录
- ✅ 适合研究和开发

---

### 🛠️ 方案2: 直接调用Python脚本 (灵活)

**适用**: 需要自定义参数的场景

```bash
# 在WSL/Linux环境下
cd /home/wuxia/projects/.../tools/nb10_windows

# 激活虚拟环境
source venv/bin/activate  # Linux/WSL
# 或
venv\Scripts\activate.bat  # Windows

# 直接调用Python脚本
python cli/run_nb10.py --config config/config.yaml --mode pilot --pilot-limit 5

# 自定义数据目录
python cli/run_nb10.py --data-dir /mnt/d/MedicalData --mode full

# 查看帮助
python cli/run_nb10.py --help
```

**特点**:
- ✅ 最大灵活性
- ✅ 跨平台 (Linux/Windows)
- ✅ 适合脚本化和自动化
- ✅ 可以精确控制所有参数

---

### 🛠️ 方案3: 使用start_nb10.bat (简化)

```bash
# 在项目根目录
cd /path/to/project/root
./tools/nb10_windows/start_nb10.bat
```

**特点**:
- ✅ 一键启动
- ✅ 自动安装依赖
- ⚠️ 功能较简单

---

## 生产环境部署

### 🏥 医院用户使用流程

**用户收到的文件**:
```
nb10-ai-cac-lite-v1.1.0.zip     # 轻量版安装包
va_non_gated_ai_cac_model.pth   # 模型文件 (单独提供)
```

**安装和使用步骤**:

```bash
# 1. 解压到C盘
C:\nb10-ai-cac-lite-v1.1.0\

# 2. 放置模型文件
C:\nb10-ai-cac-lite-v1.1.0\nb10_windows\models\va_non_gated_ai_cac_model.pth

# 3. 一键启动 (双击运行)
start_nb10.bat

# 4. 程序会自动:
#    - 检测Python环境
#    - 检测GPU/CPU
#    - 安装依赖
#    - 启动程序
```

**特点**:
- ✅ 英文界面,避免编码问题
- ✅ 一键操作,降低使用门槛
- ✅ 自动化程度高
- ✅ 适合非技术用户

---

## 脚本维护策略

### ⚠️ 当前问题: 维护两套脚本?

**回答: 不需要!** 采用以下策略:

---

### 📋 策略1: **分离开发版和发布版** (推荐)

#### 原则:
- **开发版脚本**: 保留在项目根目录,功能丰富,用于开发
- **发布版脚本**: 由打包脚本动态生成,简化功能,用于分发

#### 实施:

##### 1. **重命名开发版脚本** (避免混淆)

```bash
# 当前
tools/nb10_windows/start_nb10.bat  → 中文,开发版

# 建议重命名为
tools/nb10_windows/start_dev.bat   → 明确标识为开发版
```

##### 2. **打包脚本保持现状**

```bash
scripts/package_release_lite_en.sh
# 继续生成英文版的 start_nb10.bat
```

##### 3. **文档说明差异**

创建 `tools/nb10_windows/README.md`:
```markdown
# 开发环境脚本

## 脚本列表
- `nb10.bat`: 功能丰富的菜单系统 (推荐)
- `start_dev.bat`: 一键启动脚本 (开发版)

## 注意
这些脚本用于开发环境。
发布给医院的脚本由打包脚本自动生成,位于 dist/ 目录。
```

---

### 📋 策略2: **模板化脚本生成** (进阶)

如果担心两套脚本不一致,可以采用模板化:

#### 实施方案:

```bash
tools/nb10_windows/templates/
├── start_nb10.bat.template       # 通用模板
├── start_nb10_dev.bat.template   # 开发版模板
└── start_nb10_prod.bat.template  # 生产版模板
```

**在打包脚本中使用模板**:
```bash
# 在 package_release_lite_en.sh 中
cat templates/start_nb10_prod.bat.template | \
  sed "s/{{VERSION}}/${VERSION}/g" > \
  "${PACKAGE_DIR}/start_nb10.bat"
```

**优点**:
- ✅ 单一来源真相 (Single Source of Truth)
- ✅ 易于维护
- ✅ 减少重复代码

**缺点**:
- ⚠️ 增加复杂度
- ⚠️ 需要模板系统

---

### 📋 策略3: **Git忽略生成的脚本** (可选)

如果采用模板化,可以:

```bash
# .gitignore
tools/nb10_windows/start_nb10.bat  # 由模板生成,不纳入版本控制
```

**注意**: 这会导致开发者首次clone后需要运行生成脚本

---

## 推荐的最佳实践

### ✨ 综合推荐方案

#### 1. **开发环境** (您的使用场景)

```bash
# 推荐: 使用功能丰富的菜单系统
cd tools/nb10_windows
./nb10.bat              # 交互式菜单
./nb10.bat test         # 快速测试
./nb10.bat chd          # 处理CHD组

# 或者: 直接调用Python (最灵活)
source venv/bin/activate
python cli/run_nb10.py --config config/config.yaml --mode pilot
```

**优点**:
- ✅ 功能完整
- ✅ 灵活控制
- ✅ 适合开发和研究

---

#### 2. **生产环境** (医院用户)

```bash
# 用户操作: 双击运行
start_nb10.bat
```

**由打包脚本自动生成,特点**:
- ✅ 英文界面,避免编码问题
- ✅ 一键操作
- ✅ 简化流程

---

#### 3. **脚本管理**

##### 方案A: **分离管理** (当前推荐,最简单)

```
保持现状:
- 开发版: tools/nb10_windows/nb10.bat (中文,功能丰富)
- 发布版: 由打包脚本动态生成 (英文,简化)

维护工作:
- 开发版脚本: 手动维护,根据需求更新
- 发布版脚本: 在打包脚本中维护,确保稳定

文档说明:
- 在 tools/nb10_windows/README.md 中说明差异
- 在打包文档中说明生成逻辑
```

##### 方案B: **模板统一** (未来优化)

```
如果脚本变化频繁:
1. 创建模板目录
2. 开发版和发布版都从模板生成
3. 模板作为唯一真相来源

优点: 统一维护
缺点: 增加复杂度
```

---

## 快速参考

### 📌 您的日常开发调用

```bash
# ============================================
# 场景1: 快速测试 (最常用)
# ============================================
cd /home/wuxia/projects/.../tools/nb10_windows
./nb10.bat test

# ============================================
# 场景2: 处理完整数据集
# ============================================
./nb10.bat chd          # 处理CHD组
./nb10.bat normal       # 处理Normal组
./nb10.bat analyze      # 统计分析

# ============================================
# 场景3: 自定义参数运行 (最灵活)
# ============================================
source venv/bin/activate
python cli/run_nb10.py \
  --data-dir /mnt/d/CustomData \
  --mode full \
  --output-dir /mnt/d/Results

# ============================================
# 场景4: 交互式菜单
# ============================================
./nb10.bat              # 显示完整菜单

# ============================================
# 场景5: 跨平台Python调用 (推荐)
# ============================================
cd tools/nb10_windows
python -m venv venv     # 首次创建虚拟环境
source venv/bin/activate
pip install -r deployment/requirements_cpu.txt
python cli/run_nb10.py --help
```

---

### 📌 医院用户调用 (部署后)

```bash
# Windows系统上:
C:\nb10-ai-cac-lite-v1.1.0\

# 双击运行
start_nb10.bat

# 或命令行
cd C:\nb10-ai-cac-lite-v1.1.0
start_nb10.bat
```

---

## 总结

### 🎯 核心要点

1. **开发环境 ≠ 生产环境**
   - 开发环境: 功能丰富,中文友好,灵活控制
   - 生产环境: 简化操作,英文界面,一键启动

2. **不需要维护两套脚本**
   - 开发版: 手动维护在项目中
   - 发布版: 打包脚本自动生成
   - 两者目标用户和使用场景不同

3. **您的调用方式**
   ```bash
   # 推荐: 使用菜单系统
   cd tools/nb10_windows
   ./nb10.bat test

   # 或: 直接调用Python (最灵活)
   python cli/run_nb10.py --config config/config.yaml
   ```

4. **医生的调用方式**
   ```bash
   # 简单: 双击启动
   start_nb10.bat
   ```

5. **两者路径结构不同**
   - 开发: `tools/nb10_windows/` 下有 `venv/`
   - 发布: 解压根目录下有 `venv/` 和 `nb10_windows/`

---

## 下一步行动建议

### ✅ 立即可做

1. **重命名开发版脚本** (可选,更清晰)
   ```bash
   cd tools/nb10_windows
   mv start_nb10.bat start_dev.bat
   ```

2. **创建开发环境README**
   在 `tools/nb10_windows/README.md` 中说明脚本用途

3. **继续使用当前方式**
   - 开发: `nb10.bat` 或直接调用Python
   - 发布: 打包脚本生成英文版

### 📅 未来优化 (可选)

1. **模板化脚本** (如果脚本变化频繁)
2. **自动化测试** (验证开发版和发布版功能一致性)
3. **CI/CD集成** (自动生成和测试发布包)

---

**文档版本**: v1.0
**更新日期**: 2025-10-16
**适用项目**: NB10 AI-CAC Windows应用
