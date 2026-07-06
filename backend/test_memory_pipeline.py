import sys
import logging
import time
from dotenv import load_dotenv

sys.path.insert(0, '.')
load_dotenv(".env")
logging.basicConfig(level=logging.DEBUG) # Show debug from memory_service

from app.core.database import create_db_and_tables
create_db_and_tables()

# Initialize everything explicitly
from app.services.tools.tool_registry import ToolRegistry
from app.services.tools.memory_tools import MEMORY_TOOLS
from app.services.skills.skill_registry import SkillRegistry
from app.services.skills.tool_calling import ToolCallingSkill
from app.services.skills.reasoning import ReasoningSkill
from app.services.skills.summarization import SummarizationSkill
from app.services.agents.planner import PlannerAgent
from app.schemas.agent import AgentRequest
from app.services.agents.base import AgentContext
from app.services.memory_service import MemoryService
from app.services.context.cache_manager import IntelligentCache

for tool in MEMORY_TOOLS:
    ToolRegistry.register_tool(tool)
        
for skill in [ToolCallingSkill(), ReasoningSkill(), SummarizationSkill()]:
    SkillRegistry.register_skill(skill)

MemoryService.clear_memory("test_user_pipeline")
IntelligentCache.invalidate_all()

agent = PlannerAgent()

def run_test(msg: str):
    print(f"\n======================================")
    print(f"Request: {msg}")
    context = AgentContext(session_id="test_session")
    req = AgentRequest(user_id="test_user_pipeline", message=msg)
    
    start_time = time.time()
    res = agent.process(req, context)
    total_time = (time.time() - start_time) * 1000
    
    print(f"Content: {res.content}")
    print(f"Decision Method: {res.decision_method}")
    print(f"Cache Status: {res.cache_status}")
    print(f"Gemini Calls: {res.gemini_calls}")
    if res.used_tools:
        print(f"Used Tools:")
        for t in res.used_tools:
            print(f"  - {t.get('tool_name')} ({t.get('execution_time_ms')}ms)")
    
print("\n--- RUNNING MEMORY PIPELINE TEST ---")
# 1. Store
run_test("Remember my branch is AIML")

# 2. Inspect SQLite directly
print("\n======================================")
print("Inspecting SQLite Database Contents directly:")
mems = MemoryService.get_all_memories("test_user_pipeline")
for m in mems:
    print(f"DB Row -> ID: {m.id}, Key: {m.key}, Value: {m.value}, Category: {m.category}")

# 3. Recall
run_test("What's my branch?")

# 4. Update
run_test("Update my branch to CSE")

# 5. Recall after update
run_test("What's my branch?")

# 6. Delete
run_test("Forget my branch")

# 7. Recall after delete
run_test("What's my branch?")

print("\n--- TEST COMPLETE ---")
