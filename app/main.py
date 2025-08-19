import json
from uuid import uuid4

from fastapi import FastAPI
from psycopg import Connection
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres import PostgresSaver

from app.models.chat import ChatMessage
from app.agent import get_agent_graph
from app.config import settings, get_logger
from app.helper.db_setup import get_connection, get_checkpointer, get_document_retriever, list_threads

# Initialize the logger
logger = get_logger()

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
    checkpointer = get_checkpointer()
    try:
        if session_id not in threads:
            return {"message": f"Session {session_id} does not exist."}
        else:
            checkpointer.delete_thread(session_id)
            return {"message": f"Session {session_id} has been deleted."}
    except Exception as e:
        raise ValueError(f"Failed to delete session {session_id}: {str(e)}")
        
# Chat with llm
@app.post("/chat/{session_id}/")
def chat_completion(session_id: str, user_input: ChatMessage):
    """
    Chat completion endpoint with llms.
    """
    # init configs
    config = {"configurable": {"thread_id": session_id}}
    agent = get_agent_graph()
    responses = agent.invoke({"messages": [HumanMessage(content=user_input.content)]}, config=config)
    return {"response": responses['messages'][-1].content}

@app.get("/chat/{session_id}/")
def get_chat_history(session_id: str):
    """
    Return chat history of the given session.
    """
    return {"session_id": session_id, "chat_messages": ["action1", "action2"]}

@app.delete("/chat/{session_id}/")
def reset_chat_history(session_id: str):
    """
    Reset chat history for the given session.
    """
    return {"message": f"Chat history for session {session_id} has been reset."}