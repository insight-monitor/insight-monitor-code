---
title: Confidence Model
type: reference
domain: inference
priority: critical
status: review
version: 1.0.0
---

# Confidence Model

## Score representation

All inferences carry a confidence score in the range **[0.0, 1.0]**:
- **0.0** — No evidence supports this inference; pure guess
- **0.5** — Signal balance is neutral; multiple interpretations are equally plausible
- **0.8** — Strong evidence; alternative interpretations exist but are less supported
- **1.0** — Theoretically unattainable. Reserved for reflexivity (e.g., "this is an inference")

## Factors affecting confidence

| Factor | Impact | Example |
|---|---|---|
| Signal completeness | More signal sources → higher confidence | Screenshot + URL + interaction pattern > URL alone |
| Signal consistency | Aligned signals → higher confidence | IDE title + code screenshot + keyboard activity are all consistent with development |
| Context quality | Well-defined user context → higher confidence | Explicit role and objectives improve classification accuracy |
| Temporal continuity | Activity chain with no gaps → higher confidence | Continuous 45 minutes of related tasks vs fragmented switching |
| Historical baseline | Established patterns → more reliable deviation detection | Departure from normal workflow is meaningful when normal is known |
| Ambiguity of surface signals | Inherently ambiguous apps → lower confidence | Browser and office suites produce the widest range of possible intents |

## Confidence thresholds

| Range | Classification | Behavior |
|---|---|---|
| >= 0.8 | High confidence | Presented as likely classification with cited evidence |
| 0.5 – 0.79 | Moderate confidence | Flagged as probable. Alternative hypotheses included in output. |
| 0.3 – 0.49 | Low confidence | Marked as uncertain. Default classification is "ambiguous" unless overridden by context. |
| < 0.3 | Insufficient evidence | Not classified. Reported as "insufficient data." |

## Communication of uncertainty

All inference outputs at any confidence level must include:
1. The confidence score itself
2. The primary evidence sources used
3. Alternative hypotheses evaluated (if any)
4. The specific factor that limits confidence (e.g., "only one signal source available")

## Below-threshold handling

When confidence falls below the configurable threshold for a given classification:
- The system defaults to **"ambiguous"** — not "unproductive" or "distraction"
- The ambiguous classification is logged with the evidence and the reason for low confidence
- Downstream frontends must display the uncertainty visually (e.g., a grey badge, not red/green)
