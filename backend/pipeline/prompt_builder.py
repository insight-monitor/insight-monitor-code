import json



SYSTEM_INSTRUCTION = """Eres un analista de actividad imparcial. Tu tarea es analizar sesiones de trabajo/estudio y clasificarlas en una de las siguientes categorías RIWI:

RIWI CATEGORIES:
- skill_development: El usuario está aprendiendo una nueva habilidad técnica o teórica (tutoriales, cursos, documentación, práctica deliberada).
- applied_learning: El usuario está aplicando conocimientos en un proyecto práctico (programación, diseño, resolución de problemas reales).
- peer_collaboration: El usuario está colaborando con otras personas (reuniones, pair programming, code review, chat grupal).
- ambiguous: No hay suficiente evidencia para determinar la categoría.
- personal: Actividad personal no relacionada con trabajo/estudio.

REGLAS:
1. Basa tu análisis ÚNICAMENTE en la evidencia proporcionada.
2. Si hay poca evidencia, asigna "ambiguous" con confianza baja.
3. No hagas suposiciones sobre intenciones sin evidencia.
4. Las pestañas del navegador y títulos de ventana son pistas importantes.
5. Identifica puntos de fricción cuando sea evidente (ej: cambios frecuentes de app, errores, ventanas de búsqueda)."""


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
    def __init__(self, user_context: dict | None = None):
        self.user_context = user_context or {}

    def build(self, session: dict, events: list[dict]) -> str:
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
            f"Responde ÚNICAMENTE con un objeto JSON válido que siga este esquema:\n"
            f"{json.dumps(OUTPUT_SCHEMA, indent=2)}\n"
            f"No incluyas markdown, explicaciones ni texto adicional fuera del JSON."
        )

        return "\n".join(parts)

    def _build_environmental_context(self, session: dict, events: list[dict]) -> str:
        lines = []
        lines.append(f"Session ID: {session.get('id', 'unknown')}")
        lines.append(f"Start time: {session.get('start_time', 'unknown')}")
        lines.append(f"End time: {session.get('end_time', 'unknown')}")
        lines.append(f"Duration (seconds): {session.get('duration_seconds', 'unknown')}")

        app_sequence = session.get('app_sequence', [])
        if isinstance(app_sequence, str):
            app_sequence = json.loads(app_sequence)
        lines.append(f"App sequence: {', '.join(app_sequence) if app_sequence else 'none recorded'}")

        active_apps = session.get('active_apps', [])
        if isinstance(active_apps, str):
            active_apps = json.loads(active_apps)
        lines.append(f"Active apps: {', '.join(active_apps) if active_apps else 'none recorded'}")

        lines.append(f"Event count: {session.get('event_count', 0)}")
        lines.append(f"Screenshot count: {session.get('screenshot_count', 0)}")

        if events:
            lines.append(f"Recent events ({min(len(events), 10)} of {len(events)}):")
            for event in events[-10:]:
                title = event.get('window_title', event.get('browser_tab_title', ''))
                ts = event.get('timestamp', '')
                etype = event.get('event_type', '')
                process = event.get('process_name', '')
                line = f"  [{ts}] {etype} | {process}"
                if title:
                    line += f" | {title[:80]}"
                lines.append(line)

        return "\n".join(lines)

    def _build_user_context(self) -> str:
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
