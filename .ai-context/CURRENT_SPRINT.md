# Current Sprint: 3-Day MVP (Days 7-9 of 14)

## Sprint Goal
Deliver working MVP with Clean Architecture foundation:
- Capture Agent → API → Session Building → Intent Inference → Dashboard
- All code testable, documented, no singleton anti-patterns
- TypeScript types generated from backend

## Day 7 (Foundation) - Target: 2026-06-25
| Issue | Owner | Status | Branch |
|-------|-------|--------|--------|
| ARCH-1: Remove DB Singleton | Person A - Agent 1 | 🔄 In Progress | `refactor/remove-database-singleton` |
| ARCH-2: Repository Ports | Person A - Agent 2 | ⏳ Pending | `refactor/extract-repository-ports` |
| ARCH-3: Domain Layer | Person B - Agent 1 | ⏳ Pending | `refactor/create-domain-layer` |

**Day 7 Definition of Done**:
- [ ] `Database` class has no singleton logic
- [ ] `application/ports/repositories.py` exists with 3 protocols
- [ ] `domain/entities/`, `value_objects/`, `events/`, `services/` created
- [ ] `Session` entity encapsulates lifecycle logic
- [ ] `SessionClassifier` domain service extracts matching logic
- [ ] Unit tests for domain (no DB)
- [ ] All CI passes

## Day 8 (Application + Integration) - Target: 2026-06-26
| Issue | Owner | Status | Branch |
|-------|-------|--------|--------|
| ARCH-4: Use Cases | Person B - Agent 2 | ⏳ Pending | `refactor/create-application-layer` |
| ARCH-5: Infra Repos | Person C - Agent 1 | ⏳ Pending | `refactor/infrastructure-repositories` |
| ARCH-6: DI Container | Person C - Agent 2 | ⏳ Pending | `refactor/di-composition-root` |
| ARCH-9: TypeScript Gen | Person D - Agent 1 | ⏳ Pending | `refactor/generate-typescript-types` |

**Day 8 Definition of Done**:
- [ ] 6 use cases implemented (IngestEvent, BuildSessions, InferIntent, CloseSession, GetSession, ListSessions)
- [ ] SQLite + InMemory repositories implement ports
- [ ] `container.py` wires all dependencies
- [ ] FastAPI routes use `Depends` for use cases
- [ ] TypeScript types generated and committed
- [ ] Integration smoke test passes

## Day 9 (Hardening + MVP) - Target: 2026-06-27
| Issue | Owner | Status | Branch |
|-------|-------|--------|--------|
| ARCH-7: Transactions | Person A - Agent 1 | ⏳ Pending | `refactor/transaction-boundaries` |
| ARCH-10: Docs Update | Person A - Agent 2 | ⏳ Pending | `docs/update-architecture-docs` |
| ARCH-11: Unit Tests | Person D - Agent 2 | ⏳ Pending | `refactor/unit-tests-with-mocks` |
| MVP Integration | All | ⏳ Pending | - |

**Day 9 Definition of Done**:
- [ ] Use cases use `db.transaction()` for atomicity
- [ ] Architecture docs reflect reality (`current-state.md`, ADRs)
- [ ] Unit tests >90% domain, >80% use cases
- [ ] E2E: Capture agent → Dashboard shows session with intent
- [ ] Tag `mvp-architecture-complete`

## Parallel / Post-MVP (Optional if time)
| Issue | Priority | Owner |
|-------|----------|-------|
| ARCH-8: Capture Agent Resilience | Low (Post-MVP) | - |
| Frontend Polish | Low (Post-MVP) | - |

## Blocker Tracking
| Blocker | Issue | Owner | Resolution Target |
|---------|-------|-------|-------------------|
| - | - | - | - |

## Daily Sync (15 min)
- **When**: Start of each day (async via GitHub issue comments)
- **Format**: Each person updates their agent status in issue comments
- **Escalation**: Tag orchestrator in issue if blocked >30 min