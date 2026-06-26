# Confidence Model (Confidence Score)

## Ranges

| Range | Label | Interpretation |
|-------|-------|----------------|
| 0.00 – 0.30 | `ambiguous` | No clear signals; default fallback |
| 0.30 – 0.60 | `ambiguous` | Weak hypothesis; partial evidence |
| 0.60 – 0.80 | `moderate` | Consistent signals; probable intent |
| 0.80 – 1.00 | `high` | Strong evidence; clear intent |

## Scores by Component

- `goal_confidence`: How confident the LLM is about the textual goal
- `category_confidence`: Certainty of the category (`skill_development`, `applied_learning`, etc.)
- `friction_confidence`: Confidence in detected friction points (can be `null`)

## Behavior in E2E Tests

Synthetic tests (`scripts/test_e2e_gemini.py`) generate events **without real `input_activity`** → the LLM sees only `window_focus` and `screenshot` → confidences 0.30–0.50 (`ambiguous`).

**In production** with real capture agent (keystrokes, clicks, scrolls):
- `input_activity` present → typical `goal_confidence` 0.7–0.9
- typical `category_confidence` 0.75–0.95

## Recommended Thresholds

| Action | Minimum Threshold |
|--------|-------------------|
| Show in frontend | 0.30 |
| Alert friction | 0.60 |
| Auto-categorize | 0.75 |
| Train model | 0.80 |

## Implementation Notes

- `PromptBuilder` injects ranges into `SYSTEM_INSTRUCTION` to calibrate the LLM
- `IntentParser` validates that scores are in [0, 1]
- `null` values = "not evaluated" (different from 0.0)