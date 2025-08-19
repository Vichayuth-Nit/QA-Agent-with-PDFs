from typing import Dict

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage
from langchain_community.tools import DuckDuckGoSearchResults

from app.models.agent_state import AgentState
from app.config import settings


def agent_node(state: AgentState) -> Dict[str, AIMessage]:
    # init components
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=settings.temperature, api_key=settings.openai_api_key)
    default_prompt = "You are a helpful assistant. Answer given the question."
    tools = [DuckDuckGoSearchResults(num_results=5)]
    llm_with_tools = llm.bind_tools(tools)
    
    # get messages or use default sys_prompt
    messages = state.get("messages", [SystemMessage(content=default_prompt)])
    
    response = llm_with_tools.invoke(messages)
    return {"messages": response}
