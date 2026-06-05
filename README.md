# aklog [![Release](https://github.com/wswenyue/aklog/actions/workflows/release.yml/badge.svg)](https://github.com/wswenyue/aklog/actions/workflows/release.yml)

Android & HarmonyOS developer's Swiss Army Knife for Log

![示例](./res/demo.jpg)

### Requirements

- **Python 3.9+**

Bundled tools on macOS (optional; SDK environment variables take precedence):

- `lib/darwin/arm64/adb`, `lib/darwin/arm64/hdc` — Apple Silicon
- `lib/darwin/x86_64/adb`, `lib/darwin/x86_64/hdc` — Intel Mac

See [lib/README.md](lib/README.md). On Linux/Windows use `ANDROID_HOME` / `HARMONY_HOME`.

Environment variables (optional):

- `ANDROID_HOME` — use SDK `platform-tools/adb` instead of bundled `adb`
- `HARMONY_HOME` — use SDK `hdc` instead of bundled `hdc`

### Installation

```shell
brew tap wswenyue/aklog && brew install aklog
```

Uses system `python3` when available; otherwise Homebrew installs [python](https://formulae.brew.sh/formula/python) as a dependency (no extra pip packages).

### Update

```shell
brew upgrade aklog
```

### Usage

```shell
aklog -h
aklog -d <device_id> -pc          # specify device, filter foreground app
aklog cap-screen                   # screenshot
aklog record-video                 # screen record (Ctrl+C to stop)
aklog dump-log                     # dump crash logs
aklog install -path ./app.hap      # install hap/apk
```

When multiple USB devices are connected (adb and/or hdc), aklog prompts for selection unless `-d` is provided.

### Platforms

| Feature | Android (adb) | HarmonyOS (hdc) |
|---------|---------------|-----------------|
| Log stream | logcat | hilog |
| Foreground filter | dumpsys | aa dump |
| Screenshot | screencap | snapshot_display |
| Record | screenrecord | system screenrecorder |
| Crash dump | dropbox | faultlogger |
| Install | adb install | hdc install |

**Note:** HarmonyOS screen recording requires an unlocked physical device and system screen recorder service.

### Project layout

```
aklog/                  # bash launcher (PYTHONPATH=src, python -m aklog)
release.sh              # semver tag release → triggers release.yml
scripts/sync-version.sh # writes build_meta.py + pyproject version before tag
lib/darwin/{arm64,x86_64}/  # bundled adb / hdc for Homebrew (see lib/README.md)
src/aklog/
  build_meta.py         # version constants (generated at release)
  cli/                  # argparse & main dispatch
  core/                 # comm_tools, cmd_runner, color_print, paths
  device/               # platform abstraction (android / harmony), adb, hdc
  log/                  # parser, filters, printer
  app/                  # foreground app / process info
  tools/                # cap-screen, record-video, dump-log
```

Run from source:

```shell
pip install -e ".[dev]"
PYTHONPATH=src python3 -m aklog --version
# or after brew install:
aklog --version
```

### Release (maintainers)

```shell
git checkout master && git pull
make ci                    # same gates as CI / release workflow
./release.sh               # default patch bump; use -i for major/minor
```

Flow: `release.sh` → `sync-version.sh` → commit `build_meta.py` → push tag `vX.Y.Z` → GitHub Actions `release.yml` (quality → per-arch tarballs → GitHub Release → Homebrew formula).

Release workflow switches in [`.github/workflows/release.yml`](.github/workflows/release.yml) (`RELEASE_DARWIN_ARM64` / `RELEASE_DARWIN_X86_64`). **Default: only ARM64** release assets; Apple Silicon Homebrew uses the release tarball, Intel Mac still uses the source archive until `RELEASE_DARWIN_X86_64` is enabled and `lib/darwin/x86_64/` is populated.

Local package dry-run: `scripts/build-release-archive.sh <version> darwin arm64`

### Development

```shell
pip install -e ".[dev]"
make test          # unit tests
make test-cov      # tests + coverage (≥75%)
make lint          # ruff
make typecheck     # mypy
make smoke         # CLI --version / -h, launcher syntax
make ci            # lint + typecheck + test-cov + smoke
```

Coverage threshold is **75%** (enforced in CI). Tests mock adb/hdc; no physical device required.
