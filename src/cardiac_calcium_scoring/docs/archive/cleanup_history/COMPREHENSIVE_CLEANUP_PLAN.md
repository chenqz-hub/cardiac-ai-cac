# NB10 Windows 全面清理计划

**创建日期**: 2025-10-18
**清理范围**: 全项目深度清理
**目标**: 删除过期文件、整理冗余内容、优化项目结构

---

## 📊 清理范围分析

### 1. config/ 目录 - **12个配置文件**

**问题**: 存在大量测试用的临时配置文件

#### 保留文件 (3个)
- ✅ `config.yaml` - 主配置文件
- ✅ `config.yaml.template` - 配置模板
- ✅ `config_normal.yaml` - 正常数据集配置 (可选保留)

#### 需要清理的测试配置 (9个)
- ❌ `config_cpu_test_baseline_1case.yaml` - CPU测试基线 (1例)
- ❌ `config_cpu_test_baseline_3cases.yaml` - CPU测试基线 (3例)
- ❌ `config_cpu_test_optimized_1case.yaml` - CPU测试优化 (1例)
- ❌ `config_cpu_test_optimized_3cases.yaml` - CPU测试优化 (3例)
- ❌ `config_gpu_validation_3cases.yaml` - GPU验证 (3例)
- ❌ `config_gpu_validation_5cases.yaml` - GPU验证 (5例)
- ❌ `config_test_baseline.yaml` - 测试基线
- ❌ `config_test_optimized.yaml` - 测试优化
- ❌ `paths_windows.yaml` - Windows路径 (过时)

**清理动作**: 移动到 `config/archive/testing/`

---

### 2. logs/ 目录 - **40个日志文件**

**问题**: 大量测试和开发期间的日志文件

#### 保留文件
- ✅ `README.md` - 日志目录说明
- ✅ `.gitkeep` - Git占位文件
- ✅ `menu/` - 菜单系统日志目录

#### 需要归档的日志 (40个)
所有 `nb10_20251014_*.log` 到 `nb10_20251017_*.log` 文件

**日志统计**:
- 10月14日: 19个日志文件
- 10月15日: 6个日志文件
- 10月16日: 1个日志文件
- 10月17日: 14个日志文件

**清理动作**:
- 移动到 `logs/archive/development/` 按日期分类
- 或者直接删除 (建议保留最近3天，其余删除)

---

### 3. output/ 目录 - **40+个输出文件**

**问题**: 大量测试运行的临时输出CSV和日志

#### 保留文件
- ✅ `README.md` - 输出目录说明
- ✅ `.gitkeep` - Git占位文件
- ✅ `chd_results.csv` - CHD组结果 (如果是最终版本)
- ✅ `normal_results.csv` - Normal组结果 (如果是最终版本)
- ✅ `nb10_results_complete.csv` - 完整结果 (最新)
- ✅ `multimodal_analysis/` - 多模态分析结果 (重要)

#### 需要清理的文件
**临时测试CSV (30+个)**:
- ❌ `nb10_results_20251014_*.csv` (约19个)
- ❌ `nb10_results_20251015_*.csv` (约6个)
- ❌ `nb10_results_20251017_*.csv` (2个)

**临时测试目录**:
- ❌ `cpu_performance_tests/` - CPU性能测试结果
- ❌ `gpu_validation/` - GPU验证结果

**其他临时文件**:
- ❌ `baseline_quick.txt` - 基线快速测试
- ❌ `gpu_validation_run1.log` - GPU验证日志
- ❌ `test_suite_report_20251017_212422.json` - 测试套件报告

**清理动作**:
- 移动到 `output/archive/testing/`
- 或者直接删除临时测试文件

---

### 4. 根目录临时文件

#### 需要清理的文件
- ❌ `DEPLOY_v1.1.4.txt` - 部署临时记录，应移至 `docs/archive/releases/v1.1.4/`

---

### 5. docs/ 目录文档审查

**当前状态**: 13个文档文件 + archive目录

#### 可能需要合并的文档
检查是否有内容重复或可以合并的文档：

**安装和部署类** (3个):
- `INSTALLATION_GUIDE.md`
- `OFFLINE_DISTRIBUTION_GUIDE.md`
- `DEPLOYMENT_TEST_GUIDE.md`
评估: ✅ 内容不重复，各有侧重

**使用指南类** (4个):
- `USER_MANUAL.md` - 完整用户手册
- `ONE_CLICK_STARTUP_GUIDE.md` - 快速开始
- `USAGE_SCENARIOS.md` - 使用场景
- `SCRIPT_MANAGEMENT_GUIDE.md` - 脚本管理
评估: ✅ 各有侧重，保留

**平台特定类** (3个):
- `README_LINUX.md`
- `WINDOWS_ACCESS_GUIDE.md`
- `VSCODE_TERMINAL_GUIDE.md`
评估: ✅ 各有侧重，保留

**其他**:
- `DATA_VERSION_TRACKING.md` - 数据版本追踪
- `DOCUMENT_INDEX.md` - 文档索引

**结论**: docs/目录文档合理，无需合并

---

### 6. dist/ 目录 - 发布包

**当前状态**: 包含v1.1.3-rc2和v1.1.4两个发布包

#### 评估
- ✅ `nb10-ai-cac-lite-v1.1.4/` - 最新版本，保留
- ⚠️ `nb10-ai-cac-lite-v1.1.3-rc2/` - 旧版本RC

**清理建议**:
- 如果v1.1.4已确认稳定，可以删除v1.1.3-rc2
- 或者保留作为历史参考

---

## 🎯 清理策略

### 策略A: 保守清理 (推荐)
**原则**: 归档为主，删除为辅

1. **config/**: 移动测试配置到 `config/archive/testing/`
2. **logs/**: 移动旧日志到 `logs/archive/development/`
3. **output/**: 移动测试结果到 `output/archive/testing/`
4. **根目录**: 移动DEPLOY文件到归档
5. **dist/**: 保留两个版本

**优点**: 安全，可追溯
**缺点**: 仍占用一些空间

---

### 策略B: 激进清理
**原则**: 删除明确无用的测试文件

1. **config/**: 删除所有测试配置
2. **logs/**: 删除10月14-16日的日志，仅保留最近3天
3. **output/**: 删除所有测试CSV，仅保留最终结果
4. **根目录**: 移动DEPLOY文件到归档
5. **dist/**: 删除v1.1.3-rc2

**优点**: 项目更清爽，节省空间
**缺点**: 丢失历史测试数据

---

### 策略C: 混合策略 (推荐) ⭐
**原则**: 重要的归档，明确无用的删除

#### config/ - 归档
移动到 `config/archive/testing/`

#### logs/ - 删除
- 删除10月14-15日的日志 (25个文件)
- 保留10月16-17日的日志 (15个文件)
- 保留menu/子目录

#### output/ - 混合处理
**保留**:
- 最终结果CSV (chd_results.csv, normal_results.csv, nb10_results_complete.csv)
- multimodal_analysis/ 目录

**删除**:
- 所有时间戳的临时CSV (30+个)
- cpu_performance_tests/ 目录
- gpu_validation/ 目录
- 临时txt和log文件

#### 根目录 - 移动
- DEPLOY_v1.1.4.txt → docs/archive/releases/v1.1.4/

#### dist/ - 保留
保留两个版本作为历史参考

---

## 📋 执行清单 (策略C)

### Phase 1: 配置文件归档
```bash
mkdir -p config/archive/testing
git mv config/config_*test*.yaml config/archive/testing/
git mv config/config_gpu_validation*.yaml config/archive/testing/
git mv config/paths_windows.yaml config/archive/testing/
```

### Phase 2: 日志清理
```bash
# 删除10月14-15日的日志
rm logs/nb10_202510{14,15}_*.log

# 保留10月16-17日的日志
# (无操作，保持现状)
```

### Phase 3: 输出文件清理
```bash
# 删除时间戳CSV
rm output/nb10_results_202510*.csv

# 删除测试目录
rm -rf output/cpu_performance_tests/
rm -rf output/gpu_validation/

# 删除临时文件
rm output/baseline_quick.txt
rm output/gpu_validation_run1.log
rm output/test_suite_report_*.json
```

### Phase 4: 根目录清理
```bash
git mv DEPLOY_v1.1.4.txt docs/archive/releases/v1.1.4/
```

### Phase 5: 更新.gitignore
添加规则防止未来的临时文件：
```
# Logs
logs/*.log
!logs/README.md

# Temporary output
output/*.csv
!output/*_results.csv
!output/nb10_results_complete.csv
output/*.txt
output/*.json
output/cpu_performance_tests/
output/gpu_validation/

# Test configs
config/*test*.yaml
config/*validation*.yaml
```

---

## 📊 预期清理效果

### 文件数量
- **config/**: 12 → 3个文件 (减少75%)
- **logs/**: 41 → 16个文件 (减少61%)
- **output/**: 30+ → 7个文件 (减少77%)
- **根目录**: 移动1个临时文件

### 磁盘空间
- **logs/**: ~300KB (25个文件被删除)
- **output/**: ~300KB (测试CSV和目录被删除)
- **总计**: 预计释放 ~600KB-1MB

### 项目清晰度
- ✅ 配置文件一目了然
- ✅ 日志目录简洁
- ✅ 输出目录仅保留重要结果
- ✅ 根目录无临时文件

---

## ⚠️ 风险评估

### 低风险
- ✅ 删除时间戳日志 - 已有v1.1.4稳定版本
- ✅ 删除临时测试CSV - 已有完整结果文件
- ✅ 归档测试配置 - 模板文件仍保留

### 中风险
- ⚠️ 删除测试目录 (cpu_performance_tests, gpu_validation)
  - 建议先检查是否有重要数据

### 零风险
- ✅ 移动DEPLOY文件到归档 - 仅是位置变更

---

## ✅ 执行前检查清单

执行清理前请确认：
- [ ] 已查看cpu_performance_tests/内容，确认无重要数据
- [ ] 已查看gpu_validation/内容，确认无重要数据
- [ ] 已确认chd_results.csv和normal_results.csv是最终版本
- [ ] 已确认nb10_results_complete.csv包含所有重要结果
- [ ] 已做好git状态备份 (可选: `git stash` 或创建分支)

---

## 📝 清理后任务

清理完成后需要：
1. 更新.gitignore规则
2. 测试项目功能是否正常
3. 提交清理变更
4. 更新README或文档说明新的目录结构

---

**创建者**: Claude Code
**状态**: 待审核和执行
**推荐策略**: 策略C (混合策略)
