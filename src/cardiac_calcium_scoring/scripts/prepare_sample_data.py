#!/usr/bin/env python3
"""
Prepare Sample Data for NB10 Windows Tool

This script copies 5-10 representative cases from the full dataset
to examples/sample_data/ for testing and demonstration purposes.

Usage:
    python scripts/prepare_sample_data.py --source <data_dir> --output examples/sample_data
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Prepare sample DICOM data for NB10 testing"
    )

    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Source directory containing full DICOM dataset (with chd/ and normal/ subdirs)"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="examples/sample_data",
        help="Output directory for sample data (default: examples/sample_data)"
    )

    parser.add_argument(
        "--results",
        type=str,
        help="Path to ai_cac_scores.csv to select representative cases (optional)"
    )

    parser.add_argument(
        "--num-cases",
        type=int,
        default=5,
        help="Number of cases to prepare (default: 5, range: 5-10)"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing sample data"
    )

    return parser.parse_args()


def select_representative_cases(results_csv, num_cases=5):
    """
    Select representative cases covering different Agatston score ranges

    Strategy:
    - CHD group: 1 zero calcium, 1 low (1-100), 1 high (>400)
    - Normal group: 1 zero calcium, 1 low (1-100)
    """
    df = pd.read_csv(results_csv)
    df_success = df[df['status'] == 'success'].copy()

    selected = []

    # CHD group
    chd_df = df_success[df_success['group'] == 'chd']

    # CHD: zero calcium
    chd_zero = chd_df[chd_df['agatston_score'] == 0]
    if not chd_zero.empty:
        selected.append(chd_zero.iloc[0])

    # CHD: low score (1-100)
    chd_low = chd_df[(chd_df['agatston_score'] > 0) & (chd_df['agatston_score'] <= 100)]
    if not chd_low.empty:
        selected.append(chd_low.iloc[0])

    # CHD: high score (>400)
    chd_high = chd_df[chd_df['agatston_score'] > 400]
    if not chd_high.empty:
        selected.append(chd_high.iloc[0])

    # Normal group
    normal_df = df_success[df_success['group'] == 'normal']

    # Normal: zero calcium
    normal_zero = normal_df[normal_df['agatston_score'] == 0]
    if not normal_zero.empty:
        selected.append(normal_zero.iloc[0])

    # Normal: low score (1-100)
    normal_low = normal_df[(normal_df['agatston_score'] > 0) & (normal_df['agatston_score'] <= 100)]
    if not normal_low.empty:
        selected.append(normal_low.iloc[0])

    return selected[:num_cases]


def copy_dicom_case(source_dir, patient_id, group, output_dir):
    """Copy a single DICOM case to output directory"""
    src_case_dir = Path(source_dir) / group / patient_id
    dst_case_dir = Path(output_dir) / group / patient_id

    if not src_case_dir.exists():
        print(f"  ⚠️ Source directory not found: {src_case_dir}")
        return False

    try:
        # Create destination directory
        dst_case_dir.parent.mkdir(parents=True, exist_ok=True)

        # Copy directory
        if dst_case_dir.exists():
            shutil.rmtree(dst_case_dir)

        shutil.copytree(src_case_dir, dst_case_dir)

        # Count DICOM files
        dcm_files = list(dst_case_dir.glob("*.dcm"))
        num_files = len(dcm_files)
        total_size = sum(f.stat().st_size for f in dcm_files) / (1024 * 1024)  # MB

        print(f"  ✅ Copied: {patient_id} ({num_files} files, {total_size:.1f}MB)")
        return True

    except Exception as e:
        print(f"  ❌ Failed to copy {patient_id}: {e}")
        return False


def create_sample_readme(output_dir, selected_cases):
    """Create README for sample data"""
    readme_path = Path(output_dir) / "README.md"

    content = "# Sample DICOM Data\n\n"
    content += "This directory contains representative DICOM cases for testing NB10 tool.\n\n"
    content += "## Cases\n\n"
    content += "| Patient ID | Group | Agatston Score | Slices | Description |\n"
    content += "|------------|-------|----------------|--------|-------------|\n"

    for case in selected_cases:
        patient_id = case['patient_id']
        group = case['group']
        score = case['agatston_score']
        slices = int(case['num_slices']) if 'num_slices' in case else 'N/A'

        if score == 0:
            desc = "Zero calcium"
        elif score <= 100:
            desc = "Low calcium (1-100)"
        elif score <= 400:
            desc = "Moderate calcium (101-400)"
        else:
            desc = "High calcium (>400)"

        content += f"| {patient_id} | {group} | {score:.1f} | {slices} | {desc} |\n"

    content += "\n## Usage\n\n"
    content += "```bash\n"
    content += "# Test with sample data\n"
    content += "python cli/run_nb10.py --data-dir examples/sample_data --mode pilot\n"
    content += "```\n\n"
    content += "## Notes\n\n"
    content += "- Data has been de-identified\n"
    content += "- For testing and demonstration only\n"
    content += "- Not suitable for research use\n\n"
    content += "**Generated**: " + pd.Timestamp.now().strftime("%Y-%m-%d") + "\n"

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  ✅ Created: {readme_path}")


def main():
    """Main function"""
    args = parse_args()

    print("="*60)
    print("Preparing Sample Data for NB10 Windows Tool")
    print("="*60)

    # Validate source directory
    source_dir = Path(args.source)
    if not source_dir.exists():
        print(f"❌ Error: Source directory not found: {source_dir}")
        sys.exit(1)

    if not (source_dir / "chd").exists() or not (source_dir / "normal").exists():
        print(f"❌ Error: Source directory must contain 'chd/' and 'normal/' subdirectories")
        sys.exit(1)

    # Validate output directory
    output_dir = Path(args.output)
    if output_dir.exists() and not args.force:
        print(f"⚠️ Warning: Output directory already exists: {output_dir}")
        response = input("Overwrite? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            sys.exit(0)

    # Select cases
    print(f"\n📊 Selecting {args.num_cases} representative cases...")

    if args.results:
        print(f"   Using results from: {args.results}")
        selected_cases = select_representative_cases(args.results, args.num_cases)
    else:
        print(f"   ⚠️ No results file provided, will copy first {args.num_cases} cases")
        # Fallback: just copy first N cases
        selected_cases = []
        for group in ['chd', 'normal']:
            group_dir = source_dir / group
            cases = sorted([d.name for d in group_dir.iterdir() if d.is_dir()])
            num_from_group = args.num_cases // 2 if group == 'chd' else (args.num_cases - args.num_cases // 2)
            for case_id in cases[:num_from_group]:
                selected_cases.append({
                    'patient_id': case_id,
                    'group': group,
                    'agatston_score': 0,  # Unknown
                    'num_slices': 0
                })

    if not selected_cases:
        print("❌ Error: No cases selected")
        sys.exit(1)

    print(f"   ✅ Selected {len(selected_cases)} cases")

    # Copy cases
    print(f"\n📂 Copying cases to: {output_dir}")

    success_count = 0
    for case in selected_cases:
        if copy_dicom_case(source_dir, case['patient_id'], case['group'], output_dir):
            success_count += 1

    print(f"\n✅ Successfully copied {success_count}/{len(selected_cases)} cases")

    # Create README
    print(f"\n📝 Creating sample data README...")
    create_sample_readme(output_dir, selected_cases)

    # Summary
    print("\n" + "="*60)
    print("Sample Data Preparation Complete")
    print("="*60)
    print(f"Output directory: {output_dir.absolute()}")
    print(f"Total cases: {len(selected_cases)}")

    # Calculate total size
    total_size = 0
    for group in ['chd', 'normal']:
        group_dir = output_dir / group
        if group_dir.exists():
            for case_dir in group_dir.iterdir():
                if case_dir.is_dir():
                    total_size += sum(f.stat().st_size for f in case_dir.rglob("*.dcm"))

    total_size_mb = total_size / (1024 * 1024)
    print(f"Total size: {total_size_mb:.1f}MB")

    print("\n💡 Test with sample data:")
    print(f"   python cli/run_nb10.py --data-dir {output_dir} --mode pilot")
    print("="*60)


if __name__ == "__main__":
    main()
