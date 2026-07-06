from fastapi import APIRouter, Header
from typing import Optional
from app.schemas.agent import AgentRequest, AgentResponse
from app.services.agent_service import process_agent_request, process_direct_agent_request

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/chat", response_model=AgentResponse)
def agent_chat(request: AgentRequest, x_session_id: Optional[str] = Header("default")):
    """
    Main chat endpoint. Routes through the Planner Agent.
    """
    return process_agent_request(request, session_id=x_session_id)

@router.post("/attendance", response_model=AgentResponse)
def attendance_chat(request: AgentRequest, x_session_id: Optional[str] = Header("default")):
    """Direct route to Attendance Agent"""
    return process_direct_agent_request("attendance_agent", request, session_id=x_session_id)

@router.post("/study-plan", response_model=AgentResponse)
def study_chat(request: AgentRequest, x_session_id: Optional[str] = Header("default")):
    """Direct route to Study Agent"""
    return process_direct_agent_request("study_agent", request, session_id=x_session_id)

@router.post("/assignments", response_model=AgentResponse)
def assignment_chat(request: AgentRequest, x_session_id: Optional[str] = Header("default")):
    """Direct route to Assignment Agent"""
    return process_direct_agent_request("assignment_agent", request, session_id=x_session_id)

@router.post("/career", response_model=AgentResponse)
def career_chat(request: AgentRequest, x_session_id: Optional[str] = Header("default")):
    """Direct route to Career Agent"""
    return process_direct_agent_request("career_agent", request, session_id=x_session_id)
