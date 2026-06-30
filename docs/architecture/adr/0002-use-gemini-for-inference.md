# ADR-0002: Use Gemini 2.0 Flash for Inference

## Status

Accepted

## Context

The system needs an LLM for classifying work sessions into intent categories. Options considered: Gemini 2.0 Flash, Claude Haiku, GPT-4o mini, and local models (Llama, Mistral).

## Decision

Use Gemini 2.0 Flash as the primary inference model. Gemini 2.0 Flash provides native multimodal support (screenshots + text in a single API call) at significantly lower cost than Claude or GPT-4o. Google's free tier ($0.15/1M input tokens) allows extensive testing during development.

## Consequences

- **Positive**: Native multimodal input (screenshots + text context) in one API call
- **Positive**: Lowest cost among comparable multimodal models
- **Positive**: 1M token context window allows long session analysis
- **Negative**: Vendor lock-in to Google AI; switching costs if Gemini API changes pricing or capabilities
- **Negative**: Requires internet connectivity; not suitable for air-gapped deployments
- **Negative**: No local fallback; inference unavailable if API is down
