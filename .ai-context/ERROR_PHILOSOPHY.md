# Error Philosophy (From docs/architecture/error-philosophy.md)

## Guiding Principle
> The cost of a false accusation exceeds the cost of a missed detection. The system is tuned to minimize harm to the user, not to maximize detection.

## Classification Rules
| Error Type | Tolerance | Action |
|------------|-----------|--------|
| False Positive (Productivity) | Near Zero | Default to "ambiguous" if uncertain |
| False Negative (Productivity) | Acceptable | Better to classify nothing than misclassify work |
| False Positive (Sensitive Data) | Unacceptable | Aggressive redaction, lose context if needed |
| False Negative (Sensitive Data) | Acceptable | Log/audit can catch borderline cases |

## Implementation Requirements
1. **LLM System Prompt**: Must encode these rules (see `PromptBuilder.SYSTEM_INSTRUCTION`)
2. **Confidence Thresholds**: Low confidence → "ambiguous" category
3. **Redaction Pipeline**: Before LLM call, strip:
   - URLs with credentials (`://user:pass@`)
   - Health terms (regex patterns)
   - PII patterns (emails, phones, SSN, credit cards)
   - Private communication identifiers
4. **Default Classification**: "ambiguous" with low confidence when evidence insufficient

## Code Locations
- `backend/pipeline/prompt_builder.py` - SYSTEM_INSTRUCTION
- `backend/pipeline/intent_parser.py` - Validation enforces rules
- `capture/window_tracker.py` - URL extraction (potential PII source)
- **Future**: Redaction service in application layer