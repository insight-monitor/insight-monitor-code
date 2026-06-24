#!/usr/bin/env python3
"""
Generate TypeScript types from backend Pydantic models.
Run: python scripts/generate_types.py
CI: Fails if generated types differ from committed.
"""
import subprocess
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).parent.parent / "backend"
DASHBOARD_API = Path(__file__).parent.parent / "dashboard" / "src" / "api"
GENERATED_DIR = DASHBOARD_API / "generated"

MODELS = [
    "backend.models.raw_event:RawEvent",
    "backend.models.session_context:SessionContext",
    "backend.models.intent_record:IntentRecord",
]

def main():
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    # Generate each model
    for model_spec in MODELS:
        model_name = model_spec.split(":")[-1]
        output_file = GENERATED_DIR / f"{model_name.lower()}.ts"

        result = subprocess.run([
            "datamodel-codegen",
            "--input", model_spec,
            "--input-file-type", "python",
            "--output", str(output_file),
            "--output-model-type", "typescript",
            "--target-python-version", "3.11",
            "--use-standard-collections",
            "--use-generic-container-types",
            "--enable-version-header",
            "--class-name", model_name,
        ], capture_output=True, text=True, cwd=BACKEND_ROOT)

        if result.returncode != 0:
            print(f"ERROR generating {model_name}:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return 1

        print(f"Generated: {output_file}")

    # Create index.ts
    index_content = "// Auto-generated from backend Pydantic models\n"
    index_content += "// DO NOT EDIT MANUALLY - Run scripts/generate_types.py\n\n"
    for model_spec in MODELS:
        model_name = model_spec.split(":")[-1]
        index_content += f"export * from './{model_name.lower()}';\n"

    index_file = GENERATED_DIR / "index.ts"
    index_file.write_text(index_content)
    print(f"Generated: {index_file}")

    # Update dashboard/src/api/types.ts to re-export
    types_file = DASHBOARD_API / "types.ts"
    types_content = "// Re-exports generated types + frontend-only types\n"
    types_content += "// Generated types from: backend/models/*.py\n\n"
    types_content += "export * from './generated';\n\n"
    types_content += "// Frontend-only types (not in backend)\n"
    types_content += "export interface UIState {\n"
    types_content += "  selectedSessionId: string | null;\n"
    types_content += "  sidebarOpen: boolean;\n"
    types_content += "  theme: 'dark' | 'light';\n"
    types_content += "}\n"

    types_file.write_text(types_content)
    print(f"Updated: {types_file}")

    return 0

if __name__ == "__main__":
    sys.exit(main())