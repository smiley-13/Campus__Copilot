from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        pass
        
    @property
    @abstractmethod
    def category(self) -> str:
        pass
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def author(self) -> str:
        return "CampusCopilot System"
        
    @property
    def requires_llm(self) -> bool:
        return False
        
    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON Schema format of expected inputs"""
        pass
        
    @property
    @abstractmethod
    def output_schema(self) -> Dict[str, Any]:
        """JSON Schema format of expected outputs"""
        pass
        
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """The deterministic implementation of the tool."""
        pass
