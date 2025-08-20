from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition, ToolNode

from app.models.agent_state import AgentState
from app.nodes.agent_node import agent_node
from app.nodes.classifier_node import classifier_node, classifier_condition
from app.config import settings, get_logger
from app.helper.tools_helpers import get_tools
from app.helper.db_helpers import get_checkpointer

postgres_user = settings.postgres_user
postgres_password = settings.postgres_password
postgres_host = settings.postgres_host
postgres_port = settings.postgres_port
postgres_db = settings.postgres_db

logger = get_logger()

def get_agent_graph():
    graph = StateGraph(AgentState)
    
    # add nodes
    graph.add_node("agent_node", agent_node)
    graph.add_node("classifier_node", classifier_node)
    graph.add_node("tool_node", ToolNode(get_tools()))

    # add edges and conditional edge
    graph.add_edge(START, "classifier_node")
    graph.add_edge("tool_node", "agent_node")
    graph.add_conditional_edges(
        "classifier_node",
        classifier_condition,
        {
            "continue": "agent_node",
            "__end__": END
        }
    )
    graph.add_conditional_edges(
        "agent_node",
        tools_condition,
        {
            "tools": "tool_node",
            "__end__": END
        }
    )
    # add saver
    saver = get_checkpointer()
    agent = graph.compile(checkpointer=saver)
    return agent