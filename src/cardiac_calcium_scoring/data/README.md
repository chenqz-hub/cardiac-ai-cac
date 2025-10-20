# Data Directory

本目录用于存放DICOM原始数据或指向实际数据位置的配置。

---

## 📂 推荐目录结构

```
data/
├── dicom_original/              # DICOM原始数据
│   ├── chd/                     # 冠心病组
│   │   ├── patient_001/
│   │   │   ├── IM-0001.dcm
│   │   │   ├── IM-0002.dcm
│   │   │   └── ...
│   │   ├── patient_002/
│   │   └── ...
│   └── normal/                  # 正常对照组
│       ├── patient_101/
│       ├── patient_102/
│       └── ...
│
└── cache/                       # 扫描缓存（自动生成）
    ├── scan_cache.json          # DICOM扫描结果缓存
    └── ...
```

---

## 🔧 配置方式

### 方式1：直接放置数据（适合数据量小）

将DICOM数据直接复制到`data/dicom_original/`目录。

**优点**：
- 简单直接
- 工具和数据在一起，便于打包

**缺点**：
- 占用空间大（~50GB）
- 不适合多项目共享数据

### 方式2：配置外部路径（推荐）

在`config/config.yaml`中指定实际数据位置：

```yaml
paths:
  data_dir: "D:/Medical_Data/cardiac_dicom"
  # 或网络共享路径
  # data_dir: "//ServerName/MedicalData/DICOM"
```

**优点**：
- 节省工具目录空间
- 数据可以在多个项目间共享
- 支持网络存储

**缺点**：
- 需要手动配置路径
- 数据和工具分离

---

## 📋 数据要求

### DICOM文件要求

1. **目录结构**：每个患者一个独立文件夹
2. **文件格式**：`.dcm`或无扩展名的DICOM文件
3. **序列要求**：
   - 层厚：4-6mm（推荐5mm）
   - 方向：轴位（Axial）
   - 扫描范围：包含心脏区域
4. **元数据**：必须包含以下DICOM标签
   - `SeriesInstanceUID`：序列唯一标识
   - `SliceThickness`：层厚信息
   - `ImagePositionPatient`：图像位置

### 数据分组

- **chd/**：冠心病患者（通过冠脉造影确诊）
- **normal/**：正常对照组（排除冠心病）

患者ID命名规则：
- 可以使用任何唯一标识符
- 支持中文（但建议使用英文和数字）
- 示例：`dicom_7084967.zip_3827998`、`patient_001`

---

## 🚀 数据准备脚本

### 1. 检查数据完整性

```bash
python scripts/validate_data.py --data-dir data/dicom_original
```

检查内容：
- 目录结构是否正确
- DICOM文件是否有效
- 必要的元数据是否存在
- 层厚是否符合要求

### 2. 扫描数据

```bash
python cli/run_nb10.py --scan-only
```

生成缓存文件：`data/cache/scan_cache.json`

包含内容：
- 患者列表
- 序列信息
- 层厚统计
- 切片数量

### 3. 查看数据统计

```bash
python scripts/data_statistics.py --cache data/cache/scan_cache.json
```

输出信息：
- 总患者数
- CHD vs Normal分组统计
- 层厚分布
- 切片数分布

---

## 📊 示例数据

### 小样本测试数据

工具提供了5-10例示例数据用于测试：

位置：`examples/sample_data/`

用途：
- 验证工具安装正确
- 测试处理流程
- 学习使用方法
- 演示结果格式

运行示例：
```bash
# 使用示例数据运行
python cli/run_nb10.py --data-dir examples/sample_data --mode pilot
```

---

## ⚠️ 注意事项

### 数据安全

1. **患者隐私**：
   - DICOM数据包含患者信息
   - 确保符合医院伦理审批
   - 不要上传到公共网络

2. **数据备份**：
   - 处理前务必备份原始数据
   - 建议使用多重备份策略
   - 定期验证备份完整性

3. **访问控制**：
   - 限制数据目录访问权限
   - 不要共享包含数据的工具包
   - 使用加密存储（如BitLocker）

### 数据质量

1. **层厚检查**：
   - AI-CAC模型要求2.5-5mm层厚
   - 太薄（<2mm）或太厚（>7mm）会影响准确性
   - 使用`--scan-only`先检查层厚分布

2. **序列选择**：
   - 优先选择5mm层厚序列
   - 避免混合不同层厚
   - 确认序列为非门控平扫

3. **图像质量**：
   - 避免运动伪影严重的图像
   - 确保心脏区域完整覆盖
   - 检查是否有金属伪影

---

## 📖 相关文档

- [使用手册](../docs/user_manual.md) - 完整使用流程
- [配置说明](../docs/configuration.md) - 路径配置详解
- [常见问题](../docs/faq.md) - 数据相关FAQ

---

**最后更新**: 2025-10-14
