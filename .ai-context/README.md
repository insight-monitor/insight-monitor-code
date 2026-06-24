# AI Agent Context Directory

This directory is the **single source of truth** for all AI agents working on Insight Monitor.

## File Index

| File | Purpose | Updated By |
|------|---------|------------|
| `ARCHITECTURE.md` | Target Clean Architecture layers, patterns | Person A |
| `CODING_STANDARDS.md` | Python/TS conventions, git, security | Person A |
| `DOMAIN_MODEL.md` | Entities, VOs, events, services, rules | Person B |
| `PORT_CONTRACTS.md` | Repository, LLM, EventBus, Prompt ports | Person A/B |
| `API_CONTRACTS.md` | REST endpoints, TypeScript types (generated) | Person D |
| `ERROR_PHILOSOPHY.md` | Classification rules, redaction requirements | All (read-only) |
| `SECURITY_RULES.md` | Secrets, PII, SQL, deps, network, logging | All (read-only) |
| `BRAND_GUIDELINES.md` | Colors, typography, components, layout | Person D |
| `CURRENT_SPRINT.md` | Day 7/8/9 goals, status, blockers | All (orchestrators) |
| `AGENT_HANDOFF.md` | Agent-to-agent context transfer template | All agents |
| `AGENT_INSTRUCTIONS.md` | Mandatory startup & workflow for agents | All agents |

## Usage

### For AI Agents
```bash
# On session start - READ ALL
cat .ai-context/ARCHITECTURE.md
cat .ai-context/CODING_STANDARDS.md
cat .ai-context/DOMAIN_MODEL.md
cat .ai-context/PORT_CONTRACTS.md
cat .ai-context/SECURITY_RULES.md
cat .ai-context/AGENT_INSTRUCTIONS.md
```

### For Human Orchestrators
- Update `CURRENT_SPRINT.md` daily
- Review `AGENT_HANDOFF.md` for decisions
- Ensure context files updated at each merge

## Update Rules

**Any PR changing contracts MUST update relevant context files:**
- Domain changes → `DOMAIN_MODEL.md`
- Port changes → `PORT_CONTRACTS.md`
- Architecture changes → `ARCHITECTURE.md`
- API changes → `API_CONTRACTS.md` (auto via `scripts/generate_types.py`)
- Security changes → `SECURITY_RULES.md`

**CI enforces this**: `context-check` job fails if code changed but `.ai-context/` not updated.

## Related Files

- Main Plan: `../AI_AGENT_MVP_PLAN.md`
- CI Workflow: `../.github/workflows/ai-agent-ci.yml`
- Pre-commit: `../.pre-commit-config.yaml`
- Dependabot: `../.github/dependabot.yml`
- Type Generation: `../scripts/generate_types.py`