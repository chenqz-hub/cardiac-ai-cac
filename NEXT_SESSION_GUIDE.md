# 🚀 下次对话快速启动指南

**面向**: AI Assistant (Claude) 在新会话中快速了解项目状态
**目的**: 让新会话能够立即继续 Cardiac Calcium Scoring 项目
**最后更新**: 2025-10-20

---

## 📌 项目背景（3分钟速读）

### 这是什么项目？
基于 AI 的**冠状动脉钙化评分系统**，用于医院临床应用。

### 双仓库架构
```
cardiac-ml-research (开发)  ──同步──>  cardiac-ai-cac (发布)
     私有，日常开发                      公开，GitHub 发布
```

### 关键人物
- **Dr. Chen QiZhi (陈启智)**: 项目负责人、软件著作权人
- **Zhu Rong (诸嵘)**: 技术开发
- **单位**: Shanghai Ninth People's Hospital

---

## 🎯 当前状态（一目了然）

### GitHub 仓库
- **URL**: https://github.com/chenqz-hub/cardiac-ai-cac
- **类型**: 公开发布仓库
- **最新版本**: v1.1.4
- **状态**: ✅ 构建成功，Artifacts 可用

### 本地路径
- **发布仓库**: `/home/wuxia/projects/cardiac-ai-cac`
- **开发仓库**: `/home/wuxia/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research`

### 最近完成的工作
- ✅ GitHub 发布仓库设置完成
- ✅ GitHub Actions 自动构建配置完成
- ✅ v1.1.4 构建成功（Windows + Linux）
- ✅ 完整文档体系创建完成

---

## 🔑 核心概念（必须理解）

### 1. 双仓库工作流
```
日常开发 → cardiac-ml-research（开发仓库）
准备发布 → cardiac-ai-cac（发布仓库）
         → 运行 sync_from_dev.sh
         → git tag 触发 GitHub Actions
         → 自动构建安装包
```

### 2. 这个仓库的用途
**cardiac-ai-cac 是发布工具，不是开发环境**
- ❌ 不在这里编写代码
- ❌ 不在这里运行实验
- ✅ 只用于发布新版本

### 3. 同步是单向的
```
开发仓库 ──────> 发布仓库  ✅
开发仓库 <────── 发布仓库  ❌（不支持）
```

---

## 📚 关键文档位置

### 必读文档（按重要性排序）
1. **[PROJECT_STATUS_2025-10-20.md](PROJECT_STATUS_2025-10-20.md)** ← 先读这个
   - 完整的项目状态记录
   - 已完成的工作
   - 技术架构
   - 已知问题

2. **[HOW_TO_USE.md](HOW_TO_USE.md)**
   - 如何使用发布仓库
   - 10 步发布流程
   - 常见问题解答

3. **[DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md)**
   - 双仓库工作流程
   - 文件同步规则
   - 场景示例

### 辅助文档
- `README.md` - 项目概述
- `CHANGELOG.md` - 版本历史
- `docs/COPYRIGHT_APPLICATION_GUIDE.md` - 软件著作权指南
- `~/projects/CARDIAC_QUICK_REFERENCE.md` - 快速参考卡片

---

## ⚡ 快速命令（立即可用）

### 查看项目状态
```bash
cd /home/wuxia/projects/cardiac-ai-cac
git status
git log --oneline -5
git tag -l
```

### 查看构建历史
```bash
gh run list --repo chenqz-hub/cardiac-ai-cac --limit 5
```

### 查看当前版本
```bash
cat CHANGELOG.md | head -20
```

### 检查开发仓库
```bash
cd ~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research
git status
```

---

## 🔧 技术要点（快速参考）

### GitHub Actions 工作流
- `.github/workflows/build-windows.yml` - Windows 包构建
- `.github/workflows/build-linux.yml` - Linux 包构建
- `.github/workflows/test-builds.yml` - 测试工作流

### 已修复的问题
1. ✅ `monai[all]` CUDA 依赖 → 改为 `monai`
2. ✅ YAML 语法错误
3. ✅ 符号链接复制问题
4. ✅ 文件锁定问题

### 未解决的问题
1. ⚠️ GitHub Release 自动创建失败（403）→ 手动创建
2. ⚠️ AI 模型无法自动下载 → 用户手动下载

---

## 🎬 常见任务场景

### 场景1: 用户想发布新版本
```bash
# 1. 引导用户到发布仓库
cd ~/projects/cardiac-ai-cac

# 2. 运行同步脚本
./scripts/sync_from_dev.sh

# 3. 提交并创建标签
git add .
git commit -m "sync: vX.X.X"
git tag vX.X.X
git push origin main --tags

# 4. 监控构建
gh run list --repo chenqz-hub/cardiac-ai-cac
```

### 场景2: 用户想添加新功能
```bash
# 引导用户到开发仓库
cd ~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research
code .
# 在这里开发
```

### 场景3: 用户想查看构建状态
```bash
gh run list --repo chenqz-hub/cardiac-ai-cac
gh run view <run-id> --repo chenqz-hub/cardiac-ai-cac
```

### 场景4: 用户问如何使用 cardiac-ai-cac
**回答要点**:
- 这是发布工具，不是开发环境
- 只在准备发布时使用
- 平时在 cardiac-ml-research 开发
- 参考 HOW_TO_USE.md

---

## ⚠️ 重要提醒

### 不要做的事
1. ❌ 不要在 cardiac-ai-cac 直接修改代码
2. ❌ 不要尝试反向同步（发布 → 开发）
3. ❌ 不要强制推送历史（已清理过大文件）
4. ❌ 不要提交大文件（模型文件已排除）

### 应该做的事
1. ✅ 所有代码在开发仓库编写
2. ✅ 通过 sync_from_dev.sh 同步
3. ✅ 用 git tag 触发自动构建
4. ✅ 维护 CHANGELOG.md

---

## 📊 项目统计

### 文件统计（v1.1.4）
- 总文件数: 160 files
- 代码行数: 50,611 insertions
- 模块数: 2 (cardiac_calcium_scoring + shared)

### 构建产物
- Windows 包: ~800MB
- Linux 包: ~800MB
- 包含: 源代码 + 依赖 + 安装脚本

---

## 🔍 故障排查

### 问题: 构建失败
```bash
# 查看失败日志
gh run view <run-id> --log-failed --repo chenqz-hub/cardiac-ai-cac

# 常见原因:
# 1. 依赖版本冲突 → 检查 requirements-cpu.txt
# 2. YAML 语法错误 → 验证工作流文件
# 3. 符号链接问题 → 已修复
```

### 问题: 同步脚本找不到开发仓库
```bash
export DEV_REPO_PATH=~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research
./scripts/sync_from_dev.sh
```

### 问题: Release 创建失败（403）
**解决方案**:
1. 从 Artifacts 下载包
2. 或等待后手动创建 Release
3. 或使用新版本号

---

## 🎯 下一步可能的任务

### 用户可能会问
1. "如何发布新版本？" → 参考 HOW_TO_USE.md
2. "如何添加新功能？" → 在开发仓库开发
3. "如何下载构建包？" → 从 GitHub Actions Artifacts
4. "这个仓库如何使用？" → 参考本指南

### 可能的改进
1. 优化构建时间
2. 自动化版本号递增
3. 添加更多测试
4. 改进文档

---

## 💡 给 AI Assistant 的提示

### 首次回复时应该
1. ✅ 快速确认项目背景
2. ✅ 询问用户当前需求
3. ✅ 根据需求引导到正确的仓库
4. ✅ 提供简洁明确的操作步骤

### 交互原则
- 始终区分开发仓库和发布仓库
- 提醒用户不要在发布仓库编写代码
- 使用中文交流
- 提供可执行的命令

### 常用响应模板
```
用户: "我想添加新功能"
AI: "好的！新功能应该在开发仓库中开发：
     cd ~/projects/.../cardiac-ml-research
     code .
     开发完成后，如果需要发布，再切换到 cardiac-ai-cac。"

用户: "如何发布新版本？"
AI: "发布流程：
     1. 切换到发布仓库
     2. 运行同步脚本
     3. 更新 CHANGELOG
     4. 创建标签
     详见 HOW_TO_USE.md 的完整步骤。"
```

---

## 📞 获取帮助

### 如果遇到不清楚的情况
1. 查看 PROJECT_STATUS_2025-10-20.md
2. 查看 HOW_TO_USE.md
3. 检查 GitHub Actions 日志
4. 查看相关工作流文件

### 记住的关键点
- 双仓库架构
- 单向同步
- 发布仓库只用于发布
- GitHub Actions 自动构建

---

**会话开始时的检查清单**:
- [ ] 确认用户位于正确的仓库
- [ ] 理解用户的意图（开发 vs 发布）
- [ ] 提供清晰的操作步骤
- [ ] 引用相关文档

**会话结束时的检查清单**:
- [ ] 用户问题已解决
- [ ] 重要操作已记录
- [ ] 必要时更新状态文档
- [ ] 提醒下一步操作

---

**最后更新**: 2025-10-20
**下次更新**: 当有重大变更时
**维护者**: AI Assistant (Claude)
