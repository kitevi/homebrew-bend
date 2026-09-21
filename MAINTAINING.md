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
5. Protect `main` and require both architecture-specific formula checks plus the
   updater test job before merging. Check names appear after the first CI run.

## Why a separate token

A separate token is intentional: PRs created with the built-in `GITHUB_TOKEN`
generally do not trigger additional workflows. `TAP_UPDATE_TOKEN` lets the update
PR trigger macOS CI normally. The updater refuses to run without it; there is no
silent fallback that would leave update PRs untested. A GitHub App token can be
used instead if you later want to avoid a personal token.

## Merging update PRs

Review upstream release notes and the PR diff before merging: the updater
verifies hashes against GitHub release digests, but the release notes are your
view into what actually changed upstream. Dependabot proposes updates to the
SHA-pinned GitHub Actions weekly.
