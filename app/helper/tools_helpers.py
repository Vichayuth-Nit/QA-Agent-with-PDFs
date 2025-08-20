from typing import Annotated
from pydantic import Field

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool

from app.helper.db_helpers import get_vector_store

def get_tools():
    return [DuckDuckGoSearchResults(num_results=5), knowledge_base_search]

@tool
def knowledge_base_search(query: Annotated[str, Field(description="The query to search the knowledge base")]) -> ToolMessage:
    "A tool for searching knowledge base from database for relevant information."
    "Useful when you want to answ."
    "Input must always be search query."
    
    vector_store = get_vector_store()
    results = vector_store.similarity_search_with_score(query=query, k=10)
    return results
