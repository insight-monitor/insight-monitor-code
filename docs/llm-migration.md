# Migración Gemini → OpenAI

## Resumen
El proveedor LLM por defecto cambió de **Gemini** (`gemini-2.0-flash`) a **OpenAI** (`gpt-4o-mini`) para mejorar estabilidad, latencia y costo.

---

## Cambios en configuración

### Variables de entorno (`.env`)

| Antigua | Nueva | Descripción |
|---------|-------|-------------|
| `GEMINI_API_KEY` | `API_KEY` | API key del proveedor seleccionado |
| `GEMINI_MODEL` | `LLM_MODEL` | Nombre del modelo (`gpt-4o-mini`, `gemini-2.0-flash`, etc.) |
| — | `LLM_PROVIDER` | `openai` \| `gemini` (default: `openai`) |

**Ejemplo `.env`:**
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
API_KEY=sk-proj-xxxxxxxxxxxxx
```

---

## Cambios en código

### `backend/config.py`
```python
# Antes
gemini_api_key: str
gemini_model: str = "gemini-2.0-flash"

# Ahora
api_key: str
llm_model: str = "gpt-4o-mini"
llm_provider: str = "openai"
```

### `backend/services/llm_service.py`
Nuevo `LLMService` con factory:
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
    raise ValueError(f"Proveedor no soportado: {self.provider}")
```

Método unificado `generate_structured(prompt)` que maneja ambos SDKs.

---

## Pasos para migrar

1. **Obtener API key de OpenAI**
   - Crear cuenta en https://platform.openai.com
   - Generar API key en Settings → API Keys

2. **Actualizar `.env`**
   ```bash
   cp backend/.env.example backend/.env
   # Editar con tus valores
   ```

3. **Instalar dependencia**
   ```bash
   cd backend
   poetry install  # openai>=1.0.0 ya está en pyproject.toml
   ```

4. **Verificar**
   ```bash
   poetry run python scripts/test_e2e_gemini.py
   # Debe mostrar: "Provider: openai, Model: gpt-4o-mini"
   ```

---

## Rollback a Gemini (si necesario)

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash
API_KEY=your-gemini-api-key
```

El código soporta ambos proveedores simultáneamente.

---

## Notas
- `gpt-4o-mini` es ~10x más barato que `gpt-4o` y suficiente para clasificación de intención
- Confianza típica en tests E2E: 0.30–0.50 (`ambiguous`) por ausencia de `input_activity` en datos sintéticos
- Para producción, asegurar `input_activity` real del capture agent para subir confianza > 0.7