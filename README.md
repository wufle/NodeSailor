# NodeSailor

**A network topology mapping, configuration and testing utility**

NodeSailor is a cross-platform desktop application for visualizing, configuring, and testing network topologies. Built with Tauri, it combines the performance of Rust with a modern web-based interface to provide a lightweight yet powerful network management tool.

<img width="1745" height="1158" alt="image" src="https://github.com/user-attachments/assets/a9646bad-30a5-4576-a6b6-f28962397e58" />

## 🚀 Features

- **Visual Network Mapping**: Create and visualize network topologies with an intuitive drag-and-drop interface
- **Network Testing**: Perform ping tests, connectivity checks, and other network diagnostics
- **VLAN Support**: Configure and manage multiple VLANs within your network topology
- **Device Management**: Track and organize network devices with custom properties and connections
- **Cross-Platform**: Runs on Windows, macOS, and Linux
- **Lightweight**: Small binary size thanks to Tauri's architecture
- **Modern UI**: Built with Svelte for a responsive and intuitive user experience

## 📋 Requirements

### For Running the Application

Download the latest release from the [Releases](https://github.com/wufle/NodeSailor/releases) page for your platform:
- Windows: `.exe` installer
- macOS: `.dmg` or `.app`
- Linux: `.deb`, `.rpm`, or `.AppImage`

### For Development

- **Node.js** (v18 or later)
- **Rust** (latest stable version)
- **pnpm**, **npm**, or **yarn**

## 🛠️ Installation

### Option 1: Download Pre-built Binary (Recommended)

1. Visit the [Releases](https://github.com/wufle/NodeSailor/releases) page
2. Download the appropriate installer for your operating system
3. Install and run NodeSailor

### Option 2: Build from Source

1. **Clone the repository**
   ```bash
   git clone https://github.com/wufle/NodeSailor.git
   cd NodeSailor/tauri-app
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   pnpm install
   ```

3. **Run in development mode**
   ```bash
   npm run tauri dev
   # or
   pnpm tauri dev
   ```

4. **Build for production**
   ```bash
   npm run tauri build
   # or
   pnpm tauri build
   ```

## 📖 Usage

### Operator Mode

**Navigate and test your network:**

- **Left Click on Node**: Ping the node
  - 🟢 Green: Successfully pinged
  - 🟡 Yellow: Partial response (some VLANs responding)
  - 🔴 Red: No response
  
- **Right Click on Node**: Open context menu with options:
  - Remote Desktop
  - File Explorer
  - Web Browser
  - Additional custom user-created operations

- **VLAN Management**: Use radio buttons to show/hide specific VLANs

- **Keyboard Shortcuts**:
  - `F1`: Open help menu

### Configuration Mode

**Build and modify your network topology:**

- **Double Left Click**: Create a new node
- **Left Click + Drag**: Move nodes
- **Shift + Double Left Click**: Create a sticky note
- **Shift + Left Click + Drag**: Move sticky notes
- **Middle Click**: Create a connection between nodes (with optional label)
- **Shift + Middle Click**: Remove a connection
- **Right Click on Node**: Context menu with options:
  - Edit node properties
  - Delete node
  - Access remote desktop
  - Open file explorer
  - Launch web browser

- **File Operations**:
  - `Save`: Save the current network configuration
  - `Load`: Load a saved network configuration

## 🗂️ Project Structure

```
NodeSailor/
├── tauri-app/           # Tauri application
│   ├── src/             # Frontend source (Svelte)
│   ├── src-tauri/       # Rust backend
│   └── package.json     # Node.js dependencies
├── data/                # Application data files
├── example network.json # Example network configurations
└── README.md           # This file
```

## 🔄 Migration from Python Version

NodeSailor is currently being ported from Python (using Tkinter) to a modern Tauri application. The Tauri version offers:

- Better performance through Rust backend
- Modern, responsive UI with Svelte
- Smaller application size
- Better cross-platform support
- Enhanced security

Legacy Python files remain in the repository for reference but are no longer maintained.

## 🐛 Known Issues

- Pan and zoom functionality may have cursor alignment issues (under investigation)


## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [COPYING.TXT](COPYING.TXT) file for details.

## 🙏 Acknowledgments

- Built with [Tauri](https://tauri.app/)
- UI powered by [Svelte](https://svelte.dev/)
- Originally developed with assistance from AI tools to accelerate learning and development

---

**Note**: This project is actively under development. The Tauri version represents a complete rewrite with improved architecture and performance. For the legacy Python version, see the root directory files.
