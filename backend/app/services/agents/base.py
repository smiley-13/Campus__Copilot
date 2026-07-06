from abc import ABC, abstractmethod
import logging
from app.schemas.agent import AgentRequest, AgentResponse

# Configure logging
logger = logging.getLogger(__name__)

class AgentContext:
    """
    Shared context object that can be passed between agents.
    Useful for future extensions like memory or passing tool results.
    """
    def __init__(self, session_id: str = None):
        self.session_id = session_id
        self.memory = {}
        self.user_memories = {}  # Injected from memory_service
        self.user_profile = {}   # Future profile data
        self.preferences = {}    # Future preference data
        self.mcp_tools_available = [] # Placeholder for future MCP integration
        
    def get(self, key: str):
        return self.memory.get(key)
        
    def set(self, key: str, value):
        self.memory[key] = value


class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents.
    Enforces a consistent interface and provides shared utilities.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The unique name of the agent."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """A description of the agent's capabilities."""
        pass

    @abstractmethod
    def process(self, request: AgentRequest, context: AgentContext) -> AgentResponse:
        """
        Process the user request and return an AgentResponse.
        """
        pass
        
    def _log_processing(self, message: str):
        logger.info(f"[{self.name}] Processing request: '{message}'")
        
    def _create_response(self, content: str, data: dict = None, confidence: float = 1.0) -> AgentResponse:
        """Helper to create a standard AgentResponse."""
        return AgentResponse(
            agent_name=self.name,
            content=content,
            data=data or {},
            confidence=confidence
        )
