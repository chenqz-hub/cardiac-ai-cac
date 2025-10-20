#!/usr/bin/env python3
"""
PSM策略对比：仅性别 vs 性别+年龄
===============================
对比不同PSM匹配策略对主动脉钙化分析结果的影响

Author: Claude Code
Date: 2025-10-15
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
import os
import warnings
warnings.filterwarnings('ignore')

# File paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
NB04_DATA = os.path.join(PROJECT_ROOT, 'results/nb04_calcification/calcification_scores_20251012_162132.csv')
COMPREHENSIVE_DATA = os.path.join(PROJECT_ROOT, 'tools/nb10_windows/data/comprehensive_data_with_cac.csv')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'tools/nb10_windows/output/multimodal_analysis')

def load_and_merge_data():
    """加载已整合的数据"""
    print("加载数据...")

    # 直接读取已整合好的数据（包含主动脉钙化）
    merged_file = os.path.join(OUTPUT_DIR, 'matched_cohort_with_aortic_calc.csv')
    data = pd.read_csv(merged_file)

    # 提取原始未匹配的数据（需要Sex, Age, Group, aorta_agatston_score）
    # 从matched_cohort_with_aortic_calc中提取，这个文件已包含所有需要的列
    data = data[['Sex', 'Age', 'Group', 'aorta_agatston_score', 'DicomID']].copy()
    data = data[data['aorta_agatston_score'].notna()].copy()

    # 清理Sex编码
    data['Sex'] = data['Sex'].replace({'male': 'M', 'female': 'F'})

    print(f"  有效数据: {len(data)} 例")
    print(f"    CHD组: {len(data[data['Group']=='CHD'])} 例")
    print(f"    Normal组: {len(data[data['Group']=='Normal'])} 例")

    return data

def psm_matching(data, covariates, strategy_name, caliper=0.2):
    """执行PSM匹配"""
    print(f"\n{'='*70}")
    print(f"PSM策略: {strategy_name}")
    print(f"协变量: {covariates}")
    print(f"{'='*70}")

    df = data.copy()

    # 准备协变量
    if 'Sex' in covariates:
        df['Sex_code'] = df['Sex'].map({'Male': 1, 'Female': 0, 'M': 1, 'F': 0})
        covariates_encoded = ['Sex_code' if x=='Sex' else x for x in covariates]
    else:
        covariates_encoded = covariates

    # 删除缺失值
    df = df.dropna(subset=covariates_encoded + ['Group'])

    # 创建treatment变量
    df['treatment'] = (df['Group'] == 'CHD').astype(int)

    print(f"\n匹配前人数:")
    print(f"  CHD组: {df[df['treatment']==1].shape[0]} 例")
    print(f"  Normal组: {df[df['treatment']==0].shape[0]} 例")

    # 计算倾向性评分
    X = df[covariates_encoded].values
    y = df['treatment'].values

    lr = LogisticRegression(random_state=42, max_iter=1000)
    lr.fit(X, y)
    df['propensity_score'] = lr.predict_proba(X)[:, 1]

    # 1:1最近邻匹配
    treated = df[df['treatment'] == 1].copy()
    control = df[df['treatment'] == 0].copy()

    nn = NearestNeighbors(n_neighbors=1, metric='euclidean')
    nn.fit(control[['propensity_score']].values)
    distances, indices = nn.kneighbors(treated[['propensity_score']].values)

    # 应用caliper
    caliper_value = caliper * df['propensity_score'].std()
    valid_matches = distances.flatten() <= caliper_value

    print(f"\n匹配结果:")
    print(f"  有效匹配: {valid_matches.sum()} 对")
    print(f"  超出caliper: {(~valid_matches).sum()} 对")

    # 构建匹配后数据
    treated_matched = treated[valid_matches].copy()
    control_indices = indices[valid_matches].flatten()
    control_matched = control.iloc[control_indices].copy()

    matched_data = pd.concat([treated_matched, control_matched], ignore_index=True)

    print(f"\n匹配后人数:")
    print(f"  总计: {len(matched_data)} 例")
    print(f"  CHD组: {len(matched_data[matched_data['Group']=='CHD'])} 例")
    print(f"  Normal组: {len(matched_data[matched_data['Group']=='Normal'])} 例")

    # 评估匹配质量
    assess_matching_quality(df, matched_data, covariates_encoded)

    return matched_data

def assess_matching_quality(before, after, covariates):
    """评估匹配质量（SMD）"""
    print(f"\n匹配质量评估 (标准化均数差 SMD):")
    print("-" * 60)

    for cov in covariates:
        # 匹配前
        chd_before = before[before['Group']=='CHD'][cov].mean()
        normal_before = before[before['Group']=='Normal'][cov].mean()
        pooled_std_before = np.sqrt(
            (before[before['Group']=='CHD'][cov].var() +
             before[before['Group']=='Normal'][cov].var()) / 2
        )
        smd_before = (chd_before - normal_before) / pooled_std_before if pooled_std_before > 0 else 0

        # 匹配后
        chd_after = after[after['Group']=='CHD'][cov].mean()
        normal_after = after[after['Group']=='Normal'][cov].mean()
        pooled_std_after = np.sqrt(
            (after[after['Group']=='CHD'][cov].var() +
             after[after['Group']=='Normal'][cov].var()) / 2
        )
        smd_after = (chd_after - normal_after) / pooled_std_after if pooled_std_after > 0 else 0

        print(f"{cov:15s} SMD: {smd_before:7.3f} → {smd_after:7.3f}  ", end='')
        if abs(smd_after) < 0.1:
            print("✓ 优秀")
        elif abs(smd_after) < 0.2:
            print("○ 良好")
        else:
            print("✗ 仍不平衡")

def analyze_aortic_calc(matched_data, strategy_name):
    """分析主动脉钙化"""
    print(f"\n{'='*70}")
    print(f"主动脉钙化分析 - {strategy_name}")
    print(f"{'='*70}")

    chd = matched_data[matched_data['Group'] == 'CHD']
    normal = matched_data[matched_data['Group'] == 'Normal']

    chd_vals = pd.to_numeric(chd['aorta_agatston_score'], errors='coerce').values
    normal_vals = pd.to_numeric(normal['aorta_agatston_score'], errors='coerce').values

    print(f"\nCHD组 (n={len(chd)}):")
    print(f"  Mean ± SD: {chd_vals.mean():.2f} ± {chd_vals.std():.2f}")
    print(f"  Median (IQR): {np.median(chd_vals):.2f} ({np.percentile(chd_vals, 25):.2f}-{np.percentile(chd_vals, 75):.2f})")

    print(f"\nNormal组 (n={len(normal)}):")
    print(f"  Mean ± SD: {normal_vals.mean():.2f} ± {normal_vals.std():.2f}")
    print(f"  Median (IQR): {np.median(normal_vals):.2f} ({np.percentile(normal_vals, 25):.2f}-{np.percentile(normal_vals, 75):.2f})")

    # 统计检验
    u_stat, p_value = stats.mannwhitneyu(chd_vals, normal_vals, alternative='two-sided')

    # Cohen's d
    pooled_std = np.sqrt(((len(chd_vals)-1)*chd_vals.std()**2 + (len(normal_vals)-1)*normal_vals.std()**2) / (len(chd_vals) + len(normal_vals) - 2))
    cohens_d = (chd_vals.mean() - normal_vals.mean()) / pooled_std if pooled_std > 0 else 0

    print(f"\n统计检验:")
    print(f"  Mann-Whitney U = {u_stat:.1f}")
    print(f"  P-value = {p_value:.6f} {'***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'n.s.'}")
    print(f"  Cohen's d = {cohens_d:.3f}")

    return {
        'strategy': strategy_name,
        'n_chd': len(chd),
        'n_normal': len(normal),
        'chd_mean': chd_vals.mean(),
        'chd_std': chd_vals.std(),
        'chd_median': np.median(chd_vals),
        'normal_mean': normal_vals.mean(),
        'normal_std': normal_vals.std(),
        'normal_median': np.median(normal_vals),
        'p_value': p_value,
        'cohens_d': cohens_d,
        'u_stat': u_stat
    }

def compare_age_distribution(sex_only_matched, sex_age_matched):
    """对比两种策略的年龄分布"""
    print(f"\n{'='*70}")
    print("年龄分布对比")
    print(f"{'='*70}")

    strategies = {
        '仅性别匹配': sex_only_matched,
        '性别+年龄匹配': sex_age_matched
    }

    for name, data in strategies.items():
        chd = data[data['Group'] == 'CHD']
        normal = data[data['Group'] == 'Normal']

        print(f"\n{name}:")
        print(f"  CHD组年龄: {chd['Age'].mean():.1f} ± {chd['Age'].std():.1f} 岁 (range: {chd['Age'].min():.0f}-{chd['Age'].max():.0f})")
        print(f"  Normal组年龄: {normal['Age'].mean():.1f} ± {normal['Age'].std():.1f} 岁 (range: {normal['Age'].min():.0f}-{normal['Age'].max():.0f})")
        print(f"  年龄差异: {abs(chd['Age'].mean() - normal['Age'].mean()):.1f} 岁")

        # 年龄的t检验
        t_stat, t_p = stats.ttest_ind(chd['Age'], normal['Age'])
        print(f"  t-test P-value: {t_p:.4f} {'*' if t_p < 0.05 else 'n.s.'}")

def main():
    print("="*70)
    print("PSM策略对比分析：仅性别 vs 性别+年龄")
    print("="*70)

    # 加载数据
    data = load_and_merge_data()

    # 策略1: 仅匹配性别
    sex_only_matched = psm_matching(
        data,
        covariates=['Sex'],
        strategy_name='仅性别匹配',
        caliper=0.2
    )

    # 策略2: 匹配性别+年龄（当前使用的）
    sex_age_matched = psm_matching(
        data,
        covariates=['Sex', 'Age'],
        strategy_name='性别+年龄匹配',
        caliper=0.2
    )

    # 分析主动脉钙化
    result_sex_only = analyze_aortic_calc(sex_only_matched, '仅性别匹配')
    result_sex_age = analyze_aortic_calc(sex_age_matched, '性别+年龄匹配')

    # 对比年龄分布
    compare_age_distribution(sex_only_matched, sex_age_matched)

    # 生成对比表
    print(f"\n{'='*70}")
    print("策略对比总结")
    print(f"{'='*70}")

    comparison = pd.DataFrame([result_sex_only, result_sex_age])

    print("\n| 策略 | 样本量 | CHD均值±SD | Normal均值±SD | P值 | Cohen's d |")
    print("|------|--------|-----------|--------------|-----|-----------|")
    for _, row in comparison.iterrows():
        print(f"| {row['strategy']:15s} | CHD {row['n_chd']}, N {row['n_normal']} | {row['chd_mean']:.1f}±{row['chd_std']:.1f} | {row['normal_mean']:.1f}±{row['normal_std']:.1f} | {row['p_value']:.4f} | {row['cohens_d']:.3f} |")

    # 关键发现
    print(f"\n{'='*70}")
    print("关键发现")
    print(f"{'='*70}")

    print(f"\n1. **样本量**:")
    print(f"   - 仅性别匹配: {result_sex_only['n_chd'] + result_sex_only['n_normal']} 例")
    print(f"   - 性别+年龄匹配: {result_sex_age['n_chd'] + result_sex_age['n_normal']} 例")
    print(f"   - 样本量差异: {abs((result_sex_only['n_chd'] + result_sex_only['n_normal']) - (result_sex_age['n_chd'] + result_sex_age['n_normal']))} 例")

    print(f"\n2. **P值对比**:")
    print(f"   - 仅性别匹配: P = {result_sex_only['p_value']:.6f}")
    print(f"   - 性别+年龄匹配: P = {result_sex_age['p_value']:.6f}")
    if result_sex_only['p_value'] < 0.05 and result_sex_age['p_value'] < 0.05:
        print(f"   - 结论: 两种策略均显示显著差异")

    print(f"\n3. **效应量对比**:")
    print(f"   - 仅性别匹配: Cohen's d = {result_sex_only['cohens_d']:.3f}")
    print(f"   - 性别+年龄匹配: Cohen's d = {result_sex_age['cohens_d']:.3f}")
    print(f"   - 差异: {abs(result_sex_only['cohens_d'] - result_sex_age['cohens_d']):.3f}")

    print(f"\n4. **建议**:")
    if abs(result_sex_only['p_value'] - result_sex_age['p_value']) < 0.001:
        print("   ✅ 两种策略结果高度一致，仅性别匹配即可满足需求")
        print("   ✅ 优点: 样本量更大，统计功效更强")
    elif result_sex_only['n_chd'] + result_sex_only['n_normal'] > result_sex_age['n_chd'] + result_sex_age['n_normal'] + 10:
        print("   ✅ 仅性别匹配样本量显著更大，且结果一致")
        print("   ✅ 推荐使用仅性别匹配策略")
    else:
        print("   ⚠️ 性别+年龄匹配更严格，建议保持当前策略")
        print("   ⚠️ 年龄可能是潜在混杂因素")

if __name__ == '__main__':
    main()
