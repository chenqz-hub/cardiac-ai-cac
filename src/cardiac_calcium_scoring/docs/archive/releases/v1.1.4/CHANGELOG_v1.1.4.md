# NB10 AI-CAC Tool - Version 1.1.4 Release Notes

**Release Date**: 2025-10-17
**Type**: Critical Bug Fix Release

---

## 🐛 Critical Bug Fixes

### Fixed: Program Hanging on Last Patient Case

**Issue**: When processing multiple patients (e.g., 5 cases in pilot mode), the program would hang indefinitely after completing the last patient, appearing stuck at "Running AI analysis..." with no error message.

**Root Cause**: DataLoader with `num_workers > 0` failed to properly terminate worker processes after the last iteration, causing the main process to wait indefinitely for worker cleanup.

**Solution**:
- Forced `num_workers = 0` for single-patient inference (no performance impact as each patient is processed sequentially)
- Added explicit DataLoader cleanup in try-finally block to ensure proper resource release
- Modified code locations:
  - `core/ai_cac_inference_lib.py` lines 249-255: Force num_workers=0
  - `core/ai_cac_inference_lib.py` lines 290-372: Add try-finally cleanup

**Verification**:
- ✅ Tested with 5 consecutive cases on GPU (RTX 2060)
- ✅ All cases completed successfully in 69.4s (avg 13.9s/case)
- ✅ No hanging on last case
- ✅ Program exits normally

---

## 🔧 Minor Fixes

### Updated PyDicom API Call

**Issue**: `pydicom.read_file()` is deprecated and will be removed in future versions, causing warnings.

**Solution**: Updated to use `pydicom.dcmread()` (modern API)
- Modified `core/processing.py` line 16

---

## 📊 Testing Summary

**Test Configuration**:
- Environment: Linux + NVIDIA RTX 2060 GPU
- Test cases: 5 patients
- Mode: GPU inference

**Results**:
```
Total cases: 5
Success: 5/5 (100%)
Failed: 0
Total time: 69.4s (1.2min)
Avg time/case: 13.9s
```

**Sample Agatston Scores**:
- Patient 1: 153.0
- Patient 2: 794.0
- Patient 3: 0.0
- Patient 4: 0.0
- Patient 5: 2.0

---

## 🚀 Upgrade Instructions

### For Existing Users:

1. **Backup your current installation** (optional but recommended)

2. **Replace the following files** with v1.1.4 versions:
   - `cli/run_nb10.py`
   - `core/ai_cac_inference_lib.py`
   - `core/processing.py`

3. **No configuration changes needed** - Your existing `config.yaml` will work as-is

4. **Resume feature compatibility** - Existing `.nb10_resume_cache.csv` files are fully compatible

### For New Users:

Follow the standard installation instructions in `README.md` or `docs/INSTALLATION_GUIDE.md`

---

## 🔍 Technical Details

### What Changed Internally

**Before (v1.1.3)**:
- DataLoader used `num_workers` from performance profile (could be > 0)
- No explicit cleanup mechanism
- Worker processes sometimes failed to terminate after last iteration

**After (v1.1.4)**:
- DataLoader always uses `num_workers = 0` for single-patient inference
- Try-finally block ensures cleanup even if exception occurs
- Explicit worker shutdown call added as safety measure

**Why This Works**:
- Single-patient inference processes one DICOM folder at a time
- No opportunity for parallel loading across patients
- Main-process loading eliminates worker management overhead
- No performance loss (multiprocessing wasn't beneficial in this scenario)

---

## 📝 Version History

- **v1.1.4** (2025-10-17): Fix DataLoader hanging on last patient + PyDicom API update
- **v1.1.3** (2025-10-15): Resume feature, cache improvements, CPU optimization
- **v1.1.2** (2025-10-14): Performance profiling, safety monitoring
- **v1.1.1** (2025-10-13): Initial Windows deployment version

---

## ⚠️ Known Limitations

1. **DICOM Format Requirements**:
   - Requires standard CT DICOM format with ImagePositionPatient tag
   - Slice thickness 4-6mm recommended (fallback available)

2. **Resource Requirements**:
   - GPU mode: Minimum 4GB VRAM recommended
   - CPU mode: 4GB+ RAM, processing time ~3-5 min/case

---

## 🙏 Acknowledgments

- **Issue Reporter**: User feedback on hanging behavior with 5-case pilot runs
- **Testing**: Validated on Linux + RTX 2060 environment
- **AI-CAC Project**: Original model and processing logic by Raffi Hagopian MD

---

## 📞 Support

For issues or questions:
1. Check log files in `logs/` directory
2. Review `docs/QUICK_REFERENCE_DATA_DIR.md` for common issues
3. Contact development team with log excerpts

---

**Recommended Action**: All users experiencing hanging issues should upgrade to v1.1.4 immediately.
