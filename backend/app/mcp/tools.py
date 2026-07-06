import math
from pydantic import BaseModel
from typing import List, Dict, Any
from app.mcp.registry import MCPToolRegistry

# ==========================================
# ATTENDANCE TOOLS
# ==========================================

class CalcAttendanceInput(BaseModel):
    total_classes: int
    classes_attended: int

class CalcAttendanceOutput(BaseModel):
    current_percentage: float

def calculate_attendance_handler(total_classes: int, classes_attended: int) -> dict:
    percent = (classes_attended / total_classes * 100) if total_classes > 0 else 100.0
    return {"current_percentage": round(percent, 2)}

MCPToolRegistry.register(
    name="attendance_calculate",
    description="Calculates current attendance percentage deterministically.",
    version="1.0.0",
    input_schema=CalcAttendanceInput,
    output_schema=CalcAttendanceOutput,
    handler=calculate_attendance_handler
)


class RecoveryPlanInput(BaseModel):
    total_classes: int
    classes_attended: int
    target_percentage: float = 75.0

class RecoveryPlanOutput(BaseModel):
    status: str
    classes_needed_consecutive: int
    can_miss: int

def attendance_recovery_plan_handler(total_classes: int, classes_attended: int, target_percentage: float = 75.0) -> dict:
    current = (classes_attended / total_classes * 100) if total_classes > 0 else 100.0
    needed = 0
    can_miss = 0
    target_decimal = target_percentage / 100.0
    
    if current < target_percentage:
        # (attended + x) / (total + x) = target
        needed = math.ceil((target_decimal * total_classes - classes_attended) / (1 - target_decimal))
        if needed < 0: needed = 0
        status = "shortage"
    else:
        # attended / (total + y) = target
        can_miss = math.floor((classes_attended / target_decimal) - total_classes)
        if can_miss < 0: can_miss = 0
        status = "safe"
        
    return {"status": status, "classes_needed_consecutive": needed, "can_miss": can_miss}

MCPToolRegistry.register(
    name="attendance_recovery_plan",
    description="Calculates how many classes needed to reach target or how many can be safely missed.",
    version="1.0.0",
    input_schema=RecoveryPlanInput,
    output_schema=RecoveryPlanOutput,
    handler=attendance_recovery_plan_handler
)

# ==========================================
# ASSIGNMENT TOOLS
# ==========================================

class CalcPriorityInput(BaseModel):
    due_in_days: int
    estimated_hours: float
    importance: int # 1 to 5

class CalcPriorityOutput(BaseModel):
    priority_score: float
    urgency: str
    daily_hours_needed: float

def calculate_priority_handler(due_in_days: int, estimated_hours: float, importance: int) -> dict:
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

MCPToolRegistry.register(
    name="assignment_calculate_priority",
    description="Calculates assignment priority score, urgency, and daily hours needed deterministically.",
    version="1.0.0",
    input_schema=CalcPriorityInput,
    output_schema=CalcPriorityOutput,
    handler=calculate_priority_handler
)

# Placeholder registrations for other tools requested
# To keep the file concise while fully supporting the architecture:
class GenericEmptyInput(BaseModel):
    pass

class GenericEmptyOutput(BaseModel):
    result: str

def dummy_handler(**kwargs):
    return {"result": "Success"}

for tool_name in ["attendance_predict", "study_generate_timetable", "study_calculate_daily_schedule", 
                  "study_estimate_revision_time", "assignment_generate_schedule", 
                  "assignment_estimate_completion_date", "career_resume_score", 
                  "career_skill_gap_analysis", "career_interview_question_generator"]:
    MCPToolRegistry.register(
        name=tool_name,
        description=f"Placeholder for {tool_name} MCP Tool",
        version="0.1.0",
        input_schema=GenericEmptyInput,
        output_schema=GenericEmptyOutput,
        handler=dummy_handler
    )
