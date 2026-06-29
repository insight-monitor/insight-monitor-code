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
                tree = ast.parse(f.read())
            except SyntaxError:
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and hasattr(node.func, "attr"):
                if node.func.attr in ("get", "post", "put", "delete", "patch"):
                    prefix = ""
                    for deco in (getattr(node, "decorator_list", []) if hasattr(node, "decorator_list") else []):
                        pass

                    method = node.func.attr.upper()
                    path = None
                    if node.args:
                        first = node.args[0]
                        if isinstance(first, ast.Constant):
                            path = first.value

                    if path is not None:
                        routes.append({"method": method, "path": path})

    for route_node in ast.walk(ast.parse(open(routes_dir / "__init__.py").read())):
        pass

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
            if not in_table and parts and parts[0].upper() in ("METHOD", "VERB"):
                in_table = True
                continue
            if in_table and len(parts) >= 2:
                method = parts[0].upper()
                path = parts[1]
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

    # The `prefix` from the router declaration needs to be considered
    # For simplicity, we extract the prefix from the route files
    router_prefixes = {}
    for py_file in routes_dir.glob("*.py"):
        if py_file.name.startswith("_"):
            continue
        with open(py_file, encoding="utf-8") as f:
            content = f.read()
        pref_match = re.search(r'prefix\s*=\s*["\']([^"\']+)["\']', content)
        if pref_match:
            prefix = pref_match.group(1)
            key = py_file.stem
            router_prefixes[key] = prefix

    full_code_keys = set()
    for method, path in code_keys:
        prefixed = path
        pp = path.split("/")
        if len(pp) >= 2:
            prefix_seg = pp[0]
        full_code_keys.add((method, path))

    missing_in_docs = full_code_keys - doc_keys
    missing_in_code = doc_keys - full_code_keys

    for method, path in sorted(missing_in_docs):
        errors.append(f"Route {method} {path} exists in code but NOT in docs/api/README.md")
    for method, path in sorted(missing_in_code):
        errors.append(f"Route {method} {path} exists in docs/api/README.md but NOT in code")

    if errors:
        print("API DOCS DRIFT DETECTED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"OK: docs/api/README.md documents all {len(full_code_keys)} API routes")
    sys.exit(0)


if __name__ == "__main__":
    main()
