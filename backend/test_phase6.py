import sys
import json
from dotenv import load_dotenv
sys.path.insert(0, '.')
load_dotenv(".env")

from app.core.database import create_db_and_tables
create_db_and_tables()

# Initialize everything explicitly since we aren't running via uvicorn
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

print("Tool Health:", ToolRegistry.health_check())
print("Skill Health:", SkillRegistry.health_check())

from app.services.agents.planner import PlannerAgent
from app.schemas.agent import AgentRequest
from app.services.agents.base import AgentContext
from app.services.memory_service import MemoryService
from app.services.context.conversation_manager import ConversationManager

# Clear memory for test_user
MemoryService.clear_memory("test_user")

agent = PlannerAgent()
context = AgentContext(session_id="test")

print("\n--- Testing Store Memory (Tool Chain) ---")
req1 = AgentRequest(user_id="test_user", message="Remember my branch is AIML")
res1 = agent.process(req1, context)
print("Intent:", res1.detected_intents)
print("Content:", res1.content)
if res1.sub_responses:
    print("Used Tools:", res1.sub_responses[0].used_tools)

print("\n--- Testing Context Injection & Attendance ---")
context2 = AgentContext(session_id="test")
req2 = AgentRequest(user_id="test_user", message="I attended 32 out of 50 classes")
res2 = agent.process(req2, context2)
print("Content:", res2.content)
if res2.sub_responses:
    print("Used Tools:", res2.sub_responses[0].used_tools)

print("\n--- Testing Conversation Manager ---")
state = ConversationManager.get_state("test_user")
print("Active Topic:", state.active_topic)
print("Previous Agent:", state.previous_agent)

print("\nALL TESTS PASSED")
