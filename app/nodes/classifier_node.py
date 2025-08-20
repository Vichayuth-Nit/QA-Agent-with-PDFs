from typing import Dict, Literal

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage ,SystemMessage

from app.models.agent_state import AgentState
from app.models.classifier import VaugenessResponse
from app.config import settings, get_logger
from app.prompts.agent_prompt import classifier_sys_prompt, classifier_user_prompt

logger = get_logger()

def classifier_node(state: AgentState) -> Dict[str, AIMessage]:
    llm = ChatOpenAI(model="gpt-4o-mini", 
                     temperature=settings.temperature, 
                     api_key=settings.openai_api_key).with_structured_output(VaugenessResponse)
    
    # get messages or use default sys_prompt
    messages = state.get("messages", [])
    if messages:
        human_message = classifier_user_prompt.format(user_query=[{"role": m.type, "content": m.content} for m in messages])

    # logger.info(f"\n\nHuman message: {human_message}\n")

    messages = [SystemMessage(content=classifier_sys_prompt), HumanMessage(content=human_message)]
    raw_response: VaugenessResponse = llm.invoke(messages)
    if raw_response.is_vague:
        # logger.info("\nResponse is vague!\n")
        response = AIMessage(content=raw_response.response, is_vague=raw_response.is_vague)
        return {"messages": response}

def classifier_condition(state: AgentState) -> Literal["continue", "__end__"]:
    """
    Check if the classifier node should be executed.
    This is based on the vagueness of the last message.
    """
    last_message = state.get("messages", [])[-1]
    if isinstance(last_message, AIMessage) and hasattr(last_message, "is_vague"):
        # logger.info("\nGoing to END point!\n")
        return "__end__"
    else:
        return "continue"