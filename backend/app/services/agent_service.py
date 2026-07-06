import logging
from app.schemas.agent import AgentRequest, AgentResponse
from app.services.agents.planner import PlannerAgent
from app.services.agents.base import AgentContext
from app.services.agents.registry import AgentRegistry

logger = logging.getLogger(__name__)

# Initialize the Planner Agent (Singleton)
planner_agent = PlannerAgent()

def process_agent_request(request: AgentRequest, session_id: str = "default_session") -> AgentResponse:
    """
    Main entry point for API routes to interact with the multi-agent system.
    """
    logger.info(f"Received request for session: {session_id}")
    context = AgentContext(session_id=session_id)
    
    try:
        # Route everything through the planner
        response = planner_agent.process(request, context)
        return response
    except Exception as e:
        logger.error(f"Error processing agent request: {str(e)}", exc_info=True)
        return AgentResponse(
            agent_name="system",
            content="I encountered an internal error while processing your request. Please try again.",
            confidence=0.0
        )

def process_direct_agent_request(agent_name: str, request: AgentRequest, session_id: str = "default_session") -> AgentResponse:
    """
    Entry point for specialized API routes (e.g. /attendance) bypassing the planner.
    """
    logger.info(f"Direct request to agent '{agent_name}' for session: {session_id}")
    context = AgentContext(session_id=session_id)
    
    try:
        agent = AgentRegistry.get_agent(agent_name)
        if not agent:
             raise ValueError(f"Agent {agent_name} not found")
        response = agent.process(request, context)
        return response
    except Exception as e:
        logger.error(f"Error in direct agent request: {str(e)}", exc_info=True)
        return AgentResponse(
            agent_name="system",
            content="I encountered an error connecting to the specialized agent.",
            confidence=0.0
        )
