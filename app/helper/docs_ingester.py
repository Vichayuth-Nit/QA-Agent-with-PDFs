from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters.character import RecursiveCharacterTextSplitter

def ingest_pdf(file_path: str) -> List[Document]:
    """Load pdf files, split into chunks, and return a list of Document objects."""
    loader = PyPDFLoader(file_path)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=400)
    chunks = loader.load_and_split(text_splitter=text_splitter)
    return chunks