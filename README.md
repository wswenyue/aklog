# aklog [![Release](https://github.com/wswenyue/aklog/actions/workflows/release.yml/badge.svg)](https://github.com/wswenyue/aklog/actions/workflows/release.yml) [![CI](https://github.com/wswenyue/aklog/actions/workflows/ci.yml/badge.svg)](https://github.com/wswenyue/aklog/actions/workflows/ci.yml)

Android & HarmonyOS developer's Swiss Army Knife for Log

![示例](./res/demo.jpg)

### Requirements

- **Python 3.9+**

Bundled tools (optional; SDK environment variables take precedence):

- `lib/<os>/<arch>/adb` — Android Debug Bridge
- `lib/<os>/<arch>/hdc` — HarmonyOS Device Connector

See [lib/README.md](lib/README.md) for per-arch layout.

Environment variables (optional):

- `ANDROID_HOME` — use SDK `platform-tools/adb` instead of bundled `adb`
- `HARMONY_HOME` — use SDK `hdc` instead of bundled `hdc`

### Installation

```shell
brew tap wswenyue/aklog && brew install aklog
```

Homebrew installs [python@3.12](https://formulae.brew.sh/formula/python@3.12) and runs aklog with it (no extra pip dependencies).

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
lib/<os>/<arch>/        # bundled adb / hdc (see lib/README.md)
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

Flow: `release.sh` → `sync-version.sh` → commit `build_meta.py` → push tag `vX.Y.Z` → GitHub Actions `release.yml` (quality → Homebrew formula).

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
