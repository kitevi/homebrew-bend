# Contributing

Bug reports and PRs are welcome. Maintainer-only operations (token setup,
merging update PRs) live in [MAINTAINING.md](MAINTAINING.md).

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

## What CI checks

CI installs the formula and tests the CLI, Base library, guide, and a small Bend
program on Apple Silicon and Intel macOS runners, then runs Homebrew audit and
style checks. Update PRs must pass before merging; the checks are required on
the protected `main` branch.
