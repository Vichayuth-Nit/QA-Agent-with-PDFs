from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import Connection

from app.models.agent_state import AgentState
from app.nodes.agent_node import agent_node
from app.config import settings, get_logger
from app.helper.tools_helpers import get_tools

postgres_user = settings.postgres_user
postgres_password = settings.postgres_password
postgres_host = settings.postgres_host
postgres_port = settings.postgres_port
postgres_db = settings.postgres_db

logger = get_logger()
conn_str = f"postgresql+psycopg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

def get_agent_graph():
    graph = StateGraph(AgentState)
    
    # add nodes
    graph.add_node("agent_node", agent_node)
    graph.add_node("tool_node", ToolNode(get_tools()))

    # add edges and conditional edge
    graph.add_edge(START, "agent_node")
    graph.add_edge("tool_node", "agent_node")
    graph.add_conditional_edges(
        "agent_node",
        tools_condition,
        {
            "tools": "tool_node",
            "__end__": END
        }
    )
    # call checkpointer
    conn = Connection.connect(conn_str, autocommit=True)
    checkpointer = PostgresSaver(conn)
    checkpointer.setup()
    
    agent = graph.compile(checkpointer=checkpointer)
    return agent