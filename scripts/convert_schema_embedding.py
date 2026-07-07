import os
import psycopg2
import json
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
# from pgvector.psycopg2 import register_vector

load_dotenv()

postgres_password = os.getenv("POSTGRES_PASSWORD")

schema_docs = [
    {
        "table_name": "vehicle_production",
        "table_description": "Quarterly Tesla vehicle production data by product category.",
        "columns_info": {
            "year": "Calendar year of the quarter.",
            "quarter": "Quarter number from 1 to 4.",
            "model_3_y_production": "Number of Model 3/Y vehicles produced in the quarter.",
            "other_models_production": "Number of other Tesla vehicle models produced in the quarter.",
            "total_production": "Total number of vehicles produced in the quarter."
        },
        "join_info": "Join with vehicle_deliveries on year and quarter to compare production versus deliveries.",
        "example_questions": "How many vehicles did Tesla produce? Did production increase? Did Tesla produce more vehicles than it delivered? What was Model 3/Y production in Q4 2025?"
    },
    {
        "table_name": "vehicle_deliveries",
        "table_description": "Quarterly Tesla vehicle delivery data by product category.",
        "columns_info": {
            "year": "Calendar year of the quarter.",
            "quarter": "Quarter number from 1 to 4.",
            "model_3_y_deliveries": "Number of Model 3/Y vehicles delivered to customers in the quarter.",
            "other_models_deliveries": "Number of other Tesla vehicle models delivered to customers in the quarter.",
            "total_deliveries": "Total number of vehicles delivered to customers in the quarter.",
            "operating_lease_deliveries": "Deliveries subject to operating lease accounting."
        },
        "join_info": "Join with vehicle_production on year and quarter to analyze production-delivery gap.",
        "example_questions": "How many vehicles did Tesla deliver? Did deliveries increase? What was total demand? Did deliveries fall compared to production?"
    },
    {
        "table_name": "vehicle_inventory_leasing",
        "table_description": "Quarterly Tesla vehicle inventory and operating lease metrics.",
        "columns_info": {
            "year": "Calendar year of the quarter.",
            "quarter": "Quarter number from 1 to 4.",
            "operating_lease_count": "Total end-of-quarter operating lease vehicle count.",
            "global_vehicle_inventory_days": "Global vehicle inventory measured in days of supply."
        },
        "join_info": "Join with vehicle_production and vehicle_deliveries on year and quarter to analyze supply-demand imbalance.",
        "example_questions": "Did inventory increase? Was demand weaker? How many days of vehicle inventory did Tesla have? Was there inventory pressure?"
    },]


def build_schema_text(doc):
    return f"""
        Table name: {doc["table_name"]}

        Description:
        {doc["table_description"]}

        Columns:
        {json.dumps(doc["columns_info"], indent=2)}

        Join information:
        {doc["join_info"]}

        Useful for questions like:
        {doc["example_questions"]}
    """


model = SentenceTransformer("BAAI/bge-base-en-v1.5")

conn = psycopg2.connect(
    dbname="operation",
    user="postgres",
    password=postgres_password,
    host="localhost",
    port=5433
)

curs = conn.cursor()

insert_query = """
    INSERT INTO schema_docs (
        table_name,
        table_description,
        columns_info,
        join_info,
        example_questions,
        schema_text,
        embedding
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s::vector)
    ON CONFLICT (table_name) DO UPDATE SET
        table_description = EXCLUDED.table_description,
        columns_info = EXCLUDED.columns_info,
        join_info = EXCLUDED.join_info,
        example_questions = EXCLUDED.example_questions,
        schema_text = EXCLUDED.schema_text,
        embedding = EXCLUDED.embedding;
"""

for doc in schema_docs:
    schema_text = build_schema_text(doc)
    embedding = model.encode(schema_text, normalize_embeddings=True)

    embedding_str = "[" + ",".join(str(float(x)) for x in embedding) + "]"

    curs.execute(
        insert_query,
        (
            doc["table_name"],
            doc["table_description"],
            json.dumps(doc["columns_info"]),
            doc["join_info"],
            doc["example_questions"],
            schema_text,
            embedding_str
        )
    )

conn.commit()
