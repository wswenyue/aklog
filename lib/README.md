# Bundled platform tools

Place per-OS/arch binaries under:

```text
lib/<os>/<arch>/
  adb              # Android (optional; ANDROID_HOME overrides)
  hdc              # HarmonyOS (optional; HARMONY_HOME overrides)
  libusb_shared.dylib   # macOS hdc dependency, if needed
```

| OS | Arch directory | Examples |
|----|----------------|----------|
| macOS | `darwin/arm64`, `darwin/x86_64` | `adb`, `hdc`, `*.dylib` |
| Linux | `linux/aarch64`, `linux/x86_64` | `adb`, `hdc` |
| Windows | `windows/arm64`, `windows/x86_64` | `adb.exe`, `hdc.exe` |

Legacy flat layout (`lib/adb`, `lib/hdc`) is still supported as a fallback.
