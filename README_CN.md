# 冠脉钙化AI评分系统 (Cardiac AI-CAC)

[![版本](https://img.shields.io/badge/版本-1.1.4-blue.svg)](https://github.com/chenqz-hub/cardiac-ai-cac/releases)
[![平台](https://img.shields.io/badge/平台-Windows%20%7C%20Linux-lightgrey.svg)](https://github.com/chenqz-hub/cardiac-ai-cac)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![许可](https://img.shields.io/badge/许可-专有软件-red.svg)](LICENSE)

基于深度学习的冠状动脉钙化自动评分系统。为医院部署优化，支持纯CPU运行。

**[English](README.md)** | **[快速开始](#快速开始)** | **[下载](#下载)** | **[文档](docs/)**

---

## 👥 作者

**项目负责人（Principal Investigator）：**
- **陈启稚医生** - 上海市第九人民医院心内科，上海交通大学医学院
  - GitHub: [@chenqz-hub](https://github.com/chenqz-hub)
  - 项目设计、监督和临床验证
  - 论文通讯作者

**技术开发：**
- 诸嵘 - 软件开发和算法实现
  - GitHub: [@zhurong2020](https://github.com/zhurong2020)

---

## ✨ 主要特点

- 🚀 **快速**: CPU环境下约5分钟/患者（8核以上）
- 🎯 **准确**: 99.5%成功率（195例验证）
- 💻 **CPU优化**: 无需GPU，医院标准电脑即可运行
- 📦 **离线支持**: 完整离线安装包，无需互联网
- 🌍 **双语界面**: 中文/英文界面切换
- 🔒 **企业级**: 授权管理、可扩展架构

---

## 🎯 快速开始

### 1. 下载

选择您的操作系统下载最新版本：

**Windows**（医院推荐）:
```
cardiac-ai-cac-windows-v1.1.4.zip (2.1 GB)
```

**Linux**:
```
cardiac-ai-cac-linux-v1.1.4.tar.gz (2.0 GB)
```

👉 [**前往下载页面**](https://github.com/chenqz-hub/cardiac-ai-cac/releases/latest)

### 2. 安装

**Windows**:
1. 解压ZIP文件
2. 双击运行 `install.bat`
3. 等待安装完成（约5-10分钟）

**Linux**:
```bash
tar -xzf cardiac-ai-cac-linux-v1.1.4.tar.gz
cd cardiac-ai-cac-linux-v1.1.4
./install.sh
```

### 3. 运行

**Windows**:
```
双击 cardiac-ai-cac.bat
```

**Linux**:
```bash
./cardiac-ai-cac.sh
```

📖 **详细说明**: 参见 [安装指南](INSTALL_CN.md)

---

## 📋 系统要求

### 最低配置
- **操作系统**: Windows 10/11 或 Linux (Ubuntu 20.04+)
- **处理器**: 4核
- **内存**: 8 GB
- **硬盘**: 2 GB 可用空间
- **Python**: 3.8 - 3.12

### 推荐配置
- **处理器**: 8核以上（Intel i7/i9、AMD Ryzen 7/9）
- **内存**: 16 GB
- **硬盘**: SSD固态硬盘

### GPU支持
GPU是**可选的**。本系统专门为医院CPU环境优化，无需GPU即可高效运行。

---

## 🏥 临床验证

在195例真实临床数据上测试：

| 指标 | 数值 |
|------|------|
| 成功率 | 99.5% (194/195) |
| 平均处理时间（CPU） | 约305秒 |
| 平均处理时间（8核以上） | 约60-120秒 |
| 假阳性 | 0 |
| 假阴性 | 1例 (0.5%) |

**临床意义**: 高准确率、低假阳性，适合医院常规使用。

---

## 📊 功能特性

### 核心功能
- ✅ 冠状动脉钙化自动检测
- ✅ AI钙化评分（等效Agatston评分）
- ✅ 批量处理支持
- ✅ 支持DICOM和NIfTI格式
- ✅ CSV结果输出，便于统计分析

### 高级功能
- ✅ 可扩展菜单系统
- ✅ 中英文界面切换
- ✅ 授权管理系统
- ✅ 硬件自动检测和优化
- ✅ 详细日志和调试功能
- ✅ 断点续传（中断后可继续）

---

## 📚 文档资源

- **[安装指南](INSTALL_CN.md)** - 详细安装步骤
- **[用户手册](docs/user-manual-cn.md)** - 使用说明
- **[常见问题](docs/faq-cn.md)** - 常见问题解答
- **[故障排除](docs/troubleshooting-cn.md)** - 问题诊断和解决
- **[更新日志](CHANGELOG.md)** - 版本更新历史

---

## 🔬 技术背景

本系统实现了基于AI的冠状动脉钙化评分，采用医学影像领域的先进技术：

- **模型架构**: SwinUNETR（Swin Transformer + U-Net）
- **深度学习框架**: MONAI + PyTorch
- **训练数据**: 临床CT扫描数据
- **验证**: 195例患者，99.5%成功率

---

## 📝 引用

如果您在研究中使用本软件，请引用：

```bibtex
@software{cardiac_ai_cac_2024,
  author = {陈, 启稚},
  title = {Cardiac AI-CAC: 冠状动脉钙化AI评分系统},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/chenqz-hub/cardiac-ai-cac}
}
```

**注**: 论文发表后，请引用相应的研究论文。

---

## 🚀 版本规划

### 当前版本: v1.1.4 ✅
- 核心钙化评分功能
- CPU性能优化
- 离线部署支持
- 可扩展菜单系统
- 多语言支持
- 授权管理

### 未来版本
- **v1.2.0**: 新增心脏分析模块
- **v1.3.0**: 增强可视化功能
- **v2.0.0**: 多模态分析整合

---

## 🤝 技术支持

### 获取帮助
- 📖 查看 [常见问题](docs/faq-cn.md)
- 🐛 报告问题: [GitHub Issues](https://github.com/chenqz-hub/cardiac-ai-cac/issues)
- 💬 讨论交流: [Discussions](https://github.com/chenqz-hub/cardiac-ai-cac/discussions)

### 商业支持
为医院和科研机构提供：
- 定制化部署服务
- 培训和技术支持
- 服务等级协议（SLA）
- 定制功能开发

请联系: chenqz73@hotmail.com

---

## 📖 使用场景

### 适用科室
- ✅ 心内科
- ✅ 放射科
- ✅ 体检中心
- ✅ 心血管外科

### 适用检查
- ✅ 冠脉CT血管造影（CTA）
- ✅ 胸部CT平扫
- ✅ 心脏CT检查

### 临床价值
- 🎯 心血管风险评估
- 🎯 冠心病筛查
- 🎯 治疗方案参考
- 🎯 随访对比评估

---

## 💡 使用流程

### 典型工作流程

```
1. 启动系统
   ↓
2. 选择模式（测试/试点/完整）
   ↓
3. 选择输入文件夹（DICOM文件）
   ↓
4. 系统自动处理
   ├─ 读取DICOM
   ├─ AI分析
   ├─ 计算钙化评分
   └─ 生成结果
   ↓
5. 查看结果（CSV文件）
   ├─ 患者ID
   ├─ 钙化积分
   ├─ 风险等级
   └─ 详细报告
```

### 处理时间参考

| 配置 | 单患者处理时间 | 100患者批量处理 |
|------|----------------|------------------|
| 4核CPU | ~10分钟 | ~16小时 |
| 8核CPU | ~5分钟 | ~8小时 |
| 16核CPU | ~2-3分钟 | ~4小时 |
| GPU (可选) | ~2分钟 | ~3小时 |

---

## 📄 授权与版权

**版权所有 © 2024 陈启稚。保留所有权利。**

本软件为专有软件，受著作权法保护。未经明确书面许可，禁止复制、分发或修改本软件。

**软件著作权登记**: [审批中/登记号：2024SR-XXXXXX]

### 使用条款

- **科研使用**: 请联系通讯作者进行学术合作
- **商业使用**: 可提供商业授权方案
- **医院部署**: 需要有效的授权协议

授权咨询请联系: chenqz73@hotmail.com

---

## 🙏 致谢

本项目由[资助来源，如有]支持。

基于以下开源项目：
- [PyTorch](https://pytorch.org/) - 深度学习框架
- [MONAI](https://monai.io/) - 医学影像AI工具包
- [SimpleITK](https://simpleitk.org/) - 医学图像处理
- [pydicom](https://pydicom.github.io/) - DICOM文件处理

---

## 📞 联系方式

- **通讯作者**: 陈启稚医生
- **邮箱**: chenqz73@hotmail.com
- **单位**: 上海市第九人民医院心内科
- **GitHub**: [@chenqz-hub](https://github.com/chenqz-hub)

---

## 💬 用户反馈

> "安装简单，处理速度快，准确率高，非常适合我们医院使用。"
> — 某三甲医院心内科

> "CPU模式运行稳定，不需要购买昂贵的GPU服务器。"
> — 某体检中心技术主任

> "离线安装包非常方便，解决了我们内网环境的部署问题。"
> — 某放射科主任

---

**项目负责人**: 陈启稚医生 | **版本**: 1.1.4 | **更新日期**: 2024年10月19日
