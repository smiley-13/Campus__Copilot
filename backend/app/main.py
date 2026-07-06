from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings
from app.core.database import create_db_and_tables

# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend for CampusCopilot: AI Student Success Agent",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, configure this properly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # Initialize the SQLite Database
    create_db_and_tables()
    
    # Initialize Registries
    from app.services.tools.tool_registry import ToolRegistry
    from app.services.tools.attendance_tools import ATTENDANCE_TOOLS
    from app.services.tools.assignment_tools import ASSIGNMENT_TOOLS
    from app.services.tools.study_tools import STUDY_TOOLS
    from app.services.tools.career_tools import CAREER_TOOLS
    from app.services.tools.memory_tools import MEMORY_TOOLS
    from app.services.tools.utility_tools import UTILITY_TOOLS
    
    for tool_group in [ATTENDANCE_TOOLS, ASSIGNMENT_TOOLS, STUDY_TOOLS, CAREER_TOOLS, MEMORY_TOOLS, UTILITY_TOOLS]:
        for tool in tool_group:
            ToolRegistry.register_tool(tool)
            
    from app.services.skills.skill_registry import SkillRegistry
    from app.services.skills.tool_calling import ToolCallingSkill
    from app.services.skills.reasoning import ReasoningSkill
    from app.services.skills.summarization import SummarizationSkill
    
    for skill in [ToolCallingSkill(), ReasoningSkill(), SummarizationSkill()]:
        SkillRegistry.register_skill(skill)

# Include API Routes
app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to CampusCopilot API"}

# --- Discovery APIs ---
from app.services.tools.tool_registry import ToolRegistry
from app.services.skills.skill_registry import SkillRegistry

@app.get("/api/tools")
def list_tools(category: str = None):
    return {"tools": ToolRegistry.list_tools(category)}

@app.get("/api/tools/metadata")
def get_tool_metadata(tool_name: str):
    meta = ToolRegistry.get_tool_metadata(tool_name)
    if not meta:
        return {"error": "Tool not found"}
    return meta

@app.get("/api/tools/health")
def get_tool_health():
    return ToolRegistry.health_check()

@app.get("/api/skills")
def list_skills():
    return {"skills": SkillRegistry.list_skills()}

@app.get("/api/skills/metadata")
def get_skill_metadata(skill_name: str):
    meta = SkillRegistry.get_skill_metadata(skill_name)
    if not meta:
        return {"error": "Skill not found"}
    return meta

@app.get("/api/skills/health")
def get_skill_health():
    return SkillRegistry.health_check()
