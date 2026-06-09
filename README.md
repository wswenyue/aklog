# aklog [![Release](https://github.com/wswenyue/aklog/actions/workflows/release.yml/badge.svg)](https://github.com/wswenyue/aklog/actions/workflows/release.yml)

Android & HarmonyOS developer's Swiss Army Knife for Log

![示例](./res/demo.jpg)

### Requirements

- **Python 3.9+**
- **rich** (installed automatically via `pip install` / Homebrew `post_install`)

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

Uses system `python3` when available; otherwise Homebrew installs [python](https://formulae.brew.sh/formula/python) as a dependency. Runtime Python packages (`rich`, `argcomplete`, `tomli` on Python &lt; 3.11) are installed automatically during `brew install`.

### Shell completion

Tab completion is powered by [argcomplete](https://github.com/kislyuk/argcomplete). It completes subcommands, options, log levels, and connected device IDs (`-d`).

**Homebrew (recommended):** shell completion is installed automatically:

- zsh → `share/zsh/site-functions/_aklog` (restart shell after `brew install aklog`)
- bash → `etc/bash_completion.d/aklog` (requires [bash-completion](https://formulae.brew.sh/formula/bash-completion); add `[[ -r "$(brew --prefix)/etc/profile.d/bash_completion.sh" ]] && . "$(brew --prefix)/etc/profile.d/bash_completion.sh"` to `~/.bash_profile` if not already enabled)

**Oh My Zsh:**

```shell
git clone https://github.com/wswenyue/aklog.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/aklog
# ~/.zshrc
plugins=(... aklog)
```

Or source the bundled plugin when running from a local checkout:

```shell
source /path/to/aklog/contrib/zsh/aklog.plugin.zsh
```

**Zsh (manual / from source):**

```shell
# ~/.zshrc
fpath=(/path/to/aklog/contrib/zsh $fpath)
autoload -U compinit && compinit
```

**Bash (manual / from source):**

```shell
source /path/to/aklog/contrib/bash/aklog   # or add eval line below to ~/.bashrc
```

**Zsh / Bash (one-liner):**

```shell
eval "$(register-python-argcomplete aklog)"   # add to ~/.zshrc or ~/.bashrc
```

If completion does not work on an older setup, try `autoload -U bashcompinit && bashcompinit` before the `eval` line.

Device ID completion (`-d`) requires adb/hdc tools and at least one connected device.

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
aklog config init                  # create user color config
aklog config path                  # show config file path
```

When multiple USB devices are connected (adb and/or hdc), aklog prompts for selection unless `-d` is provided.

### Configuration

User settings are stored at `~/.config/aklog/config.toml` (or `%APPDATA%\aklog\config.toml` on Windows).

```shell
aklog config init      # generate default color theme
aklog config path      # print config location
```

Edit `[colors]` to customize log level colors. Rich color names (`green`, `bright_blue`, `#ff6600`, etc.) are supported. Invalid values fall back to built-in defaults.

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
  core/                 # comm_tools, cmd_runner, config, console, paths
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
