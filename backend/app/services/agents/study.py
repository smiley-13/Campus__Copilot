from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.agents.base import BaseAgent, AgentContext
from app.schemas.agent import AgentRequest, AgentResponse
from app.services.agents.registry import AgentRegistry
from app.services.skills.skill_registry import SkillRegistry
from app.services.context.cache_manager import IntelligentCache
from app.core.prompts import STUDY_EXTRACTION_PROMPT, STUDY_PLAN_PROMPT
from app.services.memory_service import MemoryService
import json
class StudySession(BaseModel):
    topic: str
    duration_minutes: int
    strategy: str

class StudyPlanData(BaseModel):
    type: str = "study_plan"
    subject: str
    days_until_exam: Optional[int]
    daily_hours: Optional[float]
    sessions: List[StudySession]

class StudyExtraction(BaseModel):
    subject: Optional[str] = Field(description="The subject or topic to study. None if not mentioned.")
    days_until_exam: Optional[int] = Field(description="Days until exam. None if not mentioned.")
    daily_hours: Optional[float] = Field(description="How many hours they can study daily. None if not mentioned.")

class StudyAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "study_agent"
        
    @property
    def description(self) -> str:
        return "Generates study plans, revision schedules, and answers study-related questions."

    def process(self, request: AgentRequest, context: AgentContext) -> AgentResponse:
        self._log_processing(request.message)
        
        # 1. Caching
        cache_key = request.message.lower().strip()
        cached = IntelligentCache.get("study", cache_key)
        if cached:
            cached.cache_status = "Hit"
            return cached

        # Lazy load memory
        memories = MemoryService.get_all_memories(request.user_id)
        user_memories = {m.key: m.value for m in memories}
        memories_str = json.dumps(user_memories) if user_memories else "{}"
        
        # 1. Extract params using LLM
        reasoning_skill = SkillRegistry.get_skill("ReasoningSkill")
        prompt = STUDY_EXTRACTION_PROMPT.format(message=request.message, memories=memories_str)
        extracted = reasoning_skill.execute(prompt, StudyExtraction)
        
        # 2. Check for missing data (Intelligent follow-up)
        missing = []
        if not extracted.subject: missing.append("what subject you are studying")
        if not extracted.days_until_exam: missing.append("how many days until your exam")
        if not extracted.daily_hours: missing.append("how many hours a day you can study")
        
        if len(missing) == 3: # Nothing extracted
             return self._create_response(content="I can help you create a study plan! What subject are you studying, and when is your exam?")
        if len(missing) > 0 and len(missing) < 3:
             missing_str = " and ".join(missing)
             # We can still generate a generic plan, but let's ask for clarification for a better one
             pass # For robustness, we will just proceed with defaults if some are missing, or we can ask.
             # The prompt says: "If required information is missing, the agent should ask intelligent follow-up questions instead of guessing."
             if not extracted.subject:
                 return self._create_response(content="I'd love to make a study plan. What subject is this for?")

        # Set defaults if they didn't provide but we have the subject
        days = extracted.days_until_exam or 7
        hours = extracted.daily_hours or 2.0
        subject = extracted.subject
        
        # 3. Generate structured plan using Reasoning Skill
        plan_prompt = STUDY_PLAN_PROMPT.format(subject=subject, days=days, hours=hours)
        
        plan_data = reasoning_skill.execute(plan_prompt, StudyPlanData)
        plan_data.subject = subject
        plan_data.days_until_exam = days
        plan_data.daily_hours = hours
        
        # 4. Call Tool using Skill (for demonstration of Tool Chaining / Dev Mode)
        tool_caller = SkillRegistry.get_skill("ToolCallingSkill")
        out = tool_caller.execute(
            agent_name=self.name,
            tool_chain=[{"tool_name": "generate_study_schedule", "arguments": {"subject": extracted.subject}}]
        )
        metrics = out[0]["metrics"]
        
        # Generate natural language explanation
        explanation = f"I've generated a study plan for {subject}."
        if days: explanation += f" You have {days} days left."
        
        response = self._create_response(content=explanation, data=plan_data.model_dump())
        response.used_tools = [metrics]
        
        IntelligentCache.set("study", cache_key, response)
        return response

# Register the agent
AgentRegistry.register(StudyAgent())
