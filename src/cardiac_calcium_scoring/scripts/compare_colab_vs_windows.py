#!/usr/bin/env python3
"""
对比Colab和Windows版本的AI-CAC结果

验证两个版本的数值一致性
"""

import pandas as pd
import numpy as np
from pathlib import Path

def normalize_patient_id(pid):
    """标准化patient_id以便匹配"""
    if pd.isna(pid):
        return None
    pid = str(pid).strip()
    # 去除BOM
    if pid.startswith('\ufeff'):
        pid = pid[1:]
    return pid

def main():
    # 文件路径
    colab_file = Path("../../results/nb10_ai_cac/ai_cac_scores_20251013_154420.csv")
    windows_chd_file = Path("output/nb10_results_20251014_135814.csv")
    windows_normal_file = Path("output/nb10_results_20251014_140603.csv")

    print("=" * 80)
    print("Colab vs Windows 结果对比验证")
    print("=" * 80)

    # 读取Colab结果
    print("\n[1/4] 读取Colab结果...")
    colab_df = pd.read_csv(colab_file)
    colab_df['patient_id'] = colab_df['patient_id'].apply(normalize_patient_id)
    colab_df = colab_df[colab_df['status'] == 'success'].copy()
    print(f"  Colab成功案例: {len(colab_df)} 例")
    print(f"  CHD: {len(colab_df[colab_df['group']=='chd'])} 例")
    print(f"  Normal: {len(colab_df[colab_df['group']=='normal'])} 例")

    # 读取Windows结果
    print("\n[2/4] 读取Windows结果...")
    windows_chd_df = pd.read_csv(windows_chd_file, encoding='utf-8-sig')
    windows_chd_df['group'] = 'chd'  # 添加组别标记

    windows_normal_df = pd.read_csv(windows_normal_file, encoding='utf-8-sig')
    windows_normal_df['group'] = 'normal'  # 添加组别标记

    # 合并Windows结果
    windows_df = pd.concat([windows_chd_df, windows_normal_df], ignore_index=True)
    windows_df['patient_id'] = windows_df['patient_id'].apply(normalize_patient_id)
    windows_df = windows_df[windows_df['status'] == 'success'].copy()
    print(f"  Windows成功案例: {len(windows_df)} 例")
    print(f"  CHD: {len(windows_chd_df[windows_chd_df['status']=='success'])} 例 (测试)")
    print(f"  Normal: {len(windows_normal_df[windows_normal_df['status']=='success'])} 例 (测试)")

    # 匹配患者
    print("\n[3/4] 匹配相同患者...")

    # 内连接找到共同患者
    merged_df = colab_df.merge(
        windows_df,
        on='patient_id',
        suffixes=('_colab', '_windows'),
        how='inner'
    )

    print(f"  匹配成功: {len(merged_df)} 例")

    if len(merged_df) == 0:
        print("\n⚠️ 警告: 没有找到匹配的患者ID")
        print("\nColab示例ID:")
        for pid in colab_df['patient_id'].head(5):
            print(f"  - {repr(pid)}")
        print("\nWindows示例ID:")
        for pid in windows_df['patient_id'].head(5):
            print(f"  - {repr(pid)}")
        return

    # 对比分析
    print("\n[4/4] 对比Agatston Score...")
    print("=" * 80)

    # 计算差异
    merged_df['abs_diff'] = abs(merged_df['agatston_score_colab'] - merged_df['agatston_score_windows'])
    merged_df['rel_diff'] = merged_df['abs_diff'] / merged_df['agatston_score_colab'].replace(0, 1) * 100

    # 分组统计
    by_group = {}
    for group in ['chd', 'normal']:
        group_df = merged_df[merged_df['group_colab'] == group].copy()
        if len(group_df) > 0:
            by_group[group] = group_df

    # 总体一致性
    print("\n📊 总体一致性分析")
    print("-" * 80)

    identical = (merged_df['abs_diff'] == 0).sum()
    diff_lt_1 = (merged_df['abs_diff'] < 1).sum()
    diff_lt_1pct = (merged_df['rel_diff'] < 1).sum()
    diff_gte_1pct = (merged_df['rel_diff'] >= 1).sum()

    print(f"匹配病例总数: {len(merged_df)} 例")
    print(f"  完全一致 (差异=0):        {identical:3d} 例 ({identical/len(merged_df)*100:5.1f}%)")
    print(f"  差异<1分:                 {diff_lt_1:3d} 例 ({diff_lt_1/len(merged_df)*100:5.1f}%)")
    print(f"  相对差异<1%:              {diff_lt_1pct:3d} 例 ({diff_lt_1pct/len(merged_df)*100:5.1f}%)")
    print(f"  相对差异≥1% (需要关注):   {diff_gte_1pct:3d} 例 ({diff_gte_1pct/len(merged_df)*100:5.1f}%)")

    # 数值统计
    print("\n📈 数值差异统计")
    print("-" * 80)
    print(f"绝对差异:")
    print(f"  均值:   {merged_df['abs_diff'].mean():.4f} 分")
    print(f"  中位数: {merged_df['abs_diff'].median():.4f} 分")
    print(f"  最大值: {merged_df['abs_diff'].max():.4f} 分")
    print(f"  标准差: {merged_df['abs_diff'].std():.4f} 分")

    print(f"\n相对差异 (非零Score):")
    non_zero = merged_df[merged_df['agatston_score_colab'] > 0]
    if len(non_zero) > 0:
        print(f"  均值:   {non_zero['rel_diff'].mean():.4f} %")
        print(f"  中位数: {non_zero['rel_diff'].median():.4f} %")
        print(f"  最大值: {non_zero['rel_diff'].max():.4f} %")

    # 分组对比
    print("\n📋 分组对比 (CHD vs Normal)")
    print("-" * 80)

    for group_name, group_df in by_group.items():
        print(f"\n{group_name.upper()} 组 (n={len(group_df)}):")

        colab_scores = group_df['agatston_score_colab']
        windows_scores = group_df['agatston_score_windows']

        print(f"  Colab   - 均值: {colab_scores.mean():7.2f}, 中位数: {colab_scores.median():6.2f}")
        print(f"  Windows - 均值: {windows_scores.mean():7.2f}, 中位数: {windows_scores.median():6.2f}")
        print(f"  差异    - 均值: {group_df['abs_diff'].mean():7.4f}, 最大值: {group_df['abs_diff'].max():6.2f}")

    # 详细对比表
    print("\n📝 详细对比 (前20例)")
    print("-" * 80)
    print(f"{'Patient ID':<35} {'Colab':>10} {'Windows':>10} {'差异':>10} {'%':>8}")
    print("-" * 80)

    display_df = merged_df.sort_values('abs_diff', ascending=False).head(20)
    for _, row in display_df.iterrows():
        pid = row['patient_id'][:33]
        colab_score = row['agatston_score_colab']
        windows_score = row['agatston_score_windows']
        diff = row['abs_diff']
        rel = row['rel_diff']

        marker = "⚠️" if diff >= 1 else "✓"
        print(f"{pid:<35} {colab_score:>10.1f} {windows_score:>10.1f} {diff:>10.4f} {rel:>7.2f}% {marker}")

    # 不一致案例
    if diff_gte_1pct > 0:
        print("\n⚠️ 相对差异≥1%的案例 (需要关注)")
        print("-" * 80)
        problem_df = merged_df[merged_df['rel_diff'] >= 1].copy()
        print(f"{'Patient ID':<35} {'Colab':>10} {'Windows':>10} {'差异':>10} {'%':>8}")
        print("-" * 80)
        for _, row in problem_df.iterrows():
            pid = row['patient_id'][:33]
            print(f"{pid:<35} {row['agatston_score_colab']:>10.1f} "
                  f"{row['agatston_score_windows']:>10.1f} "
                  f"{row['abs_diff']:>10.4f} {row['rel_diff']:>7.2f}%")

    # 结论
    print("\n" + "=" * 80)
    print("🎯 验证结论")
    print("=" * 80)

    if identical == len(merged_df):
        print("✅ 完美！所有{len(merged_df)}例结果完全一致")
        print("   Colab和Windows版本结果一致，可以放心继续Full模式")
    elif diff_lt_1 == len(merged_df):
        print(f"✅ 优秀！所有{len(merged_df)}例差异<1分 (可接受的浮点误差)")
        print("   结果高度一致，可以继续Full模式")
    elif diff_lt_1pct >= len(merged_df) * 0.95:
        print(f"✅ 良好！{diff_lt_1pct}/{len(merged_df)}例相对差异<1%")
        print("   结果基本一致，可以继续Full模式")
    else:
        print(f"⚠️ 注意！有{diff_gte_1pct}例相对差异≥1%")
        print("   建议调查原因后再继续Full模式")

    print("\n💡 建议:")
    if diff_gte_1pct == 0:
        print("  ✓ 验证通过，立即启动Full模式(199例)")
    else:
        print("  ⚠️ 调查差异原因:")
        print("     1. 检查SLICE_BATCH_SIZE差异影响")
        print("     2. 考虑修改为16匹配Colab")
        print("     3. 重新测试问题案例")

    print("=" * 80)

if __name__ == "__main__":
    main()
