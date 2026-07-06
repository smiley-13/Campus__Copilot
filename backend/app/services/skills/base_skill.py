from abc import ABC, abstractmethod
from typing import Any

class BaseSkill(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        pass
        
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        pass
