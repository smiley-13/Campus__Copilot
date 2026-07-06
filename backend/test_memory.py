import sys
import json
import logging
from dotenv import load_dotenv
sys.path.insert(0, '.')
load_dotenv(".env")

# Set up logging for test script
logging.basicConfig(level=logging.INFO)

from app.core.database import create_db_and_tables
create_db_and_tables()

# Initialize everything explicitly
from app.services.tools.tool_registry import ToolRegistry
from app.services.tools.memory_tools import MEMORY_TOOLS
for tool in MEMORY_TOOLS:
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

# Clear memory for test_user
MemoryService.clear_memory("test_user")

agent = PlannerAgent()

def run_test(message):
    print(f"\n--- Testing: {message} ---")
    context = AgentContext(session_id="test_mem")
    req = AgentRequest(user_id="test_user", message=message)
    res = agent.process(req, context)
    print("Detected Intents:", res.detected_intents)
    print("Content:", res.content)
    if res.sub_responses:
        print("Used Tools:", res.sub_responses[0].used_tools)
    else:
        print("Used Tools: None")

# Test 1: Store
run_test("Remember my branch is AIML")

# Test 2: Recall
run_test("What's my branch?")

# Test 3: Update
run_test("Update my branch to CSE")

# Test 4: Delete
run_test("Forget my branch")

print("\nALL MEMORY TESTS COMPLETED")
