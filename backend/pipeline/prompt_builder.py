"""
pipeline/prompt_builder.py
---------------------------
Construye el prompt completo que se envía al LLM para la inferencia de intención.

Responsabilidades:
- Mantener la instrucción de sistema (SYSTEM_INSTRUCTION) que define el rol del
  modelo y las reglas de clasificación.
- Exponer el esquema JSON de salida esperada (OUTPUT_SCHEMA) para que el LLM
  produzca respuestas estructuradas y validables.
- Serializar los datos de sesión y eventos en texto legible para el modelo
  (contexto ambiental).
- Inyectar opcionalmente contexto del usuario (preferencias, rol, proyecto).

Este módulo no hace llamadas al LLM; sólo prepara el texto del prompt.
"""

import json


# ---------------------------------------------------------------------------
# SYSTEM_INSTRUCTION
# ---------------------------------------------------------------------------
# Bloque de instrucciones que se inyecta al inicio del prompt como contexto
# del sistema. Define:
#   - El rol del modelo (analista de actividad imparcial).
#   - Las categorías de clasificación (session_type, category).
#   - Las reglas de evidencia y confianza.
#   - La lógica de desambiguación contextual (misma app, distintos contextos).
#
# Este texto es fijo para todos los prompts; no varía por sesión.
# Si necesitas ajustar el comportamiento del LLM, edita aquí.
# ---------------------------------------------------------------------------
SYSTEM_INSTRUCTION = """You are an impartial activity analyst. Your task is to analyze work/study sessions and classify them into the structured JSON output described below.

SESSION TYPE (the primary classification):
- skill_development: The user is learning a new technical or theoretical skill (tutorials, courses, documentation, deliberate practice).
- applied_learning: The user is applying knowledge in a practical project (programming, design, real-world problem solving).
- peer_collaboration: The user is collaborating with other people (meetings, pair programming, code review, group chat).
- ambiguous: There is insufficient evidence to determine the type.
- personal: Personal activity unrelated to work or study.

CATEGORY (a secondary, more specific classification):
- Provide a fine-grained sub-type within the session_type. For example, if session_type is 'skill_development', category could be 'react_tutorial' or 'python_course'. If 'applied_learning', category could be 'feature_development' or 'bug_fixing'. Use your best judgment based on the evidence.

GOAL:
- Write a concise, specific, action-oriented sentence describing what the user was trying to accomplish (e.g., \"The user was implementing a REST API endpoint for user authentication\").

ALTERNATIVES:
- List 1-3 plausible alternative interpretations of the session activity. These are other possible goals or session types that could fit the evidence. If the session is clear, list less likely alternatives. If the session is ambiguous, list more plausible alternatives.

EVIDENCE:
- Each item should be a specific, concrete observation from the event data (e.g., \"Switched from VS Code to MDN documentation for DOM API reference\", \"Discord chat messages in #coder-channel during active coding\").

APP SUMMARY:
- primary_apps: List the 3-5 most used applications in order of estimated usage time.
- total_context_switches: Count how many times the user switched between different applications during the session. A switch occurs when the focused window changes to a different application (not just different tabs within the same browser).
- estimated_typing_intensity: Classify the overall keyboard activity as 'low' (mostly browsing/reading), 'medium' (moderate typing with breaks), or 'high' (sustained typing throughout).

RAW_TIMELINE_SUMMARY:
- A brief 2-4 sentence narrative describing the chronological flow of the session (e.g., \"The session started with VS Code open on a React project. Mid-session the user consulted MDN docs and Discord, then returned to coding. Towards the end there was a YouTube break.\").

TAGS:
- 3-8 short keywords or phrases (lowercase) that characterize the session topic, tools, and activities (e.g., [\"react\", \"api\", \"documentation\", \"discord\", \"vs-code\"]).

RULES:
1. Base your analysis ONLY on the provided evidence. Do not fabricate details.
2. Do not make assumptions about intentions without evidence.
3. Browser tabs, window titles, window focus sequences, and app switches are important clues for inferring intent.
4. Use ALL available signals together to disambiguate: window titles + screenshot presence + input activity + focus continuity. A single signal in isolation is rarely sufficient for a confident classification.
5. Identify friction points when evident (e.g., frequent app switching, error dialogs, search windows). If no friction is evident, return an empty list for friction_points and null for friction_confidence.
6. When little evidence exists, assign \"ambiguous\" with low confidence and include the limiting factor in the evidence list (e.g., \"Only one signal source available: window title alone\").

CONFIDENCE MODEL:
- goal_confidence, category_confidence, and friction_confidence use the [0.0, 1.0] scale:
  - 0.8 - 1.0: High confidence. Strong evidence, alternatives may exist but are less supported.
  - 0.5 - 0.79: Moderate confidence. Multiple interpretations are plausible. Include alternatives.
  - 0.3 - 0.49: Low confidence. Mark as uncertain. Default session_type should lean toward \"ambiguous\".
  - Below 0.3: Insufficient evidence. session_type MUST be \"ambiguous\" and evidence must explain the limitation.

CONTEXTUAL DISAMBIGUATION:
- The SAME application can indicate DIFFERENT intents depending on surrounding signals:
  - YouTube + code editor visible + \"tutorial\" in title + typing activity = work-relevant learning
  - YouTube + long playback + no input activity + entertainment title = personal break
  - Discord + active coding + documentation in context = peer collaboration / support
  - Discord isolated with no work apps = personal chat
  - Frequent switching between IDE + browser + documentation in a learning context = expected learning behavior, NOT friction
- Always evaluate the full pattern of signals, not any single app in isolation."""


# ---------------------------------------------------------------------------
# OUTPUT_SCHEMA
# ---------------------------------------------------------------------------
# Esquema JSON Schema que se incluye al final de cada prompt para que el LLM
# sepa exactamente qué estructura devolver.
#
# El campo "required" lista los campos mínimos obligatorios; el resto son
# opcionales según la evidencia disponible.
#
# Este esquema está alineado 1:1 con los campos de IntentRecord para que
# IntentParser pueda validar y mapear la respuesta sin transformaciones.
# ---------------------------------------------------------------------------
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "session_type": {
            "type": "string",
            "enum": ["skill_development", "applied_learning", "peer_collaboration", "ambiguous", "personal"]
        },
        "goal": {"type": "string"},
        "goal_confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "friction_points": {
            "type": "array",
            "items": {"type": "string"}
        },
        "friction_confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "category": {"type": "string"},
        "category_confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "tags": {
            "type": "array",
            "items": {"type": "string"}
        },
        "evidence": {
            "type": "array",
            "items": {"type": "string"}
        },
        "alternatives": {
            "type": "array",
            "items": {"type": "string"}
        },
        "app_summary": {
            "type": "object",
            "properties": {
                "primary_apps": {"type": "array", "items": {"type": "string"}},
                "total_context_switches": {"type": "integer"},
                "estimated_typing_intensity": {"type": "string", "enum": ["low", "medium", "high"]}
            }
        },
        "raw_timeline_summary": {"type": "string"}
    },
    "required": ["session_type", "goal", "goal_confidence", "category", "category_confidence", "evidence"]
}


class PromptBuilder:
    """
    Construye el prompt completo para el LLM dado una sesión y sus eventos.

    El prompt resultante tiene cuatro secciones:
        1. SYSTEM INSTRUCTION  — Reglas de clasificación e instrucciones del analista.
        2. ENVIRONMENTAL CONTEXT — Datos de la sesión: tiempo, apps, eventos recientes.
        3. USER CONTEXT (opcional) — Preferencias o metadatos adicionales del usuario.
        4. OUTPUT FORMAT — El JSON Schema que el modelo debe respetar.

    Parámetros
    ----------
    user_context : dict opcional con pares clave-valor que describen preferencias
                   o información adicional del usuario (proyecto actual, idioma, etc.).
                   Si es None o vacío, la sección USER CONTEXT se omite del prompt.
    """

    def __init__(self, user_context: dict | None = None):
        self.user_context = user_context or {}

    def build(self, session: dict, events: list[dict]) -> str:
        """
        Ensambla el prompt final concatenando todas las secciones.

        Parámetros
        ----------
        session : dict con los datos de la sesión (start_time, end_time,
                  app_sequence, active_apps, event_count, screenshot_count…).
        events  : Lista de dicts de eventos crudos asociados a la sesión.

        Retorna
        -------
        str — El prompt completo listo para enviarse al LLM.
        """
        env_context = self._build_environmental_context(session, events)
        user_ctx = self._build_user_context()

        parts = [
            f"## SYSTEM INSTRUCTION\n{SYSTEM_INSTRUCTION}\n",
            f"## ENVIRONMENTAL CONTEXT\n{env_context}\n",
        ]
        if user_ctx:
            parts.append(f"## USER CONTEXT\n{user_ctx}\n")

        parts.append(
            f"## OUTPUT FORMAT\n"
            f"Respond ONLY with a valid JSON object following this schema:\n"
            f"{json.dumps(OUTPUT_SCHEMA, indent=2)}\n"
            f"Do not include markdown, explanations, or any text outside the JSON."
        )

        return "\n".join(parts)

    def _build_environmental_context(self, session: dict, events: list[dict]) -> str:
        """
        Serializa los datos de la sesión y los últimos N eventos a texto plano.

        Se muestran como máximo 20 eventos recientes para no saturar el contexto
        del modelo. Cada evento se formatea como:
            [timestamp] event_type | process_name | window_title (truncado a 120 chars)

        Los campos app_sequence y active_apps se deserializan si vienen como
        string JSON (comportamiento de SQLite que serializa listas como texto).

        Parámetros
        ----------
        session : dict con los metadatos de la sesión.
        events  : Lista completa de eventos de la sesión.

        Retorna
        -------
        str — Bloque de texto con el contexto ambiental para el prompt.
        """
        lines = []
        lines.append(f"Session ID: {session.get('id', 'unknown')}")
        lines.append(f"Start time: {session.get('start_time', 'unknown')}")
        lines.append(f"End time: {session.get('end_time', 'unknown')}")
        lines.append(f"Duration (seconds): {session.get('duration_seconds', 'unknown')}")

        # app_sequence puede venir como string JSON desde SQLite
        app_sequence = session.get('app_sequence', [])
        if isinstance(app_sequence, str):
            app_sequence = json.loads(app_sequence)
        lines.append(f"App sequence: {', '.join(app_sequence) if app_sequence else 'none recorded'}")

        # active_apps también puede venir serializado como string JSON desde SQLite
        active_apps = session.get('active_apps', [])
        if isinstance(active_apps, str):
            active_apps = json.loads(active_apps)
        lines.append(f"Active apps: {', '.join(active_apps) if active_apps else 'none recorded'}")

        lines.append(f"Event count: {session.get('event_count', 0)}")
        lines.append(f"Screenshot count: {session.get('screenshot_count', 0)}")

        if events:
            max_shown = 20  # Límite de eventos recientes para no exceder el contexto del LLM
            lines.append(f"Recent events ({min(len(events), max_shown)} of {len(events)}):")
            for event in events[-max_shown:]:
                title = event.get('window_title', event.get('browser_tab_title', ''))
                ts = event.get('timestamp', '')
                etype = event.get('event_type', '')
                process = event.get('process_name', '')
                line = f"  [{ts}] {etype} | {process}"
                if title:
                    line += f" | {title[:120]}"  # Truncar título largo para mantener el prompt compacto
                lines.append(line)

        return "\n".join(lines)

    def _build_user_context(self) -> str:
        """
        Serializa el contexto del usuario a texto con formato de lista.

        Si user_context está vacío, retorna cadena vacía para que la sección
        USER CONTEXT se omita completamente del prompt.

        Formato de salida:
            - clave: valor
            - clave_lista:
              - item1
              - item2

        Retorna
        -------
        str — Bloque de texto con el contexto del usuario, o "" si no hay.
        """
        if not self.user_context:
            return ""
        lines = []
        for key, value in self.user_context.items():
            if isinstance(value, list):
                lines.append(f"- {key}:")
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)
