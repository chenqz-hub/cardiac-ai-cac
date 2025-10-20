# Changelog

All notable changes to Cardiac AI-CAC will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.4] - 2025-10-19

### Added
- ✨ **Extensible Menu System**: Dynamic module discovery and registration
- ✨ **Multi-language Support**: Chinese/English UI toggle (i18n system)
- ✨ **License Management**: RSA2048-based license validation with machine ID binding
- ✨ **Module Metadata**: YAML-based module configuration
- ✨ **Automated Testing**: Comprehensive test suite (100% pass rate)
- 📦 **Offline Deployment**: Complete offline installation packages for Windows and Linux

### Changed
- ⚡ **CPU Optimization**: Further improved multi-core performance
- 📝 **Documentation**: Comprehensive user guides and API documentation
- 🔧 **Configuration**: Simplified configuration management

### Fixed
- 🐛 **Dependencies**: Added cryptography to requirements files
- 🐛 **Cross-platform**: Fixed Windows/Linux compatibility issues

### Performance
- Average processing time: ~305s/patient (CPU, 8 cores)
- Success rate: 99.5% (195/196 validated)

---

## [1.1.3] - 2025-10-18

### Added
- ✨ **Resume from Checkpoint**: Ability to continue interrupted processing
- 📊 **Complete Results CSV**: Export all patient data to CSV

### Changed
- ⚡ **Performance**: Optimized DICOM reading performance
- 📝 **Logging**: Improved progress information display

### Fixed
- 🐛 **DICOM Reading**: Fixed performance regression in pydicom usage
- 🐛 **Thread Configuration**: Moved PyTorch thread config to model creation

---

## [1.1.2] - 2025-10-17

### Fixed
- 🐛 **DICOM Performance**: Resolved DICOM reading performance degradation
- 📝 **Documentation**: Improved checkpoint feature documentation

---

## [1.1.1] - 2025-10-16

### Added
- ✨ **Checkpoint System**: Resume processing from interruption point
- 🧪 **Test Suite**: Added comprehensive tests for checkpoint functionality

### Changed
- 📝 **Documentation**: Enhanced checkpoint feature documentation

---

## [1.1.0] - 2025-10-15

### Added
- ✨ **Batch Processing**: Support for processing multiple patients
- ✨ **Progress Tracking**: Real-time progress bars with tqdm
- 📊 **Statistics**: Processing statistics and success rate reporting

### Changed
- ⚡ **CPU Optimization**: Multi-core support with configurable workers
- 🎨 **UI**: Interactive menu system
- 📝 **Documentation**: User manual and quick start guides

### Performance
- Reduced processing time by 50% on multi-core systems

---

## [1.0.0] - 2025-10-01

### Initial Release

- 🎉 **Core Functionality**: AI-based coronary calcium scoring
- 🧠 **AI Model**: SwinUNETR-based segmentation and scoring
- 📁 **Input Formats**: DICOM and NIfTI support
- 💻 **CPU Support**: Optimized for CPU-only deployment
- 📊 **Output**: CSV results with calcium scores
- 📝 **Documentation**: Basic user guides

### Validation
- Tested on 100+ patients
- Success rate: >95%

---

## Version Naming Convention

```
v{MAJOR}.{MINOR}.{PATCH}

MAJOR: Breaking changes, major features
MINOR: New features, backward compatible
PATCH: Bug fixes, minor improvements
```

---

## Legend

- ✨ New feature
- ⚡ Performance improvement
- 🐛 Bug fix
- 📝 Documentation
- 🔧 Configuration/build
- 🧪 Testing
- 🎨 UI/UX improvement
- 📦 Packaging/deployment
- 🔒 Security

---

## Upcoming Releases

### [1.2.0] - Planned (Q1 2026)
- Additional cardiac analysis modules (NB05: Visceral Fat)
- Enhanced visualization tools
- Improved reporting formats

### [1.3.0] - Planned (Q2 2026)
- Web-based interface
- PACS integration
- Advanced analytics dashboard

### [2.0.0] - Planned (Q3 2026)
- Multi-modal analysis integration
- AI model updates
- Advanced risk scoring

---

**Note**: Release dates are subject to change based on development progress and user feedback.
