import math
from typing import Any, Dict
from app.services.tools.base_tool import BaseTool

class CalculatePriorityTool(BaseTool):
    @property
    def name(self) -> str:
        return "calculate_priority"
        
    @property
    def description(self) -> str:
        return "Calculates assignment priority score, urgency, and daily hours needed deterministically."
        
    @property
    def category(self) -> str:
        return "Assignment"
        
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "due_in_days": {"type": "integer"},
                "estimated_hours": {"type": "number"},
                "importance": {"type": "integer"}
            },
            "required": ["due_in_days", "estimated_hours", "importance"]
        }
        
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "priority_score": {"type": "number"},
                "urgency": {"type": "string"},
                "daily_hours_needed": {"type": "number"}
            }
        }
        
    def execute(self, due_in_days: int, estimated_hours: float, importance: int, **kwargs) -> Dict[str, Any]:
        days = due_in_days if due_in_days > 0 else 0.1
        score = (importance * estimated_hours) / days
        
        if score > 10 or days < 2:
            urgency = "High"
        elif score > 3:
            urgency = "Medium"
        else:
            urgency = "Low"
            
        daily = round(estimated_hours / max(1, math.floor(days)), 1)
        
        return {"priority_score": round(score, 2), "urgency": urgency, "daily_hours_needed": daily}

ASSIGNMENT_TOOLS = [CalculatePriorityTool()]
