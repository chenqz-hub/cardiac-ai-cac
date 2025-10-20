"""
Check DICOM Metadata for Age and Gender Information
====================================================

This script checks if DICOM files contain patient age and gender information,
which is important for premature CAD (coronary artery disease) analysis.

Premature CAD criteria:
- Male: < 55 years old
- Female: < 65 years old

Author: NB10 Windows Tool
Version: 1.0.0
Date: 2025-10-15
"""

import pydicom
import sys
from pathlib import Path
from collections import defaultdict


def extract_patient_info(dcm_file):
    """Extract patient demographic information from DICOM file"""
    try:
        dcm = pydicom.dcmread(dcm_file, stop_before_pixels=True)

        info = {
            'patient_id': None,
            'patient_age': None,
            'patient_sex': None,
            'patient_birth_date': None,
            'study_date': None,
        }

        # Patient ID
        if hasattr(dcm, 'PatientID'):
            info['patient_id'] = str(dcm.PatientID)

        # Patient Age (formatted as "055Y" or similar)
        if hasattr(dcm, 'PatientAge'):
            age_str = str(dcm.PatientAge)
            # Parse age string (e.g., "055Y" -> 55)
            if age_str.endswith('Y'):
                try:
                    info['patient_age'] = int(age_str[:-1])
                except:
                    pass
            info['patient_age_raw'] = age_str

        # Patient Sex (M/F)
        if hasattr(dcm, 'PatientSex'):
            info['patient_sex'] = str(dcm.PatientSex).upper()

        # Patient Birth Date (YYYYMMDD)
        if hasattr(dcm, 'PatientBirthDate'):
            info['patient_birth_date'] = str(dcm.PatientBirthDate)

        # Study Date (YYYYMMDD) - can calculate age from birth date
        if hasattr(dcm, 'StudyDate'):
            info['study_date'] = str(dcm.StudyDate)

        # Calculate age from birth date and study date if age not directly available
        if info['patient_age'] is None and info['patient_birth_date'] and info['study_date']:
            try:
                birth_year = int(info['patient_birth_date'][:4])
                study_year = int(info['study_date'][:4])
                info['patient_age'] = study_year - birth_year
                info['patient_age_calculated'] = True
            except:
                pass

        return info

    except Exception as e:
        return {'error': str(e)}


def check_premature_cad_criteria(age, sex):
    """Check if patient meets premature CAD age criteria"""
    if age is None or sex is None:
        return None

    if sex == 'M' and age < 55:
        return True
    elif sex == 'F' and age < 65:
        return True
    else:
        return False


def scan_patient_directory(patient_dir):
    """Scan a patient directory and extract info from first DICOM file"""
    patient_dir = Path(patient_dir)

    # Find first DICOM file
    dcm_files = list(patient_dir.rglob("*.dcm"))
    if not dcm_files:
        return None

    # Extract info from first file (all files should have same patient info)
    info = extract_patient_info(dcm_files[0])
    info['patient_folder'] = patient_dir.name
    info['num_dcm_files'] = len(dcm_files)

    return info


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_dicom_metadata.py <data_dir> [--sample N]")
        print()
        print("Examples:")
        print("  python check_dicom_metadata.py ../../data/raw/dicom")
        print("  python check_dicom_metadata.py ../../data/raw/dicom --sample 10")
        sys.exit(1)

    data_dir = Path(sys.argv[1])

    # Check for --sample flag
    sample_size = None
    if '--sample' in sys.argv:
        idx = sys.argv.index('--sample')
        if idx + 1 < len(sys.argv):
            sample_size = int(sys.argv[idx + 1])

    if not data_dir.exists():
        print(f"Error: Directory not found: {data_dir}")
        sys.exit(1)

    # Find all patient directories
    patient_dirs = sorted([d for d in data_dir.iterdir() if d.is_dir()])

    if not patient_dirs:
        print(f"Error: No patient directories found in {data_dir}")
        sys.exit(1)

    print("=" * 80)
    print("DICOM Metadata Analysis - Patient Demographics")
    print("=" * 80)
    print(f"Data directory: {data_dir}")
    print(f"Total patient folders: {len(patient_dirs)}")

    if sample_size:
        patient_dirs = patient_dirs[:sample_size]
        print(f"Sampling first {sample_size} patients")

    print()

    # Scan all patients
    results = []
    stats = {
        'has_age': 0,
        'has_sex': 0,
        'has_both': 0,
        'premature_cad': 0,
        'not_premature_cad': 0,
        'cannot_determine': 0,
        'male': 0,
        'female': 0,
        'errors': 0
    }

    print("Scanning patient folders...")
    for i, patient_dir in enumerate(patient_dirs, 1):
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(patient_dirs)}")

        info = scan_patient_directory(patient_dir)
        if info is None:
            print(f"  Warning: No DICOM files in {patient_dir.name}")
            continue

        if 'error' in info:
            stats['errors'] += 1
            continue

        results.append(info)

        # Update statistics
        if info.get('patient_age') is not None:
            stats['has_age'] += 1
        if info.get('patient_sex') is not None:
            stats['has_sex'] += 1
            if info['patient_sex'] == 'M':
                stats['male'] += 1
            elif info['patient_sex'] == 'F':
                stats['female'] += 1

        if info.get('patient_age') is not None and info.get('patient_sex') is not None:
            stats['has_both'] += 1

            is_premature = check_premature_cad_criteria(info['patient_age'], info['patient_sex'])
            if is_premature:
                stats['premature_cad'] += 1
            elif is_premature is False:
                stats['not_premature_cad'] += 1
        else:
            stats['cannot_determine'] += 1

    print(f"  Completed: {len(results)}/{len(patient_dirs)}")
    print()

    # Print summary statistics
    print("-" * 80)
    print("Summary Statistics")
    print("-" * 80)
    print(f"Successfully scanned: {len(results)}")
    print(f"Errors: {stats['errors']}")
    print()

    print(f"Patients with Age info: {stats['has_age']} ({stats['has_age']/len(results)*100:.1f}%)")
    print(f"Patients with Sex info: {stats['has_sex']} ({stats['has_sex']/len(results)*100:.1f}%)")
    print(f"Patients with both Age & Sex: {stats['has_both']} ({stats['has_both']/len(results)*100:.1f}%)")
    print()

    if stats['has_sex'] > 0:
        print(f"Gender distribution:")
        print(f"  Male: {stats['male']} ({stats['male']/stats['has_sex']*100:.1f}%)")
        print(f"  Female: {stats['female']} ({stats['female']/stats['has_sex']*100:.1f}%)")
        print()

    if stats['has_both'] > 0:
        print("-" * 80)
        print("Premature CAD Criteria Check (Male <55, Female <65)")
        print("-" * 80)
        print(f"Meets premature CAD criteria: {stats['premature_cad']} ({stats['premature_cad']/stats['has_both']*100:.1f}%)")
        print(f"Does NOT meet criteria: {stats['not_premature_cad']} ({stats['not_premature_cad']/stats['has_both']*100:.1f}%)")
        print(f"Cannot determine: {stats['cannot_determine']}")
        print()

    # Show detailed sample
    print("-" * 80)
    print("Sample Patient Information (first 10)")
    print("-" * 80)
    print(f"{'Patient Folder':<30} {'Age':<8} {'Sex':<6} {'Premature CAD':<15}")
    print("-" * 80)

    for info in results[:10]:
        age = info.get('patient_age', 'N/A')
        sex = info.get('patient_sex', 'N/A')
        age_str = str(age) if age != 'N/A' else 'N/A'
        if info.get('patient_age_calculated'):
            age_str += '*'

        premature = check_premature_cad_criteria(info.get('patient_age'), info.get('patient_sex'))
        premature_str = 'Yes' if premature else ('No' if premature is False else 'Unknown')

        print(f"{info['patient_folder']:<30} {age_str:<8} {sex:<6} {premature_str:<15}")

    if len(results) > 10:
        print(f"... and {len(results) - 10} more")

    print()
    print("Note: Age with * is calculated from birth date and study date")
    print()

    # Print conclusion
    print("=" * 80)
    print("Conclusion")
    print("=" * 80)

    if stats['has_both'] > 0:
        coverage = stats['has_both'] / len(results) * 100
        print(f"✓ {coverage:.1f}% of patients have both age and sex information in DICOM metadata")
        print()

        if stats['premature_cad'] > 0:
            premature_pct = stats['premature_cad'] / stats['has_both'] * 100
            print(f"✓ {premature_pct:.1f}% of patients meet premature CAD age criteria")
            print("  (Male <55 years, Female <65 years)")
            print()

            if premature_pct > 80:
                print("✓ GOOD: Most patients are in premature CAD age range")
                print("  This confirms the study cohort selection")
            elif premature_pct < 50:
                print("⚠ WARNING: Less than half of patients meet premature CAD criteria")
                print("  Please verify the cohort selection")
            else:
                print("~ MIXED: Some patients are outside premature CAD age range")
                print("  Consider age-stratified analysis")
    else:
        print("✗ DICOM files do not contain sufficient age/sex information")
        print("  Age and sex data needs to be provided separately")

    print()
    print("Recommendations:")
    print("1. If age/sex data is available: extract and include in analysis")
    print("2. Add age/sex fields to CSV output for stratified analysis")
    print("3. Validate premature CAD criteria compliance")
    print("4. Update documentation to reflect study population characteristics")
    print()
    print("=" * 80)


if __name__ == '__main__':
    main()
