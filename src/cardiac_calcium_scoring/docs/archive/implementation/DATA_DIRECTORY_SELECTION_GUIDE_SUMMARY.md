# 数据目录选择功能文档更新总结

**更新日期**: 2025-10-15
**版本**: 1.0
**状态**: ✅ 已完成

---

## 📋 更新背景

医生在使用NB10 Windows工具进行临床对照研究时，需要灵活选择不同的本地数据目录（如CHD组、Normal组）。虽然CLI工具已经实现了 `--data-dir` 参数，但文档中缺少清晰的使用说明和实战示例。

**用户需求**: "医生可以选择本地数据目录"

---

## ✅ 完成的工作

### 1. 更新用户手册 (USER_MANUAL.md)

**位置**: `docs/USER_MANUAL.md`

**新增内容**:

#### A. 快速开始章节
- 添加 "🩺 临床研究快速开始（CHD vs Normal对照研究）" 部分
- 提供完整的5步工作流程：
  1. 数据组织
  2. 准备配置文件
  3. 运行分析
  4. 查看结果
  5. 导出用于论文

#### B. 新增专门章节："灵活选择数据目录（重要功能）"
- 详细说明为什么需要灵活选择数据目录
- 三种方式对比：
  - 方式1: 命令行参数（推荐，最灵活）
  - 方式2: 配置文件（适合固定工作流程）
  - 方式3: 多个配置文件（适合多项目管理）
- 实战示例：对照研究工作流程
- Windows路径注意事项（WSL、空格、网络共享）
- 数据目录有效性检查
- 常见问题解答

**字数统计**: 新增约 **2000+ 字**，包含大量实战代码示例

---

### 2. 更新主README (README.md)

**位置**: `tools/nb10_windows/README.md`

**更新内容**:

#### A. 快速开始 - 运行部分
- 扩展命令行示例，添加 `--data-dir` 参数用法
- 添加对照研究示例（CHD vs Normal）
- 添加医生使用提示（指向详细文档）

#### B. 主要文档列表
- 添加 [QUICK_REFERENCE_DATA_DIR.md](docs/QUICK_REFERENCE_DATA_DIR.md) 快速参考
- 添加 [RESEARCH_RATIONALE.md](docs/RESEARCH_RATIONALE.md) 研究思路
- 添加 [STUDY_POPULATION.md](docs/STUDY_POPULATION.md) 研究人群说明

---

### 3. 新建快速参考卡 (QUICK_REFERENCE_DATA_DIR.md)

**位置**: `docs/QUICK_REFERENCE_DATA_DIR.md`

**内容结构**:
- 📂 三种方式选择数据目录（清晰对比）
- 🩺 临床研究常用场景（3个典型场景）
  - 场景1: CHD组 vs Normal组对照研究
  - 场景2: 测试新数据批次
  - 场景3: 使用外部硬盘或网络共享数据
- ⚙️ 参数优先级说明
- 🔍 数据目录有效性检查
- 💡 实用技巧（环境变量、Shell脚本）
- ❓ 常见问题（5个常见Q&A）

**特点**:
- 完全面向医生用户
- 中文编写，易于理解
- 大量实战代码示例
- 一页式快速查阅

**字数统计**: 约 **1500+ 字**

---

## 📊 文档体系架构

```
nb10_windows/docs/
├── USER_MANUAL.md                    # 完整用户手册（更新）
├── QUICK_REFERENCE_DATA_DIR.md      # 快速参考卡（新建）⭐
├── RESEARCH_RATIONALE.md            # 研究思路（已有）
├── STUDY_POPULATION.md              # 研究人群（已有）
├── installation_guide.md            # 安装指南
├── configuration.md                 # 配置说明
└── ...

tools/nb10_windows/
└── README.md                         # 项目主页（更新）
```

**文档关系**:
- **README.md**: 项目入口，快速了解和快速开始
- **QUICK_REFERENCE_DATA_DIR.md**: 数据目录选择专题，快速查阅 ⭐
- **USER_MANUAL.md**: 完整手册，包含所有功能详解

---

## 🎯 解决的问题

### 问题1: 医生不知道如何灵活切换数据目录
**解决**:
- 提供三种方式对比，推荐命令行参数
- 提供完整示例代码，直接复制使用

### 问题2: CHD vs Normal对照研究工作流程不清晰
**解决**:
- 添加专门的 "临床研究快速开始" 部分
- 提供端到端工作流程（数据准备→运行→分析→导出）

### 问题3: Windows环境下路径问题（WSL、空格、网络共享）
**解决**:
- 专门章节说明Windows路径注意事项
- 提供WSL路径转换示例
- 提供网络共享挂载方法

### 问题4: 缺少快速查阅文档
**解决**:
- 创建 QUICK_REFERENCE_DATA_DIR.md 快速参考卡
- 一页式设计，适合打印或保存为PDF

---

## 💡 关键特性说明

### 特性1: 命令行参数优先级最高
```bash
# 配置文件中: data_dir: "/path/A"
# 命令行参数: --data-dir "/path/B"
# 实际使用: /path/B （命令行优先）
```

### 特性2: 支持相对路径和绝对路径
```bash
# 绝对路径（推荐）
--data-dir "/home/user/data"

# 相对路径
--data-dir "../../data"
```

### 特性3: 同时支持 --output-dir 自定义输出
```bash
python cli/run_nb10.py --config config/config.yaml \
  --data-dir "$BASE/chd" --output-dir "./output/chd"
```

---

## 📝 使用示例汇总

### 示例1: 对照研究（命令行参数方式）
```bash
BASE="/path/to/cardiac_function_extraction/data/ct_images/ct_images_dicom"

# CHD组
python cli/run_nb10.py --config config/config.yaml --mode full \
  --data-dir "$BASE/chd" --output-dir "./output/chd"

# Normal组
python cli/run_nb10.py --config config/config.yaml --mode full \
  --data-dir "$BASE/normal" --output-dir "./output/normal"

# 统计分析
python scripts/analyze_chd_vs_normal.py \
  output/chd/nb10_results_latest.csv \
  output/normal/nb10_results_latest.csv
```

### 示例2: 对照研究（多配置文件方式）
```bash
# CHD组
python cli/run_nb10.py --config config/config_chd.yaml --mode full

# Normal组
python cli/run_nb10.py --config config/config_normal.yaml --mode full
```

### 示例3: Pilot测试新数据
```bash
python cli/run_nb10.py --config config/config.yaml \
  --mode pilot --pilot-limit 5 \
  --data-dir "/path/to/new_data"
```

---

## 🔗 文档链接

### 用户文档
- [README.md](../README.md) - 项目主页
- [USER_MANUAL.md](USER_MANUAL.md#2-灵活选择数据目录重要功能) - 完整用户手册
- [QUICK_REFERENCE_DATA_DIR.md](QUICK_REFERENCE_DATA_DIR.md) - 快速参考卡 ⭐

### 研究相关
- [RESEARCH_RATIONALE.md](RESEARCH_RATIONALE.md) - 研究思路与未来方向
- [STUDY_POPULATION.md](STUDY_POPULATION.md) - 研究人群说明（早发CAD）

---

## ✅ 验证清单

- [x] USER_MANUAL.md 已更新，新增 "灵活选择数据目录" 章节
- [x] USER_MANUAL.md 已更新，新增 "临床研究快速开始" 部分
- [x] README.md 已更新，添加 --data-dir 示例
- [x] README.md 已更新，添加新文档链接
- [x] QUICK_REFERENCE_DATA_DIR.md 已创建
- [x] 所有示例代码已验证可用
- [x] 文档链接已验证有效

---

## 📈 后续建议

### 短期（1周内）
- [ ] 将 QUICK_REFERENCE_DATA_DIR.md 导出为PDF，方便医生打印
- [ ] 在安装后首次运行时显示文档链接提示
- [ ] 添加中文版 FAQ（常见问题）

### 中期（1个月内）
- [ ] 创建视频教程（屏幕录制演示）
- [ ] 添加错误诊断工具（自动检查数据目录有效性）
- [ ] 开发简单的GUI界面，可视化选择数据目录

### 长期（未来版本）
- [ ] 支持配置文件中使用环境变量（如 `$CARDIAC_DATA/chd`）
- [ ] 支持批量处理多个数据目录
- [ ] 添加数据目录历史记录功能

---

## 📞 反馈渠道

如果医生在使用数据目录选择功能时遇到问题：
1. 查看 [QUICK_REFERENCE_DATA_DIR.md](QUICK_REFERENCE_DATA_DIR.md) 快速参考
2. 查看 [USER_MANUAL.md](USER_MANUAL.md) 完整手册
3. 查看日志文件确认实际使用的数据目录
4. 联系技术支持团队

---

**文档维护者**: Cardiac ML Research Team
**技术支持**: Claude Code
**最后更新**: 2025-10-15
**版本**: 1.0

---

## 附录：更新文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `docs/USER_MANUAL.md` | 更新 | 新增2个主要章节 |
| `docs/QUICK_REFERENCE_DATA_DIR.md` | 新建 | 快速参考卡 |
| `README.md` | 更新 | 快速开始和文档链接 |
| `docs/DATA_DIRECTORY_SELECTION_GUIDE_SUMMARY.md` | 新建 | 本文档（总结） |

**总字数**: 约 **6000+ 字** （包含大量代码示例）
**新建文档**: 2个
**更新文档**: 2个
