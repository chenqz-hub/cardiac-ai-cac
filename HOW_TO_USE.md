# 如何使用 cardiac-ai-cac 发布仓库

## 🎯 核心理念

这个仓库是**发布工具**，不是开发工具。

```
开发仓库 (cardiac-ml-research) ──同步──> 发布仓库 (cardiac-ai-cac) ──构建──> 安装包
     [您在这里写代码]                    [只用来发布]              [医院使用]
```

## 📅 使用时机

### 什么时候需要操作这个仓库？

**仅在以下情况：**
1. ✅ 准备向医院发布新版本
2. ✅ 需要修复发布文档的错别字
3. ✅ 查看 GitHub Actions 构建状态
4. ✅ 下载构建好的安装包

**不需要在以下情况：**
- ❌ 日常编写代码 → 用开发仓库
- ❌ 运行实验测试 → 用开发仓库
- ❌ 添加新功能 → 用开发仓库
- ❌ 修复bug → 先在开发仓库修复

## 🔄 完整发布流程（分步详解）

### 第一步：在开发仓库完成开发

```bash
# 在开发仓库工作（这是您平时工作的地方）
cd ~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research

# 打开 VS Code
code .

# 开发新功能、修复bug、运行测试...
# ... 正常的开发工作 ...

# 提交到开发仓库
git add .
git commit -m "feat: new feature completed and tested"
git push

# ✅ 开发工作到此结束
```

### 第二步：决定发布版本

思考以下问题：
- [ ] 新功能是否已经测试通过？
- [ ] 是否有需要向医院说明的重要变更？
- [ ] 版本号应该是多少？（参考语义化版本）
  - 主版本号（1.x.x）：不兼容的API修改
  - 次版本号（x.2.x）：新功能，向后兼容
  - 修订号（x.x.5）：bug修复

确定版本号，例如：`v1.2.0`

### 第三步：切换到发布仓库并同步

```bash
# 切换到发布仓库
cd ~/projects/cardiac-ai-cac

# 确保发布仓库是最新的
git pull origin main

# 运行同步脚本
./scripts/sync_from_dev.sh
```

**脚本会提示：**
```
Enter version to sync (e.g., v1.1.4):
```

**输入版本号：**
```
v1.2.0
```

**脚本会自动执行：**
```
[1/6] Creating clean export directory...
[2/6] Exporting source code from dev repo...
  - Exporting cardiac_calcium_scoring...
  - Exporting shared modules...
[3/6] Exporting requirements files...
[4/6] Cleaning up export...
  Exported 162 files
[5/6] Syncing to release repo...
[6/6] Updating CHANGELOG...
```

### 第四步：检查同步结果

```bash
# 查看哪些文件被更新了
git status

# 查看具体改动
git diff

# 查看某个文件的详细变化
git diff src/cardiac_calcium_scoring/core/processing.py
```

### 第五步：更新 CHANGELOG

```bash
# 编辑 CHANGELOG.md
nano CHANGELOG.md

# 添加新版本说明（在文件顶部）
```

添加内容示例：
```markdown
## [v1.2.0] - 2025-10-20

### Added
- 新增 XXX 分析功能
- 支持 YYY 格式的数据导入

### Changed
- 优化了 ZZZ 算法的性能（提速30%）

### Fixed
- 修复了 AAA 在特定情况下的崩溃问题
```

### 第六步：提交更改

```bash
# 添加所有更改
git add .

# 创建提交
git commit -m "sync: update to v1.2.0 from dev repo

- Add new XXX analysis feature
- Optimize YYY algorithm performance
- Fix AAA crash issue

Synced from: cardiac-ml-research @ commit abc1234"

# 推送到 GitHub
git push origin main
```

### 第七步：创建版本标签

```bash
# 创建带注释的标签
git tag -a v1.2.0 -m "Release v1.2.0: Enhanced Analysis Features

主要更新：
- 新增 XXX 分析功能
- 性能优化（提速30%）
- Bug修复

作者: Dr. Chen QiZhi (陈启智)
技术: Zhu Rong (诸嵘)
单位: Shanghai Ninth People's Hospital"

# 推送标签到 GitHub（这会触发自动构建）
git push origin v1.2.0
```

### 第八步：监控自动构建

```bash
# 等待几秒让 GitHub Actions 启动
sleep 10

# 查看构建状态
gh run list --repo chenqz-hub/cardiac-ai-cac --limit 3

# 应该看到类似输出：
# in_progress  sync: update to v1.2.0  Build Windows Package  v1.2.0  push
# in_progress  sync: update to v1.2.0  Build Linux Package    v1.2.0  push
```

**等待构建完成（通常3-5分钟）：**

```bash
# 查看特定构建的详细信息
gh run view <run-id> --repo chenqz-hub/cardiac-ai-cac

# 如果构建成功，会显示：
# ✓ build-windows
# ✓ build-linux
# ARTIFACTS
# windows-package-v1.2.0
# linux-package-v1.2.0
```

### 第九步：获取构建包

#### 方法1: 从 GitHub Actions 下载

```bash
# 列出最新构建的 artifacts
gh run view <run-id> --repo chenqz-hub/cardiac-ai-cac

# 下载 artifact（需要先在浏览器中找到下载链接）
# 或直接访问 GitHub Actions 页面下载
```

#### 方法2: 从 GitHub Release 下载（如果自动创建成功）

访问：https://github.com/chenqz-hub/cardiac-ai-cac/releases/tag/v1.2.0

### 第十步：交付给医院

将下载的安装包交给医院IT部门：
- `cardiac-ai-cac-windows-v1.2.0.zip`
- `cardiac-ai-cac-linux-v1.2.0.tar.gz`

并提供：
- 安装说明（包内有 README.md）
- 模型下载链接（包内有 DOWNLOAD_MODEL.txt）
- CHANGELOG（说明本次更新内容）

## 🛠️ 常用命令速查

### 查看当前状态
```bash
cd ~/projects/cardiac-ai-cac
git status                    # 本地状态
git log --oneline -5          # 最近提交
git tag -l                    # 所有标签
gh run list --repo chenqz-hub/cardiac-ai-cac --limit 5  # 构建历史
```

### 快速同步最新代码（不创建发布）
```bash
cd ~/projects/cardiac-ai-cac
git pull origin main
```

### 查看特定版本的构建状态
```bash
gh run list --repo chenqz-hub/cardiac-ai-cac | grep v1.2.0
```

### 如果需要回滚发布
```bash
# 删除远程标签
git push origin :refs/tags/v1.2.0

# 删除本地标签
git tag -d v1.2.0

# 回滚提交（如果需要）
git revert HEAD
git push origin main
```

## ⚠️ 注意事项

### 1. 不要在此仓库直接修改代码
❌ **错误做法：**
```bash
cd ~/projects/cardiac-ai-cac
nano src/cardiac_calcium_scoring/core/processing.py  # ❌ 不要这样
git commit -m "fix bug"
```

✅ **正确做法：**
```bash
cd ~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research
nano tools/cardiac_calcium_scoring/core/processing.py  # ✅ 在这里修改
git commit -m "fix bug"
# 然后再同步到发布仓库
```

### 2. 模型文件不会自动包含
由于模型文件太大（1.2GB），构建包中**不包含**模型文件。

用户需要手动下载：
- Google Drive 链接在包内 `models/DOWNLOAD_MODEL.txt`
- 医院IT需要单独下载并放置到正确位置

### 3. GitHub Release 可能创建失败
如果看到 "Create GitHub Release" 步骤失败（403错误）：
- 构建包已经成功创建（在 Artifacts 中）
- 只是自动发布失败
- 可以手动从 GitHub web 界面创建 Release

### 4. 同步是单向的
```
开发仓库 ──> 发布仓库  ✅ 正确方向
开发仓库 <── 发布仓库  ❌ 不支持反向同步
```

如果在发布仓库修改了文档，记得也在开发仓库更新。

## 📊 典型时间线示例

**假设现在是 2025年10月20日：**

```
10月1日  - 在开发仓库开始开发新功能
10月5日  - 功能开发完成，提交到开发仓库
10月8日  - 在开发仓库完成测试
10月10日 - 决定发布 v1.2.0
         - 切换到 cardiac-ai-cac
         - 运行 sync_from_dev.sh
         - 更新 CHANGELOG
         - 提交并创建标签 v1.2.0
         - GitHub Actions 自动构建（5分钟）
         - 下载构建包
10月11日 - 交付安装包给医院
```

**发布仓库实际使用时间：** 约30分钟
**开发仓库使用时间：** 9天

## 🔗 相关资源

- [完整工作流程文档](DEVELOPMENT_WORKFLOW.md)
- [快速参考卡片](../CARDIAC_QUICK_REFERENCE.md)
- [GitHub 仓库](https://github.com/chenqz-hub/cardiac-ai-cac)
- [GitHub Actions 页面](https://github.com/chenqz-hub/cardiac-ai-cac/actions)

## ❓ 常见问题

### Q: 我应该多久发布一次新版本？
A: 根据需要。建议：
- 重要新功能：发布次版本（v1.2.0）
- Bug修复：发布修订版（v1.1.5）
- 累积多个小改进：每月发布一次

### Q: 如果同步脚本找不到开发仓库怎么办？
A: 设置环境变量：
```bash
export DEV_REPO_PATH=~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research
./scripts/sync_from_dev.sh
```

### Q: 构建失败了怎么办？
A: 查看错误日志：
```bash
gh run view <run-id> --log-failed --repo chenqz-hub/cardiac-ai-cac
```
通常是依赖问题或 YAML 语法错误。

### Q: 可以跳过某个版本号吗？
A: 可以。版本号只是标签，您可以自由决定。
例如：v1.1.4 → v1.2.0（跳过 v1.1.5-v1.1.9）

### Q: 如何查看某个版本包含哪些文件？
A: 切换到该标签：
```bash
git checkout v1.2.0
ls -la src/
git checkout main  # 切回 main 分支
```

---

## 🎓 学习建议

**第一次使用建议：**
1. 先阅读本文档
2. 查看 [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) 了解大局
3. 试着运行一次 `sync_from_dev.sh`（测试模式）
4. 查看生成的临时目录内容
5. 等到真的需要发布时再创建标签

**建立习惯：**
- 日常工作 → 开发仓库
- 准备发布 → cardiac-ai-cac
- 一次只关注一个仓库，避免混淆
