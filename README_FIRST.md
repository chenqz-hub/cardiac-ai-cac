# 👋 第一次打开这个项目？请先读我！

**如果您是在下次会话中打开这个项目，请从这里开始。**

---

## 🎯 这个项目是什么？

**Cardiac AI-CAC** - 基于 AI 的冠状动脉钙化评分系统

- **这个仓库**: 用于**发布**新版本给医院使用
- **另一个仓库**: 用于**日常开发**（在 `cardiac-ml-research`）

---

## ⚡ 我现在想做什么？

### 1️⃣ 我想编写代码 / 添加新功能
**→ 您走错地方了！**

请到开发仓库：
```bash
cd ~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research
code .
```

### 2️⃣ 我想发布新版本给医院
**→ 您来对地方了！**

按照以下步骤：
```bash
# 1. 同步代码
./scripts/sync_from_dev.sh

# 2. 更新变更日志
nano CHANGELOG.md

# 3. 提交并创建标签
git add .
git commit -m "sync: vX.X.X"
git tag vX.X.X
git push origin main --tags
```

详细步骤请看 **[HOW_TO_USE.md](HOW_TO_USE.md)**

### 3️⃣ 我想查看构建状态
```bash
gh run list --repo chenqz-hub/cardiac-ai-cac --limit 5
```

### 4️⃣ 我想了解项目结构
阅读 **[PROJECT_STATUS_2025-10-20.md](PROJECT_STATUS_2025-10-20.md)**

---

## 📚 文档索引

| 文档 | 用途 | 阅读时间 |
|------|------|----------|
| [README_FIRST.md](README_FIRST.md) | **👈 您在这里** | 2分钟 |
| [PROJECT_STATUS_2025-10-20.md](PROJECT_STATUS_2025-10-20.md) | 项目完整状态 | 10分钟 |
| [HOW_TO_USE.md](HOW_TO_USE.md) | 如何发布新版本 | 15分钟 |
| [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md) | 工作流程详解 | 20分钟 |
| [NEXT_SESSION_GUIDE.md](NEXT_SESSION_GUIDE.md) | AI助手指南 | 5分钟 |

---

## 🔑 核心理念（记住这一点）

```
cardiac-ml-research        cardiac-ai-cac
  (开发仓库)      ────>      (发布仓库)
     ✏️                         📦
  日常编码                  偶尔发布
  99%的时间                1%的时间
```

**只有准备向医院发布新版本时，才需要使用这个仓库（cardiac-ai-cac）。**

---

## 🚨 常见错误

### ❌ 错误做法
```bash
# 在这个仓库直接修改代码
cd ~/projects/cardiac-ai-cac
nano src/cardiac_calcium_scoring/core/processing.py  # ❌
```

### ✅ 正确做法
```bash
# 在开发仓库修改代码
cd ~/projects/.../cardiac-ml-research
nano tools/cardiac_calcium_scoring/core/processing.py  # ✅

# 然后通过同步脚本发布
cd ~/projects/cardiac-ai-cac
./scripts/sync_from_dev.sh
```

---

## 📞 需要帮助？

1. **查看详细文档**: [HOW_TO_USE.md](HOW_TO_USE.md)
2. **查看项目状态**: [PROJECT_STATUS_2025-10-20.md](PROJECT_STATUS_2025-10-20.md)
3. **快速参考**: `~/projects/CARDIAC_QUICK_REFERENCE.md`

---

## 🎯 下一步

**如果您是为了开发**:
```bash
cd ~/projects/family_management_hub/members/wife/medical_research/cardiac-ml-research
code .
```

**如果您是为了发布**:
```bash
# 留在这里
cat HOW_TO_USE.md  # 阅读发布指南
```

---

**记住**: 这个仓库是**发布工具**，不是**开发环境**！
