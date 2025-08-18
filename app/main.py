import json
from uuid import uuid4

from fastapi import FastAPI
from langchain_core.messages import HumanMessage

from app.models.chat import ChatMessage
from app.agent import get_agent_graph

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the PDF-Agent-Chatbot application BY Vichayuth!"}

# Session management 
@app.get("/sessions/")
def list_sessions():
    """
    List all active sessions.
    """
    with open("sessions.jsonl", "r") as f:
        sessions = [json.loads(line) for line in f]
    # print(sessions)
    if not sessions:
        return {"message": "No active sessions."}
    else:
        return {"session_id": [session["id"] for session in sessions]}

@app.post("/sessions/")
def create_session():
    """
    Create a new session.
    """
    new_session = {"id": str(uuid4()), "messages": []}
    with open("sessions.jsonl", "a") as f:
        f.write(json.dumps(new_session) + "\n")
    return {"message": "Session created successfully.", "session_id": new_session["id"]}

@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    """
    Delete a session by ID.
    """
    with open("sessions.jsonl", "r") as f:
        sessions = [json.loads(line) for line in f]
    sessions = [session for session in sessions if session["id"] != session_id]
    with open("sessions.jsonl", "w") as f:
        for session in sessions:
            f.write(json.dumps(session) + "\n")
    return {"message": f"Session {session_id} has been deleted."}


# Chat with llm
@app.post("/chat/{session_id}/")
def chat_completion(session_id: str, user_input: ChatMessage):
    """
    Chat completion endpoint with llms.
    """
    # init configs
    config = {"configurable": {"session_id": session_id}}
    agent = get_agent_graph()

    response = agent.invoke({"messages": [HumanMessage(content=user_input.content)]}, config=config)
    return {"response": response}

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