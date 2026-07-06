from pydantic import BaseModel, Field
from typing import Optional
from app.services.agents.base import BaseAgent, AgentContext
from app.schemas.agent import AgentRequest, AgentResponse
from app.services.agents.registry import AgentRegistry
from app.services.skills.skill_registry import SkillRegistry
from app.services.context.cache_manager import IntelligentCache
from app.core.prompts import ATTENDANCE_EXTRACTION_PROMPT
from app.services.memory_service import MemoryService
import json
class AttendanceExtraction(BaseModel):
    total_classes: Optional[int] = Field(description="Total number of classes held so far")
    classes_attended: Optional[int] = Field(description="Number of classes the student has attended")
    current_percentage: Optional[float] = Field(description="Current attendance percentage if explicitly stated")

class AttendanceAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "attendance_agent"
        
    @property
    def description(self) -> str:
        return "Calculates attendance percentage and recommends recovery plans using MCP tools."

    def process(self, request: AgentRequest, context: AgentContext) -> AgentResponse:
        self._log_processing(request.message)
        
        # 1. Caching check
        cache_key = request.message.lower().strip()
        cached = IntelligentCache.get("attendance", cache_key)
        if cached:
            cached.cache_status = "Hit"
            return cached

        # Lazy load memory
        memories = MemoryService.get_all_memories(request.user_id)
        user_memories = {m.key: m.value for m in memories}
        memories_str = json.dumps(user_memories) if user_memories else "{}"

        # 2. Parameter Extraction
        extracted_params = context.get("extracted_params")
        if extracted_params and "classes_attended" in extracted_params and "total_classes" in extracted_params:
            extracted = AttendanceExtraction(
                classes_attended=extracted_params["classes_attended"],
                total_classes=extracted_params["total_classes"],
                current_percentage=None
            )
        else:
            reasoning = SkillRegistry.get_skill("ReasoningSkill")
            prompt = ATTENDANCE_EXTRACTION_PROMPT.format(message=request.message, memories=memories_str)
            extracted = reasoning.execute(prompt, AttendanceExtraction)
        
        total = extracted.total_classes
        attended = extracted.classes_attended
        percent = extracted.current_percentage
        
        # 2. Check for missing data
        if total is None and attended is None and percent is None:
            return self._create_response(content="I can calculate your attendance shortage. Could you tell me how many classes you've attended out of the total held, or your current percentage?")
            
        if percent is not None and (total is None or attended is None):
            if total is None: total = 100
            attended = int((percent / 100.0) * total)
            
        if attended is not None and total is None:
            return self._create_response(content=f"You've attended {attended} classes, but how many total classes have been held so far?")

        # 3. Call Tools using Skill Registry
        used_tools = []
        tool_caller = SkillRegistry.get_skill("ToolCallingSkill")
        
        # Tool 1: Calculate exact percentage
        out1 = tool_caller.execute(
            agent_name=self.name,
            tool_chain=[{"tool_name": "calculate_attendance_percentage", "arguments": {
                "total_classes": total,
                "classes_attended": attended
            }}]
        )
        used_tools.append(out1[0]["metrics"])
        current_perc = out1[0]["result"]["current_percentage"]
        
        # 4. Get recovery plan
        out_needed = tool_caller.execute(self.name, [{"tool_name": "classes_needed_for_target", "arguments": {"total_classes": total, "classes_attended": attended}}])
        out_safe = tool_caller.execute(self.name, [{"tool_name": "safe_bunks_remaining", "arguments": {"total_classes": total, "classes_attended": attended}}])
        
        metrics = [out1[0]["metrics"], out_needed[0]["metrics"], out_safe[0]["metrics"]]
        
        needed_val = out_needed[0]["result"]["classes_needed_consecutive"]
        safe_val = out_safe[0]["result"]["can_miss"]
        
        status = "shortage" if current_perc < 75.0 else "safe"
        
        # 4. Format Output
        result = {
            "data": {
                "type": "attendance",
                "current_percentage": current_perc,
                "total_classes": total,
                "classes_attended": attended,
                "classes_needed": needed_val,
                "can_miss": safe_val,
                "status": status
            }
        }
        
        if current_perc < 75.0:
            explanation = f"Your attendance is below 75%. You must attend the next {needed_val} classes to recover."
        else:
            explanation = f"Your attendance is safe. You can miss up to {safe_val} classes."
            
        response = self._create_response(content=explanation, data=result["data"])
        response.used_tools = metrics
        
        IntelligentCache.set("attendance", cache_key, response)
        return response

# Register the agent
AgentRegistry.register(AttendanceAgent())
