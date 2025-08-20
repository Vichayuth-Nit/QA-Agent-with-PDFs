import os
from uuid import uuid4

from fastapi import FastAPI
from psycopg import Connection
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.base import Checkpoint

from app.models.chat import ChatMessage
from app.models.agent_state import AgentState
from app.agent import get_agent_graph
from app.config import get_logger
from app.helper.db_helpers import setup_docs, get_checkpointer, list_threads, get_connection

# Initialize the logger
logger = get_logger()

# Check file existence and add to PGvector if not added yet
setup_docs()
checkpointer = get_checkpointer()
checkpointer.setup()
if not checkpointer.conn.closed:
    checkpointer.conn.close()

app = FastAPI(
    title="PDF-Agent-Chatbot API BY Vichayuth",
    description="An API for interacting with a PDF-based chatbot using LangGraph and PGVector for persistent storage.",
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the PDF-Agent-Chatbot application BY Vichayuth!"}

# Session management 
@app.get("/sessions/")
def list_sessions():
    """
    List all active sessions.
    """
    threads = list_threads()
    logger.info(f"list_sessions: {threads}")
    return {"session_ids": threads}

@app.post("/sessions/")
def create_session():
    """
    Create a new session.
    """
    # WARNING: new session will not be remember if it only created and not used.
    return {"message": "Session created successfully. Please initialize the given session to make the service records your history.", "session_id": str(uuid4())}

@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    """
    Delete a session by ID.
    """
    threads = list_threads()
    try:
        if session_id not in threads:
            return {"message": f"Session {session_id} does not exist."}
        else:
            checkpointer = get_checkpointer()
            checkpointer.delete_thread(session_id)
            if not checkpointer.conn.closed:
                checkpointer.conn.close()
            return {"message": f"Session {session_id} has been deleted."}
    except Exception as e:
        raise ValueError(f"Failed to delete session {session_id}: {str(e)}")
        
# Chat with llm
@app.post("/sessions/{session_id}/chat/")
def chat_completion(session_id: str, user_input: ChatMessage):
    """
    Chat completion endpoint with llms.
    """
    config = {"configurable": {"thread_id": session_id}}
    agent = get_agent_graph()
    responses = agent.invoke({"messages": [HumanMessage(content=user_input.content)]}, config=config)
    return {"response": responses['messages'][-1].content}

@app.get("/sessions/{session_id}/chat/")
def get_chat_history(session_id: str):
    """
    Return chat history of the given session.
    """
    config = {"configurable": {"thread_id": session_id}}
    checkpointer = get_checkpointer()
    chat_messages = checkpointer.get(config=config)
    if not chat_messages:
        return {"system_message": "This session has no chat history OR has never been used before."}
    chat_messages = chat_messages.get("channel_values", []).get("messages", [])
    if not checkpointer.conn.closed:
        checkpointer.conn.close()
    # logging the message state in terminal
    logger.info(f"get_chat_history: {chat_messages}")
    return {"session_id": session_id, "chat_messages": chat_messages}

@app.delete("/sessions/{session_id}/chat/")
def reset_chat_history(session_id: str):
    """
    Reset chat history for the given session.
    """
    # currently using the same method as delete session as it gave `the same` result
    threads = list_threads()
    try:
        if session_id not in threads:
            
            return {"system_message": f"Session {session_id} does not exist in the first place."}
        else:
            checkpointer = get_checkpointer()
            checkpointer.delete_thread(session_id)
            if not checkpointer.conn.closed:
                checkpointer.conn.close()
            return {"message": f"Session {session_id} has been reset."}
    except Exception as e:
        raise ValueError(f"Failed to reset session {session_id}: {str(e)}")