from langchain_community.tools import DuckDuckGoSearchResults

def get_tools():
    return [DuckDuckGoSearchResults(num_results=5)]