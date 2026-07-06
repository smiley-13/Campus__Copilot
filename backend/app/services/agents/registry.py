import logging
from typing import Dict, Type
from app.services.agents.base import BaseAgent

logger = logging.getLogger(__name__)

class AgentRegistry:
    """
    Central registry for managing specialized agents.
    Acts as an AgentFactory/Dependency Injection mechanism.
    """
    _agents: Dict[str, BaseAgent] = {}

    @classmethod
    def register(cls, agent: BaseAgent):
        """Register a new agent instance."""
        if agent.name in cls._agents:
            logger.warning(f"Agent '{agent.name}' is already registered. Overwriting.")
        cls._agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name} - {agent.description}")

    @classmethod
    def get_agent(cls, name: str) -> BaseAgent:
        """Retrieve an agent by name."""
        agent = cls._agents.get(name)
        if not agent:
            logger.error(f"Agent '{name}' not found in registry.")
            # Fallback to general agent if possible, but for strictness we raise or return None
            return cls._agents.get("general_agent")
        return agent

    @classmethod
    def get_all_agents(cls) -> Dict[str, str]:
        """Return a mapping of agent names to their descriptions for routing."""
        return {name: agent.description for name, agent in cls._agents.items()}
