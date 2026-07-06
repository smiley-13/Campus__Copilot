import math
from typing import Any, Dict
from app.services.tools.base_tool import BaseTool

class CalculateAttendanceTool(BaseTool):
    @property
    def name(self) -> str:
        return "calculate_attendance_percentage"
        
    @property
    def description(self) -> str:
        return "Calculates current attendance percentage deterministically."
        
    @property
    def category(self) -> str:
        return "Attendance"
        
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "total_classes": {"type": "integer"},
                "classes_attended": {"type": "integer"}
            },
            "required": ["total_classes", "classes_attended"]
        }
        
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "current_percentage": {"type": "number"}
            }
        }
        
    def execute(self, total_classes: int, classes_attended: int, **kwargs) -> Dict[str, Any]:
        percent = (classes_attended / total_classes * 100) if total_classes > 0 else 100.0
        return {"current_percentage": round(percent, 2)}

class ClassesNeededTool(BaseTool):
    @property
    def name(self) -> str:
        return "classes_needed_for_target"
        
    @property
    def description(self) -> str:
        return "Calculates how many classes are needed consecutively to reach a target percentage."
        
    @property
    def category(self) -> str:
        return "Attendance"
        
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "total_classes": {"type": "integer"},
                "classes_attended": {"type": "integer"},
                "target_percentage": {"type": "number", "default": 75.0}
            },
            "required": ["total_classes", "classes_attended"]
        }
        
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "classes_needed_consecutive": {"type": "integer"}
            }
        }
        
    def execute(self, total_classes: int, classes_attended: int, target_percentage: float = 75.0, **kwargs) -> Dict[str, Any]:
        target_decimal = target_percentage / 100.0
        # (attended + x) / (total + x) = target
        needed = math.ceil((target_decimal * total_classes - classes_attended) / (1 - target_decimal))
        if needed < 0: needed = 0
        return {"classes_needed_consecutive": needed}

class SafeBunksTool(BaseTool):
    @property
    def name(self) -> str:
        return "safe_bunks_remaining"
        
    @property
    def description(self) -> str:
        return "Calculates how many classes can be safely missed while staying above a target percentage."
        
    @property
    def category(self) -> str:
        return "Attendance"
        
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "total_classes": {"type": "integer"},
                "classes_attended": {"type": "integer"},
                "target_percentage": {"type": "number", "default": 75.0}
            },
            "required": ["total_classes", "classes_attended"]
        }
        
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "can_miss": {"type": "integer"}
            }
        }
        
    def execute(self, total_classes: int, classes_attended: int, target_percentage: float = 75.0, **kwargs) -> Dict[str, Any]:
        target_decimal = target_percentage / 100.0
        # attended / (total + y) = target
        can_miss = math.floor((classes_attended / target_decimal) - total_classes)
        if can_miss < 0: can_miss = 0
        return {"can_miss": can_miss}

# For registering in registry later
ATTENDANCE_TOOLS = [CalculateAttendanceTool(), ClassesNeededTool(), SafeBunksTool()]
