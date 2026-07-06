from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.agents.base import BaseAgent, AgentContext
from app.schemas.agent import AgentRequest, AgentResponse
from app.services.agents.registry import AgentRegistry
from app.services.skills.skill_registry import SkillRegistry
from app.services.context.cache_manager import IntelligentCache
from app.core.prompts import CAREER_EXTRACTION_PROMPT, CAREER_PLAN_PROMPT
from app.services.memory_service import MemoryService
import json
class CareerRoadmapStep(BaseModel):
    step: str
    description: str

class CareerData(BaseModel):
    type: str = "career"
    focus_area: str = Field(description="The main focus area (e.g. Resume, Interview, General Career)")
    skill_gaps: List[str] = Field(description="Identified skills to improve")
    roadmap: List[CareerRoadmapStep] = Field(description="Steps to achieve the goal")
    recommended_resources: List[str] = Field(description="Recommended tools or books")

class CareerExtraction(BaseModel):
    goal: Optional[str] = Field(description="The user's career goal (e.g. software engineer, data scientist)")
    current_skills: Optional[List[str]] = Field(description="Skills the user already has")

class CareerAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "career_agent"
        
    @property
    def description(self) -> str:
        return "Provides structured resume feedback, skill gap analysis, and placement roadmaps using Gemini."

    def process(self, request: AgentRequest, context: AgentContext) -> AgentResponse:
        self._log_processing(request.message)
        
        # 1. Caching
        cache_key = request.message.lower().strip()
        cached = IntelligentCache.get("career", cache_key)
        if cached:
            cached.cache_status = "Hit"
            return cached

        # Lazy load memory
        memories = MemoryService.get_all_memories(request.user_id)
        user_memories = {m.key: m.value for m in memories}
        memories_str = json.dumps(user_memories) if user_memories else "{}"
        
        # 1. Extract params using LLM
        reasoning_skill = SkillRegistry.get_skill("ReasoningSkill")
        prompt = CAREER_EXTRACTION_PROMPT.format(message=request.message, memories=memories_str)
        extracted = reasoning_skill.execute(prompt, CareerExtraction)
        
        if not extracted.goal:
            return self._create_response(content="I'd love to help you prep for placements! What specific role or field are you aiming for (e.g., Software Engineering, Data Science)?")
            
        # 3. Generate Roadmap via LLM
        goal = extracted.goal
        skills_str = ", ".join(extracted.current_skills) if extracted.current_skills else "Unknown"
        roadmap_prompt = CAREER_PLAN_PROMPT.format(goal=goal, skills=skills_str)
        
        roadmap_data = reasoning_skill.execute(roadmap_prompt, CareerData)
        
        # 3. Call Tool using Skill
        tool_caller = SkillRegistry.get_skill("ToolCallingSkill")
        out = tool_caller.execute(
            agent_name=self.name,
            tool_chain=[{"tool_name": "skill_gap_analysis", "arguments": {"current_skills": extracted.current_skills or []}}]
        )
        metrics = out[0]["metrics"]
        
        content = f"Here is your roadmap for {extracted.goal}."
        
        response = self._create_response(content=content, data=roadmap_data.model_dump())
        response.used_tools = [metrics]
        
        IntelligentCache.set("career", cache_key, response)
        return response

# Register the agent
AgentRegistry.register(CareerAgent())
