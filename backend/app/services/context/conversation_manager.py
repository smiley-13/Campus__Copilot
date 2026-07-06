from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class ConversationState:
    def __init__(self):
        self.history: List[Dict[str, str]] = []
        self.active_topic: str = "general"
        self.previous_agent: str = None
        self.current_task: str = None
        
    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        # Keep only last 20 messages to prevent infinite growth
        if len(self.history) > 20:
            self.history = self.history[-20:]
            
    def get_summary(self) -> str:
        """Simple summarization for long histories."""
        if not self.history:
            return ""
        return " | ".join(f"{msg['role']}: {msg['content'][:50]}..." for msg in self.history[-5:])

class ConversationManager:
    _conversations: Dict[str, ConversationState] = {}
    
    @classmethod
    def get_state(cls, user_id: str) -> ConversationState:
        if user_id not in cls._conversations:
            cls._conversations[user_id] = ConversationState()
        return cls._conversations[user_id]
        
    @classmethod
    def update_state(cls, user_id: str, role: str, content: str, topic: str = None, agent: str = None):
        state = cls.get_state(user_id)
        state.add_message(role, content)
        if topic:
            state.active_topic = topic
        if agent:
            state.previous_agent = agent
        logger.info(f"Updated ConversationState for {user_id}. Topic: {state.active_topic}")
