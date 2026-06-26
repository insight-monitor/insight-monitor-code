# AI Context Directory

This directory contains the **source of truth** for all AI agents and human developers working on Insight Monitor.

## File Index

| File | Purpose | Audience |
|------|---------|----------|
| `ARCHITECTURE.md` | Target Clean Architecture layer structure, dependency rules, patterns | All |
| `CODING_STANDARDS.md` | Python/TS conventions, layer boundaries, security rules, Git conventions | All |
| `AGENT_INSTRUCTIONS.md` | Mandatory startup checklist, workflow, code conventions, when blocked | AI Agents |
| `PORT_CONTRACTS.md` | Application layer port interfaces (Repository, LLM, EventBus, etc.) | Backend |
| `DOMAIN_MODEL.md` | Domain entities, value objects, events, services, business rules | Backend |
| `SECURITY_RULES.md` | Secrets, input validation, PII, SQL safety, dependency security, logging | All |
| `ERROR_PHILOSOPHY.md` | Classification rules, false positive/negative tolerance, redaction | All |
| `API_CONTRACTS.md` | REST endpoints, request/response types, TypeScript generation | Fullstack |
| `CURRENT_SPRINT.md` | 3-day sprint plan, issue assignments, daily gates, blocker tracking | Orchestrators |
| `AGENT_HANDOFF.md` | Template for inter-agent communication, context updates | AI Agents |
| `BRAND_GUIDELINES.md` | Voice, terminology, visual identity, messaging principles | Docs/Marketing |

## Usage

### For AI Agents (Mandatory Startup)
```bash
# Read all context files
cat .ai-context/ARCHITECTURE.md
cat .ai-context/CODING_STANDARDS.md
cat .ai-context/DOMAIN_MODEL.md
cat .ai-context/PORT_CONTRACTS.md
cat .ai-context/SECURITY_RULES.md
cat .ai-context/ERROR_PHILOSOPHY.md
cat .ai-context/API_CONTRACTS.md
cat .ai-context/AGENT_INSTRUCTIONS.md
cat .ai-context/CURRENT_SPRINT.md
```

### For Human Developers
1. Start with `ARCHITECTURE.md` and `CODING_STANDARDS.md`
2. Reference `PORT_CONTRACTS.md` when implementing use cases
3. Follow `DOMAIN_MODEL.md` for domain logic
4. Enforce `SECURITY_RULES.md` and `ERROR_PHILOSOPHY.md` in all code
5. Update `AGENT_HANDOFF.md` when completing work

## Maintenance
- **Update on every PR** that changes contracts, architecture, or standards
- **Source of truth**: This directory — not external docs
- **Version**: Increment in frontmatter when significant changes
- **CI**: Architecture tests enforce layer boundaries from `ARCHITECTURE.md`