# Gemini → OpenAI Migration

## Summary
The default LLM provider changed from **Gemini** (`gemini-2.0-flash`) to **OpenAI** (`gpt-4o-mini`) to improve stability, latency, and cost.

---

## Configuration Changes

### Environment Variables (`.env`)

| Old | New | Description |
|-----|-----|-------------|
| `GEMINI_API_KEY` | `API_KEY` | API key of the selected provider |
| `GEMINI_MODEL` | `LLM_MODEL` | Model name (`gpt-4o-mini`, `gemini-2.0-flash`, etc.) |
| — | `LLM_PROVIDER` | `openai` \| `gemini` (default: `openai`) |

**Example `.env`:**
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
API_KEY=sk-proj-xxxxxxxxxxxxx
```

---

## Code Changes

### `backend/config.py`
```python
# Before
gemini_api_key: str
gemini_model: str = "gemini-2.0-flash"

# Now
api_key: str
llm_model: str = "gpt-4o-mini"
llm_provider: str = "openai"
```

### `backend/services/llm_service.py`
New `LLMService` with factory:
```python
def __init__(self, provider: str | None = None, model: str | None = None, api_key: str | None = None):
    self.provider = provider or settings.llm_provider
    self.model = model or settings.llm_model
    self.api_key = api_key or settings.api_key
    self._client = self._create_client()

def _create_client(self):
    if self.provider == "openai":
        from openai import OpenAI
        return OpenAI(api_key=self.api_key)
    elif self.provider == "gemini":
        from google import genai
        return genai.Client(api_key=self.api_key)
    raise ValueError(f"Unsupported provider: {self.provider}")
```

Unified `generate_structured(prompt)` method that handles both SDKs.

---

## Migration Steps

1. **Get OpenAI API Key**
   - Create account at https://platform.openai.com
   - Generate API key in Settings → API Keys

2. **Update `.env`**
   ```bash
   cp backend/.env.example backend/.env
   # Edit with your values
   ```

3. **Install Dependency**
   ```bash
   cd backend
   poetry install  # openai>=1.0.0 already in pyproject.toml
   ```

4. **Verify**
   ```bash
   poetry run python scripts/test_e2e_gemini.py
   # Should show: "Provider: openai, Model: gpt-4o-mini"
   ```

---

## Rollback to Gemini (if needed)

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash
API_KEY=your-gemini-api-key
```

The code supports both providers simultaneously.

---

## Notes
- `gpt-4o-mini` is ~10x cheaper than `gpt-4o` and sufficient for intent classification
- Typical confidence in E2E tests: 0.30–0.50 (`ambiguous`) due to lack of `input_activity` in synthetic data
- For production, ensure real `input_activity` from capture agent to raise confidence > 0.7