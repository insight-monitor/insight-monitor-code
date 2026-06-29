#!/usr/bin/env python3
"""
CI: Verify that docs/api/README.md documents all API routes from backend/routes/*.py.
Exit 1 on mismatch, 0 on success.
"""

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def extract_routes(routes_dir: Path) -> list[dict]:
    routes = []
    for py_file in routes_dir.glob("*.py"):
        if py_file.name.startswith("_"):
            continue
        with open(py_file, encoding="utf-8") as f:
            try:
                content = f.read()
                tree = ast.parse(content)
            except SyntaxError:
                continue

        # Extract router prefix
        prefix = ""
        pref_match = re.search(r'prefix\s*=\s*["\']([^"\']+)["\']', content)
        if pref_match:
            prefix = pref_match.group(1)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and hasattr(node.func, "attr"):
                if node.func.attr in ("get", "post", "put", "delete", "patch"):
                    method = node.func.attr.upper()
                    path = None
                    if node.args:
                        first = node.args[0]
                        if isinstance(first, ast.Constant):
                            path = first.value

                    if path is not None:
                        full_path = prefix + path
                        routes.append({"method": method, "path": full_path})

    return routes


def parse_api_docs(doc_path: Path) -> list[dict]:
    routes = []
    if not doc_path.exists():
        return routes

    with open(doc_path, encoding="utf-8") as f:
        content = f.read()

    in_table = False
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("|") and "---" not in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if not in_table and parts and parts[0].lower() in ("method", "verb"):
                in_table = True
                continue
            if in_table and len(parts) >= 2:
                method = parts[0].replace("`", "").upper()  # Remove backticks
                path = parts[1].replace("`", "")  # Remove backticks
                if method in ("GET", "POST", "PUT", "DELETE", "PATCH"):
                    routes.append({"method": method, "path": path})

    return routes


def main():
    routes_dir = ROOT / "backend" / "routes"
    doc_path = ROOT / "docs" / "api" / "README.md"

    if not routes_dir.exists():
        print(f"ERROR: Routes directory not found: {routes_dir}")
        sys.exit(1)
    if not doc_path.exists():
        print(f"WARNING: API docs not found at {doc_path}, skipping check")
        sys.exit(0)

    code_routes = extract_routes(routes_dir)
    doc_routes = parse_api_docs(doc_path)

    code_keys = {(r["method"], r["path"]) for r in code_routes}
    doc_keys = {(r["method"], r["path"]) for r in doc_routes}

    errors = []

    missing_in_docs = code_keys - doc_keys
    missing_in_code = doc_keys - code_keys

    for method, path in sorted(missing_in_docs):
        errors.append(f"Route {method} {path} exists in code but NOT in docs/api/README.md")
    for method, path in sorted(missing_in_code):
        errors.append(f"Route {method} {path} exists in docs/api/README.md but NOT in code")

    if errors:
        print("API DOCS DRIFT DETECTED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"OK: docs/api/README.md documents all {len(code_keys)} API routes")
    sys.exit(0)


if __name__ == "__main__":
    main()
