# Changelog

All notable changes to the NB10 AI-CAC Windows Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.4] - 2025-10-17

### Fixed
- **Critical: Program hanging on last patient case** - Fixed DataLoader worker process termination issue
  - Root cause: DataLoader with `num_workers > 0` failed to properly terminate after last iteration
  - Solution: Forced `num_workers = 0` for single-patient inference (no performance impact)
  - Added explicit DataLoader cleanup in try-finally block
  - Modified: `core/ai_cac_inference_lib.py` lines 249-255, 290-372
- **Updated PyDicom API** - Replaced deprecated `pydicom.read_file()` with modern `pydicom.dcmread()`
  - Modified: `core/processing.py` line 16

### Tested
- ✅ 5 consecutive cases on GPU (RTX 2060) - All completed successfully
- ✅ Average processing time: 13.9s/case
- ✅ No hanging on last case
- ✅ Program exits normally

### Documentation
Detailed release documentation: [docs/archive/releases/v1.1.4/](docs/archive/releases/v1.1.4/)
- [CHANGELOG_v1.1.4.md](docs/archive/releases/v1.1.4/CHANGELOG_v1.1.4.md) - Detailed changes and technical analysis
- [TEST_REPORT_v1.1.4.md](docs/archive/releases/v1.1.4/TEST_REPORT_v1.1.4.md) - Testing results
- [FINAL_TEST_REPORT_v1.1.4.md](docs/archive/releases/v1.1.4/FINAL_TEST_REPORT_v1.1.4.md) - Comprehensive test report
- [RELEASE_v1.1.4_SUMMARY.md](docs/archive/releases/v1.1.4/RELEASE_v1.1.4_SUMMARY.md) - Release summary

## [1.1.3-rc2] - 2025-10-17

### Added
- **Complete results CSV generation** - Automatic aggregation of resume sessions
- **CPU mode optimization** - Significant performance improvements (30-40% expected)

### Documentation
Detailed release documentation: [docs/archive/releases/v1.1.3/](docs/archive/releases/v1.1.3/)
- [DEPLOYMENT_SUMMARY_v1.1.3-rc2.md](docs/archive/releases/v1.1.3/DEPLOYMENT_SUMMARY_v1.1.3-rc2.md)
- [TEST_REPORT_v1.1.3-rc2.md](docs/archive/releases/v1.1.3/TEST_REPORT_v1.1.3-rc2.md)

## [1.1.2] - 2025-10-17

### Fixed
- **Resume display order** - Resume information now shows before "Processing X cases" message
  - Previously caused confusion as resume info appeared after processing count
  - Now clearly shows: Total found → Previously processed → Remaining to process
  - Cache file path now shows as relative path for clarity
- **DICOM reading performance degradation** - Eliminated duplicate file reading
  - Fixed `identify_dicom_series()` reading all files twice (sample + full scan)
  - Reduced I/O operations by 50% (from 2N to N file reads)
  - Expected 30-40% faster DICOM loading times
  - Eliminated cumulative slowdown on repeated runs

### Performance
- DICOM loading is now significantly faster and consistent across multiple cases
- No more progressive slowdown during batch processing

## [1.1.1] - 2025-10-17

### Added
- **Resume/Checkpoint functionality** for long-running processing tasks
  - Automatic progress tracking via `.nb10_resume_cache.csv` in output directory
  - Incremental save after each processed case (crash-safe)
  - Automatically skips successfully processed cases on restart
  - Failed cases are retried (not skipped) on subsequent runs
  - New command-line options:
    - `--clear-cache`: Clear resume cache and process all cases from scratch
    - `--no-resume`: Disable resume feature for current run
  - Particularly useful for CPU mode (3-5 min/case) and large datasets
  - Cache management functions: `load_processed_cache()`, `append_to_cache()`, `clear_resume_cache()`

### Changed
- Default `enable_resume: true` in configuration (can be disabled in config or via `--no-resume`)
- Enhanced progress display shows resume information when continuing from previous run
- Updated [USER_MANUAL.md](docs/USER_MANUAL.md) with comprehensive resume feature documentation

### Documentation
- Added detailed resume/checkpoint usage guide in user manual
- Added configuration comments explaining resume functionality
- Created test suite: [tests/test_resume.py](tests/test_resume.py)

## [1.1.0] - 2025-10-17

### Added
- Offline installation support with nested directory structure detection
  - Automatically detects `deployment/offline_wheels/gpu/` and `deployment/offline_wheels/cpu/`
  - Falls back to `deployment/offline_wheels/` and `offline_packages/` directories
  - Priority-based wheel package discovery for hospital deployment scenarios
- Processing time estimates for individual cases
  - CPU mode: "~3-5 minutes" estimate displayed
  - GPU mode: "~10-20 seconds" estimate displayed
  - Helps users understand processing progress

### Changed
- All user-facing text now in English only (removed mixed language strings)
  - Performance tier names simplified: "Minimal", "Standard", "Performance", "Professional", "Enterprise"
  - Eliminates encoding issues in pure English environments
- Improved progress display and time estimation during processing
- Enhanced distribution guide with offline installation instructions

### Fixed
- Removed double pause at program end
  - Eliminated redundant `input()` call in Python code
  - Kept single pause in batch file for user convenience
- Offline installation now works correctly with wheel packages in subdirectories

### Documentation
- Updated [USER_MANUAL.md](docs/USER_MANUAL.md) to version 1.1.0
- Updated [INSTALLATION_GUIDE.md](docs/INSTALLATION_GUIDE.md) with offline installation improvements
- Added [DISTRIBUTION_GUIDE_v1.1.0.md](dist/DISTRIBUTION_GUIDE_v1.1.0.md) for hospital deployments

## [1.0.0] - 2025-10-15

### Added
- Initial production release
- Core AI-CAC inference functionality
  - Automatic coronary artery calcification detection
  - Agatston score calculation
  - Risk stratification (0, 1-100, 101-400, >400)
- Hardware profiling and performance optimization
  - Automatic GPU/CPU detection
  - Dynamic performance tier selection
  - Memory optimization for 6GB GPUs
- Configuration management system
  - YAML-based configuration
  - Command-line parameter overrides
  - Environment-specific settings
- Batch processing capabilities
  - Pilot mode for testing (limited cases)
  - Full mode for production (all cases)
  - Resume support for interrupted processing
- Result export and logging
  - CSV format output
  - Detailed processing logs
  - Error tracking and reporting
- Windows-specific deployment features
  - Batch file launchers
  - Virtual environment support
  - Offline installation preparation

### Documentation
- Comprehensive user manual with clinical research examples
- Installation guide for Windows and Linux
- Research rationale documentation
- Deployment and packaging guides

## [1.0.0-beta] - 2025-10-14

### Added
- Beta release for testing
- Core inference engine
- Basic configuration system
- Command-line interface
- Documentation framework

---

## Version History Summary

- **v1.1.4** (2025-10-17): Critical bug fix - DataLoader hanging on last patient case
- **v1.1.3-rc2** (2025-10-17): CPU optimization + complete results CSV
- **v1.1.2** (2025-10-17): Bug fixes for resume display and DICOM reading performance
- **v1.1.1** (2025-10-17): Resume/checkpoint functionality for interrupted processing
- **v1.1.0** (2025-10-17): Offline installation support, English-only UI, time estimates
- **v1.0.0** (2025-10-15): Initial production release
- **v1.0.0-beta** (2025-10-14): Beta testing release

---

## Planned Features

See [REFACTORING_PLAN.md](REFACTORING_PLAN.md) for detailed future roadmap.

### v2.0.0 (Planned)
- Hardware-adaptive optimization system (20-40% performance improvement expected)
  - Detailed design: [docs/archive/planning/HARDWARE_ADAPTIVE_OPTIMIZATION_DESIGN.md](docs/archive/planning/HARDWARE_ADAPTIVE_OPTIMIZATION_DESIGN.md)
- GitHub-based authorization management
  - Detailed design: [docs/archive/planning/LICENSE_MANAGEMENT_SYSTEM_DESIGN.md](docs/archive/planning/LICENSE_MANAGEMENT_SYSTEM_DESIGN.md)
- Hospital deployment enhancements
  - Implementation roadmap: [docs/archive/planning/HOSPITAL_DEPLOYMENT_ROADMAP.md](docs/archive/planning/HOSPITAL_DEPLOYMENT_ROADMAP.md)

### v3.0.0 (Future)
- Shared module architecture for Colab integration
- Multi-GPU parallel processing
- Advanced statistical analysis tools
- Web-based interface option
