import psycopg2
from psycopg2.extras import RealDictCursor
from .config import settings
from typing import Optional


def get_connection(readonly: bool = False):
    conn = psycopg2.connect(
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
        host=settings.postgres_host,
        port=settings.postgres_port,
    )

    if readonly:
        conn.set_session(readonly=True, autocommit=True)

    return conn


def fetch_all(sql: str, params: Optional[tuple] = None) -> list[dict]:
    with get_connection(readonly=True) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as curs:
            curs.execute(sql, params or ())
            rows = curs.fetchall()
            return [dict(row) for row in rows]


def execute_readonly_sql(sql: str) -> list[dict]:
    from .sql_validator import clean_sql, validate_readonly_sql

    cleaned_sql = clean_sql(sql)
    validate_readonly_sql(cleaned_sql)

    return fetch_all(cleaned_sql)