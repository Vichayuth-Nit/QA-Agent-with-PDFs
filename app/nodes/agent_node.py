from typing import Dict

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage

from app.models.agent_state import AgentState
from app.config import settings, get_logger
from app.helper.tools_helpers import get_tools
from app.prompts.agent_prompt import default_sys_prompt

logger = get_logger()

def agent_node(state: AgentState) -> Dict[str, AIMessage]:
    # init components
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=settings.temperature, api_key=settings.openai_api_key)
    tools = get_tools()
    llm_with_tools = llm.bind_tools(tools)
    
    # get messages or use default sys_prompt
    messages = state.get("messages", [])
    
    logger.info(f"Agent messages: {messages}")

    response = llm_with_tools.invoke([SystemMessage(content=default_sys_prompt)] + messages)
    return {"messages": response}
