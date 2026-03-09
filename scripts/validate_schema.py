#!/usr/bin/env python3
"""
Database Schema Validator v2.0
Validates SQL schema files against production best-practice rules.

Usage:
    python validate_schema.py <schema_file.sql> [schema_file2.sql ...]
    python validate_schema.py --dir ./database/schema/
    python validate_schema.py --help

Rules checked:
    1.  Every CREATE TABLE has a PRIMARY KEY
    2.  Every REFERENCES has ON DELETE behavior
    3.  Every table has created_at column
    4.  Uses TIMESTAMPTZ (not bare TIMESTAMP)
    5.  No FLOAT/DOUBLE/REAL for monetary values
    6.  FK columns have explicit indexes
    7.  Soft delete (deleted_at) present on important tables
    8.  CHECK constraints exist for value validation
    9.  Table/column names follow snake_case convention
    10. Migrations wrapped in BEGIN/COMMIT transactions
    11. No SELECT * usage
    12. No reserved SQL keywords used as identifiers
    13. updated_at column with trigger on mutable tables
    14. ENUM or CHECK used for status-like fields
    15. No VARCHAR(255) overuse (lazy sizing)
"""

import re
import sys
import os
import argparse
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


# ─── Constants ───────────────────────────────────────────────────────────────

SQL_RESERVED_WORDS = {
    "user", "order", "group", "table", "column", "index", "key", "select",
    "insert", "update", "delete", "drop", "create", "alter", "grant",
    "revoke", "where", "from", "join", "left", "right", "inner", "outer",
    "on", "in", "not", "null", "primary", "foreign", "references",
    "check", "default", "constraint", "unique", "cascade", "set",
    "type", "role", "comment", "limit", "offset", "values", "into",
    "having", "between", "like", "as", "and", "or", "is", "exists",
    "case", "when", "then", "else", "end", "begin", "commit", "rollback",
    "trigger", "function", "procedure", "view", "schema", "database",
    "sequence", "partition", "range", "all", "any", "some", "true", "false",
}

SNAKE_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")

# Common status-like column names that should use ENUM or CHECK
STATUS_COLUMN_NAMES = {"status", "state", "type", "role", "level", "category", "kind"}


# ─── Data Classes ────────────────────────────────────────────────────────────

class Severity(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class Finding:
    rule: str
    severity: Severity
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class TableInfo:
    name: str
    line_number: int
    has_primary_key: bool = False
    has_created_at: bool = False
    has_updated_at: bool = False
    has_deleted_at: bool = False
    foreign_keys: list = field(default_factory=list)
    columns: list = field(default_factory=list)
    has_check_constraints: bool = False


@dataclass
class ValidationResult:
    file_path: str
    findings: list = field(default_factory=list)
    tables: list = field(default_factory=list)
    errors: int = 0
    warnings: int = 0
    passes: int = 0


# ─── Color Output ────────────────────────────────────────────────────────────

class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    BOLD = "\033[1m"
    NC = "\033[0m"

    @staticmethod
    def disable():
        Colors.RED = ""
        Colors.GREEN = ""
        Colors.YELLOW = ""
        Colors.BLUE = ""
        Colors.CYAN = ""
        Colors.BOLD = ""
        Colors.NC = ""


def print_finding(finding: Finding):
    """Print a single finding with color-coded severity."""
    icon_map = {
        Severity.ERROR: f"{Colors.RED}  ❌ FAIL{Colors.NC}",
        Severity.WARNING: f"{Colors.YELLOW}  ⚠️  WARN{Colors.NC}",
        Severity.INFO: f"{Colors.GREEN}  ✅ PASS{Colors.NC}",
    }
    icon = icon_map[finding.severity]
    line_info = f" (line {finding.line_number})" if finding.line_number else ""
    print(f"{icon}: [{finding.rule}]{line_info} {finding.message}")
    if finding.suggestion:
        print(f"          💡 {finding.suggestion}")


# ─── Parser ──────────────────────────────────────────────────────────────────

def parse_tables(content: str) -> list[TableInfo]:
    """Parse SQL content and extract table definitions with metadata."""
    tables = []
    lines = content.split("\n")

    current_table = None
    paren_depth = 0

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        upper = stripped.upper()

        # Skip comments
        if stripped.startswith("--") or stripped.startswith("/*"):
            continue

        # Detect CREATE TABLE
        match = re.match(
            r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:(\w+)\.)?(\w+)",
            stripped,
            re.IGNORECASE,
        )
        if match:
            table_name = match.group(2)
            current_table = TableInfo(name=table_name, line_number=i)
            tables.append(current_table)
            paren_depth = 0

        if current_table:
            paren_depth += stripped.count("(") - stripped.count(")")

            # Check for PRIMARY KEY
            if "PRIMARY KEY" in upper:
                current_table.has_primary_key = True

            # Check for created_at / updated_at / deleted_at
            if re.search(r"\bcreated_at\b", stripped, re.IGNORECASE):
                current_table.has_created_at = True
            if re.search(r"\bupdated_at\b", stripped, re.IGNORECASE):
                current_table.has_updated_at = True
            if re.search(r"\bdeleted_at\b", stripped, re.IGNORECASE):
                current_table.has_deleted_at = True

            # Check for REFERENCES (Foreign Keys)
            fk_match = re.search(
                r"(\w+)\s+\w+.*?REFERENCES\s+(\w+)\s*\((\w+)\)",
                stripped,
                re.IGNORECASE,
            )
            if fk_match:
                fk_col = fk_match.group(1)
                ref_table = fk_match.group(2)
                has_on_delete = "ON DELETE" in upper
                current_table.foreign_keys.append({
                    "column": fk_col,
                    "references": ref_table,
                    "has_on_delete": has_on_delete,
                    "line": i,
                })

            # Check for CHECK constraints
            if "CHECK" in upper and "CHECK (" in upper.replace("CHECK(", "CHECK ("):
                current_table.has_check_constraints = True

            # Extract column names (simplified)
            col_match = re.match(r"(\w+)\s+(UUID|VARCHAR|INTEGER|INT|BIGINT|BIGSERIAL|SERIAL|TEXT|BOOLEAN|DECIMAL|NUMERIC|FLOAT|DOUBLE|REAL|DATE|TIME|TIMESTAMP|TIMESTAMPTZ|JSONB?|BYTEA|INET|SMALLINT|CHAR)\b", stripped, re.IGNORECASE)
            if col_match:
                col_name = col_match.group(1).lower()
                col_type = col_match.group(2).upper()
                current_table.columns.append({
                    "name": col_name,
                    "type": col_type,
                    "line": i,
                    "raw": stripped,
                })

            # End of table definition
            if paren_depth <= 0 and ";" in stripped and current_table:
                current_table = None

    return tables


def find_indexes(content: str) -> list[dict]:
    """Extract all CREATE INDEX statements."""
    indexes = []
    for match in re.finditer(
        r"CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s+ON\s+(\w+)\s*(?:USING\s+\w+\s*)?\(([^)]+)\)",
        content,
        re.IGNORECASE,
    ):
        idx_name = match.group(1)
        table_name = match.group(2)
        columns = [c.strip().split()[0] for c in match.group(3).split(",")]
        indexes.append({
            "name": idx_name,
            "table": table_name,
            "columns": columns,
        })
    return indexes


# ─── Validation Rules ────────────────────────────────────────────────────────

def validate(content: str, file_path: str) -> ValidationResult:
    """Run all validation rules against a SQL schema file."""
    result = ValidationResult(file_path=file_path)
    tables = parse_tables(content)
    indexes = find_indexes(content)
    result.tables = tables
    lines = content.split("\n")
    upper_content = content.upper()

    # Build a set of indexed columns per table
    indexed_columns = {}
    for idx in indexes:
        tbl = idx["table"].lower()
        if tbl not in indexed_columns:
            indexed_columns[tbl] = set()
        for col in idx["columns"]:
            indexed_columns[tbl].add(col.lower())

    # ── Rule 1: PRIMARY KEY ──
    tables_without_pk = [t for t in tables if not t.has_primary_key]
    if tables_without_pk:
        for t in tables_without_pk:
            result.findings.append(Finding(
                rule="PRIMARY_KEY",
                severity=Severity.ERROR,
                message=f"Table `{t.name}` has no PRIMARY KEY",
                line_number=t.line_number,
                suggestion="Add a PRIMARY KEY column (e.g., id UUID PRIMARY KEY DEFAULT gen_random_uuid())",
            ))
    else:
        result.findings.append(Finding(
            rule="PRIMARY_KEY",
            severity=Severity.INFO,
            message=f"All {len(tables)} tables have PRIMARY KEY",
        ))

    # ── Rule 2: ON DELETE behavior ──
    fks_without_on_delete = []
    total_fks = 0
    for t in tables:
        for fk in t.foreign_keys:
            total_fks += 1
            if not fk["has_on_delete"]:
                fks_without_on_delete.append((t.name, fk))
    if fks_without_on_delete:
        for tname, fk in fks_without_on_delete:
            result.findings.append(Finding(
                rule="ON_DELETE",
                severity=Severity.WARNING,
                message=f"`{tname}.{fk['column']}` → `{fk['references']}` missing ON DELETE",
                line_number=fk["line"],
                suggestion="Add ON DELETE CASCADE, SET NULL, or RESTRICT",
            ))
    elif total_fks > 0:
        result.findings.append(Finding(
            rule="ON_DELETE",
            severity=Severity.INFO,
            message=f"All {total_fks} foreign keys have ON DELETE behavior",
        ))

    # ── Rule 3: created_at ──
    tables_without_created_at = [t for t in tables if not t.has_created_at]
    if tables_without_created_at:
        for t in tables_without_created_at:
            result.findings.append(Finding(
                rule="CREATED_AT",
                severity=Severity.WARNING,
                message=f"Table `{t.name}` missing `created_at` column",
                line_number=t.line_number,
                suggestion="Add: created_at TIMESTAMPTZ DEFAULT NOW()",
            ))
    else:
        result.findings.append(Finding(
            rule="CREATED_AT",
            severity=Severity.INFO,
            message=f"All {len(tables)} tables have created_at",
        ))

    # ── Rule 4: TIMESTAMPTZ vs TIMESTAMP ──
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        # Match bare TIMESTAMP (not followed by TZ)
        if re.search(r"\bTIMESTAMP\b(?!TZ)", stripped, re.IGNORECASE):
            # Exclude comments and strings
            if not stripped.startswith("--"):
                result.findings.append(Finding(
                    rule="TIMESTAMPTZ",
                    severity=Severity.WARNING,
                    message=f"Bare TIMESTAMP found (not timezone-aware)",
                    line_number=i,
                    suggestion="Use TIMESTAMPTZ instead of TIMESTAMP for timezone safety",
                ))

    if not any(f.rule == "TIMESTAMPTZ" for f in result.findings):
        if "TIMESTAMPTZ" in upper_content:
            result.findings.append(Finding(
                rule="TIMESTAMPTZ",
                severity=Severity.INFO,
                message="All timestamps use TIMESTAMPTZ (timezone-aware)",
            ))

    # ── Rule 5: No FLOAT/DOUBLE/REAL ──
    float_lines = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        if re.search(r"\b(FLOAT|DOUBLE|REAL)\b", stripped, re.IGNORECASE):
            float_lines.append(i)
    if float_lines:
        for ln in float_lines:
            result.findings.append(Finding(
                rule="NO_FLOAT",
                severity=Severity.ERROR,
                message=f"FLOAT/DOUBLE/REAL found — unsafe for monetary values",
                line_number=ln,
                suggestion="Use DECIMAL(12, 2) or INTEGER (store cents) instead",
            ))
    else:
        result.findings.append(Finding(
            rule="NO_FLOAT",
            severity=Severity.INFO,
            message="No FLOAT/DOUBLE/REAL types found",
        ))

    # ── Rule 6: FK columns have indexes ──
    fks_without_index = []
    for t in tables:
        tbl_lower = t.name.lower()
        tbl_indexes = indexed_columns.get(tbl_lower, set())
        for fk in t.foreign_keys:
            col_lower = fk["column"].lower()
            # PK columns are auto-indexed, skip those
            if col_lower == "id":
                continue
            if col_lower not in tbl_indexes:
                fks_without_index.append((t.name, fk))
    if fks_without_index:
        for tname, fk in fks_without_index:
            result.findings.append(Finding(
                rule="FK_INDEX",
                severity=Severity.WARNING,
                message=f"`{tname}.{fk['column']}` (FK → {fk['references']}) has no explicit index",
                line_number=fk["line"],
                suggestion=f"Add: CREATE INDEX idx_{tname}_{fk['column']} ON {tname}({fk['column']});",
            ))
    elif total_fks > 0:
        result.findings.append(Finding(
            rule="FK_INDEX",
            severity=Severity.INFO,
            message="All FK columns have corresponding indexes",
        ))

    # ── Rule 7: Soft delete ──
    tables_with_delete = [t for t in tables if t.has_deleted_at]
    if not tables_with_delete and len(tables) > 0:
        result.findings.append(Finding(
            rule="SOFT_DELETE",
            severity=Severity.WARNING,
            message="No tables have `deleted_at` — consider soft delete for important entities",
            suggestion="Add: deleted_at TIMESTAMPTZ (NULL = active, NOT NULL = deleted)",
        ))
    elif tables_with_delete:
        result.findings.append(Finding(
            rule="SOFT_DELETE",
            severity=Severity.INFO,
            message=f"Soft delete found on {len(tables_with_delete)}/{len(tables)} tables",
        ))

    # ── Rule 8: CHECK constraints ──
    tables_with_checks = [t for t in tables if t.has_check_constraints]
    if not tables_with_checks and len(tables) > 0:
        result.findings.append(Finding(
            rule="CHECK_CONSTRAINTS",
            severity=Severity.WARNING,
            message="No CHECK constraints found",
            suggestion="Add value validation, e.g. CHECK (price >= 0), CHECK (rating BETWEEN 1 AND 5)",
        ))
    else:
        result.findings.append(Finding(
            rule="CHECK_CONSTRAINTS",
            severity=Severity.INFO,
            message=f"CHECK constraints found on {len(tables_with_checks)}/{len(tables)} tables",
        ))

    # ── Rule 9: snake_case naming ──
    non_snake = []
    for t in tables:
        if not SNAKE_CASE_PATTERN.match(t.name):
            non_snake.append(t)
    if non_snake:
        for t in non_snake:
            result.findings.append(Finding(
                rule="SNAKE_CASE",
                severity=Severity.WARNING,
                message=f"Table `{t.name}` does not follow snake_case convention",
                line_number=t.line_number,
                suggestion=f"Rename to: {t.name.lower()}",
            ))
    elif tables:
        result.findings.append(Finding(
            rule="SNAKE_CASE",
            severity=Severity.INFO,
            message="All table names follow snake_case convention",
        ))

    # ── Rule 10: Transaction wrapping ──
    has_begin = "BEGIN" in upper_content
    has_commit = "COMMIT" in upper_content
    if has_begin and has_commit:
        result.findings.append(Finding(
            rule="TRANSACTION",
            severity=Severity.INFO,
            message="Migration wrapped in transaction (BEGIN/COMMIT)",
        ))
    elif tables:
        result.findings.append(Finding(
            rule="TRANSACTION",
            severity=Severity.WARNING,
            message="No BEGIN/COMMIT found — wrap migrations in transactions",
            suggestion="Add BEGIN; at start and COMMIT; at end of migration",
        ))

    # ── Rule 11: No SELECT * ──
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        if re.search(r"\bSELECT\s+\*\b", stripped, re.IGNORECASE):
            result.findings.append(Finding(
                rule="NO_SELECT_STAR",
                severity=Severity.WARNING,
                message="SELECT * found — always specify columns explicitly",
                line_number=i,
                suggestion="List specific columns instead of using *",
            ))

    # ── Rule 12: Reserved words as identifiers ──
    for t in tables:
        if t.name.lower() in SQL_RESERVED_WORDS:
            result.findings.append(Finding(
                rule="RESERVED_WORD",
                severity=Severity.ERROR,
                message=f"Table name `{t.name}` is a SQL reserved word",
                line_number=t.line_number,
                suggestion=f"Rename to avoid conflicts (e.g., `{t.name}` → `app_{t.name}s`)",
            ))
        for col in t.columns:
            if col["name"] in SQL_RESERVED_WORDS:
                result.findings.append(Finding(
                    rule="RESERVED_WORD",
                    severity=Severity.WARNING,
                    message=f"Column `{t.name}.{col['name']}` is a SQL reserved word",
                    line_number=col["line"],
                    suggestion=f"Consider renaming to avoid potential issues",
                ))

    # ── Rule 13: updated_at with trigger ──
    has_trigger_func = bool(re.search(r"updated_at\s*=\s*NOW\(\)", content, re.IGNORECASE))
    mutable_tables = [t for t in tables if t.has_updated_at]
    if mutable_tables and not has_trigger_func:
        result.findings.append(Finding(
            rule="UPDATED_AT_TRIGGER",
            severity=Severity.WARNING,
            message=f"{len(mutable_tables)} tables have updated_at but no auto-update trigger found",
            suggestion="Create a trigger function that sets updated_at = NOW() on UPDATE",
        ))
    elif mutable_tables and has_trigger_func:
        result.findings.append(Finding(
            rule="UPDATED_AT_TRIGGER",
            severity=Severity.INFO,
            message="updated_at auto-update trigger found",
        ))

    # ── Rule 14: Status fields should use ENUM or CHECK ──
    for t in tables:
        for col in t.columns:
            if col["name"] in STATUS_COLUMN_NAMES:
                has_constraint = (
                    "CHECK" in col["raw"].upper()
                    or "ENUM" in col["raw"].upper()
                    or re.search(r"\b\w+_\w+\b", col["type"])  # custom type
                )
                if col["type"] in ("VARCHAR", "TEXT") and not t.has_check_constraints:
                    result.findings.append(Finding(
                        rule="STATUS_TYPE_SAFETY",
                        severity=Severity.WARNING,
                        message=f"`{t.name}.{col['name']}` uses {col['type']} without ENUM or CHECK",
                        line_number=col["line"],
                        suggestion="Use PostgreSQL ENUM type or CHECK constraint for type safety",
                    ))

    # ── Rule 15: VARCHAR(255) overuse ──
    varchar_255_count = len(re.findall(r"VARCHAR\(255\)", content, re.IGNORECASE))
    if varchar_255_count > 3:
        result.findings.append(Finding(
            rule="VARCHAR_SIZING",
            severity=Severity.WARNING,
            message=f"VARCHAR(255) used {varchar_255_count} times — may indicate lazy column sizing",
            suggestion="Use appropriate sizes: phone VARCHAR(20), country CHAR(2), etc.",
        ))

    # ── Count totals ──
    for f in result.findings:
        if f.severity == Severity.ERROR:
            result.errors += 1
        elif f.severity == Severity.WARNING:
            result.warnings += 1
        else:
            result.passes += 1

    return result


# ─── Output Formatters ───────────────────────────────────────────────────────

def print_results(result: ValidationResult):
    """Print validation results in human-readable format."""
    print(f"\n{Colors.BOLD}Validating:{Colors.NC} {result.file_path}")
    print(f"{'─' * 60}")
    print(f"  Tables found: {len(result.tables)}")
    if result.tables:
        print(f"  Tables: {', '.join(t.name for t in result.tables)}")
    print()

    for finding in result.findings:
        print_finding(finding)

    print()


def print_summary(results: list[ValidationResult]):
    """Print overall summary across all files."""
    total_errors = sum(r.errors for r in results)
    total_warnings = sum(r.warnings for r in results)
    total_passes = sum(r.passes for r in results)
    total_tables = sum(len(r.tables) for r in results)

    print(f"\n{'═' * 60}")
    print(f" {Colors.BOLD}SUMMARY{Colors.NC}")
    print(f"{'═' * 60}")
    print(f"  Files validated: {len(results)}")
    print(f"  Tables found:    {total_tables}")
    print(f"  {Colors.GREEN}Passed{Colors.NC}:    {total_passes}")
    print(f"  {Colors.YELLOW}Warnings{Colors.NC}:  {total_warnings}")
    print(f"  {Colors.RED}Errors{Colors.NC}:    {total_errors}")
    print(f"{'═' * 60}")

    if total_errors > 0:
        print(f"{Colors.RED}Schema validation FAILED with {total_errors} error(s){Colors.NC}")
    elif total_warnings > 0:
        print(f"{Colors.YELLOW}Schema validation PASSED with {total_warnings} warning(s){Colors.NC}")
    else:
        print(f"{Colors.GREEN}Schema validation PASSED ✨{Colors.NC}")

    return total_errors


def output_json(results: list[ValidationResult]):
    """Output results as JSON for CI/CD integration."""
    output = {
        "files": [],
        "summary": {
            "total_files": len(results),
            "total_tables": sum(len(r.tables) for r in results),
            "total_errors": sum(r.errors for r in results),
            "total_warnings": sum(r.warnings for r in results),
            "total_passes": sum(r.passes for r in results),
            "passed": sum(r.errors for r in results) == 0,
        }
    }
    for r in results:
        file_output = {
            "file": r.file_path,
            "tables": [t.name for t in r.tables],
            "errors": r.errors,
            "warnings": r.warnings,
            "passes": r.passes,
            "findings": [
                {
                    "rule": f.rule,
                    "severity": f.severity.value,
                    "message": f.message,
                    "line": f.line_number,
                    "suggestion": f.suggestion,
                }
                for f in r.findings
            ],
        }
        output["files"].append(file_output)

    print(json.dumps(output, indent=2))
    return output["summary"]["total_errors"]


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Database Schema Validator — checks SQL files against best practices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_schema.py schema.sql
  python validate_schema.py --dir ./database/schema/
  python validate_schema.py --json schema.sql  # JSON output for CI/CD
  python validate_schema.py --no-color schema.sql
        """,
    )
    parser.add_argument("files", nargs="*", help="SQL schema files to validate")
    parser.add_argument("--dir", "-d", help="Directory containing SQL files to validate")
    parser.add_argument("--json", "-j", action="store_true", help="Output results as JSON")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    parser.add_argument("--strict", "-s", action="store_true", help="Treat warnings as errors")

    args = parser.parse_args()

    if args.no_color or not sys.stdout.isatty():
        Colors.disable()

    # Collect files
    files = list(args.files) if args.files else []
    if args.dir:
        dir_path = Path(args.dir)
        if dir_path.is_dir():
            files.extend(str(f) for f in sorted(dir_path.rglob("*.sql")))
        else:
            print(f"Error: {args.dir} is not a directory", file=sys.stderr)
            sys.exit(1)

    if not files:
        parser.print_help()
        sys.exit(1)

    # Validate each file
    results = []
    for file_path in files:
        if not os.path.isfile(file_path):
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        result = validate(content, file_path)
        results.append(result)

    if not results:
        print("No valid files to validate.", file=sys.stderr)
        sys.exit(1)

    # Output
    if args.json:
        error_count = output_json(results)
    else:
        print(f"\n{'═' * 60}")
        print(f" {Colors.BOLD}Database Schema Validator v2.0{Colors.NC}")
        print(f"{'═' * 60}")
        for result in results:
            print_results(result)
        error_count = print_summary(results)

    # Strict mode: treat warnings as errors
    if args.strict:
        total_warnings = sum(r.warnings for r in results)
        if total_warnings > 0:
            error_count += total_warnings

    sys.exit(1 if error_count > 0 else 0)


if __name__ == "__main__":
    main()
