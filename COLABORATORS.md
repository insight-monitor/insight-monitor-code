# Colaborators Guide

## Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to run automated checks (linting, type checking, secrets scanning) before every commit. The configuration is in `.pre-commit-config.yaml`.

### Getting Started

1. Install pre-commit: `pip install pre-commit`
2. Install the hooks: `pre-commit install`
3. (Optional) Install the pre-push hook: `pre-commit install --hook-type pre-push`

Hooks run automatically on `git commit`. If a hook fails, fix the issue and stage the changes again.

### Tutorials

- [Pre-commit Official Docs](https://pre-commit.com/#intro)
- [Pre-commit: A Quick Guide (YouTube)](https://www.youtube.com/results?search_query=pre-commit+tutorial)

### What Runs

| Hook | Stage | Purpose |
|------|-------|---------|
| ruff | commit | Lint and auto-format Python |
| mypy | commit | Type check Python with `--strict` |
| gitleaks | commit | Scan for secrets and API keys |
| pre-commit-hooks | commit | Trailing whitespace, YAML/JSON/TOML validation, merge conflict detection |
| pytest-unit | push | Run fast unit tests before pushing |
