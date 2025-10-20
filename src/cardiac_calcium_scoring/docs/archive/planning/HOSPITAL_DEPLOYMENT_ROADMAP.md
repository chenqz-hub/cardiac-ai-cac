# NB10 Windows 医院部署实施路线图
# Hospital Deployment Implementation Roadmap

**文档版本**: 1.0.0
**创建日期**: 2025-10-14
**状态**: 待审核

---

## 📋 执行摘要 (Executive Summary)

本路线图整合了硬件自适应优化和授权管理两大系统的实施计划，为NB10 Windows应用的医院部署提供分阶段实施方案。

### 关键指标

| 项目 | 指标 |
|------|------|
| **总实施周期** | 10周 (2.5个月) |
| **最小可用版本** | 2周 (基础授权系统) |
| **推荐版本** | 6周 (授权 + 核心优化) |
| **完整版本** | 10周 (全功能) |
| **预期性能提升** | 20-40% (Standard硬件) |
| **目标硬件** | RTX 2060 6GB (医院主流配置) |

---

## 🎯 战略目标

### 1. 医院部署场景

**典型医院硬件环境** (基于市场调研):
- GPU: RTX 2060 / RTX 3060 (6-12GB)
- CPU: i5-10400 / i7-10700 (6-8核)
- RAM: 16-32GB
- 存储: 512GB SSD + 1TB HDD

**关键需求**:
1. **授权管理**: 防止未授权使用，支持试用和商业授权
2. **性能优化**: 在主流硬件上达到可接受速度 (15秒/患者 → 10秒/患者)
3. **稳定性**: 长时间运行不崩溃，GPU内存安全
4. **易用性**: 医生和技术员可轻松操作

### 2. 分阶段目标

#### Phase 1: 基础可用版本 (2周)
- ✅ 授权系统上线
- ✅ 支持试用和研究授权
- ✅ 基本离线验证
- 🎯 目标: 可控分发，收集医院试用反馈

#### Phase 2: 优化版本 (4周，累计6周)
- ✅ 硬件自动检测
- ✅ 核心性能优化 (DataLoader, pin_memory)
- ✅ 基础安全监控
- 🎯 目标: 20-30% 性能提升，适合医院日常使用

#### Phase 3: 专业版本 (4周，累计10周)
- ✅ 完整硬件自适应系统
- ✅ UI集成和智能建议
- ✅ 全面测试和文档
- 🎯 目标: 完整商业化产品

---

## 📅 实施时间线

```
Week 1-2:  授权管理系统 (Priority: 🔴 Critical)
           ├─ Week 1: 基础架构 + GitHub集成
           └─ Week 2: 验证逻辑 + CLI集成

Week 3-4:  硬件检测基础 (Priority: 🟡 High)
           ├─ Week 3: 硬件检测模块 + 配置引擎
           └─ Week 4: 核心优化 (DataLoader, pin_memory)

Week 5-6:  集成测试 + 文档 (Priority: 🟡 High)
           ├─ Week 5: 单元测试 + 集成测试
           └─ Week 6: 用户文档 + 部署指南

Week 7-8:  高级优化 (Priority: 🟢 Medium)
           ├─ Week 7: 智能缓存 + 安全监控
           └─ Week 8: 多GPU支持

Week 9-10: UI + 最终验证 (Priority: 🟢 Medium)
           ├─ Week 9: UI集成 + 设置页面
           └─ Week 10: 医院环境测试 + 发布
```

---

## 🔧 详细实施计划

### Phase 1: 授权管理系统 (Week 1-2)

#### Week 1: 基础架构搭建

**目标**: 建立GitHub私有仓库和本地授权基础设施

**任务清单**:
- [ ] 创建私有仓库 `nb10-licenses` (30分钟)
  ```bash
  gh repo create nb10-licenses --private
  cd nb10-licenses
  echo '{"authorized_users": []}' > authorized.json
  git add authorized.json && git commit -m "Initial commit"
  git push
  ```

- [ ] 实现授权码生成器 `tools/nb10_windows/utils/license_generator.py` (2小时)
  ```python
  def generate_license_code(license_type: str) -> dict:
      """生成授权码"""
      # 格式: NB10-{TYPE}-{RANDOM}
      # 返回: {code, hardware_id, expire_date, max_cases}
  ```

- [ ] 实现本地验证器 `tools/nb10_windows/core/license_validator.py` (4小时)
  ```python
  class LicenseValidator:
      def validate_local(self) -> bool:
          """本地验证逻辑"""

      def validate_online(self) -> bool:
          """在线验证逻辑"""

      def check_expiry(self) -> bool:
          """检查过期时间"""
  ```

- [ ] 创建本地授权文件结构 (1小时)
  ```
  ~/.nb10/
  ├── license.json      # 授权信息
  ├── cache.json        # 在线验证缓存(24h)
  └── usage.json        # 使用统计
  ```

**交付物**:
- ✅ GitHub私有仓库 `nb10-licenses`
- ✅ 授权码生成工具
- ✅ 本地验证模块
- ✅ 单元测试 (覆盖率 >80%)

**验收标准**:
```bash
# 测试授权码生成
python utils/license_generator.py --type trial

# 测试本地验证
python -m pytest tests/test_license_validator.py -v

# 输出示例:
# ✅ Trial license generated: NB10-TRIAL-8F3A2D1C4B5E
# ✅ Valid until: 2025-11-14
# ✅ Max cases: 100
```

---

#### Week 2: CLI集成和在线验证

**目标**: 将授权系统集成到现有CLI工具

**任务清单**:
- [ ] 修改 `cli/run_nb10.py` 添加授权检查 (3小时)
  ```python
  # 在main()开始处添加
  from core.license_validator import LicenseValidator

  validator = LicenseValidator()
  if not validator.validate():
      print("❌ 授权验证失败，请联系管理员")
      sys.exit(1)
  ```

- [ ] 实现在线验证逻辑 (4小时)
  ```python
  def validate_online(self) -> bool:
      """从GitHub拉取authorized.json验证"""
      try:
          response = requests.get(
              f"https://raw.githubusercontent.com/user/nb10-licenses/main/authorized.json",
              headers={'Authorization': f'token {GITHUB_TOKEN}'}
          )
          # 验证逻辑
      except:
          # 降级到本地缓存
          return self.validate_from_cache()
  ```

- [ ] 添加使用统计功能 (2小时)
  ```python
  def track_usage(patient_id: str):
      """记录使用情况"""
      usage = load_usage_data()
      usage['total_cases'] += 1
      usage['cases'].append({
          'patient_id': patient_id,
          'timestamp': datetime.now().isoformat()
      })
      save_usage_data(usage)
  ```

- [ ] 创建授权管理命令 (2小时)
  ```bash
  python cli/run_nb10.py --license activate NB10-TRIAL-8F3A2D1C
  python cli/run_nb10.py --license status
  python cli/run_nb10.py --license info
  ```

**交付物**:
- ✅ CLI授权集成
- ✅ 在线/离线验证
- ✅ 使用统计功能
- ✅ 用户文档 `docs/LICENSE_USER_GUIDE.md`

**验收标准**:
```bash
# 测试完整流程
python cli/run_nb10.py --license activate NB10-TRIAL-XXX
# ✅ License activated successfully
# ✅ Type: Trial
# ✅ Valid until: 2025-11-14
# ✅ Remaining cases: 100/100

python cli/run_nb10.py --config config.yaml --mode pilot --pilot-limit 1
# ✅ [1/1] Processing patient_001... SUCCESS (12.5s)
# ✅ Remaining cases: 99/100
```

**风险控制**:
- 🔒 GitHub token 安全存储 (使用环境变量或加密配置)
- 🔒 离线验证降级机制 (24小时缓存)
- 🔒 硬件ID绑定防止授权转移

---

### Phase 2: 硬件检测与核心优化 (Week 3-4)

#### Week 3: 硬件检测模块

**目标**: 实现自动硬件检测和配置文件生成

**任务清单**:
- [ ] 创建硬件检测器 `core/hardware_profiler.py` (4小时)
  ```python
  class HardwareProfiler:
      def detect_gpu(self) -> dict:
          """检测GPU型号、VRAM、CUDA版本"""

      def detect_cpu(self) -> dict:
          """检测CPU核心数、频率"""

      def detect_memory(self) -> dict:
          """检测系统内存"""

      def classify_tier(self) -> str:
          """分类硬件等级: minimal/standard/performance/professional/enterprise"""
  ```

- [ ] 实现配置生成引擎 `core/config_generator.py` (3小时)
  ```python
  def generate_optimal_config(hardware_tier: str) -> dict:
      """根据硬件等级生成最优配置"""
      configs = {
          'minimal': {
              'num_workers': 0,
              'pin_memory': False,
              'slice_batch_size': 2,
              'prefetch_factor': 1
          },
          'standard': {
              'num_workers': 4,
              'pin_memory': True,
              'slice_batch_size': 4,
              'prefetch_factor': 2
          },
          # ... 其他等级
      }
      return configs[hardware_tier]
  ```

- [ ] 添加首次启动硬件检测 (2小时)
  ```python
  # 在run_nb10.py main()开始处
  if not os.path.exists(HARDWARE_CONFIG_FILE):
      print("🔍 首次运行，正在检测硬件配置...")
      profiler = HardwareProfiler()
      hardware_info = profiler.detect_all()
      tier = profiler.classify_tier()

      print(f"✅ 检测到硬件等级: {tier}")
      print(f"   GPU: {hardware_info['gpu']['name']} ({hardware_info['gpu']['vram']}GB)")
      print(f"   CPU: {hardware_info['cpu']['cores']}核")

      # 生成并保存配置
      optimal_config = generate_optimal_config(tier)
      save_hardware_config(optimal_config)
  ```

**交付物**:
- ✅ 硬件检测模块
- ✅ 配置生成引擎
- ✅ 硬件信息报告
- ✅ 单元测试

**验收标准**:
```bash
# 首次运行输出
python cli/run_nb10.py --config config.yaml --mode pilot --pilot-limit 1

# 输出:
# 🔍 首次运行，正在检测硬件配置...
# ✅ 检测到硬件等级: standard
#    GPU: NVIDIA GeForce RTX 2060 (6GB VRAM)
#    CPU: Intel i5-10400 (6核)
#    RAM: 16GB
# ✅ 已生成优化配置: ~/.nb10/hardware_config.json
#
# 建议配置:
#   - num_workers: 4 (CPU核心优化)
#   - pin_memory: True (启用GPU内存固定)
#   - slice_batch_size: 4 (适配6GB VRAM)
#
# 预期性能提升: 25-30%
```

---

#### Week 4: 核心性能优化

**目标**: 应用硬件配置到数据加载和推理流程

**任务清单**:
- [ ] 修改 `core/ai_cac_inference_lib.py` 使用动态配置 (3小时)
  ```python
  # Line 76-77 (原代码)
  dataloader = DataLoader(dataset, batch_size=1, shuffle=False,
                         num_workers=0,        # ❌ 硬编码
                         pin_memory=False)     # ❌ 硬编码

  # 修改为:
  from .config_manager import ConfigManager
  config = ConfigManager.load_hardware_config()

  dataloader = DataLoader(
      dataset,
      batch_size=1,
      shuffle=False,
      num_workers=config['num_workers'],           # ✅ 动态配置
      pin_memory=config['pin_memory'],             # ✅ 动态配置
      prefetch_factor=config.get('prefetch_factor', 2) if config['num_workers'] > 0 else None
  )
  ```

- [ ] 实现智能缓存策略 (4小时)
  ```python
  class SmartCacheManager:
      def should_clear_cache(self, vram_usage: float) -> bool:
          """根据VRAM使用率决定是否清理缓存"""
          # Minimal: >80% 清理
          # Standard: >85% 清理
          # Performance: >90% 清理

      def clear_cache_adaptive(self):
          """自适应缓存清理"""
          if self.should_clear_cache(get_vram_usage()):
              torch.cuda.empty_cache()
  ```

- [ ] 添加性能监控 (2小时)
  ```python
  class PerformanceMonitor:
      def track_inference_time(self, patient_id: str, time_seconds: float):
          """记录推理时间"""

      def get_average_speed(self) -> float:
          """获取平均速度"""

      def compare_baseline(self) -> dict:
          """与基线性能比较"""
          # 基线: 15秒/患者 (num_workers=0, pin_memory=False)
          # 返回: {'baseline': 15.0, 'current': 11.2, 'improvement': '25.3%'}
  ```

**交付物**:
- ✅ 动态配置集成
- ✅ 智能缓存管理
- ✅ 性能监控模块
- ✅ 性能基准测试

**验收标准**:
```bash
# 运行性能基准测试
python tests/benchmark_performance.py --mode comparison

# 输出:
# 📊 性能基准测试 (RTX 2060, 6GB VRAM)
#
# 基线配置 (num_workers=0, pin_memory=False):
#   ⏱️  平均速度: 15.3秒/患者
#   💾 VRAM峰值: 4.2GB
#
# 优化配置 (num_workers=4, pin_memory=True):
#   ⏱️  平均速度: 11.2秒/患者 ⬆️ 26.8% faster
#   💾 VRAM峰值: 4.5GB
#
# ✅ 性能提升达标 (目标: >20%)
```

---

### Phase 3: 集成测试与文档 (Week 5-6)

#### Week 5: 全面测试

**目标**: 确保授权系统和优化系统协同工作

**任务清单**:
- [ ] 单元测试覆盖 (2天)
  ```bash
  tests/
  ├── test_license_validator.py      # 授权验证测试
  ├── test_hardware_profiler.py      # 硬件检测测试
  ├── test_config_generator.py       # 配置生成测试
  ├── test_performance_monitor.py    # 性能监控测试
  └── test_integration.py            # 集成测试
  ```

- [ ] 集成测试场景 (2天)
  ```python
  # 场景1: 新用户首次使用 (Trial授权)
  def test_new_user_trial_license():
      # 1. 激活Trial授权
      # 2. 首次运行硬件检测
      # 3. 处理1个患者
      # 4. 验证授权扣减 (99/100)
      # 5. 验证性能提升

  # 场景2: 授权过期处理
  def test_license_expiry():
      # 1. 模拟授权过期
      # 2. 尝试运行 -> 应该拒绝
      # 3. 更新授权
      # 4. 验证恢复正常

  # 场景3: 离线使用
  def test_offline_validation():
      # 1. 在线验证并缓存
      # 2. 断网
      # 3. 验证仍可使用 (24小时内)
      # 4. 超过24小时 -> 提示需在线验证
  ```

- [ ] 医院环境模拟测试 (1天)
  ```bash
  # 模拟不同硬件环境
  docker run --gpus '"device=0"' \
    -e CUDA_VISIBLE_DEVICES=0 \
    -v $(pwd):/workspace \
    nb10-test:rtx2060 \
    python cli/run_nb10.py --config config.yaml --mode full
  ```

**交付物**:
- ✅ 单元测试套件 (覆盖率 >85%)
- ✅ 集成测试套件
- ✅ 性能回归测试
- ✅ 硬件兼容性测试报告

---

#### Week 6: 用户文档和部署指南

**目标**: 完善文档，支持医院IT部门独立部署

**任务清单**:
- [ ] 用户手册 `docs/USER_MANUAL.md` (2天)
  ```markdown
  # NB10 Windows 用户手册

  ## 1. 系统要求
  - 最低配置: GTX 1060 3GB / 8GB RAM
  - 推荐配置: RTX 2060 6GB / 16GB RAM
  - 最佳配置: RTX 3060 12GB / 32GB RAM

  ## 2. 安装步骤
  1. Python 3.10环境准备
  2. 依赖安装
  3. 模型下载
  4. 授权激活

  ## 3. 使用指南
  - 试用版使用 (100例限制)
  - 数据准备 (DICOM格式要求)
  - 运行分析
  - 结果解读

  ## 4. 常见问题
  - GPU内存不足怎么办?
  - 授权过期如何续期?
  - 性能优化建议
  ```

- [ ] IT部署指南 `docs/IT_DEPLOYMENT_GUIDE.md` (1天)
  ```markdown
  # 医院IT部署指南

  ## 环境准备检查清单
  - [ ] GPU驱动版本 ≥ 520.61.05
  - [ ] CUDA 11.8 已安装
  - [ ] Python 3.10 已安装
  - [ ] 网络策略允许访问 raw.githubusercontent.com (在线验证)

  ## 部署步骤
  1. 克隆代码仓库
  2. 创建虚拟环境
  3. 安装依赖
  4. 下载AI-CAC模型
  5. 申请并激活授权
  6. 硬件检测和配置
  7. 试运行验证

  ## 授权管理
  - 试用版申请流程
  - 研究版申请流程 (需要伦理审批证明)
  - 商业版采购流程

  ## 故障排查
  - GPU不可用 -> 检查驱动和CUDA
  - 授权验证失败 -> 检查网络或使用离线缓存
  - 性能不达预期 -> 查看硬件配置建议
  ```

- [ ] 授权申请模板 (1天)
  ```markdown
  # 研究版授权申请表

  申请单位: __________
  联系人: __________
  邮箱: __________

  研究项目信息:
  - 项目名称: __________
  - 伦理批号: __________
  - 预计样本量: __________
  - 研究期限: __________

  附件:
  - [ ] 伦理审批文件扫描件
  - [ ] 单位证明
  - [ ] 硬件ID (运行 `python cli/run_nb10.py --license hwid` 获取)
  ```

**交付物**:
- ✅ 用户手册
- ✅ IT部署指南
- ✅ 授权申请流程文档
- ✅ FAQ文档

---

### Phase 4: 高级优化 (Week 7-8) - 可选

#### Week 7: 智能监控和多GPU支持

**目标**: 增强系统稳定性和高端硬件支持

**任务清单**:
- [ ] GPU温度监控 (1天)
  ```python
  class GPUMonitor:
      def check_temperature(self) -> float:
          """检查GPU温度"""
          temp = pynvml.nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
          if temp > 80:
              warnings.warn(f"⚠️ GPU温度过高: {temp}°C")
          return temp
  ```

- [ ] OOM保护机制 (2天)
  ```python
  class OOMProtector:
      def predict_oom_risk(self, batch_size: int) -> bool:
          """预测是否有OOM风险"""
          current_usage = get_gpu_memory_usage()
          estimated_usage = current_usage + estimate_batch_memory(batch_size)
          return estimated_usage > 0.9 * total_vram

      def adaptive_batch_size(self, initial_size: int) -> int:
          """自适应调整batch_size"""
          while self.predict_oom_risk(initial_size):
              initial_size = max(1, initial_size // 2)
          return initial_size
  ```

- [ ] 多GPU支持 (2天)
  ```python
  # 仅针对 Enterprise 等级
  if hardware_tier == 'enterprise' and num_gpus > 1:
      model = nn.DataParallel(model, device_ids=list(range(num_gpus)))
  ```

---

#### Week 8: 性能优化收尾

**任务清单**:
- [ ] 模型预热机制 (1天)
- [ ] 批量处理优化 (2天)
- [ ] 性能分析报告 (2天)

---

### Phase 5: UI集成与最终验证 (Week 9-10) - 可选

#### Week 9: GUI集成

**目标**: 为非技术用户提供图形界面

**任务清单**:
- [ ] 创建设置页面 (2天)
  ```python
  # 使用 tkinter 或 PyQt5
  class SettingsWindow:
      def show_hardware_info(self):
          """显示硬件信息和优化建议"""

      def show_license_status(self):
          """显示授权状态"""

      def manual_config_override(self):
          """允许手动调整配置"""
  ```

- [ ] 添加进度条和日志查看器 (1天)
- [ ] 集成到现有CLI (1天)

---

#### Week 10: 医院环境最终验证

**目标**: 在真实医院环境测试

**任务清单**:
- [ ] 医院A试点测试 (RTX 2060, 3天)
- [ ] 收集反馈并修复问题 (2天)
- [ ] 发布 v1.0.0

---

## 🎯 优先级和快速路径

### 方案A: 最小可用版本 (2周)

**适用场景**: 快速启动医院试用，收集反馈

**包含内容**:
- ✅ 授权系统 (Week 1-2)
- ✅ 基础文档

**不包含**:
- ❌ 硬件优化 (仍使用默认配置)
- ❌ 性能监控

**优点**:
- 快速上线 (2周)
- 控制授权分发
- 收集真实使用数据

**缺点**:
- 性能未优化 (仍是15秒/患者)
- 用户体验一般

---

### 方案B: 推荐版本 (6周) ⭐

**适用场景**: 平衡功能和时间，适合医院正式使用

**包含内容**:
- ✅ 授权系统 (Week 1-2)
- ✅ 硬件检测和核心优化 (Week 3-4)
- ✅ 测试和文档 (Week 5-6)

**不包含**:
- ❌ 高级监控
- ❌ 多GPU支持
- ❌ GUI界面

**优点**:
- 性能提升 25-30%
- 稳定可靠
- 文档完善
- 适合医院日常使用

**缺点**:
- 需要6周开发时间
- 缺少高级功能

**推荐理由**:
此方案提供了授权控制和显著性能提升，同时开发周期可控。对于医院部署来说，6周是可接受的时间，且能提供专业级的用户体验。

---

### 方案C: 完整版本 (10周)

**适用场景**: 商业化产品，支持高端硬件

**包含内容**:
- ✅ 所有Phase 1-5功能

**优点**:
- 完整功能
- 支持多GPU
- GUI界面
- 智能监控

**缺点**:
- 开发周期长 (2.5个月)
- 可能over-engineering (医院未必需要所有功能)

---

## 📊 资源分配

### 人力需求

| 角色 | 方案A (2周) | 方案B (6周) | 方案C (10周) |
|------|-------------|-------------|--------------|
| **后端开发** | 1人 × 2周 | 1人 × 6周 | 1人 × 10周 |
| **测试工程师** | - | 0.5人 × 2周 | 1人 × 4周 |
| **文档工程师** | - | 0.5人 × 2周 | 0.5人 × 4周 |
| **总工作量** | 2人周 | 8人周 | 16人周 |

### 技术栈

**必需**:
- Python 3.10
- PyTorch 2.1.0
- MONAI 1.3.2
- pydicom
- requests (GitHub API)

**可选** (方案C):
- pynvml (GPU监控)
- PyQt5 (GUI)
- pytest-xdist (并行测试)

---

## 🚀 里程碑和验收标准

### Milestone 1: 授权系统上线 (Week 2)

**验收标准**:
```bash
# 1. 激活试用授权
python cli/run_nb10.py --license activate NB10-TRIAL-XXX
# ✅ License activated

# 2. 查看授权状态
python cli/run_nb10.py --license status
# ✅ Type: Trial
# ✅ Remaining: 100/100 cases
# ✅ Valid until: 2025-11-14

# 3. 处理一个患者
python cli/run_nb10.py --config config.yaml --mode pilot --pilot-limit 1
# ✅ [1/1] Processing... SUCCESS
# ✅ Remaining: 99/100 cases

# 4. 授权用尽测试
# (处理100个患者后)
python cli/run_nb10.py --config config.yaml --mode pilot --pilot-limit 1
# ❌ License quota exceeded. Please upgrade to Research or Commercial license.
```

---

### Milestone 2: 性能优化验证 (Week 4)

**验收标准**:
```bash
# 在RTX 2060 (6GB) 环境测试
python tests/benchmark_performance.py

# 期望输出:
# 📊 基线性能: 15.3秒/患者
# 📊 优化性能: 11.2秒/患者
# ✅ 性能提升: 26.8% (目标: >20%)
# ✅ VRAM峰值: 4.5GB (安全范围: <5.5GB)
# ✅ GPU温度: 72°C (安全)
```

---

### Milestone 3: 医院试点验证 (Week 6 或 Week 10)

**验收标准**:
- ✅ 连续运行 100 个患者无崩溃
- ✅ 平均速度 <12 秒/患者 (RTX 2060)
- ✅ 授权系统无误报
- ✅ 医生反馈可用性评分 ≥4.0/5.0

---

## 🔄 迭代和维护

### 版本规划

**v1.0.0** (Week 2 或 Week 6):
- 授权系统
- (可选) 硬件优化

**v1.1.0** (Week 10):
- 高级监控
- 多GPU支持

**v1.2.0** (未来):
- GUI界面
- 云端结果同步

### 维护计划

**月度维护**:
- 授权数据库更新
- 性能监控报告
- Bug修复

**季度更新**:
- 新硬件适配 (新GPU型号)
- 性能优化
- 功能增强

---

## 📝 决策建议

### 给用户的建议

**如果目标是快速医院试用** (收集反馈):
👉 **选择方案A** (2周)
- 专注授权系统
- 快速上线收集数据
- 后续迭代优化

**如果目标是正式部署使用** (推荐):
👉 **选择方案B** (6周) ⭐
- 平衡功能和时间
- 性能提升显著 (25-30%)
- 文档完善易部署
- 适合医院日常工作流程

**如果目标是商业化产品**:
👉 **选择方案C** (10周)
- 完整功能
- 支持高端硬件
- GUI界面

### 下一步行动

**立即行动** (无论选择哪个方案):
1. 创建GitHub私有仓库 `nb10-licenses`
2. 设置GitHub Personal Access Token (用于在线验证)
3. 准备试用授权申请表模板

**Week 1 启动检查清单**:
- [ ] GitHub仓库已创建
- [ ] 开发环境准备完毕
- [ ] 确认硬件测试环境可用 (RTX 2060 或类似)
- [ ] 团队成员角色分配明确

---

## 📞 联系和支持

**技术支持**:
- 项目负责人: Chen Doctor Team
- 技术文档: `tools/nb10_windows/docs/`
- Issue追踪: GitHub Issues

**授权咨询**:
- 邮箱: [待填写]
- 试用申请: [待填写表单链接]

---

**文档结束**

最后更新: 2025-10-14
版本: 1.0.0
状态: 待用户审核和选择实施方案
