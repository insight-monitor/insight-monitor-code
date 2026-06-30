# Git Branching Strategy

This repository follows the same convention as the docs repository. See [insight-monitor-docs: Git-branching.md](https://github.com/insight-monitor/insight-monitor-docs/blob/main/000-META/Git-branching.md) for the full strategy.

## Quick reference

| Branch | Purpose |
|---|---|
| `main` | Stable, published. Protected — requires PR + review. |
| `develop` | Integration branch. Daily work base. Light protection. |
| `<prefix>/<slug>` | Short-lived topic branches. Branch from `develop`, merge via PR. |

## Branch prefixes

| Prefix | Purpose | Example |
|---|---|---|
| `feat/` | New features, endpoints, components | `feat/inference-pipeline` |
| `fix/` | Bug fixes | `fix/session-builder-timeout` |
| `refactor/` | Restructuring without changing behavior | `refactor/database-connection` |
| `chore/` | CI/CD, config, tooling | `chore/add-pytest-workflow` |
| `security/` | Security patches (mandatory prefix) | `security/sanitize-input` |
| `topic/` | General changes | `topic/update-dependencies` |

## Commit format

Conventional commits: `<type>(<scope>): <subject>`

Examples:
- `feat(api): add POST /events/batch endpoint`
- `fix(capture): handle Wayland window detection`
- `refactor(storage): extract repository pattern`
