# Cardiac AI-CAC 项目状态记录

**日期**: 2025年10月20日
**会话**: GitHub 发布仓库设置完成
**记录人**: AI Assistant (Claude)

---

## 📊 项目概览

### 仓库信息
- **GitHub 仓库**: https://github.com/chenqz-hub/cardiac-ai-cac
- **本地路径**: `/home/wuxia/projects/cardiac-ai-cac`
- **仓库类型**: 公开发布仓库
- **当前版本**: v1.1.4
- **分支**: main

### 关联仓库
- **开发仓库**: `/home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research`
- **关系**: 开发仓库 → 单向同步 → 发布仓库

---

## ✅ 已完成的工作

### 1. 仓库初始化与清理
- [x] 从开发仓库创建发布仓库模板
- [x] 清理 Git 历史中的大文件（1.2GB 模型文件）
- [x] 创建干净的初始提交（160 files, 50,611 insertions）
- [x] 推送到 GitHub: chenqz-hub/cardiac-ai-cac

### 2. GitHub Actions 自动构建配置
- [x] 配置 Windows 包构建工作流 (`.github/workflows/build-windows.yml`)
- [x] 配置 Linux 包构建工作流 (`.github/workflows/build-linux.yml`)
- [x] 配置测试工作流 (`.github/workflows/test-builds.yml`)
- [x] 实现自动下载依赖包（离线安装）
- [x] 处理模型文件下载失败的优雅降级

### 3. 修复的技术问题
- [x] 修复 `monai[all]` CUDA 依赖问题 → 改为 `monai`
- [x] 修复 GitHub Actions YAML 语法错误
- [x] 修复符号链接复制问题（external/AI-CAC）
- [x] 修复 PowerShell 文件锁定问题（checksum 生成）
- [x] 处理 Google Drive 模型下载权限问题

### 4. 成功构建验证
- [x] Windows 包构建成功 ✓
- [x] Linux 包构建成功 ✓
- [x] Artifacts 上传成功
  - `windows-package-v1.1.4`
  - `linux-package-v1.1.4`

### 5. 文档创建
- [x] `README.md` - 项目说明（中英文）
- [x] `CHANGELOG.md` - 版本变更历史
- [x] `LICENSE` - 软件许可证
- [x] `DEVELOPMENT_WORKFLOW.md` - 双仓库工作流程
- [x] `HOW_TO_USE.md` - 发布仓库使用指南
- [x] `docs/COPYRIGHT_APPLICATION_GUIDE.md` - 软件著作权申请指南
- [x] `scripts/sync_from_dev.sh` - 同步脚本
- [x] `scripts/verify_package.sh` - 包验证脚本

### 6. 辅助文档（项目外）
- [x] `~/projects/cardiac-workspace.code-workspace` - VS Code 工作区配置
- [x] `~/projects/CARDIAC_QUICK_REFERENCE.md` - 快速参考卡片
- [x] `~/projects/CARDIAC_AI_CAC_使用指南.md` - 简明使用指南

---

## 📁 仓库结构

```
cardiac-ai-cac/
├── .github/
│   └── workflows/
│       ├── build-windows.yml       # Windows 包自动构建
│       ├── build-linux.yml         # Linux 包自动构建
│       └── test-builds.yml         # 测试工作流
├── docs/
│   └── COPYRIGHT_APPLICATION_GUIDE.md  # 软件著作权指南
├── requirements/
│   ├── requirements.txt            # 通用依赖
│   ├── requirements-cpu.txt        # CPU 版本依赖
│   └── requirements-gpu.txt        # GPU 版本依赖
├── scripts/
│   ├── sync_from_dev.sh           # 从开发仓库同步脚本
│   └── verify_package.sh          # 包验证脚本
├── src/
│   ├── cardiac_calcium_scoring/   # 核心模块（从开发仓库同步）
│   └── shared/                    # 共享模块（从开发仓库同步）
├── CHANGELOG.md                   # 版本历史
├── DEVELOPMENT_WORKFLOW.md        # 工作流程文档
├── HOW_TO_USE.md                 # 使用指南
├── LICENSE                        # 许可证
├── README.md                      # 项目说明（英文）
├── README_CN.md                   # 项目说明（中文）
└── PROJECT_STATUS_2025-10-20.md  # 本状态文档
```

---

## 🔧 技术架构

### 自动构建流程
```
git push tag vX.X.X
    ↓
GitHub Actions 触发
    ↓
并行构建 Windows & Linux
    ↓
├── 下载 Python 依赖（pip download）
├── 尝试下载 AI 模型（可能失败，继续）
├── 创建包结构
├── 生成安装脚本
├── 压缩打包
└── 上传 Artifact
    ↓
（尝试）创建 GitHub Release
```

### 依赖管理
- **Python**: 3.10+
- **核心依赖**: PyTorch 2.2.0 (CPU), MONAI 1.3.2, SimpleITK 2.3.1
- **模型**: SwinUNETR (1.2GB, 需手动下载)

### 构建产物
- Windows: `cardiac-ai-cac-windows-vX.X.X.zip`
- Linux: `cardiac-ai-cac-linux-vX.X.X.tar.gz`
- 包含: 源代码 + 所有依赖 wheel 包 + 安装脚本

---

## ⚠️ 已知问题与解决方案

### 问题1: GitHub Release 自动创建失败（403 Forbidden）
**原因**: 频繁强制更新同一标签导致 API 限制
**影响**: 构建成功，但无法自动创建 Release
**解决方案**:
- 方案A: 从 GitHub Actions Artifacts 手动下载包
- 方案B: 等待几小时后手动创建 Release
- 方案C: 使用新的版本号而不是强制更新旧标签

### 问题2: AI 模型文件无法自动下载
**原因**: Google Drive 文件权限设置为私有
**影响**: 构建包中不包含模型文件
**解决方案**:
- 用户需要手动下载模型文件（1.2GB）
- 包内包含 `models/DOWNLOAD_MODEL.txt` 说明文件
- Google Drive 链接: https://drive.google.com/file/d/1uD12kphnWlJ5R6K-mDQnxS8LjYhPGSfm/view

### 问题3: 符号链接在 Windows 构建时失败
**原因**: `src/cardiac_calcium_scoring/external/AI-CAC` 是符号链接
**解决方案**: 构建脚本中排除此符号链接（已修复）

---

## 🔄 工作流程说明

### 日常开发（在开发仓库）
```bash
cd ~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research
code .
# 正常开发、测试、提交...
```

### 发布新版本（在发布仓库）
```bash
cd ~/projects/cardiac-ai-cac
./scripts/sync_from_dev.sh          # 同步代码
nano CHANGELOG.md                    # 更新变更日志
git add . && git commit -m "sync: vX.X.X"
git tag vX.X.X && git push origin main --tags
```

### 监控构建
```bash
gh run list --repo chenqz-hub/cardiac-ai-cac
gh run view <run-id> --repo chenqz-hub/cardiac-ai-cac
```

---

## 📋 当前 Git 状态

### 最新提交
```
7f06e11 docs: add comprehensive usage guide for release repository
5423444 docs: add development workflow guide for dual-repo setup
baea22c fix: resolve file locking issue in checksum generation
2878ce9 fix: exclude symlink to external AI-CAC during package copy
40d0e7c fix: resolve YAML syntax errors in GitHub Actions workflows
```

### 标签
- `v1.1.4` - 最新发布版本

### 构建状态（v1.1.4）
- Windows 包: ✓ 构建成功（除 Release 创建）
- Linux 包: ✓ 构建成功（除 Release 创建）
- Test 工作流: ✓ 通过

---

## 🎯 下一步建议

### 短期（下次发布时）
1. 在开发仓库完成新功能开发
2. 运行同步脚本到发布仓库
3. 创建新版本标签（建议 v1.1.5 或 v1.2.0）
4. 等待 GitHub Actions 构建完成
5. 从 Artifacts 下载构建包
6. 可选：手动创建 GitHub Release

### 中期优化
1. 考虑将 AI 模型上传到 GitHub Release 或其他公开存储
2. 优化 GitHub Actions 构建时间
3. 添加自动化测试到构建流程
4. 考虑使用 GitHub Release 的自动化工具

### 长期规划
1. 建立发布自动化 CI/CD 流程
2. 添加版本号自动递增机制
3. 实现多语言安装包构建
4. 建立用户反馈收集机制

---

## 📞 团队信息

### 项目负责人
- **作者**: Dr. Chen QiZhi (陈启智)
- **Email**: chenqz73@hotmail.com
- **单位**: Shanghai Ninth People's Hospital (上海交通大学医学院附属第九人民医院)

### 技术开发
- **开发者**: Zhu Rong (诸嵘)
- **GitHub**: zhurong2020

### 软件著作权
- **权利人**: Chen QiZhi (单独所有)
- **目的**: 医院职称评审

---

## 🔗 重要链接

### GitHub
- 仓库: https://github.com/chenqz-hub/cardiac-ai-cac
- Actions: https://github.com/chenqz-hub/cardiac-ai-cac/actions
- Releases: https://github.com/chenqz-hub/cardiac-ai-cac/releases

### 文档
- [完整使用指南](HOW_TO_USE.md)
- [工作流程文档](DEVELOPMENT_WORKFLOW.md)
- [快速参考卡片](../CARDIAC_QUICK_REFERENCE.md)
- [简明使用指南](../CARDIAC_AI_CAC_使用指南.md)

### 本地路径
- 发布仓库: `/home/wuxia/projects/cardiac-ai-cac`
- 开发仓库: `/home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research`
- VS Code 工作区: `/home/wuxia/projects/cardiac-workspace.code-workspace`

---

## 📝 会话记录

### 本次会话完成的主要任务
1. ✅ 设置 GitHub 发布仓库（chenqz-hub/cardiac-ai-cac）
2. ✅ 配置 GitHub Actions 自动构建流程
3. ✅ 修复所有构建错误（依赖、YAML、符号链接、文件锁定）
4. ✅ 成功构建 Windows 和 Linux 包
5. ✅ 创建完整的文档体系
6. ✅ 解释双仓库工作流程

### 下次对话时需要了解的关键信息
- 这是一个**双仓库架构**：开发仓库（私有）+ 发布仓库（公开）
- **开发仓库**用于日常编程（cardiac-ml-research）
- **发布仓库**仅用于发布（cardiac-ai-cac）
- 同步是**单向的**：开发 → 发布
- GitHub Actions 已配置好自动构建
- v1.1.4 构建成功，包已上传到 Artifacts

### 未解决的问题
- GitHub Release 自动创建失败（403）- 需手动创建或等待
- AI 模型文件需手动下载（Google Drive 权限问题）

---

## 🎓 技术要点

### Git 历史清理
- 使用 `rm -rf .git && git init` 方式清理
- 原因：包含 1.2GB 大文件，超过 GitHub 限制
- 结果：干净的仓库，无大文件

### GitHub Actions 优化
- 使用 `continue-on-error: true` 处理模型下载失败
- 使用 `-Exclude` 参数排除符号链接
- 分步骤生成校验和避免文件锁定

### 依赖管理策略
- `monai==1.3.2` (不带 [all]) 避免 CUDA 依赖
- 使用 `pip download` 预下载所有依赖
- 支持完全离线安装

---

**记录完成日期**: 2025-10-20
**下次更新**: 当发布新版本或有重大变更时

---

## 📌 快速启动命令（下次会话）

```bash
# 查看项目状态
cd ~/projects/cardiac-ai-cac
git status
git log --oneline -5
gh run list --repo chenqz-hub/cardiac-ai-cac --limit 5

# 查看文档
cat HOW_TO_USE.md
cat DEVELOPMENT_WORKFLOW.md
cat PROJECT_STATUS_2025-10-20.md

# 开始新的开发
cd ~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research
code .
```
