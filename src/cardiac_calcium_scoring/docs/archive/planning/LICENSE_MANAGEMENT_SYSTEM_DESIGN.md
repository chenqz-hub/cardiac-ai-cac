# NB10 授权管理系统 - 技术设计文档

**版本**: 1.0.0
**创建日期**: 2025-10-14
**文档状态**: 设计提案 (Proposal)
**目标版本**: NB10 v2.0.0+

---

## 📋 执行摘要

本文档描述了NB10 AI-CAC软件的**授权管理与知识产权保护方案**，旨在：

1. **保护核心知识产权** - 防止未授权的商业使用
2. **简化授权管理** - 无需VPS，基于GitHub私有仓库
3. **平衡学术传播与商业保护** - 学术免费 + 商业收费双轨制
4. **支持论文与专利** - 预留知识产权申报空间

**核心价值**：
- 初期推广阶段0成本、快速部署
- 灵活生成试用/商业激活码
- 支持离线激活（适配医院内网环境）
- 为未来商业化预留升级路径

---

## 🎯 设计目标

### 业务目标

1. **知识产权保护**
   - 防止未授权的商业使用
   - 追踪授权医院和使用范围
   - 为论文发表和专利申请提供支持

2. **灵活授权管理**
   - 快速生成试用激活码（用于医院评估）
   - 支持商业授权（年费或永久）
   - 可随时撤销或延期

3. **用户体验优先**
   - 激活流程简单（输入激活码即可）
   - 支持离线环境（医院内网）
   - 不影响软件性能

### 技术约束

- **无VPS要求** - 利用GitHub作为"授权数据库"
- **轻量级实现** - 1-2天开发周期
- **跨平台兼容** - Windows/Linux都支持
- **安全性适度** - 初期重点是管理便利性，而非强加密

---

## 🏗️ 系统架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    授权管理生态系统                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐       ┌──────────────────┐              │
│  │  你的本地电脑     │       │  GitHub私有仓库   │              │
│  │                  │       │                  │              │
│  │ generate_license │  →    │ authorized.json  │              │
│  │     .py          │ push  │                  │              │
│  │ (生成激活码)      │       │ (存储授权列表)    │              │
│  └──────────────────┘       └─────────┬────────┘              │
│                                       │                        │
│                                       │ HTTPS GET              │
│                                       │ (GitHub Raw URL)       │
│                                       ↓                        │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              医院客户端 (NB10 Software)                   │ │
│  │                                                           │ │
│  │  启动 → 检查激活 → 从GitHub获取authorized.json → 验证    │ │
│  │           ↓                                               │ │
│  │        已激活？                                           │ │
│  │       ┌──┴──┐                                             │ │
│  │      是      否                                            │ │
│  │       ↓      ↓                                             │ │
│  │    正常运行  显示激活界面 → 用户输入激活码 → 本地保存      │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 核心组件

1. **激活码生成器** (`scripts/generate_license.py`)
   - 本地运行，不分发给用户
   - 生成激活码并更新 `authorized.json`
   - 支持试用/商业等多种类型

2. **授权数据存储** (GitHub私有仓库)
   - 文件：`authorized.json`
   - 存储所有有效激活码
   - 支持在线/离线访问

3. **激活码验证器** (`core/license_validator.py`)
   - 集成到NB10客户端
   - 启动时验证激活状态
   - 支持在线验证 + 离线缓存

4. **启动流程集成** (`cli/run_nb10.py`)
   - 启动前检查授权
   - 未激活时显示激活界面
   - 激活后正常运行

---

## 📝 激活码设计

### 激活码格式

```
格式: NB10-{TYPE}-{RANDOM}

示例:
- NB10-TRIAL-8F3A2D1C4B5E        (试用版)
- NB10-COMME-A1B2C3D4E5F6        (商业版)
- NB10-RESEA-1A2B3C4D5E6F        (科研版)
```

**组成部分**：
- `NB10`: 产品标识
- `TYPE`: 许可类型（5字符）
  - `TRIAL`: 试用版
  - `COMME`: 商业版 (Commercial)
  - `RESEA`: 科研版 (Research)
- `RANDOM`: 12位随机十六进制（安全性）

### 授权类型定义

| 类型 | 代码 | 有效期 | 病例数限制 | 适用场景 | 价格 |
|------|------|--------|-----------|---------|------|
| **试用版** | TRIAL | 30天 | 100例 | 医院评估测试 | 免费 |
| **科研版** | RESEA | 1年 | 无限制 | 学术研究、论文发表 | 免费（需证明） |
| **商业版** | COMME | 1年 | 无限制 | 临床诊疗使用 | ¥50,000/年 |
| **永久版** | PERMA | 永久 | 无限制 | 一次性购买 | ¥200,000 |

---

## 🔧 技术实现

### 1. 激活码生成脚本

**文件位置**: `scripts/generate_license.py`

**功能**：
- 生成符合规范的激活码
- 更新 `authorized.json` 文件
- 显示激活码信息（供发送给医院）

**完整代码**：

```python
#!/usr/bin/env python3
"""
NB10 License Generator - 激活码生成工具

此脚本用于生成NB10软件的激活码，仅供内部使用，不分发给用户。

Usage:
    python scripts/generate_license.py

Author: 陈医生团队
License: Proprietary (内部工具)
"""

import secrets
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# 授权类型配置
LICENSE_TYPES = {
    "trial": {
        "code": "TRIAL",
        "name": "试用版",
        "default_days": 30,
        "default_max_cases": 100
    },
    "research": {
        "code": "RESEA",
        "name": "科研版",
        "default_days": 365,
        "default_max_cases": -1  # -1表示无限制
    },
    "commercial": {
        "code": "COMME",
        "name": "商业版",
        "default_days": 365,
        "default_max_cases": -1
    },
    "permanent": {
        "code": "PERMA",
        "name": "永久版",
        "default_days": 36500,  # 100年
        "default_max_cases": -1
    }
}


class LicenseGenerator:
    """激活码生成器"""

    def __init__(self, authorized_file: str = "authorized.json"):
        """
        初始化生成器

        Args:
            authorized_file: 授权文件路径
        """
        self.authorized_file = Path(authorized_file)
        self.licenses = self.load_licenses()

    def load_licenses(self) -> List[Dict]:
        """加载现有授权数据"""
        if self.authorized_file.exists():
            with open(self.authorized_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("licenses", [])
        return []

    def save_licenses(self):
        """保存授权数据到文件"""
        data = {
            "version": "1.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "licenses": self.licenses
        }

        with open(self.authorized_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def generate_code(self, license_type: str) -> str:
        """
        生成激活码

        Args:
            license_type: 许可类型 (trial/research/commercial/permanent)

        Returns:
            激活码字符串
        """
        type_code = LICENSE_TYPES[license_type]["code"]
        random_part = secrets.token_hex(6).upper()  # 12位随机十六进制
        return f"NB10-{type_code}-{random_part}"

    def create_license(
        self,
        hospital_name: str,
        license_type: str = "trial",
        days: int = None,
        max_cases: int = None,
        notes: str = ""
    ) -> Dict:
        """
        创建许可证

        Args:
            hospital_name: 医院名称
            license_type: 许可类型
            days: 有效天数（None则使用默认值）
            max_cases: 最大病例数（None则使用默认值，-1表示无限制）
            notes: 备注信息

        Returns:
            许可证数据字典
        """
        if license_type not in LICENSE_TYPES:
            raise ValueError(f"无效的许可类型: {license_type}")

        # 使用默认值
        config = LICENSE_TYPES[license_type]
        if days is None:
            days = config["default_days"]
        if max_cases is None:
            max_cases = config["default_max_cases"]

        # 生成激活码
        code = self.generate_code(license_type)

        # 计算过期日期
        expire_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

        # 构建许可证数据
        license_data = {
            "code": code,
            "type": license_type,
            "hospital": hospital_name,
            "expire": expire_date,
            "max_cases": max_cases,
            "issued_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "active",
            "notes": notes,
            "usage_count": 0  # 未来可用于统计（需要客户端回传）
        }

        # 添加到列表
        self.licenses.append(license_data)

        # 保存到文件
        self.save_licenses()

        # 显示信息
        self.print_license_info(license_data)

        return license_data

    def print_license_info(self, license_data: Dict):
        """打印激活码信息"""
        config = LICENSE_TYPES[license_data["type"]]

        print("=" * 70)
        print("✓ 新激活码生成成功！")
        print("=" * 70)
        print(f"激活码:      {license_data['code']}")
        print(f"医院名称:    {license_data['hospital']}")
        print(f"许可类型:    {config['name']}")
        print(f"有效期至:    {license_data['expire']}")

        if license_data['max_cases'] == -1:
            print(f"病例数限制:  无限制")
        else:
            print(f"病例数限制:  {license_data['max_cases']} 例")

        if license_data['notes']:
            print(f"备注:        {license_data['notes']}")

        print("=" * 70)
        print()

    def list_licenses(self, status: str = None):
        """
        列出所有激活码

        Args:
            status: 过滤状态 (active/expired/revoked/None表示全部)
        """
        print("=" * 70)
        print("当前授权列表")
        print("=" * 70)
        print()

        filtered = self.licenses
        if status:
            filtered = [lic for lic in self.licenses if lic["status"] == status]

        if not filtered:
            print("（暂无授权记录）")
            return

        for i, lic in enumerate(filtered, 1):
            print(f"[{i}] {lic['code']}")
            print(f"    医院: {lic['hospital']}")
            print(f"    类型: {LICENSE_TYPES[lic['type']]['name']}")
            print(f"    有效期至: {lic['expire']}")
            print(f"    状态: {lic['status']}")
            print()

    def revoke_license(self, code: str) -> bool:
        """
        撤销激活码

        Args:
            code: 要撤销的激活码

        Returns:
            是否成功撤销
        """
        for lic in self.licenses:
            if lic["code"] == code:
                lic["status"] = "revoked"
                lic["revoked_date"] = datetime.now().strftime("%Y-%m-%d")
                self.save_licenses()
                print(f"✓ 激活码 {code} 已撤销")
                return True

        print(f"✗ 未找到激活码: {code}")
        return False


def interactive_mode():
    """交互式生成激活码"""
    print("=" * 70)
    print("NB10 激活码生成工具")
    print("=" * 70)
    print()

    generator = LicenseGenerator()

    while True:
        print("\n请选择操作:")
        print("  [1] 生成新激活码")
        print("  [2] 查看所有激活码")
        print("  [3] 撤销激活码")
        print("  [4] 退出")
        print()

        choice = input("请输入选项 [1-4]: ").strip()

        if choice == "1":
            # 生成新激活码
            print("\n--- 生成新激活码 ---")

            hospital_name = input("医院名称: ").strip()
            if not hospital_name:
                print("✗ 医院名称不能为空")
                continue

            print("\n许可类型:")
            for key, value in LICENSE_TYPES.items():
                print(f"  [{key}] {value['name']}")

            license_type = input("\n选择类型 [trial/research/commercial/permanent]: ").strip().lower()
            if license_type not in LICENSE_TYPES:
                print("✗ 无效的许可类型")
                continue

            # 可选参数
            days_input = input(f"有效天数 [默认: {LICENSE_TYPES[license_type]['default_days']}]: ").strip()
            days = int(days_input) if days_input else None

            cases_input = input(f"最大病例数 [默认: {'无限制' if LICENSE_TYPES[license_type]['default_max_cases'] == -1 else LICENSE_TYPES[license_type]['default_max_cases']}]: ").strip()
            max_cases = int(cases_input) if cases_input else None

            notes = input("备注 [可选]: ").strip()

            # 生成
            try:
                generator.create_license(
                    hospital_name=hospital_name,
                    license_type=license_type,
                    days=days,
                    max_cases=max_cases,
                    notes=notes
                )

                print("\n✓ 激活码已保存到 authorized.json")
                print("✓ 请提交到GitHub私有仓库:")
                print(f"  git add {generator.authorized_file}")
                print(f"  git commit -m \"Add license for {hospital_name}\"")
                print(f"  git push origin main")

            except Exception as e:
                print(f"✗ 生成失败: {e}")

        elif choice == "2":
            # 查看激活码
            print("\n--- 授权列表 ---")
            generator.list_licenses()

        elif choice == "3":
            # 撤销激活码
            print("\n--- 撤销激活码 ---")
            code = input("请输入要撤销的激活码: ").strip()
            generator.revoke_license(code)

        elif choice == "4":
            print("\n再见！")
            break

        else:
            print("✗ 无效选项")


def quick_generate():
    """快速生成3个初始激活码（用于首次部署）"""
    print("=" * 70)
    print("快速生成初始激活码")
    print("=" * 70)
    print()

    generator = LicenseGenerator()

    # 示例1：试用版
    generator.create_license(
        hospital_name="示例医院A",
        license_type="trial",
        notes="初始试用激活码 - 可删除"
    )

    # 示例2：科研版
    generator.create_license(
        hospital_name="示例大学B",
        license_type="research",
        notes="科研合作机构 - 示例"
    )

    # 示例3：商业版
    generator.create_license(
        hospital_name="示例医院C",
        license_type="commercial",
        notes="商业客户 - 示例"
    )

    print("=" * 70)
    print("✓ 已生成3个示例激活码")
    print("✓ 请编辑 authorized.json 修改医院名称")
    print("✓ 然后提交到GitHub私有仓库")
    print("=" * 70)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # 快速生成模式
        quick_generate()
    else:
        # 交互式模式
        interactive_mode()
```

**使用方法**：

```bash
# 交互式生成激活码
python scripts/generate_license.py

# 快速生成3个示例激活码
python scripts/generate_license.py --quick
```

---

### 2. 授权数据文件

**文件位置**: GitHub私有仓库 → `authorized.json`

**文件结构**：

```json
{
  "version": "1.0",
  "last_updated": "2025-10-14 15:30:00",
  "licenses": [
    {
      "code": "NB10-TRIAL-8F3A2D1C4B5E",
      "type": "trial",
      "hospital": "北京某三甲医院",
      "expire": "2025-11-13",
      "max_cases": 100,
      "issued_date": "2025-10-14",
      "status": "active",
      "notes": "初次试用评估",
      "usage_count": 0
    },
    {
      "code": "NB10-COMME-A1B2C3D4E5F6",
      "type": "commercial",
      "hospital": "上海某医院影像中心",
      "expire": "2026-10-14",
      "max_cases": -1,
      "issued_date": "2025-10-14",
      "status": "active",
      "notes": "年度商业许可",
      "usage_count": 0
    },
    {
      "code": "NB10-TRIAL-AABBCCDDEEFF",
      "type": "trial",
      "hospital": "深圳某诊所",
      "expire": "2025-10-01",
      "max_cases": 50,
      "issued_date": "2025-09-01",
      "status": "revoked",
      "notes": "试用期结束后撤销",
      "revoked_date": "2025-10-05",
      "usage_count": 45
    }
  ]
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | string | 激活码（唯一标识） |
| `type` | string | 许可类型 (trial/research/commercial/permanent) |
| `hospital` | string | 医院名称 |
| `expire` | string | 过期日期 (YYYY-MM-DD) |
| `max_cases` | int | 最大病例数 (-1表示无限制) |
| `issued_date` | string | 发放日期 |
| `status` | string | 状态 (active/revoked/expired) |
| `notes` | string | 备注信息 |
| `usage_count` | int | 使用次数（未来功能，需客户端回传） |
| `revoked_date` | string | 撤销日期（可选） |

---

### 3. 激活码验证器

**文件位置**: `core/license_validator.py`

**功能**：
- 从GitHub获取授权列表（支持离线缓存）
- 验证激活码有效性
- 检查过期时间和使用限制

**完整代码**：

```python
"""
NB10 License Validator - 激活码验证模块

用于验证NB10软件的激活码，支持在线/离线模式。

Author: 陈医生团队
License: Proprietary
"""

import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

__version__ = "1.0.0"


class LicenseValidator:
    """
    激活码验证器

    支持:
    - 在线验证（从GitHub获取最新授权数据）
    - 离线验证（使用本地缓存）
    - 自动缓存（减少网络请求）
    """

    # GitHub Raw URL配置
    # TODO: 替换为你的实际仓库地址
    GITHUB_RAW_URL = "https://raw.githubusercontent.com/YOUR-USERNAME/nb10-licenses/main/authorized.json"

    # GitHub Personal Access Token（可选，私有仓库需要）
    # TODO: 替换为你的GitHub Token（只读权限）
    GITHUB_TOKEN = None  # 格式: "ghp_xxxxxxxxxxxxxxxxxxxx"

    # 本地缓存路径
    LOCAL_CACHE = Path.home() / ".nb10" / "license_cache.json"

    # 缓存有效期（秒）- 24小时
    CACHE_VALIDITY = 24 * 3600

    def __init__(self, offline_mode: bool = False):
        """
        初始化验证器

        Args:
            offline_mode: 是否强制离线模式（不尝试联网）
        """
        self.offline_mode = offline_mode
        self.license_data = None
        self.load_license_data()

    def load_license_data(self):
        """
        加载授权数据

        优先级:
        1. 在线获取（如果不是离线模式）
        2. 本地缓存（如果在线获取失败或离线模式）
        """
        if not self.offline_mode:
            # 尝试在线获取
            try:
                self.license_data = self._fetch_from_github()
                if self.license_data:
                    self._save_cache(self.license_data)
                    return
            except Exception as e:
                print(f"⚠️ 无法从GitHub获取授权数据: {e}")

        # 回退到本地缓存
        if self.LOCAL_CACHE.exists():
            try:
                with open(self.LOCAL_CACHE, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

                # 检查缓存是否过期
                cache_time = datetime.fromisoformat(cache_data.get("cached_at", "2000-01-01"))
                age = (datetime.now() - cache_time).total_seconds()

                if age < self.CACHE_VALIDITY:
                    self.license_data = cache_data.get("data")
                    print(f"ℹ️ 使用本地缓存的授权数据（{age/3600:.1f}小时前更新）")
                else:
                    print(f"⚠️ 本地缓存已过期（{age/3600:.1f}小时前），请联网更新")
                    self.license_data = cache_data.get("data")  # 仍然使用，但提示
            except Exception as e:
                print(f"⚠️ 无法加载本地缓存: {e}")
                self.license_data = None
        else:
            print("⚠️ 无授权数据可用，请检查网络连接或联系技术支持")
            self.license_data = None

    def _fetch_from_github(self) -> Optional[Dict]:
        """
        从GitHub获取授权数据

        Returns:
            授权数据字典，失败返回None
        """
        headers = {}
        if self.GITHUB_TOKEN:
            headers["Authorization"] = f"token {self.GITHUB_TOKEN}"

        response = requests.get(self.GITHUB_RAW_URL, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise ValueError("授权文件不存在，请联系技术支持")
        elif response.status_code == 401:
            raise ValueError("GitHub Token无效或权限不足")
        else:
            raise ValueError(f"GitHub返回错误: {response.status_code}")

    def _save_cache(self, data: Dict):
        """
        保存授权数据到本地缓存

        Args:
            data: 授权数据
        """
        cache_data = {
            "cached_at": datetime.now().isoformat(),
            "data": data
        }

        self.LOCAL_CACHE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.LOCAL_CACHE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

    def validate(self, license_code: str) -> Dict:
        """
        验证激活码

        Args:
            license_code: 激活码字符串

        Returns:
            验证结果字典:
            {
                "valid": bool,           # 是否有效
                "message": str,          # 结果消息
                "license": dict or None  # 许可证详情（有效时）
            }
        """
        # 检查是否有授权数据
        if not self.license_data:
            return {
                "valid": False,
                "message": "无法加载授权数据，请检查网络连接或联系技术支持",
                "license": None
            }

        # 标准化激活码（去除空格，转大写）
        license_code = license_code.strip().upper()

        # 查找激活码
        license_info = None
        for lic in self.license_data.get("licenses", []):
            if lic["code"].upper() == license_code:
                license_info = lic
                break

        if not license_info:
            return {
                "valid": False,
                "message": "激活码无效，请检查输入或联系技术支持",
                "license": None
            }

        # 检查状态
        status = license_info.get("status", "unknown")
        if status == "revoked":
            return {
                "valid": False,
                "message": f"激活码已被撤销（撤销日期: {license_info.get('revoked_date', '未知')}）",
                "license": None
            }
        elif status != "active":
            return {
                "valid": False,
                "message": f"激活码状态异常: {status}",
                "license": None
            }

        # 检查有效期
        try:
            expire_date = datetime.strptime(license_info["expire"], "%Y-%m-%d")
            now = datetime.now()

            if now > expire_date:
                return {
                    "valid": False,
                    "message": f"激活码已过期（过期日期: {license_info['expire']}）",
                    "license": None
                }

            # 计算剩余天数
            days_left = (expire_date - now).days

            # 验证通过
            return {
                "valid": True,
                "message": f"激活成功！剩余 {days_left} 天",
                "license": license_info,
                "days_left": days_left
            }

        except Exception as e:
            return {
                "valid": False,
                "message": f"验证过程出错: {e}",
                "license": None
            }

    def get_license_info(self, license_code: str) -> Optional[Dict]:
        """
        获取激活码详细信息

        Args:
            license_code: 激活码

        Returns:
            许可证信息字典，无效返回None
        """
        result = self.validate(license_code)
        return result.get("license")


# 单例模式（可选）
_validator_instance = None

def get_validator(offline_mode: bool = False) -> LicenseValidator:
    """
    获取验证器单例

    Args:
        offline_mode: 是否离线模式

    Returns:
        LicenseValidator实例
    """
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = LicenseValidator(offline_mode=offline_mode)
    return _validator_instance


# 测试代码
if __name__ == "__main__":
    print("=" * 70)
    print("NB10 激活码验证器 - 测试模式")
    print("=" * 70)
    print()

    # 创建验证器
    validator = LicenseValidator()

    # 测试激活码
    test_code = input("请输入要测试的激活码: ").strip()

    result = validator.validate(test_code)

    print()
    print("=" * 70)
    print(f"验证结果: {result['message']}")
    print("=" * 70)

    if result['valid']:
        lic = result['license']
        print(f"医院名称:    {lic['hospital']}")
        print(f"许可类型:    {lic['type']}")
        print(f"有效期至:    {lic['expire']}")
        print(f"最大病例数:  {'无限制' if lic['max_cases'] == -1 else lic['max_cases']}")
        if lic.get('notes'):
            print(f"备注:        {lic['notes']}")

    print("=" * 70)
```

---

### 4. 启动流程集成

**文件位置**: `cli/run_nb10.py`

**修改点**: 在 `main()` 函数开始处添加授权检查

**代码示例**：

```python
# cli/run_nb10.py (部分代码)

from pathlib import Path
from core.license_validator import LicenseValidator

def check_and_activate():
    """
    检查激活状态，未激活则引导激活

    Returns:
        bool: 是否已激活
    """
    license_file = Path.home() / ".nb10" / "license.key"

    # 检查本地是否已保存激活码
    if license_file.exists():
        try:
            with open(license_file, "r", encoding="utf-8") as f:
                saved_code = f.read().strip()

            # 验证激活码
            validator = LicenseValidator()
            result = validator.validate(saved_code)

            if result["valid"]:
                # 激活有效
                lic = result['license']
                print("=" * 70)
                print("✓ NB10 已激活")
                print("=" * 70)
                print(f"授权单位:    {lic['hospital']}")
                print(f"许可类型:    {lic['type']}")
                print(f"有效期至:    {lic['expire']} ({result.get('days_left', 0)} 天)")
                if lic['max_cases'] != -1:
                    print(f"病例数限制:  {lic['max_cases']} 例")
                print("=" * 70)
                print()
                return True
            else:
                # 激活码失效
                print("=" * 70)
                print(f"⚠️ 激活失效: {result['message']}")
                print("=" * 70)
                print()
                # 删除失效的激活码
                license_file.unlink()

        except Exception as e:
            print(f"⚠️ 激活验证出错: {e}")
            print()

    # 需要激活
    return show_activation_dialog()


def show_activation_dialog() -> bool:
    """
    显示激活对话框

    Returns:
        bool: 是否激活成功
    """
    print()
    print("=" * 70)
    print("NB10 AI-CAC 需要激活")
    print("=" * 70)
    print()
    print("本软件需要有效的激活码才能使用。")
    print()
    print("授权说明:")
    print("  • 试用版: 30天有效期，100例限制")
    print("  • 科研版: 1年有效期，需提供科研证明")
    print("  • 商业版: 1年有效期，无限制使用")
    print()
    print("如需获取激活码，请联系:")
    print("  Email:   license@example.com")
    print("  Website: https://nb10.example.com")
    print("  电话:    138-xxxx-xxxx")
    print()
    print("=" * 70)
    print()

    # 输入激活码
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        license_code = input(f"请输入激活码 (尝试 {attempt}/{max_attempts}，输入 'q' 退出): ").strip()

        if license_code.lower() == 'q':
            print("\n用户取消激活，程序退出。")
            return False

        if not license_code:
            print("✗ 激活码不能为空\n")
            continue

        # 验证激活码
        print("\n正在验证激活码...")
        validator = LicenseValidator()
        result = validator.validate(license_code)

        if result["valid"]:
            # 激活成功，保存到本地
            license_file = Path.home() / ".nb10" / "license.key"
            license_file.parent.mkdir(parents=True, exist_ok=True)

            with open(license_file, "w", encoding="utf-8") as f:
                f.write(license_code)

            lic = result['license']
            print()
            print("=" * 70)
            print("✓ 激活成功！")
            print("=" * 70)
            print(f"授权单位:    {lic['hospital']}")
            print(f"许可类型:    {lic['type']}")
            print(f"有效期至:    {lic['expire']} ({result.get('days_left', 0)} 天)")
            if lic['max_cases'] != -1:
                print(f"病例数限制:  {lic['max_cases']} 例")
            print("=" * 70)
            print()
            print("按 Enter 继续...")
            input()
            return True
        else:
            print(f"✗ {result['message']}\n")

    # 超过最大尝试次数
    print("=" * 70)
    print("激活失败次数过多，程序退出。")
    print("如有问题，请联系技术支持。")
    print("=" * 70)
    return False


def main():
    """主入口（修改后）"""

    # ========== 添加授权检查 ==========
    if not check_and_activate():
        return 1
    # ==================================

    # 原有的main逻辑
    parser = argparse.ArgumentParser(...)
    # ... 其余代码保持不变 ...
```

---

## 🚀 部署流程

### 第一步：创建GitHub私有仓库

1. **登录GitHub**，创建新仓库：
   - 名称: `nb10-licenses`
   - 可见性: **Private** (私有)
   - 不要初始化README（手动添加）

2. **克隆仓库到本地**：
   ```bash
   git clone https://github.com/YOUR-USERNAME/nb10-licenses.git
   cd nb10-licenses
   ```

3. **创建初始文件**：
   ```bash
   # 创建README
   echo "# NB10 License Database" > README.md
   echo "This is a private repository for NB10 license management." >> README.md

   # 创建空的授权文件
   echo '{"version": "1.0", "licenses": []}' > authorized.json

   # 提交
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

---

### 第二步：生成GitHub Token

1. **进入GitHub设置**：
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **生成新Token**：
   - 点击 "Generate new token (classic)"
   - Note: `NB10 License Read-Only Token`
   - Expiration: `No expiration` 或 `1 year`
   - 权限：只勾选 **`repo`** (完整勾选，因为是私有仓库)

3. **复制Token**：
   - 格式: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - ⚠️ **立即保存**，离开页面后无法再查看

4. **配置到代码**：
   - 编辑 `core/license_validator.py`
   - 替换以下两行：
     ```python
     GITHUB_RAW_URL = "https://raw.githubusercontent.com/YOUR-USERNAME/nb10-licenses/main/authorized.json"
     GITHUB_TOKEN = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
     ```

---

### 第三步：生成初始激活码

在NB10项目根目录运行：

```bash
# 快速生成3个示例激活码
python scripts/generate_license.py --quick
```

**输出示例**：
```
============================================================
✓ 新激活码生成成功！
============================================================
激活码:      NB10-TRIAL-8F3A2D1C4B5E
医院名称:    示例医院A
许可类型:    试用版
有效期至:    2025-11-13
病例数限制:  100 例
============================================================
...
```

**编辑生成的 `authorized.json`**：
- 修改医院名称为实际医院
- 调整有效期和病例数限制
- 删除不需要的示例激活码

---

### 第四步：提交到GitHub

```bash
# 在nb10-licenses仓库目录
cp /path/to/nb10_windows/authorized.json .
git add authorized.json
git commit -m "Add initial licenses"
git push origin main
```

---

### 第五步：测试激活流程

1. **本地测试验证器**：
   ```bash
   cd /path/to/nb10_windows
   python core/license_validator.py

   # 输入生成的激活码进行测试
   ```

2. **测试完整启动流程**：
   ```bash
   # 删除本地已保存的激活码（如果有）
   rm -rf ~/.nb10/license.key

   # 启动NB10
   python cli/run_nb10.py --config config/config.yaml

   # 应该看到激活界面，输入激活码测试
   ```

3. **验证离线模式**：
   ```bash
   # 断开网络后再次启动
   python cli/run_nb10.py

   # 应该使用本地缓存，不报错
   ```

---

### 第六步：分发给医院

**邮件模板**：

```
主题: NB10 AI-CAC 系统试用激活码

尊敬的 XXX医院：

感谢您对NB10 AI-CAC冠状动脉钙化评分系统的关注。

您的试用激活码：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        NB10-TRIAL-XXXXXXXXXXXXXXX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

激活信息：
  • 有效期: 30天（至 2025-XX-XX）
  • 病例数限制: 100例
  • 许可类型: 试用版

使用方法：
  1. 下载并安装NB10软件（见附件）
  2. 启动软件，在激活界面输入上述激活码
  3. 点击"确认"完成激活
  4. 参考《用户手册》开始使用

技术支持：
  Email: support@example.com
  电话: 138-xxxx-xxxx
  文档: https://nb10.example.com/docs

注意事项：
  • 激活码仅供贵单位使用，请勿分享
  • 试用期结束后，如需继续使用请联系我们
  • 软件支持离线使用（医院内网环境）

陈医生团队
2025-10-14
```

---

## 🔒 安全性与局限性

### 安全措施

本系统采用的安全措施：

1. **私有仓库** - 授权文件不公开
2. **GitHub Token** - 只读权限，即使泄露也无法修改授权
3. **本地缓存** - 减少网络请求，提高性能
4. **激活码唯一性** - 12位随机hex，暴力破解难度高

### 已知局限性

⚠️ **本系统不是强加密保护**，存在以下局限：

1. **Token可被反编译获取**
   - 代码中硬编码了GitHub Token
   - 技术熟练者可以通过反编译获取
   - **缓解**: Token只有只读权限，无法修改授权文件

2. **激活码可能被分享**
   - 一个激活码可在多台电脑使用
   - **缓解**: 激活码绑定医院名称，审计时可追溯

3. **离线模式下撤销不及时**
   - 已缓存的客户端在离线时无法即时撤销
   - **缓解**: 缓存有24小时过期机制

4. **代码可被修改绕过验证**
   - 开源代码可能被修改，去除授权检查
   - **缓解**: 依赖法律协议，技术手段为辅

### 升级路径

当需要更强保护时（商业化阶段），可升级到：

```
阶段1（当前）:        阶段2（6个月后）:       阶段3（商业化）:
GitHub授权    →    GitHub + 硬件绑定   →    VPS激活服务器

特点：                                     特点：
• 简单快速                                • 精确控制
• 0成本                                  • 实时撤销
• 适合试用推广                            • 使用统计
                                         • 强加密保护
```

**升级方向**：

1. **硬件绑定**（中期）
   - 激活码绑定主板UUID或MAC地址
   - 一机一码，防止多台电脑共用

2. **VPS激活服务器**（长期）
   - 部署独立的激活服务器
   - 实时验证，实时撤销
   - 收集使用统计数据

3. **代码混淆**（可选）
   - 使用PyInstaller + 混淆工具
   - 增加反编译难度

---

## 📖 知识产权保护策略

### 版权声明

**在所有代码文件头部添加**：

```python
"""
NB10 AI-CAC Windows Tool
Copyright (c) 2025 陈医生团队
All Rights Reserved.

本软件受版权法保护，未经授权不得用于商业用途。

授权说明:
  • 学术研究: 免费使用，需在论文中引用
  • 商业用途: 需购买商业许可

联系方式: license@example.com
许可证文件: LICENSE.txt
"""
```

**在启动界面显示**：

```
========================================
NB10 AI-CAC v2.0.0
Copyright (c) 2025 陈医生团队
========================================

⚠️ 授权声明：
本软件受版权保护，仅供授权用户使用。
商业用途需获得书面许可。

继续使用即表示您同意遵守许可条款。
按 Enter 继续...
```

---

### 许可证文件

**创建 `LICENSE.txt`**（项目根目录）：

```
NB10 AI-CAC SOFTWARE LICENSE AGREEMENT

版权所有 (c) 2025 陈医生团队
保留所有权利。

一、授权范围

1.1 学术研究许可（免费）
本软件允许学术机构、科研单位免费用于非商业性研究，但需遵守以下条件：
  (a) 不得用于临床诊疗或其他商业活动
  (b) 在发表的论文中引用本软件
  (c) 不得移除或修改版权声明

1.2 商业使用许可（收费）
任何商业用途（包括但不限于临床诊疗、销售、集成到商业产品）需要获得
书面商业许可。商业许可需联系：license@example.com

二、禁止事项

未经授权，您不得：
  (a) 销售、出租或以其他方式转让本软件
  (b) 反向工程、反编译或反汇编本软件
  (c) 移除或修改版权声明和许可信息
  (d) 将本软件用于商业用途

三、免责声明

本软件"按原样"提供，不提供任何明示或暗示的保证。在任何情况下，
版权所有者不对因使用本软件而产生的任何损害承担责任。

四、终止

如果您违反本许可协议的任何条款，您的使用权将自动终止。

五、联系方式

  Email: license@example.com
  Website: https://nb10.example.com

本许可协议受中华人民共和国法律管辖。

陈医生团队
2025年10月
```

---

### 软件著作权登记

**建议优先进行软件著作权登记**（优于专利）：

**优势**：
- ✅ 成本低（约¥300）
- ✅ 周期短（1-2个月）
- ✅ 保护代码版权
- ✅ 对论文和商业化都有帮助

**申请材料**：
1. 软件著作权登记申请表
2. 软件源代码（前30页 + 后30页）
3. 软件说明书（用户手册）
4. 身份证明文件

**申请流程**：
```
1. 准备材料
   ↓
2. 在线提交（中国版权保护中心）
   ↓
3. 审查（30-60天）
   ↓
4. 获得登记证书
```

**登记后的权益**：
- 法律承认的版权证明
- 侵权时的有力证据
- 技术成果认定的依据

---

## 📊 使用统计（未来功能）

### 设计思路

在未来版本中，可以添加**匿名使用统计**功能：

**收集数据**（用户同意后）：
- 激活码（匿名哈希）
- 处理病例数
- 平均处理时间
- 硬件配置信息
- 软件版本

**上传方式**：
- 定期（每周）后台上传
- 或手动导出日志文件发送

**用途**：
- 了解实际使用情况
- 优化性能配置
- 生成使用报告（用于论文）

**实现方式**（可选）：
```python
# 在run_nb10.py中添加
def report_usage_statistics(license_code, cases_processed, avg_time):
    """上传使用统计（匿名）"""
    if user_agreed_to_statistics():
        data = {
            "license_hash": hashlib.sha256(license_code.encode()).hexdigest(),
            "cases": cases_processed,
            "avg_time": avg_time,
            "version": __version__,
            "timestamp": datetime.now().isoformat()
        }
        # 发送到统计服务器（可选）
        requests.post("https://stats.example.com/api/usage", json=data)
```

---

## 🎓 论文与专利建议

### 专利申请建议

**当前评估**：
- 单独申请"硬件自适应配置系统"专利 - **可能性较低（30%）**
- 原因：类似技术在游戏、深度学习框架中已存在

**更可行的专利策略**：

1. **组合专利**（推荐）
   ```
   专利名称:
   "基于硬件自适应的医学影像AI推理系统及方法"

   技术方案包括：
   ├─ DICOM系列智能选择算法
   ├─ 硬件自适应配置系统
   ├─ 医疗级安全保护机制
   └─ 冠状动脉钙化评分优化方法
   ```

2. **软件著作权**（优先）
   - 成本低、周期短
   - 保护代码版权
   - 对商业化和论文都有帮助

3. **观察市场反馈**
   - 论文发表后看审稿人意见
   - 医院试用后收集反馈
   - 6-12个月后再评估专利价值

**专利申请流程**（如果确定申请）：
```
1. 技术交底书 → 2. 专利检索 → 3. 撰写申请 → 4. 提交申请
   (1-2周)        (1周)         (2-4周)        (即时)
                                                  ↓
                                          5. 获得申请号
                                          （可标注"专利申请中"）
                                                  ↓
                                          6. 实质审查
                                          （12-24个月）
```

---

### 论文发表策略

**发表时机**：

```
当前（2025 Q4）  →  专利申请（2026 Q1）  →  论文投稿（2026 Q2）
     ↓                    ↓                      ↓
  不公开技术          提交专利申请           可以发表论文
                   （标注"申请中"）        （说明专利申请中）
```

**论文中的知识产权说明**：

```markdown
## Availability of Data and Materials

The NB10 AI-CAC software is available for academic research under
specific license terms. A patent application for the core technology
is currently pending (Application No: CN202XXXXXXX).

For commercial use, please contact: license@example.com

Software Repository (Academic Use Only):
https://github.com/xxx/nb10 (upon request)
```

---

## 📋 实施清单

### 第1周：基础设施搭建

- [ ] 创建GitHub私有仓库 `nb10-licenses`
- [ ] 生成GitHub Personal Access Token
- [ ] 编写 `scripts/generate_license.py`
- [ ] 编写 `core/license_validator.py`
- [ ] 修改 `cli/run_nb10.py` 集成授权检查
- [ ] 创建 `LICENSE.txt` 许可证文件
- [ ] 添加版权声明到所有代码文件

**验收标准**：
- ✅ 能够生成激活码
- ✅ 能够验证激活码（在线/离线）
- ✅ 启动时正确显示激活界面

---

### 第2周：测试与完善

- [ ] 生成3个测试激活码（试用/科研/商业各1个）
- [ ] 测试完整激活流程
- [ ] 测试过期激活码处理
- [ ] 测试撤销激活码功能
- [ ] 测试离线模式
- [ ] 准备激活码发送邮件模板
- [ ] 撰写《授权管理手册》（内部文档）

**验收标准**：
- ✅ 所有测试场景通过
- ✅ 文档完整
- ✅ 准备好分发给医院

---

### 第3-4周：推广与收集反馈

- [ ] 联系2-3家目标医院
- [ ] 发送试用激活码
- [ ] 收集医院使用反馈
- [ ] 跟踪激活码使用情况
- [ ] 根据反馈优化流程

**验收标准**：
- ✅ 至少1家医院成功激活并使用
- ✅ 收集到有价值的反馈

---

### 长期计划

**3-6个月后**：
- [ ] 软件著作权登记
- [ ] 评估专利申请可行性
- [ ] 根据使用情况调整授权策略

**6-12个月后**：
- [ ] 论文投稿（如已申请专利）
- [ ] 考虑升级到硬件绑定激活
- [ ] 评估VPS激活服务器需求

---

## 🔄 维护与更新

### 日常维护

**定期检查**（每月）：
- 查看授权列表，标记即将过期的激活码
- 联系即将到期的医院，询问续费意向
- 检查是否有需要撤销的激活码

**激活码管理**：

```bash
# 查看所有激活码
python scripts/generate_license.py
# 选择"查看所有激活码"

# 撤销激活码
python scripts/generate_license.py
# 选择"撤销激活码"
# 输入要撤销的激活码

# 提交到GitHub
cd /path/to/nb10-licenses
git add authorized.json
git commit -m "Update license status"
git push origin main
```

---

### 版本更新

**当NB10软件更新时**：

1. 不需要更新激活系统（向后兼容）
2. 如果改变授权逻辑，需更新：
   - `core/license_validator.py`
   - `authorized.json` 数据结构
3. 通知已授权医院升级软件

---

## 📞 技术支持

### 常见问题

**Q1: 医院说无法激活，提示"无法连接授权服务器"**

A: 检查以下几点：
- 医院网络是否能访问GitHub（可能被防火墙屏蔽）
- GitHub Token是否正确配置
- 授权文件URL是否正确

解决方案：
```bash
# 测试GitHub连接
curl https://raw.githubusercontent.com/YOUR-USERNAME/nb10-licenses/main/authorized.json

# 如果无法访问，提供离线激活方案：
# 1. 手动下载authorized.json
# 2. 放到医院电脑的 ~/.nb10/license_cache.json
# 3. 启动软件（会使用本地缓存）
```

---

**Q2: 如何延长激活码有效期？**

A:
```bash
# 编辑authorized.json，修改expire字段
{
  "code": "NB10-TRIAL-XXXXXXXX",
  "expire": "2025-11-13"  → "2026-01-13"  # 延长2个月
}

# 提交到GitHub
git add authorized.json
git commit -m "Extend license for XXX Hospital"
git push origin main

# 医院端：重新联网启动软件，会自动更新
```

---

**Q3: 如何撤销已分发的激活码？**

A:
```bash
# 方式1：使用脚本
python scripts/generate_license.py
# 选择"撤销激活码"

# 方式2：手动编辑
# 编辑authorized.json，修改status
{
  "code": "NB10-TRIAL-XXXXXXXX",
  "status": "active"  → "revoked"  # 撤销
}

# 提交到GitHub
git push origin main

# 注意：已缓存的客户端需要联网更新才能生效
```

---

## 📄 附录

### A. 文件清单

**新增文件**：

```
nb10_windows/
├── scripts/
│   └── generate_license.py          # 激活码生成脚本
├── core/
│   └── license_validator.py         # 激活码验证模块
├── LICENSE.txt                       # 许可证文件
└── docs/
    └── LICENSE_MANAGEMENT_SYSTEM_DESIGN.md  # 本文档
```

**GitHub仓库文件**：

```
nb10-licenses/ (私有仓库)
├── README.md                        # 仓库说明
├── authorized.json                  # 授权数据（核心文件）
└── revoked_history.json            # 撤销记录（可选）
```

---

### B. 激活码示例

**生成的激活码示例**：

```
试用版:
NB10-TRIAL-8F3A2D1C4B5E
NB10-TRIAL-A1B2C3D4E5F6
NB10-TRIAL-1A2B3C4D5E6F

科研版:
NB10-RESEA-9G8H7I6J5K4L
NB10-RESEA-B2C3D4E5F6A1

商业版:
NB10-COMME-3M4N5O6P7Q8R
NB10-COMME-C3D4E5F6A1B2

永久版:
NB10-PERMA-4S5T6U7V8W9X
```

---

### C. 参考资料

**GitHub相关**：
- GitHub Personal Access Token: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- GitHub Raw Content: https://docs.github.com/en/repositories/working-with-files/using-files/viewing-a-file

**版权保护**：
- 中国版权保护中心: http://www.ccopyright.com.cn/
- 软件著作权登记指南: http://www.ccopyright.com.cn/cpcc/RJZZQjIndex.jsp

**许可证参考**：
- 开源许可证选择: https://choosealicense.com/
- 双许可模式案例: MySQL, Qt, Gitlab等

---

## ✅ 文档状态

- **版本**: 1.0.0
- **状态**: 设计提案 (Proposal)
- **审核状态**: 待审核
- **实施状态**: 未开始

**变更历史**：
- 2025-10-14: 初始版本，基于授权管理讨论创建

---

## 👥 贡献者

- **设计**: Claude (AI Assistant) + 陈医生团队
- **技术方案**: 基于GitHub的轻量级授权系统
- **目标**: 初期推广阶段的知识产权保护

---

## 📞 联系与反馈

如有问题或建议，请通过以下方式反馈：

- 项目Issue: (待添加GitHub仓库链接)
- 内部讨论: 在本文档所在目录创建 `FEEDBACK.md`

---

**文档结束**
