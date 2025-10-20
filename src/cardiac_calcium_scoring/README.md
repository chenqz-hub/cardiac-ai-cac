# NB10 Windows Local Tool - AI-CAC Coronary Calcium Scoring

**Version**: 1.1.0
**Last Updated**: 2025-10-17
**Status**: ✅ Production Ready - Offline Installation Supported

---

## 🎯 核心特性：完全独立的AI-CAC评分工具

### ✅ NB10的独立性声明

**NB10可以完全独立运行，无需任何前置步骤！**

- ✅ **输入**: 仅需DICOM文件
- ✅ **输出**: AI-CAC冠状动脉钙化评分
- ✅ **依赖**: 无需NB08、NB09或其他Notebook
- ✅ **成功率**: 99.5% (196/197例)
- ✅ **处理速度**: ~15秒/患者 (RTX 2060 6GB)

**这意味着**：
- 医生可以直接使用本工具进行钙化评分，无需了解其他复杂的数据处理流程
- 适合日常临床工作中的快速评估和诊断
- 不需要学习TotalSegmentator、L1椎体定位等复杂技术

**何时需要其他Notebook？**
- 仅当您需要进行**多模态特征整合研究**（整合脂肪特征、主动脉结构等）时
- 详见下方"[使用场景区分](#-重要说明单独nb10-vs-多模态分析)"

---

## ✅ Phase 4 验证完成！

**所有阶段已完成** (Phase 1-4)，验证通过**199例完整DICOM数据集** (CHD: 101例, Normal: 96例)

### 验证结果摘要
- **Pilot模式**: 60/60例 与Colab 100%一致 ✅
- **Full模式**: 189/194例 完全一致 (97.4%) ✅
- **性能**: 平均 ~15秒/患者 (RTX 2060 6GB)
- **成功率**: 99.5% (196/197例)

### v1.1.0 (Current) ✅
- ✅ 离线安装支持（嵌套目录结构）
- ✅ 用户界面全英文（无编码问题）
- ✅ 单个病例处理时间提示
- ✅ 改进的进度显示和时间估算
- ✅ 移除双重暂停问题

### v1.2.0 规划
- ⏳ 硬件自适应优化系统（预期性能提升20-40%）
- ⏳ 授权管理系统（GitHub-based）
- ⏳ 医院部署优化和批量处理增强

---

## 项目概述

NB10 Windows本地工具提供AI-CAC（人工智能冠状动脉钙化评分）系统的Windows本地版本。

**核心功能**：
- ✅ AI-CAC深度学习模型推理（CPU/GPU）
- ✅ DICOM数据批量处理
- ✅ 统计分析和风险分层
- ✅ 结果可视化和报告生成
- ✅ 断点续传和缓存管理
- ✅ 患者年龄性别信息提取和分析
- 🔧 可选: 多模态特征整合分析 (需要额外的NB08+NB09处理)

**研究人群特征**（Premature CAD）：
本工具当前用于**早发冠心病（Premature CAD）**研究：
- **年龄标准**：男性 <55岁，女性 <65岁
- **CHD组**：经造影确诊冠心病，已行支架植入
- **Normal组**：经造影检查，未发现异常

**目标用户**：
- 医学研究人员（临床数据分析）
- 临床医生（辅助诊断工具）
- 医疗机构（批量数据处理）

---

## ⚠️ 重要说明：单独NB10 vs 多模态分析

### 📋 使用场景选择指南

| 对比项 | 场景A: 单独NB10 (推荐) | 场景B: 多模态分析 (高级) |
|--------|----------------------|----------------------|
| **适用人群** | 临床医生、日常诊断 | 科研人员、论文数据 |
| **前置要求** | ✅ 无 - 完全独立 | ⚠️ 需要NB08+NB09 |
| **处理时间** | ~15秒/患者 | ~10-20分钟/患者 |
| **成功率** | 99.5% (196/197) | ~50% (完整链) |
| **技术难度** | 🟢 低 - 一键运行 | 🔴 高 - 需要多个工具 |
| **部署难度** | 🟢 简单 - 500MB模型 | 🔴 复杂 - 5GB+多个依赖 |
| **维护成本** | 🟢 低 | 🔴 高 |

---

### 场景A: 单独NB10分析（临床日常使用）✅ 推荐

#### ✅ 完全独立运行

**NB10是一个完全独立的AI-CAC评分工具**：
- ✅ 仅需DICOM文件输入
- ✅ 无需任何前置Notebook（NB08/NB09）
- ✅ 无需L1椎体定位、脂肪提取等复杂处理
- ✅ 99.5%高成功率，快速可靠

**适用场景**：
- 日常门诊快速钙化评分
- 单个患者的心血管风险评估
- CHD vs Normal组的钙化对比研究
- 临床科研中仅需钙化指标的研究

**运行方式**：
```bash
nb10 chd      # 处理CHD组
nb10 normal   # 处理Normal组
nb10 analyze  # 统计分析
```

**输出结果**：
- AI-CAC Agatston评分
- 钙化体积和质量
- 风险分层
- CHD vs Normal统计对比

**处理性能**：
- 时间: ~15秒/患者 (RTX 2060 6GB)
- 成功率: 99.5% (196/197例)
- 磁盘空间: ~500MB

**前置要求**: ✅ **无** - 完全独立运行

---

### 场景B: 多模态特征整合分析（科研高级功能）⭐

#### ⚠️ 需要额外的数据处理流程

**这是一个可选的高级功能**，用于：
- 多模态特征整合研究（论文发表）
- AI-CAC + 主动脉旁脂肪 + 主动脉结构的综合分析
- 倾向性评分匹配(PSM)统计研究

**分析内容**：
- **模态1**: AI-CAC冠状动脉钙化 (来自NB10)
- **模态2**: 主动脉周围脂肪 (来自NB09)
- **模态3**: 主动脉结构特征 (来自NB09)
- **协变量**: 患者临床数据 (性别/年龄/代谢指标等)
- **统计方法**: 倾向性评分匹配(PSM) + 多变量分析

**运行方式**：
```bash
# Step 1: 先完成NB08和NB09 (需要单独安装和运行)
# Step 2: 运行NB10获取AI-CAC数据
nb10 chd
nb10 normal

# Step 3: 运行多模态整合分析
python integrate_multimodal_data.py
```

**前置要求**: ⚠️ **必须先完成以下步骤**

| 前置任务 | 功能 | 处理时间 | 成功率 | 复杂度 |
|---------|------|---------|--------|--------|
| **NB08** | L1椎体定位 (TotalSegmentator) | ~5分钟/例 | 100% | 🔴 高 |
| **NB09** | 主动脉旁脂肪提取 | ~5分钟/例 | 51% | 🔴 高 |
| **NB10** | AI-CAC冠脉钙化 | ~15秒/例 | 99.5% | 🟢 低 |
| **临床数据** | 患者基本信息 | - | - | 🟢 低 |

**数据依赖链**：
```
多模态分析结果
  ↑
  ├── NB10 (AI-CAC) ✅ 本工具提供 - 独立运行
  ├── NB09 (主动脉旁脂肪) ⚠️ 需要单独安装和运行
  │   ↑
  │   └── NB08 (L1椎体定位) ⚠️ 需要单独安装和运行
  └── 临床数据 (性别/年龄等) ✅ 医院提供
```

**处理性能**：
- 完整流程时间: ~10-20分钟/患者
- 完整链成功率: ~50% (由于NB09成功率较低)
- 磁盘空间: ~5GB+ (TotalSegmentator等模型)
- GPU内存: 建议16GB+

**输出结果**：
- PSM匹配后的队列 (195例成功合并)
- 11个多模态生物标志物统计结果
- 森林图、相关性热图、倾向性评分图
- 完整分析报告 (`output/multimodal_analysis/COMPREHENSIVE_SUMMARY.md`)

**详细文档**：
- [多模态分析完整总结](output/multimodal_analysis/COMPREHENSIVE_SUMMARY.md)
- [数据版本追踪说明](docs/DATA_VERSION_TRACKING.md)
- [使用场景详细指南](docs/USAGE_SCENARIOS.md)

---

### 🎯 如何选择使用场景？

#### ✅ 选择场景A（单独NB10）如果您：
- 只需要AI-CAC钙化评分
- 需要快速、可靠的结果
- 在临床门诊环境使用
- 不熟悉深度学习和复杂数据处理
- 希望部署和维护简单

#### ⭐ 选择场景B（多模态分析）如果您：
- 需要发表多模态特征整合论文
- 研究需要脂肪特征和主动脉结构数据
- 有技术团队支持（会使用TotalSegmentator等工具）
- 有充足的时间和计算资源
- 能接受较低的成功率（~50%完整链）

---

### 💡 推荐策略：渐进式使用

**第一阶段：先用场景A验证工具**
```bash
# 1. 用少量数据测试NB10
nb10 test   # 测试5例

# 2. 如果成功，处理完整数据集
nb10 chd
nb10 normal
nb10 analyze
```

**第二阶段：评估是否需要多模态**
- 如果钙化评分已满足研究需求 → 完成 ✅
- 如果需要更多生物标志物 → 考虑场景B

**第三阶段：可选的多模态扩展**
- 联系技术团队安装NB08/NB09
- 单独运行脂肪提取流程
- 使用`integrate_multimodal_data.py`整合结果

---

### ⚠️ 关键警告

**请勿为了功能完整性牺牲可靠性**：
- NB10单独运行成功率: **99.5%**
- 完整多模态链成功率: **~50%**
- 临床工具最重要的是**可靠和快速**

**多模态功能主要用于科研**：
- 适合批量数据处理和论文数据生成
- 不适合实时临床决策
- 需要专门的技术支持团队

**不确定？**
- 联系研究团队讨论您的具体需求
- 可以先用场景A验证，再决定是否需要场景B

---

## 快速开始

### 1. 环境要求

**硬件**：
- CPU：Intel i5或以上（推荐i7/i9）
- 内存：16GB以上（推荐32GB）
- 硬盘：100GB可用空间
- GPU：可选（NVIDIA GPU可加速47倍）

**软件**：
- 操作系统：Windows 10/11 (64-bit)
- Python：3.10（必须，不支持3.12）
- CUDA：12.x（仅GPU版本需要）

### 2. 安装步骤

详见：[docs/INSTALLATION_GUIDE.md](docs/INSTALLATION_GUIDE.md)

**快速安装**（有网络环境）：
```bash
# 1. 创建虚拟环境
python -m venv venv
venv\Scripts\activate

# 2. 安装依赖
pip install -r deployment/requirements_cpu.txt

# 3. 下载模型
python deployment/download_models.py

# 4. 验证安装
python scripts/validate_installation.py
```

**离线安装**（无网络环境）：
详见：[deployment/offline_wheels/README.md](deployment/offline_wheels/README.md)

### 3. 配置

```bash
# 首次运行创建配置文件
python cli/run_nb10.py --init

# 编辑配置文件
notepad config/config.yaml
```

### 4. 运行

The Cardiac Calcium Scoring System now provides **three ways** to run the application:

#### 🎯 方式1: Bash菜单（Linux/WSL推荐）⭐

**交互式菜单**:
```bash
bash calcium_scoring.sh
```

**快捷命令**（命令行直接使用）:
```bash
bash calcium_scoring.sh test      # 快速测试（5例）
bash calcium_scoring.sh chd       # 处理CHD组
bash calcium_scoring.sh normal    # 处理Normal组
bash calcium_scoring.sh analyze   # 统计分析
bash calcium_scoring.sh config    # 查看配置
bash calcium_scoring.sh logs      # 查看日志
bash calcium_scoring.sh help      # 显示帮助
```

**特性**:
- ✅ 原生Linux/WSL支持
- ✅ 自动日志记录（logs/menu/）
- ✅ 虚拟环境自动检测
- ✅ 完整错误追踪

详细说明: [MENU_GUIDE.md](MENU_GUIDE.md) 📖

---

#### 🐍 方式2: Python菜单（跨平台）

**交互式菜单**（支持Windows/Linux/macOS）:
```bash
../../venv/bin/python menu.py
```

**特性**:
- ✅ 彩色交互式界面
- ✅ 配置文件编辑功能
- ✅ 硬件状态监控
- ✅ 查看处理结果CSV
- ✅ 查看用户手册
- ✅ 跨平台兼容

**功能菜单**:
```
【快速处理】
  1. 快速测试 (Pilot模式 - 处理5例)
  2. 处理CHD组 (完整模式)
  3. 处理Normal组 (完整模式)
  4. 自定义数据目录处理

【统计分析】
  5. CHD vs Normal组对比分析
  6. 查看最新处理结果

【配置管理】
  7. 编辑CHD组配置文件
  8. 编辑Normal组配置文件
  9. 查看系统配置

【工具与帮助】
  A. 查看用户手册
  B. 查看快速参考卡
  C. 检查硬件配置
  D. 查看日志文件
```

详细说明: [MENU_GUIDE.md](MENU_GUIDE.md) 📖

---

#### 💻 方式3: 直接命令行（开发者/高级用户）

**直接运行CLI**（无菜单）:
```bash
# 快速1例测试
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 1

# Pilot模式（测试10例）
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode pilot --pilot-limit 10

# Full模式（全部数据）
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode full

# 指定数据目录（灵活切换数据集）
../../venv/bin/python cli/run_calcium_scoring.py --mode full --data-dir /path/to/your/data

# 对照研究示例（CHD vs Normal）
echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config.yaml --mode full

echo "" | ../../venv/bin/python cli/run_calcium_scoring.py --config config/config_normal.yaml --mode full

# 查看所有选项
../../venv/bin/python cli/run_calcium_scoring.py --help
```

**重要参数**:
- `--mode {pilot,full}` - 处理模式
- `--pilot-limit N` - Pilot模式处理例数
- `--device {cuda,cpu}` - 强制使用GPU或CPU
- `--data-dir PATH` - 自定义数据目录
- `--clear-cache` - 清除缓存重新处理
- `--no-resume` - 禁用断点续传

详细说明: [HOW_TO_RUN.md](HOW_TO_RUN.md) 📖

> **💡 医生使用提示**:
> - **初学者**: 使用Bash菜单或Python菜单（方式1或2）
> - **日常使用**: 使用快捷命令如 `bash calcium_scoring.sh test`
> - **高级用户**: 使用直接命令行（方式3）进行灵活控制

---

## 项目结构

```
nb10_windows/
├── core/               # 核心代码（与Colab共享）
├── cli/                # 命令行工具
├── config/             # 配置文件模板
├── tests/              # 测试代码
├── deployment/         # 部署和打包
├── docs/               # 文档
├── examples/           # 示例和模板
├── scripts/            # 辅助脚本
├── data/               # 数据目录（用户放置DICOM数据）
├── models/             # 模型目录（AI-CAC模型）
├── output/             # 输出目录（结果CSV/图表）
└── logs/               # 日志目录
```

---

## 主要文档

### 快速入门（必读）⭐
| 文档 | 说明 | 推荐度 |
|------|------|--------|
| [HOW_TO_RUN.md](HOW_TO_RUN.md) | **如何运行应用** - 当前系统状态、3种运行方法、结果查看 | ⭐⭐⭐ |
| [MENU_GUIDE.md](MENU_GUIDE.md) | **菜单系统完整指南** - 两种菜单对比、10个常见用例、扩展指南 | ⭐⭐⭐ |
| [VSCODE_QUICK_START.md](VSCODE_QUICK_START.md) | **VS Code Terminal快速入门** - 开发环境使用指南 | ⭐⭐ |

### 用户文档
| 文档 | 说明 |
|------|------|
| [USER_MANUAL.md](docs/USER_MANUAL.md) | 完整用户手册 |
| [INSTALLATION_GUIDE.md](docs/INSTALLATION_GUIDE.md) | 详细安装步骤 |
| [VSCODE_TERMINAL_GUIDE.md](docs/VSCODE_TERMINAL_GUIDE.md) | VS Code Terminal详细指南 |

### 研究文档
| 文档 | 说明 |
|------|------|
| [RESEARCH_RATIONALE.md](docs/RESEARCH_RATIONALE.md) | 研究思路与未来方向 |
| [STUDY_POPULATION.md](docs/STUDY_POPULATION.md) | 研究人群说明（早发CAD） |
| [USAGE_SCENARIOS.md](docs/USAGE_SCENARIOS.md) | 使用场景详细指南 |

---

## 性能预期

**基于Colab T4 GPU实测**：
- GPU模式：约30秒/例
- CPU模式：约15-20分钟/例（估算）

**本地机器预期**：
- RTX 2060 (6GB)：30-60秒/例
- 无GPU（CPU）：10-20分钟/例

**优化建议**：
- GPU版本：推荐用于批量处理
- CPU版本：适合小批量处理或单例诊断

---

---

## 开发状态

### v1.0.0 (当前) ✅
- ✅ 目录结构创建
- ✅ 核心代码迁移和适配
- ✅ 依赖管理方案（在线/离线）
- ✅ 命令行工具开发
- ✅ 测试和验证（Phase 1-4完成）
- ✅ GPU性能测试通过（RTX 2060, ~15秒/患者）
- ✅ 平台兼容性验证（97.4%一致性）
- ✅ 用户文档完善

### v1.1.0 (规划中) - 医院部署优化
- ⏳ 硬件自适应优化系统（预期性能提升20-40%）
- ⏳ 授权管理系统（GitHub-based）
- ⏳ UI集成和设置页面
- ⏳ 智能缓存和OOM保护
- ⏳ 多GPU支持（Enterprise级别）

### v1.2.0 (未来)
- 结果对比和可视化增强
- 多模态分析整合（NB09/NB12）
- 批量处理优化
- 云端结果同步

---

## 技术支持

**问题反馈**：
- GitHub Issues: [cardiac-ml-research/issues](https://github.com/zhurong2020/cardiac-ml-research/issues)
- Email: [添加联系邮箱]

**开发团队**：
- 核心开发：Claude Code + 陈医生团队
- AI模型：U.S. Department of Veterans Affairs (AI-CAC)

---

## 许可证

本工具基于：
- 项目代码：MIT License
- AI-CAC模型：MIT License (U.S. Department of Veterans Affairs)

详见：[LICENSE](../../LICENSE)

---

**最后更新**: 2025-10-14
**维护者**: 陈医生团队
