# ADR-0006: Service Abstractions and Expanded Clean Architecture

## Status

Accepted

## Context

The initial Clean Architecture migration (ADR-0005) covered domain entities, repository ports, and use cases but left external services (LLM, prompt building, intent parsing) as direct concrete dependencies. Additionally, the ticket feature was originally implemented bypassing domain ports by directly depending on the SQLite Database class from routes.

Separate concerns:

- **External services** (LLM providers, prompt builders, response parsers) needed abstract interfaces so use cases could depend on abstractions rather than concrete implementations.
- **Tickets** needed proper Clean Architecture treatment with domain ports and use cases, consistent with the rest of the codebase.

## Decision

### 1. Service Abstraction Layer

Define abstract interfaces (`backend/domain/ports/services.py`) for external services:

- `ILLMService` — abstract interface for LLM completion services with `generate_structured()` and `_parse_json_response()` methods
- `IPromptBuilder` — abstract interface for building LLM prompts from session/event data
- `IIntentParser` — abstract interface for parsing LLM responses into `IntentRecord` domain entities

Concrete implementations (`LLMService`, `PromptBuilder`, `IntentParser`) inherit from these interfaces, enabling:
- Dependency injection of mock services in unit tests
- Future LLM provider swaps without modifying use cases
- Type checking across the application layer

### 2. Ticket System with Clean Architecture

Implement tickets using the established pattern:

- **Domain ports**: `ITicketRepository`, `ICommentRepository` in `backend/domain/ports/repositories.py`
- **Infrastructure**: SQLite implementations (`TicketRepository`, `CommentRepository`) and InMemory implementations for testing
- **Use case**: `ManageTicketsUseCase` encapsulating all ticket business logic (CRUD, comments, stats, validation, cascade delete)
- **Presentation**: FastAPI routes (`/tickets`) depend only on the use case via DI — no direct database access

### 3. In-Memory Repositories for Testing

Implement `InMemoryTicketRepository` and `InMemoryCommentRepository` alongside existing in-memory repositories, enabling zero-dependency unit tests for the ticket use case.

## Consequences

- **Positive**: Service implementations are now swappable — e.g., switching from Gemini to OpenAI or a local model only requires a new concrete class implementing `ILLMService`
- **Positive**: All 26 ticket unit tests run with in-memory repos, no database required
- **Positive**: Routes have zero knowledge of database implementation — all wiring happens in DI
- **Positive**: Consistent architecture across all features (events, sessions, intents, tickets)
- **Negative**: Added boilerplate for three new port interfaces and their implementations
- **Negative**: Added boilerplate for ticket DI wiring
