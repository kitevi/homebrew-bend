# Homebrew tap for Bend

An unofficial macOS Homebrew tap for [Bend 2](https://github.com/bendlang/bend).
Supports Apple Silicon and Intel Macs. Bend 1 programs are not compatible with Bend 2.

## Install

```sh
brew install kitevi/bend/bend
bend version
bend guide
```

The formula installs upstream's prebuilt binary and support files into Homebrew's
Cellar. It does not execute Bend's shell installer. Native compilation needs a
compatible Clang toolchain; see the upstream guide for CPU/GPU requirements.

If you already installed Bend using its shell installer, run `which -a bend` and
ensure Homebrew's `bin` directory appears before `~/.bend/bin` in your PATH.
The executable is named `bend`, so it can also conflict with a Bend 1 installation.

## Upgrade

```sh
brew update
brew upgrade kitevi/bend/bend
```

Do **not** use `bend update`: it invokes upstream's installer and can create a
second installation outside Homebrew. Homebrew does not upgrade installed
packages in the background.

Bend checks for new versions daily, sending its version, OS, and CPU type to
bend-lang.com. Disable that check with:

```sh
export BEND_NO_TELEMETRY=1
```

## Automated release PRs

`.github/workflows/update.yml` checks the latest stable upstream release daily
at 08:23 UTC and can also be run manually from GitHub's Actions tab. GitHub may
delay scheduled runs or disable schedules in inactive public repositories.

The updater downloads both macOS archives, calculates SHA-256 hashes, checks
them against GitHub release asset digests, and opens or updates one PR. It does
not execute downloaded code or merge PRs. Missing assets/digests, unexpected
URLs, downgrades, and new major versions fail for manual review. Digests verify
consistency with the GitHub release, not an independent publisher signature.

## Contributing

Bug reports and PRs are welcome: see [CONTRIBUTING.md](CONTRIBUTING.md) for the
local development setup and what CI checks. Maintainer-only operational docs
(token setup, merging update PRs) live in [MAINTAINING.md](MAINTAINING.md).
