import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings:
    postgres_db: str = os.getenv("POSTGRES_DB", "operation")
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5433"))

    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen3-coder:480b-cloud")
    ollama_host: Optional[str] = os.getenv("OLLAMA_HOST") or None

    embedding_model: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
    schema_top_k: int = int(os.getenv("SCHEMA_TOP_K", "3"))
    max_agent_steps: int = int(os.getenv("MAX_AGENT_STEPS", "8"))


settings = Settings()

