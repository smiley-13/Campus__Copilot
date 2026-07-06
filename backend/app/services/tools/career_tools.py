from typing import Any, Dict
from app.services.tools.base_tool import BaseTool

class CareerRoadmapTool(BaseTool):
    @property
    def name(self) -> str: return "career_roadmap"
    @property
    def description(self) -> str: return "Generates a career roadmap."
    @property
    def category(self) -> str: return "Career"
    @property
    def requires_llm(self) -> bool: return True
    @property
    def input_schema(self) -> Dict[str, Any]: return {"type": "object", "properties": {"goal": {"type": "string"}}}
    @property
    def output_schema(self) -> Dict[str, Any]: return {"type": "object", "properties": {"roadmap": {"type": "string"}}}
    def execute(self, goal: str, **kwargs) -> Dict[str, Any]:
        return {"roadmap": f"Roadmap for {goal}"}

class SkillGapAnalysisTool(BaseTool):
    @property
    def name(self) -> str: return "skill_gap_analysis"
    @property
    def description(self) -> str: return "Analyzes skill gaps for a role."
    @property
    def category(self) -> str: return "Career"
    @property
    def requires_llm(self) -> bool: return True
    @property
    def input_schema(self) -> Dict[str, Any]: return {"type": "object", "properties": {"current_skills": {"type": "array"}}}
    @property
    def output_schema(self) -> Dict[str, Any]: return {"type": "object", "properties": {"missing_skills": {"type": "array"}}}
    def execute(self, current_skills: list, **kwargs) -> Dict[str, Any]:
        return {"missing_skills": ["SQL", "Docker"]}

CAREER_TOOLS = [CareerRoadmapTool(), SkillGapAnalysisTool()]
