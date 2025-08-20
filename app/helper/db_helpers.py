import os

from psycopg import Connection
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
# from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config import settings, get_logger
from app.helper.docs_ingester import ingest_pdf

postgres_user = settings.postgres_user
postgres_password = settings.postgres_password
postgres_host = settings.postgres_host
postgres_port = settings.postgres_port
postgres_db = settings.postgres_db
collection_name = settings.collection_name
openai_api_key = settings.openai_api_key

logger = get_logger()
conn_str = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_api_key)

# ref: https://medium.com/@sajith_k/using-postgresql-with-langgraph-for-state-management-and-vector-storage-df4ca9d9b89e

def get_connection() -> Connection:
    conn = Connection.connect(conninfo=conn_str, autocommit=True)
    return conn

def get_checkpointer() -> PostgresSaver:
    checkpointer = PostgresSaver(get_connection())
    return checkpointer

def get_vector_store() -> PGVector:
    new_conn_str = conn_str.replace("postgresql://", "postgresql+psycopg://")
    vector_store = PGVector(embeddings=embeddings, collection_name=collection_name, connection=new_conn_str, use_jsonb=True)
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
        if not cur.closed:
            cur.close()
    if not checkpointer.conn.closed:
        checkpointer.conn.close()
    return threads

def get_embedded_docs_list():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT cmetadata ->> 'source' FROM langchain_pg_embedding;")
        embedded_doc_list = [doc[0] for doc in cur.fetchall()]
        if not cur.closed:
            cur.close()
    if not conn.closed:
        conn.close()
        
    return embedded_doc_list

def setup_docs():
    """Set up PGvector and embedded documents in /papers at the same times"""
    vector_store = get_vector_store() # setup PGvector
    embedded_doc_list = get_embedded_docs_list() # get list of embedded documents for filtering

    if not os.path.exists("papers"):
        logger.warning("The 'papers' directory does not exist. No document will be added to the vector store.")
    else:
        raw_file_list = [os.path.join("papers", file) for file in os.listdir("papers") if file.endswith(".pdf")]
        file_list = [file for file in raw_file_list if file not in embedded_doc_list]
        logger.info(f"Files to be added: {file_list}")
        
        for file in file_list:
            chunks = ingest_pdf(file_path=file)
            vector_store.add_documents(chunks)
            logger.info(f"Added {len(chunks)} chunks from `{file}` to the vector store.")

def clear_docs():
    """Clear all documents from the vector store."""
    vector_store = get_vector_store()
    vector_store.delete_collection()

# No time to handle this yet!
# def delete_docs(file_name: str):
#     """Delete documents from the vector store by file name."""
#     vector_store = get_vector_store()
#     vector_store.delete({"source": file_name})
