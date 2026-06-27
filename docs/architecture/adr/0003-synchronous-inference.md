# ADR-0003: Synchronous Inference (No Celery/Redis)

## Status

Accepted

## Context

The inference pipeline needs to run when sessions close. Options included synchronous execution within the FastAPI request-response cycle, or async via Celery + Redis.

## Decision

Run inference synchronously within the request-response cycle. Celery + Redis would add two infrastructure dependencies that increase complexity without proportional benefit for an MVP where inference runs at most once per session close (not continuously).

## Consequences

- **Positive**: No Redis or Celery infrastructure to deploy and maintain
- **Positive**: Simpler codebase; no message queue, no worker management
- **Positive**: Immediate feedback on inference success/failure
- **Negative**: Request blocks during inference (typically 2-5 seconds for Gemini API)
- **Negative**: Not scalable under high concurrency; multiple simultaneous session closes would queue on the server
- **Negative**: No retry mechanism if inference fails mid-request; client must retry
