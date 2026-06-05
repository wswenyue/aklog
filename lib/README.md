# Bundled macOS tools (Homebrew release)

Place per-arch binaries under:

```text
lib/darwin/<arch>/
  adb                   # Android (optional; ANDROID_HOME overrides)
  hdc                   # HarmonyOS (optional; HARMONY_HOME overrides)
  libusb_shared.dylib   # hdc dependency, if needed
```

| Arch directory | CPU |
|----------------|-----|
| `darwin/arm64` | Apple Silicon |
| `darwin/x86_64` | Intel Mac |

Legacy flat layout (`lib/adb`, `lib/hdc`) is still supported as a fallback at runtime.

Non-macOS: use `ANDROID_HOME` / `HARMONY_HOME` instead of bundled tools.
