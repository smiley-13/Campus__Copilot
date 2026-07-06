from pydantic import BaseModel, Field
from typing import Optional
from app.services.agents.base import BaseAgent, AgentContext
from app.schemas.agent import AgentRequest, AgentResponse
from app.services.agents.registry import AgentRegistry
from app.services.skills.skill_registry import SkillRegistry
from app.services.context.cache_manager import IntelligentCache
from app.core.prompts import ASSIGNMENT_EXTRACTION_PROMPT
from app.services.memory_service import MemoryService
import json
class AssignmentExtraction(BaseModel):
    title: Optional[str] = Field(description="The title or subject of the assignment")
    due_in_days: Optional[int] = Field(description="Number of days until it is due")
    estimated_hours: Optional[float] = Field(description="Estimated hours of effort required")
    importance_1_to_5: Optional[int] = Field(description="Importance score from 1 to 5")

class AssignmentAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "assignment_agent"
        
    @property
    def description(self) -> str:
        return "Tracks assignments and delegates priority calculation to MCP tools."

    def process(self, request: AgentRequest, context: AgentContext) -> AgentResponse:
        self._log_processing(request.message)
        
        # 1. Caching
        cache_key = request.message.lower().strip()
        cached = IntelligentCache.get("assignment", cache_key)
        if cached:
            cached.cache_status = "Hit"
            return cached

        # Lazy load memory
        memories = MemoryService.get_all_memories(request.user_id)
        user_memories = {m.key: m.value for m in memories}
        memories_str = json.dumps(user_memories) if user_memories else "{}"
        
        # 1. Extract params using LLM
        reasoning_skill = SkillRegistry.get_skill("ReasoningSkill")
        prompt = ASSIGNMENT_EXTRACTION_PROMPT.format(message=request.message, memories=memories_str)
        extracted = reasoning_skill.execute(prompt, AssignmentExtraction)
        
        # 2. Check missing fields
        missing = []
        if not extracted.title: missing.append("what the assignment is")
        if extracted.due_in_days is None: missing.append("when it is due")
        
        if missing:
            missing_str = " and ".join(missing)
            return self._create_response(content=f"I can help schedule that. Please tell me {missing_str}.")
            
        hours = extracted.estimated_hours or 2.0
        importance = extracted.importance_1_to_5 or 3
        days = extracted.due_in_days
        
        # 3. Call Tool using Skill
        tool_caller = SkillRegistry.get_skill("ToolCallingSkill")
        out = tool_caller.execute(
            agent_name=self.name,
            tool_chain=[{"tool_name": "calculate_priority", "arguments": {
                "due_in_days": days,
                "estimated_hours": hours,
                "importance": importance
            }}]
        )
        
        metrics = out[0]["metrics"]
        priority_result = out[0]["result"]
        
        data = {
            "type": "assignment",
            "title": extracted.title,
            "due_in_days": days,
            "estimated_hours": hours,
            "importance": importance,
            "priority_score": priority_result["priority_score"],
            "urgency": priority_result["urgency"],
            "daily_hours_needed": priority_result["daily_hours_needed"]
        }
        
        content = f"'{extracted.title}' requires {priority_result['daily_hours_needed']} hours/day."
        
        response = self._create_response(content=content, data=data)
        response.used_tools = [metrics]
        
        IntelligentCache.set("assignment", cache_key, response)
        
        return response

AgentRegistry.register(AssignmentAgent())
