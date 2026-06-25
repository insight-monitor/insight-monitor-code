# Modelo de Confianza (Confidence Score)

## Rangos

| Rango | Etiqueta | Interpretación |
|-------|----------|----------------|
| 0.00 – 0.30 | `ambiguous` | Sin señales claras; fallback por defecto |
| 0.30 – 0.60 | `ambiguous` | Hipótesis débil; evidencia parcial |
| 0.60 – 0.80 | `moderate` | Señales consistentes; intención probable |
| 0.80 – 1.00 | `high` | Evidencia fuerte; intención clara |

## Scores por componente

- `goal_confidence`: Qué tan seguro está el LLM del objetivo textual
- `category_confidence`: Certidumbre de la categoría (`skill_development`, `applied_learning`, etc.)
- `friction_confidence`: Confianza en puntos de fricción detectados (puede ser `null`)

## Comportamiento en tests E2E

Tests sintéticos (`scripts/test_e2e_gemini.py`) generan eventos **sin `input_activity` real** → el LLM ve solo `window_focus` y `screenshot` → confianzas 0.30–0.50 (`ambiguous`).

**En producción** con capture agent real (keystrokes, clicks, scrolls):
- `input_activity` presente → `goal_confidence` típico 0.7–0.9
- `category_confidence` típico 0.75–0.95

## Umbrales recomendados

| Acción | Umbral mínimo |
|--------|---------------|
| Mostrar en dashboard | 0.30 |
| Alertar fricción | 0.60 |
| Auto-categorizar | 0.75 |
| Entrenar modelo | 0.80 |

## Notas de implementación

- `PromptBuilder` inyecta rangos en `SYSTEM_INSTRUCTION` para calibrar al LLM
- `IntentParser` valida que scores estén en [0, 1]
- Valores `null` = "no evaluado" (distinto de 0.0)