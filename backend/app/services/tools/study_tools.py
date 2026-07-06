from typing import Any, Dict
from app.services.tools.base_tool import BaseTool

class GenerateStudyScheduleTool(BaseTool):
    @property
    def name(self) -> str: return "generate_study_schedule"
    @property
    def description(self) -> str: return "Generates a study schedule using LLM."
    @property
    def category(self) -> str: return "Study"
    @property
    def requires_llm(self) -> bool: return True
    @property
    def input_schema(self) -> Dict[str, Any]: return {"type": "object", "properties": {"subject": {"type": "string"}}}
    @property
    def output_schema(self) -> Dict[str, Any]: return {"type": "object", "properties": {"schedule": {"type": "string"}}}
    def execute(self, subject: str, **kwargs) -> Dict[str, Any]:
        return {"schedule": f"Study plan for {subject}"}

class EstimateTopicDurationTool(BaseTool):
    @property
    def name(self) -> str: return "estimate_topic_duration"
    @property
    def description(self) -> str: return "Estimates how many hours a topic takes."
    @property
    def category(self) -> str: return "Study"
    @property
    def input_schema(self) -> Dict[str, Any]: return {"type": "object", "properties": {"topic": {"type": "string"}}}
    @property
    def output_schema(self) -> Dict[str, Any]: return {"type": "object", "properties": {"hours": {"type": "number"}}}
    def execute(self, topic: str, **kwargs) -> Dict[str, Any]:
        return {"hours": 2.5}

STUDY_TOOLS = [GenerateStudyScheduleTool(), EstimateTopicDurationTool()]
