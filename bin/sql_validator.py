import re
from typing import Optional, Set

DANGEROUS_KEYWORDS = {
    "insert",
    "update",
    "delete",
    "drop",
    "alter",
    "create",
    "truncate",
    "grant",
    "revoke",
    "copy",
    "execute",
    "call",
    "merge",
}


def clean_sql(raw_sql: str) -> str:
    sql = raw_sql.strip()

    if sql.startswith("```"):
        sql = re.sub(r"^```(?:sql)?", "", sql, flags=re.IGNORECASE).strip()
        sql = re.sub(r"```$", "", sql).strip()

    return sql


def find_tables(sql: str) -> set[str]:
    matches = re.findall(
        r"\b(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_\.]*)",
        sql,
        flags=re.IGNORECASE,
    )

    tables = set()

    for match in matches:
        table = match.split(".")[-1]
        tables.add(table)

    return tables


def validate_readonly_sql(sql: str, allowed_tables: Optional[Set[str]] = None) -> None:
    cleaned = clean_sql(sql)
    lowered = cleaned.lower().strip()

    if not lowered:
        raise ValueError("SQL is empty.")

    if not (lowered.startswith("select") or lowered.startswith("with")):
        raise ValueError("Only SELECT or WITH queries are allowed.")

    normalized_for_semicolon_check = lowered.rstrip(";")
    if ";" in normalized_for_semicolon_check:
        raise ValueError("Multiple SQL statements are not allowed.")

    tokens = set(re.findall(r"\b[a-z_]+\b", lowered))
    blocked = tokens.intersection(DANGEROUS_KEYWORDS)

    if blocked:
        raise ValueError(f"Unsafe SQL keyword found: {blocked}")

    used_tables = find_tables(cleaned)

    if allowed_tables is not None:
        illegal_tables = used_tables - allowed_tables
        if illegal_tables:
            raise ValueError(
                f"SQL uses tables that were not retrieved/allowed: {illegal_tables}"
            )