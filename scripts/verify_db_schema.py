#!/usr/bin/env python3
"""
CI: Verify that docs/data-model/database-schema.md matches the actual SQL schema
defined in backend/infrastructure/db/sqlite/database.py.
Exit 1 on mismatch, 0 on success.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def parse_sql_schema(path: Path) -> dict[str, list[dict]]:
    tables: dict[str, list[dict]] = {}
    with open(path, encoding="utf-8") as f:
        content = f.read()

    create_pattern = re.compile(
        r'CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+(\w+)\s*\((.*?)\);',
        re.DOTALL | re.IGNORECASE,
    )
    col_pattern = re.compile(
        r'(\w+)\s+(\w+)(.*?)(?:,|$)',
        re.DOTALL,
    )

    for match in create_pattern.finditer(content):
        table_name = match.group(1)
        body = match.group(2)
        columns = []
        for cm in col_pattern.finditer(body):
            col_name = cm.group(1)
            col_type = cm.group(2).upper()
            if col_name.upper() in ("PRIMARY", "FOREIGN", "UNIQUE", "CHECK", "CONSTRAINT", "CREATE", "INDEX"):
                continue
            columns.append({"name": col_name, "type": col_type})
        if columns:
            tables[table_name] = columns

    return tables


def parse_md_schema(path: Path) -> dict[str, list[dict]]:
    tables: dict[str, list[dict]] = {}
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Match ### `table_name` or ### table_name
    table_sections = re.split(r'(?:^|\n)###\s+`(\w+)`', content, flags=re.MULTILINE)
    for i in range(1, len(table_sections), 2):
        table_name = table_sections[i].strip()
        section = table_sections[i + 1] if i + 1 < len(table_sections) else ""

        columns = []
        in_table = False
        for line in section.split("\n"):
            line = line.strip()
            if line.startswith("|") and "---" not in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if not in_table and parts and parts[0].lower() in ("column", "name"):
                    in_table = True
                    continue
                if in_table and len(parts) >= 2:
                    col_name = parts[0].strip("`")
                    col_type = parts[1].upper() if len(parts) > 1 else ""
                    if col_name and col_name.lower() not in ("column", "name"):
                        columns.append({"name": col_name, "type": col_type})
        if columns:
            tables[table_name] = columns

    return tables


def main():
    sql_path = ROOT / "backend" / "infrastructure" / "db" / "sqlite" / "database.py"
    md_path = ROOT / "docs" / "data-model" / "database-schema.md"

    if not sql_path.exists():
        print(f"ERROR: SQL schema file not found: {sql_path}")
        sys.exit(1)
    if not md_path.exists():
        print(f"WARNING: database-schema.md not found at {md_path}, skipping check")
        sys.exit(0)

    sql_tables = parse_sql_schema(sql_path)
    md_tables = parse_md_schema(md_path)

    errors = []

    for table_name, sql_columns in sql_tables.items():
        if table_name not in md_tables:
            errors.append(f"Table '{table_name}' exists in code but NOT in database-schema.md")
            continue

        md_columns = md_tables[table_name]
        sql_names = {c["name"] for c in sql_columns}
        md_names = {c["name"] for c in md_columns}

        missing_in_docs = sql_names - md_names
        missing_in_code = md_names - sql_names

        for col in sorted(missing_in_docs):
            errors.append(f"Column '{table_name}.{col}' exists in code but NOT in database-schema.md")
        for col in sorted(missing_in_code):
            errors.append(f"Column '{table_name}.{col}' exists in database-schema.md but NOT in code")

    # Check for tables in docs but not in code
    for table_name in md_tables:
        if table_name not in sql_tables:
            errors.append(f"Table '{table_name}' exists in database-schema.md but NOT in code")

    if errors:
        print("SCHEMA DRIFT DETECTED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print("OK: database-schema.md matches actual SQL schema")
    sys.exit(0)


if __name__ == "__main__":
    main()
