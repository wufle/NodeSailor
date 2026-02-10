# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Known False Positives

### glib v0.18.5 - RUSTSEC-2024-0429
**Status**: Not a security issue for NodeSailor

GitHub flags `glib v0.18.5` as having a vulnerability in its `Iterator` implementation. However, this is a **false positive** for NodeSailor because:

- **Platform**: NodeSailor is a Windows-only application
- **Dependency Chain**: glib is pulled in through `gtk → muda → tauri`
- **Conditional Compilation**: GTK and glib are only compiled on Linux systems
- **Windows Impact**: Zero - these dependencies are not included in Windows builds

**Evidence**:
```bash
# On Windows, glib doesn't appear in the compiled dependencies
cargo tree -i glib
# Output: "nothing to print"
```

**Upstream Status**: The Tauri team has marked this as "not planned" because:
1. GTK3 Rust bindings are unmaintained
2. Only affects Linux builds
3. Tauri 2.x is moving away from GTK dependencies

**References**:
- [Tauri Issue #12048](https://github.com/tauri-apps/tauri/issues/12048)
- [RUSTSEC-2024-0429](https://rustsec.org/advisories/RUSTSEC-2024-0429)

## Reporting a Vulnerability

If you discover a security vulnerability in NodeSailor itself (not a false positive like the above), please report it by:

1. **Do not** open a public GitHub issue
2. Email the maintainer or create a private security advisory
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to resolve the issue before public disclosure.
