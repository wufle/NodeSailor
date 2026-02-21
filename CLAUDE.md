# NodeSailor - Claude Development Guide

## Project Overview

NodeSailor is a network topology mapping, configuration, and testing tool designed for visualizing and managing network infrastructures. It provides an intuitive GUI for creating network diagrams, managing nodes and connections, and performing basic network testing operations.

**Current Version**: 1.1.6
**Original Implementation**: Python/Tkinter
**Current Implementation**: Tauri 2.x + Svelte 5 + Rust

## Tech Stack

### Frontend
- **Svelte 5** - UI framework (using runes: $state, $derived, $props)
- **TypeScript** - Type safety
- **Tailwind CSS 4** - Styling (via @tailwindcss/vite plugin)
- **Vite** - Build tool and dev server

### Backend
- **Tauri 2.x** - Desktop application framework
- **Rust** - Backend logic and system commands
- **Tauri Plugins**:
  - `tauri-plugin-dialog` - File dialogs and message boxes
  - `tauri-plugin-shell` - Shell command execution
  - `tauri-plugin-fs` - File system operations

### Key Libraries
- `lightningcss` - Fast CSS processing
- `regex` (Rust) - Pattern matching for IP addresses

## Project Structure

```
NodeSailor/
├── tauri-app/                    # Main application directory
│   ├── src/                      # Frontend source
│   │   ├── components/           # Svelte components
│   │   │   ├── canvas/           # Canvas-related components (nodes, connections, groups)
│   │   │   ├── dialogs/          # Modal dialogs
│   │   │   ├── editors/          # List editors and config panels
│   │   │   └── layout/           # Layout components (toolbar, etc.)
│   │   ├── lib/
│   │   │   ├── actions/          # Business logic (file, ping, system actions)
│   │   │   ├── stores/           # Svelte stores (state management)
│   │   │   ├── theme/            # Theme colors and presets
│   │   │   ├── types/            # TypeScript type definitions
│   │   │   └── utils/            # Utility functions (geometry, etc.)
│   │   ├── assets/               # Images and textures
│   │   ├── App.svelte            # Root component
│   │   └── main.ts               # Entry point
│   ├── src-tauri/                # Rust backend
│   │   ├── src/
│   │   │   ├── commands/         # Tauri commands (Rust functions callable from frontend)
│   │   │   │   ├── file_io.rs    # File loading/saving
│   │   │   │   ├── ping.rs       # Ping operations
│   │   │   │   ├── network.rs    # Network utilities (get local IPs)
│   │   │   │   ├── system.rs     # System operations (RDP, file explorer, etc.)
│   │   │   │   └── settings.rs   # App settings persistence
│   │   │   ├── lib.rs            # Command registration
│   │   │   └── main.rs           # Entry point
│   │   ├── icons/                # Application icons
│   │   ├── Cargo.toml            # Rust dependencies
│   │   └── tauri.conf.json       # Tauri configuration
│   ├── public/                   # Static assets (screenshots for tutorial)
│   ├── package.json              # Node dependencies
│   └── vite.config.ts            # Vite configuration
├── data/                         # Example networks and assets
│   ├── favicon.ico               # Application icon source
│   └── screenshots/              # Tutorial screenshots
└── example network.json          # Sample network configuration
```

## Key Files and Their Purposes

### Frontend Core
- **`src/App.svelte`** - Root component, handles auto-load, dialogs, and global state
- **`src/components/canvas/TopologyCanvas.svelte`** - Main canvas for network topology (SVG-based)
- **`src/lib/stores/networkStore.ts`** - Network data (nodes, connections, groups, VLANs)
- **`src/lib/stores/uiStore.ts`** - UI state (mode, theme, dialogs, selection)
- **`src/lib/stores/settingsStore.ts`** - Persistent app settings

### Backend Core
- **`src-tauri/src/commands/ping.rs`** - Ping functionality (uses native ping command)
- **`src-tauri/src/commands/network.rs`** - Network utilities (get_local_ips)
- **`src-tauri/src/commands/system.rs`** - System integrations (RDP, file explorer, browser, custom commands)
- **`src-tauri/src/commands/file_io.rs`** - File operations and save dialog

### Configuration
- **`tauri-app/src-tauri/tauri.conf.json`** - App configuration (version, bundle settings, icons)
- **`tauri-app/src-tauri/Cargo.toml`** - Rust dependencies and version
- **`tauri-app/package.json`** - Node dependencies and version

## Data Structures

### NetworkNode
```typescript
interface NetworkNode {
  name: string;
  x: number;
  y: number;
  vlans: Record<string, string>;  // VLAN key -> IP address
  remote_desktop_address: string;
  file_path: string;
  web_config_url: string;
}
```

### NetworkConnection
```typescript
interface NetworkConnection {
  from: number;  // Node index
  to: number;    // Node index
  label: string;
  connectioninfo?: string;
  waypoints?: [number, number][];  // Optional path waypoints
}
```

### GroupRect
```typescript
interface GroupRect {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  name: string;
  color: string;
  light_bg: string;
  light_border: string;
  dark_bg: string;
  dark_border: string;
  color_preset_id: string;
}
```

## Operating Modes

### Configuration Mode
- Create/edit nodes (double-click canvas)
- Create/edit connections (middle-click between nodes)
- Create/edit groups (draw rectangles with Groups mode active)
- Move nodes (drag)
- Add waypoints to connections (middle-click on line)
- Full editing capabilities

### Operator Mode
- Ping nodes (left-click)
- Access context menu (right-click)
- View network status
- Execute custom commands
- Read-only for topology

## Themes

Three themes available:
1. **Light** - Standard light theme
2. **Dark** - Standard dark theme
3. **Ironclad** - Special theme with industrial metal textures

Theme colors defined in `src/lib/theme/colors.ts`
Metal textures: `src/assets/textures/`

## Common Development Tasks

### Building an Installer
```bash
cd tauri-app
npm run tauri build
```
Outputs:
- NSIS: `src-tauri/target/release/bundle/nsis/NodeSailor_*_x64-setup.exe`
- MSI: `src-tauri/target/release/bundle/msi/NodeSailor_*_x64_en-US.msi`

### Running in Development
```bash
cd tauri-app
npm run tauri dev
```

### Updating Version Number
Update in 3 places (must match):
1. `tauri-app/src-tauri/Cargo.toml` - `version = "1.0.2"`
2. `tauri-app/src-tauri/tauri.conf.json` - `"version": "1.0.2"` and window title
3. `tauri-app/package.json` - `"version": "1.0.2"`

After changing Cargo.toml:
```bash
cd tauri-app/src-tauri
cargo update
```

Then update version display in:
- `src/components/dialogs/StartMenu.svelte` - Version text under logo

### Adding a New Tauri Command

1. Create/modify command in `src-tauri/src/commands/*.rs`:
```rust
#[tauri::command]
pub fn my_command(param: String) -> Result<String, String> {
    Ok(format!("Result: {}", param))
}
```

2. Register in `src-tauri/src/lib.rs`:
```rust
.invoke_handler(tauri::generate_handler![
    // ... existing commands
    commands::module::my_command,
])
```

3. Call from frontend:
```typescript
import { invoke } from "@tauri-apps/api/core";
const result = await invoke<string>("my_command", { param: "value" });
```

### Adding a New Dialog

1. Create component in `src/components/dialogs/MyDialog.svelte`:
```svelte
<script lang="ts">
  import DialogWrapper from "./DialogWrapper.svelte";
  import { activeDialog } from "../../lib/stores/uiStore";

  function close() {
    activeDialog.set(null);
  }
</script>

<DialogWrapper title="My Dialog" width={400} onClose={close}>
  <!-- Dialog content -->
</DialogWrapper>
```

2. Add dialog type to `src/lib/stores/uiStore.ts` (if using TypeScript union type)

3. Show dialog in `src/App.svelte`:
```svelte
{#if $activeDialog === "myDialog"}
  <MyDialog />
{/if}
```

## Important Patterns and Conventions

### Svelte 5 Runes (New Syntax)
- Use `$state()` for reactive local state
- Use `$derived()` for computed values
- Use `$derived.by()` for complex derivations
- Use `$props()` for component props
- Store subscriptions: `$storeName` (auto-subscribes)

### State Management
- **Global state**: Use Svelte stores in `src/lib/stores/`
- **Trigger unsaved changes**: Call `unsavedChanges.set(true)` after modifications
- **Store updates**: Use `.update()` or `.set()` methods

### File Operations
- All file I/O goes through Rust backend for security
- File paths stored in settings: `%AppData%/NodeSailor/settings.json`
- Network data: JSON format with nodes, connections, groups, etc.

### Coordinate System
- Canvas uses SVG coordinates with pan/zoom transforms
- Transform: `translate({$panX},{$panY}) scale({$zoom})`
- Convert screen to world: `screenToWorld()` function in TopologyCanvas.svelte
- Node positions stored in world coordinates

### Ping Results
- Stored as: `Record<number, boolean[]>` (node index -> array of ping results per VLAN)
- Colors: Green (all success), Yellow (partial), Red (failure)
- Clear with: `pingResults.set({})`

## Recent Changes (v1.0.0 → v1.0.2)

### v1.0.1
- Fixed parallel ping execution (Promise.all instead of sequential)
- Hide CMD windows on ping operations (Windows CREATE_NO_WINDOW flag)
- Documented glib security issue (Linux-only, doesn't affect Windows builds)

### v1.0.2
**Icon & Version Display**:
- Replaced app icon with favicon.ico (129KB)
- Version number in window title and Start Menu
- Explicit window icon configuration for taskbar

**Auto-load Feature**:
- Checkbox in Start Menu to auto-load last file on startup
- Settings persistence via `auto_load_last_file` flag

**Tutorial Walkthrough**:
- New TutorialWalkthrough.svelte component
- 9-step tutorial with screenshots (5 config + 4 operator mode)
- Accessible from Start Menu

**Group Editing UX**:
- Resize handles at group corners (drag to resize)
- Double-click group name to edit inline
- Right-click context menu (Edit Colors, Delete)
- Resize handles show only when Groups mode active
- Fixed group color editing bug (Svelte parser issue)

**List Editors**:
- Column sorting in Node List and Connection List editors
- Click headers to sort (ascending/descending with indicators)
- Maintains original indices when sorted

**"Who am I?" Button**:
- Optimized speed (3 flashes in 1.05s instead of 5 in 2.5s)
- Reduced socket timeout to 100ms
- Smart fallback: only runs ipconfig if socket method fails
- Leaves node highlighted after flashing

**Save Dialog**:
- Prompt: "Overwrite existing or Save As?"
- Three options: Overwrite, Save As, Cancel
- New Rust command: `show_save_dialog`

**Toolbar Enhancements**:
- "Edit Groups" button added for easier access

## Known Issues

### GitHub Security Alert
- `glib` dependency flagged (Unsoundness in Iterator impls)
- **Status**: Linux-only dependency, doesn't affect Windows builds
- **Impact**: None for Windows distribution

### Windows Icon Caching
- Windows caches application icons aggressively
- **Solution**: Clear `%LocalAppData%\IconCache.db` and restart Explorer after uninstall/reinstall

## Troubleshooting

### Build Failures
- Ensure all 3 version numbers match (Cargo.toml, tauri.conf.json, package.json)
- Run `cargo update` after changing Cargo.toml
- Delete `target/` and `node_modules/` if issues persist

### Icon Not Updating
- Windows caches icons - see "Windows Icon Caching" above
- Ensure `icon.ico` is 129KB (the favicon)
- Check `tauri.conf.json` has explicit window icon path

### Ping Not Working
- Windows: Requires administrator privileges in some cases
- CMD windows should be hidden (CREATE_NO_WINDOW flag)
- Check firewall settings

### Performance Issues
- "Who am I?" function optimized in v1.0.2
- Large networks: Consider pagination in list editors
- Canvas rendering: SVG performs well up to ~100 nodes

## Git Workflow

**Current Branch**: `tauri-bug-fixin`
**Main Branch**: `main`

**Commit Convention**:
```
type: Brief description

Detailed changes:
- Change 1
- Change 2

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

Types: `feat`, `fix`, `perf`, `refactor`, `docs`, `chore`

## Building for Production

1. Update version in all 3 locations
2. Run `cargo update` in `tauri-app/src-tauri/`
3. Commit version changes
4. Build: `npm run tauri build`
5. Test installer on clean machine
6. Push to GitHub
7. Create GitHub release with changelog

## File Format (.json)

Network files store:
- `nodes[]` - Array of NetworkNode objects (VLANs flattened as properties)
- `connections[]` - Array of NetworkConnection objects
- `vlan_labels{}` - VLAN key to display name mapping
- `vlan_label_order[]` - Order of VLAN columns
- `stickynotes[]` - Sticky note annotations
- `groups[]` - Group rectangles
- `group_color_presets[]` - Color palette for groups
- `custom_commands{}` - User-defined commands
- `display_options{}` - Canvas display settings

## Tips for Future Development

1. **Always read files before editing** - Use Read tool before Write/Edit
2. **Svelte 5 syntax** - Use runes, not legacy reactive statements
3. **Parallel operations** - Use Promise.all() for independent async tasks
4. **Type safety** - TypeScript interfaces in `src/lib/types/network.ts`
5. **Windows compatibility** - Test on Windows, handle path separators
6. **Icon updates** - Update all icon sizes, not just .ico
7. **Performance** - Profile before optimizing, avoid premature optimization
8. **Git commits** - Include Co-Authored-By for Claude contributions

## Contact & Resources

- **GitHub**: https://github.com/wufle/NodeSailor
- **Releases**: https://github.com/wufle/NodeSailor/releases
- **Tauri Docs**: https://v2.tauri.app/
- **Svelte 5 Docs**: https://svelte.dev/docs/svelte/overview
