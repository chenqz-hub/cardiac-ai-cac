"""
CHD vs Normal Group Statistical Analysis - Premature CAD Study
================================================================

Compare AI-CAC results between CHD (coronary heart disease) and Normal groups
in premature CAD patients (Male <55, Female <65).

Author: NB10 Windows Tool
Version: 1.1.0
Date: 2025-10-15
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import sys


def load_results(chd_csv, normal_csv):
    """Load CHD and Normal group results"""
    chd_df = pd.read_csv(chd_csv)
    chd_df['group'] = 'CHD'

    normal_df = pd.read_csv(normal_csv)
    normal_df['group'] = 'Normal'

    # Filter successful cases only
    chd_df = chd_df[chd_df['status'] == 'success']
    normal_df = normal_df[normal_df['status'] == 'success']

    return chd_df, normal_df


def compute_statistics(df, group_name):
    """Compute descriptive statistics"""
    scores = df['agatston_score']

    stats_dict = {
        'Group': group_name,
        'N': len(scores),
        'Mean': scores.mean(),
        'Std': scores.std(),
        'Median': scores.median(),
        'Min': scores.min(),
        'Max': scores.max(),
        'Q1': scores.quantile(0.25),
        'Q3': scores.quantile(0.75),
        'IQR': scores.quantile(0.75) - scores.quantile(0.25)
    }

    return stats_dict


def risk_stratification(score):
    """Classify into risk categories"""
    if score == 0:
        return 'Very Low (0)'
    elif score <= 100:
        return 'Low (1-100)'
    elif score <= 400:
        return 'Moderate (101-400)'
    else:
        return 'High (>400)'


def compute_risk_distribution(df):
    """Compute risk category distribution"""
    df['risk_category'] = df['agatston_score'].apply(risk_stratification)
    risk_dist = df['risk_category'].value_counts().sort_index()
    risk_pct = (risk_dist / len(df) * 100).round(1)

    return risk_dist, risk_pct


def compare_groups(chd_df, normal_df):
    """Statistical comparison between groups"""
    chd_scores = chd_df['agatston_score']
    normal_scores = normal_df['agatston_score']

    # Mann-Whitney U test (non-parametric, for skewed distributions)
    statistic, p_value = stats.mannwhitneyu(chd_scores, normal_scores, alternative='two-sided')

    # Effect size (Cliff's Delta)
    # Range: -1 to 1, 0 = no effect
    n1, n2 = len(chd_scores), len(normal_scores)
    dominance = sum(1 for c in chd_scores for n in normal_scores if c > n)
    cliffs_delta = (2 * dominance - n1 * n2) / (n1 * n2)

    return {
        'mann_whitney_u': statistic,
        'p_value': p_value,
        'cliffs_delta': cliffs_delta,
        'significant': p_value < 0.05
    }


def analyze_demographics(chd_df, normal_df):
    """Analyze age and sex demographics"""
    result = {
        'has_demographics': False,
        'chd_age_available': 0,
        'normal_age_available': 0,
        'chd_sex_available': 0,
        'normal_sex_available': 0,
    }

    # Check if demographic columns exist
    if 'patient_age' not in chd_df.columns or 'patient_age' not in normal_df.columns:
        return result

    result['has_demographics'] = True

    # Count available demographics
    result['chd_age_available'] = chd_df['patient_age'].notna().sum()
    result['normal_age_available'] = normal_df['patient_age'].notna().sum()
    result['chd_sex_available'] = chd_df['patient_sex'].notna().sum()
    result['normal_sex_available'] = normal_df['patient_sex'].notna().sum()

    # Age statistics
    if result['chd_age_available'] > 0:
        result['chd_age_mean'] = chd_df['patient_age'].mean()
        result['chd_age_std'] = chd_df['patient_age'].std()
        result['chd_age_range'] = (chd_df['patient_age'].min(), chd_df['patient_age'].max())

    if result['normal_age_available'] > 0:
        result['normal_age_mean'] = normal_df['patient_age'].mean()
        result['normal_age_std'] = normal_df['patient_age'].std()
        result['normal_age_range'] = (normal_df['patient_age'].min(), normal_df['patient_age'].max())

    # Sex distribution
    if result['chd_sex_available'] > 0:
        result['chd_sex_dist'] = chd_df['patient_sex'].value_counts().to_dict()

    if result['normal_sex_available'] > 0:
        result['normal_sex_dist'] = normal_df['patient_sex'].value_counts().to_dict()

    # Premature CAD compliance
    if 'is_premature_cad' in chd_df.columns:
        result['chd_premature_cad'] = chd_df['is_premature_cad'].sum()
        result['chd_premature_cad_pct'] = chd_df['is_premature_cad'].sum() / len(chd_df) * 100

    if 'is_premature_cad' in normal_df.columns:
        result['normal_premature_cad'] = normal_df['is_premature_cad'].sum()
        result['normal_premature_cad_pct'] = normal_df['is_premature_cad'].sum() / len(normal_df) * 100

    return result


def print_report(chd_df, normal_df, comparison):
    """Print formatted analysis report"""
    print("=" * 80)
    print("CHD vs Normal Group Analysis - Premature CAD Study")
    print("AI-CAC Coronary Calcium Scoring")
    print("=" * 80)
    print()

    # Study population note
    print("Study Population:")
    print("  Premature CAD patients (Male <55 years, Female <65 years)")
    print("  CHD group: Angiography confirmed, stent implanted")
    print("  Normal group: Angiography confirmed, no abnormality")
    print()

    # Sample sizes
    print("Sample Sizes:")
    print(f"  CHD Group: {len(chd_df)} cases")
    print(f"  Normal Group: {len(normal_df)} cases")
    print()

    # Demographics analysis
    demographics = analyze_demographics(chd_df, normal_df)

    if demographics['has_demographics']:
        print("-" * 80)
        print("Patient Demographics")
        print("-" * 80)

        # Age statistics
        if demographics.get('chd_age_available', 0) > 0:
            print(f"\nAge Distribution (years):")
            print(f"  CHD Group:")
            print(f"    Mean ± SD: {demographics['chd_age_mean']:.1f} ± {demographics['chd_age_std']:.1f}")
            print(f"    Range: {demographics['chd_age_range'][0]:.0f} - {demographics['chd_age_range'][1]:.0f}")
            print(f"    Available: {demographics['chd_age_available']}/{len(chd_df)}")

        if demographics.get('normal_age_available', 0) > 0:
            print(f"  Normal Group:")
            print(f"    Mean ± SD: {demographics['normal_age_mean']:.1f} ± {demographics['normal_age_std']:.1f}")
            print(f"    Range: {demographics['normal_age_range'][0]:.0f} - {demographics['normal_age_range'][1]:.0f}")
            print(f"    Available: {demographics['normal_age_available']}/{len(normal_df)}")

        # Sex distribution
        if demographics.get('chd_sex_available', 0) > 0 or demographics.get('normal_sex_available', 0) > 0:
            print(f"\nSex Distribution:")
            if 'chd_sex_dist' in demographics:
                chd_male = demographics['chd_sex_dist'].get('M', 0)
                chd_female = demographics['chd_sex_dist'].get('F', 0)
                print(f"  CHD Group: Male {chd_male} ({chd_male/len(chd_df)*100:.1f}%), "
                      f"Female {chd_female} ({chd_female/len(chd_df)*100:.1f}%)")

            if 'normal_sex_dist' in demographics:
                normal_male = demographics['normal_sex_dist'].get('M', 0)
                normal_female = demographics['normal_sex_dist'].get('F', 0)
                print(f"  Normal Group: Male {normal_male} ({normal_male/len(normal_df)*100:.1f}%), "
                      f"Female {normal_female} ({normal_female/len(normal_df)*100:.1f}%)")

        # Premature CAD criteria compliance
        if 'chd_premature_cad' in demographics:
            print(f"\nPremature CAD Criteria Compliance:")
            print(f"  CHD Group: {demographics['chd_premature_cad']}/{len(chd_df)} "
                  f"({demographics['chd_premature_cad_pct']:.1f}%) meet criteria")
            print(f"  Normal Group: {demographics['normal_premature_cad']}/{len(normal_df)} "
                  f"({demographics['normal_premature_cad_pct']:.1f}%) meet criteria")

        print()

    # Descriptive statistics
    print("-" * 80)
    print("Descriptive Statistics (Agatston Score)")
    print("-" * 80)

    chd_stats = compute_statistics(chd_df, 'CHD')
    normal_stats = compute_statistics(normal_df, 'Normal')

    # Print as table
    print(f"{'Metric':<15} {'CHD':>15} {'Normal':>15} {'Difference':>15}")
    print("-" * 65)
    print(f"{'N':<15} {chd_stats['N']:>15} {normal_stats['N']:>15} {'':<15}")
    print(f"{'Mean':<15} {chd_stats['Mean']:>15.2f} {normal_stats['Mean']:>15.2f} {chd_stats['Mean']-normal_stats['Mean']:>15.2f}")
    print(f"{'Std':<15} {chd_stats['Std']:>15.2f} {normal_stats['Std']:>15.2f} {'':<15}")
    print(f"{'Median':<15} {chd_stats['Median']:>15.2f} {normal_stats['Median']:>15.2f} {chd_stats['Median']-normal_stats['Median']:>15.2f}")
    print(f"{'Min':<15} {chd_stats['Min']:>15.2f} {normal_stats['Min']:>15.2f} {'':<15}")
    print(f"{'Max':<15} {chd_stats['Max']:>15.2f} {normal_stats['Max']:>15.2f} {'':<15}")
    print(f"{'Q1':<15} {chd_stats['Q1']:>15.2f} {normal_stats['Q1']:>15.2f} {'':<15}")
    print(f"{'Q3':<15} {chd_stats['Q3']:>15.2f} {normal_stats['Q3']:>15.2f} {'':<15}")
    print()

    # Risk stratification
    print("-" * 80)
    print("Risk Stratification")
    print("-" * 80)

    chd_risk_dist, chd_risk_pct = compute_risk_distribution(chd_df)
    normal_risk_dist, normal_risk_pct = compute_risk_distribution(normal_df)

    all_categories = ['Very Low (0)', 'Low (1-100)', 'Moderate (101-400)', 'High (>400)']

    print(f"{'Risk Category':<25} {'CHD N':>12} {'CHD %':>10} {'Normal N':>12} {'Normal %':>10}")
    print("-" * 75)
    for cat in all_categories:
        chd_n = chd_risk_dist.get(cat, 0)
        chd_p = chd_risk_pct.get(cat, 0)
        normal_n = normal_risk_dist.get(cat, 0)
        normal_p = normal_risk_pct.get(cat, 0)
        print(f"{cat:<25} {chd_n:>12} {chd_p:>9.1f}% {normal_n:>12} {normal_p:>9.1f}%")
    print()

    # Statistical comparison
    print("-" * 80)
    print("Statistical Comparison")
    print("-" * 80)
    print(f"Mann-Whitney U statistic: {comparison['mann_whitney_u']:.2f}")
    print(f"P-value: {comparison['p_value']:.4f}")
    print(f"Significant (p < 0.05): {'Yes' if comparison['significant'] else 'No'}")
    print()
    print(f"Effect Size (Cliff's Delta): {comparison['cliffs_delta']:.3f}")
    if abs(comparison['cliffs_delta']) < 0.147:
        effect = "negligible"
    elif abs(comparison['cliffs_delta']) < 0.330:
        effect = "small"
    elif abs(comparison['cliffs_delta']) < 0.474:
        effect = "medium"
    else:
        effect = "large"
    print(f"Effect size interpretation: {effect}")
    print()

    # Clinical interpretation
    print("-" * 80)
    print("Clinical Interpretation")
    print("-" * 80)
    if comparison['significant']:
        if chd_stats['Mean'] > normal_stats['Mean']:
            print("CHD group has significantly HIGHER Agatston scores than Normal group.")
        else:
            print("CHD group has significantly LOWER Agatston scores than Normal group.")
    else:
        print("No significant difference in Agatston scores between CHD and Normal groups.")
    print()

    # Calcification prevalence
    chd_with_calc = (chd_df['has_calcification'] == True).sum()
    normal_with_calc = (normal_df['has_calcification'] == True).sum()

    print(f"Calcification Prevalence:")
    print(f"  CHD: {chd_with_calc}/{len(chd_df)} ({chd_with_calc/len(chd_df)*100:.1f}%)")
    print(f"  Normal: {normal_with_calc}/{len(normal_df)} ({normal_with_calc/len(normal_df)*100:.1f}%)")
    print()

    print("=" * 80)


def main():
    if len(sys.argv) != 3:
        print("Usage: python analyze_chd_vs_normal.py <chd_csv> <normal_csv>")
        print()
        print("Example:")
        print("  python analyze_chd_vs_normal.py output/chd_results.csv output/normal_results.csv")
        sys.exit(1)

    chd_csv = sys.argv[1]
    normal_csv = sys.argv[2]

    # Check files exist
    if not Path(chd_csv).exists():
        print(f"Error: CHD CSV not found: {chd_csv}")
        sys.exit(1)

    if not Path(normal_csv).exists():
        print(f"Error: Normal CSV not found: {normal_csv}")
        sys.exit(1)

    # Load data
    print("Loading data...")
    chd_df, normal_df = load_results(chd_csv, normal_csv)

    # Perform comparison
    comparison = compare_groups(chd_df, normal_df)

    # Print report
    print_report(chd_df, normal_df, comparison)


if __name__ == '__main__':
    main()
