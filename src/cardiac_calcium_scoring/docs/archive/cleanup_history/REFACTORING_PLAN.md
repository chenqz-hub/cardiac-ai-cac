# NB10 Windows 重构计划

**创建日期**: 2025-10-18
**当前版本**: v1.1.4
**目标版本**: v2.0.0
**状态**: 规划中

---

## 📋 执行摘要

基于当前代码和文档审查，nb10_windows应用已完成v1.1.4版本发布，解决了关键bug。现在是进行系统性重构的最佳时机，目标是提升性能、可维护性和用户体验。

### 当前状态
- ✅ **核心功能稳定**: AI-CAC评分功能工作正常，成功率99.5%
- ✅ **关键bug已修复**: v1.1.4解决了DataLoader hanging和PyDicom API更新问题
- ⚠️ **文档分散**: 根目录有多个版本相关的临时文档
- ⚠️ **架构待优化**: 存在硬编码配置，缺少硬件自适应系统
- ⚠️ **缺少授权管理**: 无商业化部署的授权控制机制

### 重构优先级
1. **高优先级**: 文档整理和归档 (立即执行)
2. **中优先级**: 硬件自适应优化系统 (性能提升20-40%)
3. **中优先级**: 授权管理系统 (医院部署必需)
4. **低优先级**: UI增强和多GPU支持

---

## 🗂️ Phase 1: 文档整理和归档 (立即执行)

### 问题分析

当前根目录存在大量临时性文档：
```
tools/nb10_windows/
├── CHANGELOG_v1.1.4.md              # 版本特定文档
├── TEST_REPORT_v1.1.4.md            # 版本特定文档
├── FINAL_TEST_REPORT_v1.1.4.md      # 版本特定文档
├── RELEASE_v1.1.4_SUMMARY.md        # 版本特定文档
├── DEPLOYMENT_SUMMARY_v1.1.3-rc2.md # 旧版本文档
├── TEST_REPORT_v1.1.3-rc2.md        # 旧版本文档
├── CPU_TEST_REPORT_FINAL.md         # 测试报告
├── CHANGELOG.md                     # 主更新日志 ✅
└── README.md                        # 主文档 ✅
```

### 整理方案

#### 1.1 归档版本特定文档
将所有版本特定的文档移至归档目录：

```bash
# 创建版本归档目录
mkdir -p docs/archive/releases/v1.1.4
mkdir -p docs/archive/releases/v1.1.3

# 移动v1.1.4相关文档
mv CHANGELOG_v1.1.4.md docs/archive/releases/v1.1.4/
mv TEST_REPORT_v1.1.4.md docs/archive/releases/v1.1.4/
mv FINAL_TEST_REPORT_v1.1.4.md docs/archive/releases/v1.1.4/
mv RELEASE_v1.1.4_SUMMARY.md docs/archive/releases/v1.1.4/

# 移动v1.1.3相关文档
mv DEPLOYMENT_SUMMARY_v1.1.3-rc2.md docs/archive/releases/v1.1.3/
mv TEST_REPORT_v1.1.3-rc2.md docs/archive/releases/v1.1.3/

# 移动测试报告
mkdir -p docs/archive/testing
mv CPU_TEST_REPORT_FINAL.md docs/archive/testing/
```

#### 1.2 更新CHANGELOG.md
确保主CHANGELOG包含所有版本信息，并在v1.1.4条目中添加归档文档的引用：

```markdown
## [1.1.4] - 2025-10-17

详细文档参见：
- [完整变更日志](docs/archive/releases/v1.1.4/CHANGELOG_v1.1.4.md)
- [测试报告](docs/archive/releases/v1.1.4/TEST_REPORT_v1.1.4.md)
- [发布总结](docs/archive/releases/v1.1.4/RELEASE_v1.1.4_SUMMARY.md)
```

#### 1.3 创建文档索引
在`docs/`目录创建`DOCUMENT_INDEX.md`：

```markdown
# NB10 文档索引

## 核心文档
- [README.md](../README.md) - 项目概览
- [CHANGELOG.md](../CHANGELOG.md) - 版本历史
- [USER_MANUAL.md](USER_MANUAL.md) - 用户手册
- [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) - 安装指南

## 归档文档
- [发布版本归档](archive/releases/) - 历史版本详细文档
- [开发阶段归档](archive/development/) - Phase 1-4开发文档
- [实施文档归档](archive/implementation/) - 实施过程文档
- [规划文档归档](archive/planning/) - 未来规划文档
```

#### 1.4 清理过期文档
审查并删除或归档以下类别的文档：
- 已过时的临时笔记
- 重复的文档
- 已整合到主文档中的内容

---

## 🚀 Phase 2: 硬件自适应优化系统 (v2.0.0核心功能)

### 目标
实现自动硬件检测和性能优化，预期性能提升20-40%。

### 参考文档
- [HARDWARE_ADAPTIVE_OPTIMIZATION_DESIGN.md](docs/archive/planning/HARDWARE_ADAPTIVE_OPTIMIZATION_DESIGN.md)
- [HARDWARE_OPTIMIZATION_IMPLEMENTATION_PLAN.md](docs/archive/planning/HARDWARE_OPTIMIZATION_IMPLEMENTATION_PLAN.md)

### 实施计划

#### 2.1 硬件检测模块 (Week 1-2)
**文件**: `core/hardware_profiler.py` (已存在于dist中，需要整合到主代码)

**任务**:
1. 完善GPU检测
   - VRAM容量和可用性
   - CUDA版本
   - 计算能力
   - 温度监控支持

2. CPU/RAM检测
   - 物理核心数
   - 逻辑核心数
   - 系统内存
   - 磁盘类型(SSD/HDD)

3. 硬件分级
   ```python
   class HardwareTier(Enum):
       MINIMAL = 1      # ≤4GB GPU or CPU-only
       STANDARD = 2     # 6GB GPU (RTX 2060)
       PERFORMANCE = 3  # 8-12GB GPU
       PROFESSIONAL = 4 # 16-24GB GPU
       ENTERPRISE = 5   # Multi-GPU
   ```

#### 2.2 性能配置引擎 (Week 2-3)
**文件**: `core/performance_profiles.py` (已存在于dist中)

**任务**:
1. 为每个硬件等级定义配置profile
2. 动态调整DataLoader参数
3. GPU缓存清理策略
4. 批处理大小优化

**示例配置**:
```python
PROFILES = {
    'STANDARD': {
        'num_workers': 2,
        'pin_memory': True,
        'slice_batch_size': 4,
        'clear_cache_interval': 1,
        'expected_time_per_patient': 28
    },
    'PERFORMANCE': {
        'num_workers': 4,
        'pin_memory': True,
        'slice_batch_size': 6,
        'clear_cache_interval': 3,
        'expected_time_per_patient': 20
    }
}
```

#### 2.3 集成到推理流程 (Week 3-4)
**修改文件**:
- `core/ai_cac_inference_lib.py` - 应用动态配置
- `cli/run_nb10.py` - 启动时硬件检测和用户选择

**关键修改**:
```python
# ai_cac_inference_lib.py Line 249-255
# 当前: num_workers = 0 (硬编码)
# 修改为:
from core.performance_profiles import get_active_profile
profile = get_active_profile()

dataloader = DataLoader(
    dataset,
    batch_size=1,
    shuffle=False,
    num_workers=profile.num_workers,    # 动态
    pin_memory=profile.pin_memory,      # 动态
    prefetch_factor=profile.prefetch_factor if profile.num_workers > 0 else None
)
```

#### 2.4 安全监控系统 (Week 4-5)
**新文件**: `core/safety_monitor.py` (已存在于dist中)

**功能**:
1. OOM保护
2. GPU温度监控
3. 性能跟踪
4. 自动降级机制

---

## 🔐 Phase 3: 授权管理系统 (医院部署必需)

### 目标
实现授权管理，支持试用版、研究版和商业版分发。

### 参考文档
- [LICENSE_MANAGEMENT_SYSTEM_DESIGN.md](docs/archive/planning/LICENSE_MANAGEMENT_SYSTEM_DESIGN.md)
- [HOSPITAL_DEPLOYMENT_ROADMAP.md](docs/archive/planning/HOSPITAL_DEPLOYMENT_ROADMAP.md)

### 实施计划

#### 3.1 授权架构 (Week 1)
**基于GitHub私有仓库的轻量级方案**:

```
授权验证流程:
1. 本地授权文件 (~/.nb10/license.json)
2. 在线验证 (GitHub私有仓库API)
3. 离线缓存 (24小时有效期)
```

**授权类型**:
```python
class LicenseType(Enum):
    TRIAL = "trial"           # 100例限制，30天有效
    RESEARCH = "research"     # 无例数限制，需要伦理审批
    COMMERCIAL = "commercial" # 无限制，商业授权
```

#### 3.2 实现步骤
1. 创建GitHub私有仓库 `nb10-licenses`
2. 实现授权生成器 `utils/license_generator.py`
3. 实现本地验证器 `core/license_validator.py`
4. 集成到CLI `cli/run_nb10.py`

---

## 🎨 Phase 4: 用户体验增强 (可选)

### 4.1 统一配置管理
当前配置分散，需要整合：
- `config/config.yaml` - 主配置
- `~/.nb10/hardware_config.json` - 硬件配置
- `~/.nb10/license.json` - 授权信息

### 4.2 进度显示优化
- 实时进度条 (使用tqdm)
- 预计剩余时间
- 当前患者处理状态

### 4.3 结果可视化
- 钙化评分分布图
- 风险分层饼图
- 处理时间趋势

---

## 📊 重构时间表

### 方案A: 快速整理 (1周)
**目标**: 仅整理文档，不改动代码

| 阶段 | 任务 | 耗时 |
|------|------|------|
| Phase 1 | 文档归档整理 | 2天 |
| 文档审查 | 更新索引和链接 | 1天 |
| 测试验证 | 确保所有链接有效 | 1天 |

**交付物**:
- ✅ 清理后的根目录 (仅保留README.md和CHANGELOG.md)
- ✅ 完整的文档归档结构
- ✅ 文档索引和导航

---

### 方案B: 性能优化重构 (6周)
**目标**: 文档整理 + 硬件自适应系统

| 阶段 | 任务 | 耗时 |
|------|------|------|
| Phase 1 | 文档归档整理 | 1周 |
| Phase 2.1 | 硬件检测模块 | 2周 |
| Phase 2.2 | 性能配置引擎 | 1周 |
| Phase 2.3 | 集成测试 | 1周 |
| Phase 2.4 | 文档更新 | 1周 |

**预期收益**:
- 📈 性能提升: 20-40%
- 📈 用户体验: 自动优化，零配置
- 📈 硬件适配: 支持从4GB到24GB GPU

---

### 方案C: 完整商业化重构 (10周)
**目标**: 文档 + 性能优化 + 授权管理

| 阶段 | 任务 | 耗时 |
|------|------|------|
| Phase 1 | 文档归档整理 | 1周 |
| Phase 2 | 硬件自适应系统 | 4周 |
| Phase 3 | 授权管理系统 | 3周 |
| Phase 4 | 用户体验增强 | 2周 |

**交付物**:
- ✅ v2.0.0完整版本
- ✅ 医院可部署的商业版
- ✅ 完整的用户和IT文档

---

## 🎯 推荐方案

### 立即执行: 方案A (文档整理)
**理由**:
1. **低风险**: 不涉及代码改动
2. **快速见效**: 1周完成
3. **改善可维护性**: 清晰的文档结构
4. **为后续重构铺路**: 理清技术债务

**执行步骤**:
```bash
# 1. 创建归档目录结构
mkdir -p docs/archive/releases/{v1.1.3,v1.1.4}
mkdir -p docs/archive/testing

# 2. 移动版本特定文档
# (见Phase 1详细命令)

# 3. 创建文档索引
# (见Phase 1模板)

# 4. 更新主README
# 添加文档导航链接

# 5. Git提交
git add .
git commit -m "docs: reorganize documentation structure"
```

### 中期计划: 方案B (性能优化)
**时机**: 完成文档整理后
**前提**:
- 有清晰的硬件测试环境 (RTX 2060, RTX 3060等)
- 有充足的测试数据集

### 长期目标: 方案C (商业化)
**时机**: 确定医院部署需求后
**前提**:
- 明确商业化路线
- 有授权管理需求

---

## ✅ 下一步行动

### 立即执行 (今天)
1. ✅ 创建本重构计划文档
2. ⏭️ 执行Phase 1文档整理
3. ⏭️ 提交清理后的代码库

### 本周内
1. 完成文档归档
2. 更新主README和CHANGELOG
3. 创建文档索引

### 评审时机
- 文档整理完成后，评审是否继续Phase 2
- 如有医院部署计划，优先考虑Phase 3授权系统

---

## 📝 参考文档

### 已有规划文档
- [硬件自适应优化设计](docs/archive/planning/HARDWARE_ADAPTIVE_OPTIMIZATION_DESIGN.md)
- [医院部署路线图](docs/archive/planning/HOSPITAL_DEPLOYMENT_ROADMAP.md)
- [授权管理系统设计](docs/archive/planning/LICENSE_MANAGEMENT_SYSTEM_DESIGN.md)

### 开发文档
- [Phase 1-4开发报告](docs/archive/development/)
- [实施文档](docs/archive/implementation/)

### 用户文档
- [用户手册](docs/USER_MANUAL.md)
- [安装指南](docs/INSTALLATION_GUIDE.md)
- [离线分发指南](docs/OFFLINE_DISTRIBUTION_GUIDE.md)

---

**创建者**: Claude Code
**最后更新**: 2025-10-18
**状态**: 等待审核和执行
