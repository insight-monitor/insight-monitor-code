"""Prompt builder for LLM intent classification pipeline."""

import json


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
- Write a concise, specific, action-oriented sentence describing what the user was trying to accomplish (e.g., "The user was implementing a REST API endpoint for user authentication").

ALTERNATIVES:
- List 1-3 plausible alternative interpretations of the session activity. These are other possible goals or session types that could fit the evidence. If the session is clear, list less likely alternatives. If the session is ambiguous, list more plausible alternatives.

EVIDENCE:
- Each item should be a specific, concrete observation from the event data (e.g., "Switched from VS Code to MDN documentation for DOM API reference", "Discord chat messages in #coder-channel during active coding").

APP SUMMARY:
- primary_apps: List the 3-5 most used applications in order of estimated usage time.
- total_context_switches: Count how many times the user switched between different applications during the session. A switch occurs when the focused window changes to a different application (not just different tabs within the same browser).
- estimated_typing_intensity: Classify the overall keyboard activity as 'low' (mostly browsing/reading), 'medium' (moderate typing with breaks), or 'high' (sustained typing throughout).

RAW_TIMELINE_SUMMARY:
- A brief 2-4 sentence narrative describing the chronological flow of the session (e.g., "The session started with VS Code open on a React project. Mid-session the user consulted MDN docs and Discord, then returned to coding. Towards the end there was a YouTube break.").

TAGS:
- 3-8 short keywords or phrases (lowercase) that characterize the session topic, tools, and activities (e.g., ["react", "api", "documentation", "discord", "vs-code"]).

RULES:
1. Base your analysis ONLY on the provided evidence. Do not fabricate details.
2. Do not make assumptions about intentions without evidence.
3. Browser tabs, window titles, window focus sequences, and app switches are important clues for inferring intent.
4. Use ALL available signals together to disambiguate: window titles + screenshot presence + input activity + focus continuity. A single signal in isolation is rarely sufficient for a confident classification.
5. Identify friction points when evident (e.g., frequent app switching, error dialogs, search windows). If no friction is evident, return an empty list for friction_points and null for friction_confidence.
6. When little evidence exists, assign "ambiguous" with low confidence and include the limiting factor in the evidence list (e.g., "Only one signal source available: window title alone").

CONFIDENCE MODEL:
- goal_confidence, category_confidence, and friction_confidence use the [0.0, 1.0] scale:
  - 0.8 - 1.0: High confidence. Strong evidence, alternatives may exist but are less supported.
  - 0.5 - 0.79: Moderate confidence. Multiple interpretations are plausible. Include alternatives.
  - 0.3 - 0.49: Low confidence. Mark as uncertain. Default session_type should lean toward "ambiguous".
  - Below 0.3: Insufficient evidence. session_type MUST be "ambiguous" and evidence must explain the limitation.

CONTEXTUAL DISAMBIGUATION:
- The SAME application can indicate DIFFERENT intents depending on surrounding signals:
  - YouTube + code editor visible + "tutorial" in title + typing activity = work-relevant learning
  - YouTube + long playback + no input activity + entertainment title = personal break
  - Discord + active coding + documentation in context = peer collaboration / support
  - Discord isolated with no work apps = personal chat
  - Frequent switching between IDE + browser + documentation in a learning context = expected learning behavior, NOT friction
- Always evaluate the full pattern of signals, not any single app in isolation."""


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
    """Builds structured prompts for session classification."""

    def __init__(self, user_context: dict | None = None):
        self.user_context = user_context or {}

    def build(self, session: dict, events: list[dict]) -> str:
        """Construct the final prompt from system instruction, environmental data, and output schema."""
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
            max_shown = 20
            lines.append(f"Recent events ({min(len(events), max_shown)} of {len(events)}):")
            for event in events[-max_shown:]:
                title = event.get('window_title', event.get('browser_tab_title', ''))
                ts = event.get('timestamp', '')
                etype = event.get('event_type', '')
                process = event.get('process_name', '')
                line = f"  [{ts}] {etype} | {process}"
                if title:
                    line += f" | {title[:120]}"
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
