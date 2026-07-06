import sys
import logging
import time
from dotenv import load_dotenv

sys.path.insert(0, '.')
load_dotenv(".env")
logging.basicConfig(level=logging.INFO)

from app.core.database import create_db_and_tables
create_db_and_tables()

# Initialize everything explicitly
from app.services.tools.tool_registry import ToolRegistry
from app.services.tools.memory_tools import MEMORY_TOOLS
from app.services.tools.attendance_tools import ATTENDANCE_TOOLS
from app.services.tools.study_tools import STUDY_TOOLS
from app.services.tools.career_tools import CAREER_TOOLS

for t_list in [MEMORY_TOOLS, ATTENDANCE_TOOLS, STUDY_TOOLS, CAREER_TOOLS]:
    for tool in t_list:
        ToolRegistry.register_tool(tool)
        
from app.services.skills.skill_registry import SkillRegistry
from app.services.skills.tool_calling import ToolCallingSkill
from app.services.skills.reasoning import ReasoningSkill
from app.services.skills.summarization import SummarizationSkill

for skill in [ToolCallingSkill(), ReasoningSkill(), SummarizationSkill()]:
    SkillRegistry.register_skill(skill)

from app.services.agents.planner import PlannerAgent
from app.schemas.agent import AgentRequest
from app.services.agents.base import AgentContext
from app.services.memory_service import MemoryService
from app.services.context.cache_manager import IntelligentCache

# Clear for fresh test
MemoryService.clear_memory("test_user")
IntelligentCache.invalidate_all()

agent = PlannerAgent()

def run_test(msg: str):
    print(f"\n======================================")
    print(f"Request: {msg}")
    context = AgentContext(session_id="test_session")
    req = AgentRequest(user_id="test_user", message=msg)
    
    start_time = time.time()
    res = agent.process(req, context)
    total_time = (time.time() - start_time) * 1000
    
    print(f"Content: {res.content}")
    print(f"Decision Method: {res.decision_method}")
    print(f"Cache Status: {res.cache_status}")
    print(f"Gemini Calls: {res.gemini_calls}")
    print(f"Execution Time: {res.total_execution_time_ms} ms (Script measured: {total_time:.2f} ms)")
    
# 1. Rule-Based Route (Attendance)
run_test("I attended 30 out of 50 classes")

# 2. Cache Hit Route (Attendance)
run_test("I attended 30 out of 50 classes")

# 3. Rule-Based Route + Tool Action (Memory Store)
run_test("Remember my branch is AIML")

# 4. Cache Miss (Memory Recall)
run_test("What is my branch?")

# 5. Cache Hit (Memory Recall)
run_test("What is my branch?")

# 6. Memory Invalidation + Store
run_test("Update my branch to CSE")

# 7. Cache Miss due to Invalidation (Memory Recall)
run_test("What is my branch?")

print("\n--- PERFORMANCE SUMMARY ---")
print("Optimization checks complete.")
