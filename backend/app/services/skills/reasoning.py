from typing import Any, Type
from pydantic import BaseModel
from app.services.skills.base_skill import BaseSkill
from app.core.llm import generate_structured_data

class ReasoningSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "ReasoningSkill"
        
    @property
    def description(self) -> str:
        return "Uses LLM for logical extraction and structured reasoning."

    def execute(self, prompt: str, schema: Type[BaseModel], **kwargs) -> Any:
        return generate_structured_data(prompt, schema)
