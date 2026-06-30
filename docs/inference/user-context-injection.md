---
title: User Context Injection
type: concept
domain: inference
priority: high
status: review
version: 0.1.0
---

# User Context Injection

## How context reaches the model

User-defined context is serialized into a structured block appended to the system prompt before every inference cycle.

## Example: Full-time software developer

```
USER CONTEXT:
- Role: Senior Backend Developer
- Industry: Fintech
- Current objectives:
  - Deploy payment microservice (priority: high)
  - Refactor authentication module (priority: medium)
  - Code review for team PRs (priority: medium)
- Working hours: 09:00 - 18:00
- Meeting blocks: 10:00-11:00 daily standup, 14:00-15:00 sprint planning (Tue/Thu)
- App classifications:
  - VS Code / IntelliJ -> work-critical
  - Postman -> work-critical
  - Slack -> work-critical (team communication)
  - GitHub / GitLab -> work-critical
  - YouTube -> personal (except technical tutorials)
  - Stack Overflow / documentation -> work-critical
- Environment: Remote work, single monitor
- Break periods: 12:00-13:00 lunch, 15-min breaks at 11:00 and 16:00
```

## Effect on inference

The model uses this context to weight evidence:

- Slack message activity during work hours → **team collaboration** (not distraction)
- VS Code + Postman + terminal simultaneously → **active development / debugging**
- YouTube with "tutorial" in title → **work-relevant research**
- Browser open on GitHub during work hours → **code review task**
- YouTube with music or entertainment content → **personal / flagged as break**
- No activity during 12:00-13:00 → **scheduled lunch** (not unproductive idle)
- Context switch from IDE to Slack to documentation → **task coordination** (not distraction)
