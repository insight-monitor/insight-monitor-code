#!/usr/bin/env python3
"""
ARCH-9: Generate TypeScript types from Pydantic models.

Uses datamodel-codegen to generate TypeScript interfaces from backend Pydantic models.
Output: dashboard/src/api/generated-types.ts

Prerequisites:
    pip install datamodel-codegen
    # or: poetry add --group dev datamodel-codegen (in backend/)
"""

import shutil
import subprocess
import sys
from pathlib import Path


BACKEND_MODELS_DIR = Path(__file__).parent.parent / "backend" / "domain" / "entities"
OUTPUT_FILE = Path(__file__).parent.parent / "dashboard" / "src" / "api" / "generated-types.ts"


MODELS = [
    "raw_event.py",
    "session_context.py",
    "intent_record.py",
]


def main() -> int:
    # Check if datamodel-codegen is available
    if not shutil.which("datamodel-codegen"):
        print("Error: datamodel-codegen not found in PATH", file=sys.stderr)
        print("Install it with: pip install datamodel-codegen", file=sys.stderr)
        return 1

    # Build the command to generate TypeScript from multiple Pydantic files
    cmd = [
        "datamodel-codegen",
        "--input-file-type", "python",
        "--output", str(OUTPUT_FILE),
        "--output-model-type", "typescript",
        "--use-standard-collections",
        "--use-default-kwarg",
        "--field-constraints",
        "--use-schema-description",
        "--enum-field-as-literal", "all",
        "--disable-timestamp",
        "--use-title-as-name",
        "--wrap-in-class", "false",
    ]

    # Add all model files as input
    for model in MODELS:
        model_path = BACKEND_MODELS_DIR / model
        if model_path.exists():
            cmd.extend(["--input", str(model_path)])
        else:
            print(f"Warning: {model_path} not found", file=sys.stderr)

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return result.returncode

    # Post-process: add header comment
    header = """// AUTO-GENERATED FROM BACKEND PYDANTIC MODELS
// DO NOT EDIT MANUALLY - Run: python scripts/generate_types.py
// Source: backend/domain/entities/*.py

"""
    content = OUTPUT_FILE.read_text()
    if not content.startswith("// AUTO-GENERATED"):
        OUTPUT_FILE.write_text(header + content)
        print(f"Added header to {OUTPUT_FILE}")

    print(f"Generated {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())