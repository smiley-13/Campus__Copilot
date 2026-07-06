from typing import Any
from app.services.skills.base_skill import BaseSkill
from app.core.llm import generate_text

class SummarizationSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "SummarizationSkill"
        
    @property
    def description(self) -> str:
        return "Generates natural language summaries from structured data or events."

    def execute(self, prompt: str, **kwargs) -> str:
        return generate_text(prompt)
