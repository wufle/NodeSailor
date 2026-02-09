# NodeSailor v1.0.1

## 🎉 What's New

### Hover Information Display
- **Node Hover**: Hover over any node to instantly see its details in the info panel
- **Connection Info**: Hover over connection lines to view connection details via tooltip
- Info panel now shows hovered node info with fallback to selected node

## 🐛 Bug Fixes

### Connection Label Positioning
- **Fixed**: Connection labels now properly display on top of their connection lines
- **Fixed**: Labels were previously appearing stacked in the top-left corner
- Labels are now visible and positioned correctly along connections

### JSON File Compatibility
- **Fixed**: Handle legacy JSON files with `NaN` values gracefully
- The app now automatically sanitizes `NaN` → `null` when loading files
- Example network files now load correctly without errors

### Build & Module Resolution
- **Fixed**: Module resolution issues in CI/CD environment
- Added comprehensive file extension resolution for Vite
- Build process now works reliably across all platforms

## 🔧 Technical Improvements

- Split connection rendering into separate layers for proper z-ordering
- Added `hoveredNodeIndex` store for tracking cursor state
- Enhanced ConnectionLine component with `showLine` prop for flexible rendering
- Improved file loading with sanitization for malformed JSON

## 📦 Installation

Download the installer for your platform:
- **Windows**: `NodeSailor_1.0.1_x64_en-US.msi`
- **macOS (Apple Silicon)**: `NodeSailor_aarch64.dmg`
- **macOS (Intel)**: `NodeSailor_x64.dmg`
- **Linux**: `node-sailor_1.0.1_amd64.deb` or `.AppImage`

## 🙏 Acknowledgments

Special thanks to Claude Sonnet 4.5 for development assistance.

---

**Full Changelog**: https://github.com/wufle/NodeSailor/compare/v1.0.0...v1.0.1
