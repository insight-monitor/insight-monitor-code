---
title: Prompt Architecture
type: reference
domain: inference
priority: high
status: review
version: 0.1.0
---

# Prompt Architecture

## Structure

The system prompt has four layers, assembled at inference time:

### 1. System instruction (immutable)
Defines the model's role: impartial activity analyst. Cannot be modified. Contains safety constraints, output format, and redaction rules.

### 2. Environmental context (auto-populated)
Injected automatically from collected signals: active window, visible content, recent activity history, time of day, current objective if defined.

### 3. User context (configurable)
Injected from the user's defined context: role, objectives, app classifications, schedule, sensitivity keywords.

### 4. Custom instructions (restricted)
In enterprise mode: disabled or limited to approved templates. In personal mode: user can append additional instructions within a character limit, subject to safety filtering.

## Output format

All inferences must follow a structured JSON schema:
```json
{
  "task_hypothesis": "string",
  "confidence": 0.0-1.0,
  "evidence": ["signal1", "signal2"],
  "alternatives": ["alt1", "alt2"],
  "sensitivity_flag": "none|low|medium|high"
}
```
