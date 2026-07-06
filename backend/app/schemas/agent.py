from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class AgentRequest(BaseModel):
    user_id: str = Field(default="anonymous", description="ID of the user making the request")
    message: str = Field(..., description="The user's message")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context or state")

class AgentResponse(BaseModel):
    agent_name: str = Field(..., description="Name of the agent that generated the response")
    content: str = Field(..., description="The response content to display to the user")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Structured data returned by the agent")
    confidence: float = Field(default=1.0, description="Confidence score of the response")
    sub_responses: Optional[List['AgentResponse']] = Field(default_factory=list, description="Responses from delegated agents")
    used_tools: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="List of MCP tools invoked with metrics")
    detected_intents: Optional[List[str]] = Field(default_factory=list, description="Intents detected by Planner")
    
    # Phase 6.5 Execution Metrics
    decision_method: str = Field(default="Gemini", description="Whether intent was resolved via Rule-Based or Gemini")
    gemini_calls: int = Field(default=0, description="Number of Gemini LLM calls made")
    cache_status: str = Field(default="Miss", description="Cache status: Hit or Miss")
    total_execution_time_ms: float = Field(default=0.0, description="Total request execution time in ms")

class PlannerRouteRequest(BaseModel):
    message: str

class PlannerClassification(BaseModel):
    intents: List[str] = Field(description="The detected intents of the user")
    target_agents: List[str] = Field(description="List of agent names to route to. Valid agents: study_agent, attendance_agent, assignment_agent, career_agent, general_agent, memory_agent")
