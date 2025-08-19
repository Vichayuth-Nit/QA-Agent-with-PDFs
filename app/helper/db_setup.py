from psycopg import Connection
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_postgres import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import settings

postgres_user = settings.postgres_user
postgres_password = settings.postgres_password
postgres_host = settings.postgres_host
postgres_port = settings.postgres_port
postgres_db = settings.postgres_db
collection_name = settings.collection_name
google_api_key = settings.google_api_key

conn_str = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=google_api_key)

# TYPICAL USAGE WILL BE LIKE THIS
# conn = Connection.connect(conn_str, autocommit=True)
# checkpointer = PostgresSaver(conn)

def get_connection() -> Connection:
    conn = Connection.connect(conn_str, autocommit=True)
    return conn

def get_checkpointer() -> PostgresSaver:
    checkpointer = PostgresSaver(get_connection())
    return checkpointer

def get_vector_store() -> PGVector:
    vector_store = PGVector(embeddings=embeddings, collection_name=collection_name, connection=conn_str, use_jsonb=True)
    return vector_store

def get_document_retriever():
    retriever = get_vector_store().as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={'score_threshold': 0.7, 'k': 10}
    )
    return retriever

def list_threads():
    checkpointer = get_checkpointer()
    with checkpointer.conn.cursor() as cur:
        cur.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id;")
        threads = [row[0] for row in cur.fetchall()]
    return threads