# 开发与发布工作流程

本文档说明如何在两个仓库之间协作：开发仓库和发布仓库。

## 📁 仓库结构

### 开发仓库（私有）
- **路径**: `~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research`
- **用途**: 日常开发、研究、实验
- **包含**:
  - 完整开发历史
  - 研究数据和笔记
  - 实验性代码
  - Week 7+ 新功能

### 发布仓库（公开）
- **路径**: `~/projects/cardiac-ai-cac`
- **GitHub**: https://github.com/chenqz-hub/cardiac-ai-cac
- **用途**: 对外发布、医院部署
- **包含**:
  - 生产就绪的代码
  - 用户文档
  - 自动构建流程

## 🔄 日常工作流程

### 1️⃣ 日常开发（在开发仓库）

```bash
# 在 VS Code 中打开开发仓库
cd ~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research
code .

# 或者使用多根工作区
code ~/projects/cardiac-workspace.code-workspace

# 正常开发、提交
git add .
git commit -m "feat: add new feature"
git push origin main
```

**在开发仓库做什么：**
- ✅ 编写新功能
- ✅ 运行实验
- ✅ 测试代码
- ✅ 编写研究笔记
- ✅ Week 7+ 功能开发

### 2️⃣ 准备发布新版本

当您准备向医院发布新版本时：

```bash
# 1. 确保开发仓库的代码已测试通过
cd ~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research
pytest  # 运行测试

# 2. 更新版本号（如果需要）
# 编辑 tools/cardiac_calcium_scoring/module_info.yaml

# 3. 切换到发布仓库
cd ~/projects/cardiac-ai-cac

# 4. 运行同步脚本
./scripts/sync_from_dev.sh
# 输入版本号，例如: v1.1.5

# 5. 检查同步的文件
git status
git diff

# 6. 更新 CHANGELOG.md
nano CHANGELOG.md
# 添加新版本的更新说明

# 7. 提交更改
git add .
git commit -m "sync: update to v1.1.5 from dev repo"
git push origin main

# 8. 创建版本标签（触发自动构建）
git tag -a v1.1.5 -m "Release v1.1.5: 新功能描述"
git push origin v1.1.5
```

### 3️⃣ GitHub Actions 自动构建

标签推送后，GitHub Actions 会自动：
1. 下载所有 Python 依赖
2. 尝试下载 AI 模型（可能失败）
3. 打包 Windows 和 Linux 发布包
4. 上传 Artifacts 到 GitHub

**检查构建状态：**
```bash
gh run list --repo chenqz-hub/cardiac-ai-cac --limit 3
```

**下载构建包：**
- 访问 GitHub Actions 页面
- 或使用 gh CLI 下载 artifacts

### 4️⃣ 手动创建 GitHub Release（如果自动创建失败）

```bash
# 如果 GitHub Actions 的自动 Release 创建失败（403错误）
# 可以从 GitHub web 界面手动创建

# 或使用 gh CLI:
gh release create v1.1.5 \
  --repo chenqz-hub/cardiac-ai-cac \
  --title "v1.1.5 - CPU-Optimized Coronary Calcium Scoring" \
  --notes "发布说明..." \
  path/to/downloaded/packages/*.zip
```

## 📋 文件同步规则

### ✅ 会同步到发布仓库：
- `src/cardiac_calcium_scoring/` - 核心代码
- `src/shared/` - 共享模块
- `requirements/*.txt` - 依赖文件
- `README.md`, `CHANGELOG.md`, `LICENSE` - 文档

### ❌ 不会同步（仅在开发仓库）：
- `data/` - 研究数据
- `output/` - 实验输出
- `docs/research/` - 研究笔记
- `docs/weekly_reports/` - 周报
- `vendors/` - 外部依赖
- `test_*.py` - 测试文件
- `__pycache__/`, `*.pyc` - 缓存

## 🔍 常见场景

### 场景1: 修复紧急bug

```bash
# 1. 在开发仓库修复
cd ~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research
# 修改代码
git commit -m "fix: critical bug"
git push

# 2. 立即同步到发布仓库
cd ~/projects/cardiac-ai-cac
./scripts/sync_from_dev.sh  # 输入 v1.1.5-hotfix
git add .
git commit -m "hotfix: critical bug fix"
git tag v1.1.5-hotfix
git push origin main --tags
```

### 场景2: 仅更新文档

```bash
# 如果只修改用户文档，直接在发布仓库操作
cd ~/projects/cardiac-ai-cac
nano README.md
git commit -m "docs: update installation guide"
git push origin main
```

### 场景3: 添加新功能（需要几周开发）

```bash
# 1. 在开发仓库创建功能分支
cd ~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research
git checkout -b feature/new-analysis

# 2. 正常开发、测试
# ... 多次提交 ...

# 3. 功能完成后合并到 main
git checkout main
git merge feature/new-analysis
git push

# 4. 测试通过后，同步到发布仓库
cd ~/projects/cardiac-ai-cac
./scripts/sync_from_dev.sh  # 输入 v1.2.0
```

## 🛠️ VS Code 配置建议

### 方式1: 每次只打开一个项目（简单）

```bash
# 开发时
code ~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research

# 发布时
code ~/projects/cardiac-ai-cac
```

### 方式2: 使用多根工作区（高级）

打开工作区配置文件：
```bash
code ~/projects/cardiac-workspace.code-workspace
```

在 VS Code 中可以看到两个文件夹：
- 🔬 Cardiac ML Research (Development)
- 📦 Cardiac AI-CAC (Release)

**优点**: 可以同时查看两边的代码，方便对比
**缺点**: 需要注意在正确的目录下操作

## ⚠️ 重要提醒

1. **始终在开发仓库编写新代码** - 发布仓库只用于发布
2. **同步是单向的** - 从开发仓库 → 发布仓库
3. **测试后再同步** - 确保代码在开发仓库测试通过
4. **模型文件需手动下载** - 发布包中不包含1.2GB的模型文件
5. **GitHub Actions 可能失败** - Release创建可能因权限问题失败，需手动创建

## 📞 问题排查

### 问题: 同步脚本找不到开发仓库
```bash
# 设置环境变量
export DEV_REPO_PATH=~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research
./scripts/sync_from_dev.sh
```

### 问题: GitHub Actions 构建失败
```bash
# 查看失败日志
gh run list --repo chenqz-hub/cardiac-ai-cac
gh run view <run-id> --log-failed
```

### 问题: 想要回滚某个文件
```bash
# 在发布仓库
cd ~/projects/cardiac-ai-cac
git checkout HEAD~1 -- src/cardiac_calcium_scoring/specific_file.py
git commit -m "revert: rollback specific file"
```

## 📚 相关文档

- [README.md](README.md) - 项目概述
- [CHANGELOG.md](CHANGELOG.md) - 版本历史
- [docs/COPYRIGHT_APPLICATION_GUIDE.md](docs/COPYRIGHT_APPLICATION_GUIDE.md) - 软件著作权指南
- [.github/workflows/](github/workflows/) - GitHub Actions 配置
