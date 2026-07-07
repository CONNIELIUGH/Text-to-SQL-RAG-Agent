import json
from .db import fetch_all
from .embeddings import embed_query, to_pgvector


def retrieve_relevant_tables(query: str, top_k: int = 3) -> list[dict]:
    query_embedding = embed_query(query)
    query_vector = to_pgvector(query_embedding)

    sql = """
        SELECT
            table_name,
            table_description,
            columns_info,
            join_info,
            example_questions,
            schema_text,
            embedding <=> %s::vector AS distance
        FROM schema_docs
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
    """

    return fetch_all(sql, (query_vector, query_vector, top_k))


def format_schema_context(schema_rows: list[dict]) -> str:
    chunks = []

    for row in schema_rows:
        columns_info = row.get("columns_info", {})

        if isinstance(columns_info, str):
            try:
                columns_info = json.loads(columns_info)
            except json.JSONDecodeError:
                pass

        chunks.append(
            f"""
                Table: {row["table_name"]}
                Description: {row["table_description"]}

                Columns:
                {json.dumps(columns_info, indent=2)}

                Join info:
                {row.get("join_info") or "No join info provided."}

                Useful for:
                {row.get("example_questions") or "No example questions provided."}
            """.strip()
        )

    return "\n\n---\n\n".join(chunks)