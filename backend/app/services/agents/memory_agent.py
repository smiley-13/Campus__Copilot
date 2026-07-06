import logging
from typing import Optional, Any
from pydantic import BaseModel, Field
import json

from app.services.agents.base import BaseAgent, AgentContext
from app.schemas.agent import AgentRequest, AgentResponse
from app.services.agents.registry import AgentRegistry
from app.services.skills.skill_registry import SkillRegistry
from app.services.skills.tool_calling import ToolCallingSkill
from app.services.context.cache_manager import IntelligentCache
from app.core.prompts import (
    MEMORY_STORE_EXTRACTION_PROMPT,
    MEMORY_RECALL_EXTRACTION_PROMPT,
    MEMORY_DELETE_EXTRACTION_PROMPT
)
from app.schemas.memory import MemoryCreate

logger = logging.getLogger(__name__)

class MemoryExtraction(BaseModel):
    key: str = Field(description="The exact variable or concept to remember, e.g., 'name', 'branch', 'semester', 'career goal', 'favorite subject'. Keep it short.")
    value: str = Field(description="The value of the memory")
    category: str = Field(description="One of: identity, education, career, schedule, assignment, preference, general")
    priority: str = Field(description="One of: high, medium, low")
    confidence: float = Field(description="Confidence from 0.0 to 1.0 based on user phrasing")
    metadata_reason: Optional[str] = Field(description="Reason for confidence or other context")

class MemoryRecallExtraction(BaseModel):
    search_query: str = Field(description="The core topic to search for, e.g., 'branch', 'department', 'name', 'goal'")

class MemoryDeleteExtraction(BaseModel):
    search_query: str = Field(description="The core topic to delete, e.g., 'career goal', 'semester', 'favorite language'")

class MemoryAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "memory_agent"
        
    @property
    def description(self) -> str:
        return "Manages long-term memory for the user (store, recall, update, delete)."

    def process(self, request: AgentRequest, context: AgentContext) -> AgentResponse:
        self._log_processing(f"Handling memory operation for: {request.message}")
        
        intents = context.get("detected_intents") or []
        intent = intents[0] if intents else None
        
        if intent in ["memory_store", "memory_update"]:
            return self._handle_store(request, context)
        elif intent == "memory_recall":
            return self._handle_recall(request, context)
        elif intent == "memory_delete":
            return self._handle_delete(request, context)
        else:
            return self._handle_store(request, context)

    def _handle_store(self, request: AgentRequest, context: AgentContext) -> AgentResponse:
        # Invalidate cache on store/update
        IntelligentCache.invalidate("memory")
        
        try:
            # Check if DecisionEngine already extracted params
            extracted_params = context.get("extracted_params")
            if extracted_params and "key" in extracted_params and "value" in extracted_params:
                extracted = MemoryExtraction(
                    key=extracted_params["key"],
                    value=extracted_params["value"],
                    category="general",
                    priority="normal",
                    confidence=1.0,
                    metadata_reason=None
                )
            else:
                reasoning = SkillRegistry.get_skill("ReasoningSkill")
                prompt = MEMORY_STORE_EXTRACTION_PROMPT.format(message=request.message)
                extracted = reasoning.execute(prompt, MemoryExtraction)
            
            if not extracted.key or not extracted.value:
                return self._create_response(content="I couldn't quite catch what you wanted me to remember. Could you rephrase?")
            
            tool_caller = SkillRegistry.get_skill("ToolCallingSkill")
            out = tool_caller.execute(
                agent_name=self.name,
                tool_chain=[{"tool_name": "store_memory_tool", "arguments": {
                    "user_id": request.user_id,
                    "key": extracted.key,
                    "value": extracted.value,
                    "category": extracted.category,
                    "priority": extracted.priority,
                    "confidence": extracted.confidence
                }}]
            )
            return self._create_response(
                content=f"I'll remember that your {extracted.key} is {extracted.value}.",
                data={"memory_saved": True, "key": extracted.key, "value": extracted.value}
            )
        except Exception as e:
            logger.error(f"[MemoryAgent] Store failed: {e}")
            return self._create_response("I had trouble saving that information.")

    def _handle_recall(self, request: AgentRequest, context: AgentContext) -> AgentResponse:
        # Check cache
        cache_key = request.message.lower().strip()
        cached = IntelligentCache.get("memory", cache_key)
        if cached:
            cached.cache_status = "Hit"
            return cached
            
        try:
            extracted_params = context.get("extracted_params")
            if extracted_params and "key" in extracted_params:
                key = extracted_params["key"]
            else:
                reasoning = SkillRegistry.get_skill("ReasoningSkill")
                prompt = MEMORY_RECALL_EXTRACTION_PROMPT.format(message=request.message)
                
                class RecallExtraction(BaseModel):
                    key: str = Field(description="The key to recall")
                
                extracted = reasoning.execute(prompt, RecallExtraction)
                key = extracted.key
            
            if not key:
                return self._create_response(content="What would you like me to recall?")
                
            tool_caller = SkillRegistry.get_skill("ToolCallingSkill")
            out = tool_caller.execute(
                agent_name=self.name,
                tool_chain=[{"tool_name": "recall_memory_tool", "arguments": {
                    "user_id": request.user_id,
                    "query": key
                }}]
            )
            result = out[0]["result"]
            if result and result.get("found"):
                value = result.get("value", "unknown")
                response = self._create_response(content=f"Your {key} is {value}.")
                IntelligentCache.set("memory", cache_key, response)
                return response
            else:
                return self._create_response(content="I don't have that information yet.")
        except Exception as e:
            logger.error(f"[MemoryAgent] Recall failed: {e}")
            return self._create_response("I couldn't retrieve that information right now.")

    def _handle_delete(self, request: AgentRequest, context: AgentContext) -> AgentResponse:
        IntelligentCache.invalidate("memory")
        try:
            extracted_params = context.get("extracted_params")
            if extracted_params and "key" in extracted_params:
                key = extracted_params["key"]
            else:
                reasoning = SkillRegistry.get_skill("ReasoningSkill")
                prompt = MEMORY_DELETE_EXTRACTION_PROMPT.format(message=request.message)
                
                class DeleteExtraction(BaseModel):
                    key: str = Field(description="The key to delete")
                
                extracted = reasoning.execute(prompt, DeleteExtraction)
                key = extracted.key
                
            if not key:
                return self._create_response(content="What should I forget?")
                
            tool_caller = SkillRegistry.get_skill("ToolCallingSkill")
            out = tool_caller.execute(
                agent_name=self.name,
                tool_chain=[{"tool_name": "delete_memory_tool", "arguments": {
                    "user_id": request.user_id,
                    "key": key
                }}]
            )
            res = out[0]["result"]
            if res and res.get("success"):
                return self._create_response(content=f"I've forgotten your {key}.")
            else:
                return self._create_response(content=f"I couldn't find any memory for {key}.")
        except Exception as e:
            logger.error(f"[MemoryAgent] Delete failed: {e}")
            return self._create_response("I had trouble deleting that information.")

# Register agent
AgentRegistry.register(MemoryAgent())
