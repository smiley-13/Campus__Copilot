from app.services.agents.base import BaseAgent, AgentContext
from app.schemas.agent import AgentRequest, AgentResponse
from app.services.agents.registry import AgentRegistry

class GeneralAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "general_agent"
        
    @property
    def description(self) -> str:
        return "A fallback agent for general conversations and greetings that do not fit specialized categories."

    def process(self, request: AgentRequest, context: AgentContext) -> AgentResponse:
        self._log_processing(request.message)
        
        # Placeholder logic
        content = f"👋 Hello! I am CampusCopilot. You said: '{request.message}'. I can help you with studies, attendance, assignments, and career planning. What do you need help with?"
        
        return self._create_response(
            content=content,
            data={"category": "general"}
        )

# Register the agent
AgentRegistry.register(GeneralAgent())
