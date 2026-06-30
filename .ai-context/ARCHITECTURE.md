# Target Architecture (Clean Architecture)

## Layer Structure
```
backend/
├── domain/                 # Pure business logic (NO external deps)
│   ├── entities/           # Session, IntentRecord, RawEvent
│   ├── value_objects/      # SessionId, EventId, Timestamp, InactivityThreshold
│   ├── events/             # SessionCreated, SessionClosed, IntentInferred
│   └── services/           # SessionClassifier (domain logic)
├── application/            # Use cases (orchestration, NO infra)
│   ├── ports/              # RepositoryPort, LLMPort, EventBusPort
│   ├── use_cases/          # IngestEvent, BuildSessions, InferIntent, CloseSession, GetSession, ListSessions
│   ├── dtos/               # Request/Response DTOs
│   └── services/           # EventPublisher
├── infrastructure/         # Concrete implementations
│   ├── persistence/        # SQLiteEventRepository, SQLiteSessionRepository, SQLiteIntentRepository, InMemory* (tests)
│   ├── llm/                # GeminiLLMService
│   └── config/             # Settings
└── interfaces/             # Delivery mechanisms
    ├── http/               # FastAPI routes (thin)
    └── cli/                # Capture agent
```

## Dependency Rule
```
domain ← application ← infrastructure
                ↑
         interfaces (depend on application)
```
**NEVER**: domain/application import from infrastructure
**ALWAYS**: infrastructure implements application ports

## Current State (Ref: ARCH-0 #41)
- ARCH-1: Remove DB singleton → Pass DB explicitly
- ARCH-2: Extract repository ports → application/ports/repositories.py
- ARCH-3: Domain layer → domain/
- ARCH-4: Application layer → application/
- ARCH-5: Infrastructure repos → infrastructure/persistence/
- ARCH-6: DI composition root → container.py
- ARCH-7: Transaction boundaries → Use cases manage transactions
- ARCH-8: Capture agent resilience → Post-MVP (optional)
- ARCH-9: TypeScript generation → scripts/generate_types.py
- ARCH-10: Update docs → docs/architecture/
- ARCH-11: Unit tests with mocks → tests/unit/

## Key Patterns
- **Repository Pattern**: Ports in application/ports, adapters in infrastructure/persistence
- **Use Case Pattern**: Single responsibility, input DTO → output DTO, depend on ports
- **Domain Events**: Emitted by entities, published after transaction commits
- **Value Objects**: Wrap primitives with validation (SessionId, InactivityThreshold)
- **Dependency Injection**: container.py creates all, FastAPI Depends for routes