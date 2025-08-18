from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition, ToolNode

from app.models.agent_state import AgentState
from app.nodes.agent_node import agent_node


def get_agent_graph():
    graph = StateGraph(AgentState)
    # add nodes
    graph.add_node("agent_node", agent_node)
    graph.add_node("tool_node", ToolNode)
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
    agent = graph.compile()
    return agent