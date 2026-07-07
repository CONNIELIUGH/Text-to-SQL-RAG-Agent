from functools import lru_cache
from sentence_transformers import SentenceTransformer
from .config import settings

# For this embedding model, each short query should start with an instruction
QUERY_INSTRUCTION = "Represent this sentence for searching relevant database schema: "


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model)


def embed_document(text: str) -> list[float]:
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return [float(x) for x in embedding]


def embed_query(query: str) -> list[float]:
    model = get_embedding_model()
    embedding = model.encode(QUERY_INSTRUCTION + query, normalize_embeddings=True)
    return [float(x) for x in embedding]


def to_pgvector(values: list[float]) -> str:
    return "[" + ",".join(str(float(x)) for x in values) + "]"