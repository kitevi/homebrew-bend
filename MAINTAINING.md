# Maintainer guide

Operational details for maintaining this tap. End users only need the README.

## One-time setup

1. Push this repository to `kitevi/homebrew-bend`, using `main` as its default branch.
2. Create a fine-grained GitHub personal access token restricted to this repository:
   **Contents: read/write** and **Pull requests: read/write**. Use a short expiry
   and rotate it before expiration.
3. Add it under **Settings → Secrets and variables → Actions** as the repository
   secret **`TAP_UPDATE_TOKEN`**. Never put the token in a file or commit.
4. Run **Update Bend** manually once to check the configuration.
5. Protect `main` with required checks from GitHub Actions: `updater`,
   `formula (macos-15)`, and `formula (macos-15-intel)`. Require the branch to be
   up to date and enforce these rules for administrators too. Do not give the
   update token a bypass. These checks must remain required: without them,
   requesting auto-merge can merge immediately without waiting for CI.
6. Enable **Settings → General → Pull Requests → Allow auto-merge** and allow
   squash merging. No automatic review approval is needed.

## Why a separate token

A separate token is intentional: PRs created with the built-in `GITHUB_TOKEN`
generally do not trigger additional workflows. `TAP_UPDATE_TOKEN` lets the update
PR trigger macOS CI normally. The updater refuses to run without it; there is no
silent fallback that would leave update PRs untested. A GitHub App token can be
used instead if you later want to avoid a personal token.

## Merging update PRs

The updater requests squash auto-merge using `TAP_UPDATE_TOKEN` whenever its
create-PR step returns a PR number. GitHub merges only when required checks and
repository rules permit it. Failing checks, conflicts, or required reviews leave
the PR open. If the auto-merge request itself fails, the workflow emits a warning
and leaves the PR for manual handling. It never approves reviews or bypasses rules.

This deliberately trusts stable upstream releases: hashes checked against GitHub
release digests do not protect against a compromised upstream release. Disable
auto-merge on a PR if you want to review its release notes before it lands.
Dependabot's weekly updates to SHA-pinned GitHub Actions are not auto-merged by
this workflow.
