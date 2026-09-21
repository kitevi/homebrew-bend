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

### One-time maintainer setup

1. Push this repository to `kitevi/homebrew-bend`, using `main` as its default branch.
2. Create a fine-grained GitHub personal access token restricted to this repository:
   **Contents: read/write** and **Pull requests: read/write**. Use a short expiry
   and rotate it before expiration.
3. Add it under **Settings → Secrets and variables → Actions** as the repository
   secret **`TAP_UPDATE_TOKEN`**. Never put the token in a file or commit.
4. Run **Update Bend** manually once to check the configuration.
5. Protect `main` and require both architecture-specific formula checks plus the
   updater test job before merging. Check names appear after the first CI run.

A separate token is intentional: PRs created with the built-in `GITHUB_TOKEN`
generally do not trigger additional workflows. `TAP_UPDATE_TOKEN` lets the update
PR trigger macOS CI normally. The updater refuses to run without it; there is no
silent fallback that would leave update PRs untested. A GitHub App token can be
used instead if you later want to avoid a personal token.

CI installs the formula and tests the CLI, Base library, guide, and a small Bend
program on Apple Silicon and Intel macOS runners, then runs Homebrew audit and
style checks. Review upstream release notes and the PR diff before merging.
Dependabot proposes updates to the SHA-pinned GitHub Actions weekly.

## Local development

```sh
python3 -m unittest discover -s tests -v
python3 scripts/update_formula.py --verify-current
```

The second command contacts GitHub, downloads both archives, and updates the
formula if a newer stable Bend 2 release exists. It does not install Bend.
`GH_TOKEN` is optional locally and raises the GitHub API rate limit.

To test a local checkout as a tap (only if `kitevi/bend` is not already tapped):

```sh
brew tap --custom-remote kitevi/bend "$PWD"
brew install kitevi/bend/bend
brew test kitevi/bend/bend
brew audit --strict kitevi/bend/bend
brew style kitevi/bend/bend
```

Commit local changes before tapping: Homebrew clones the repository rather than
reading uncommitted files from your working tree. For an existing installation,
use `brew reinstall kitevi/bend/bend` to test an updated formula.
