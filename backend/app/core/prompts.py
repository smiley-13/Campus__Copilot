# Centralized prompt templates

PLANNER_CLASSIFICATION_PROMPT = """
Analyze the following student request and strictly categorize it into zero or more intents, 
and select the correct target agents.

Target Agents Available:
- study_agent: Anything related to exams, revision, topics, study plans, or schedules.
- attendance_agent: Anything related to attendance, missing classes, percentages, or tracking.
- assignment_agent: Anything related to homework, projects, tasks, due dates, or deadlines.
- career_agent: Anything related to interviews, resumes, skills, placements, or roadmaps.
- memory_agent: Storing, recalling, updating, or deleting personal information/facts about the user.
- general_agent: ONLY greetings, small talk, or non-academic questions.

CRITICAL ROUTING RULES:
1. NEVER route academic questions to the general_agent.
2. If multiple intents are present, return ALL corresponding agents.
3. Intents for memory_agent must be specific: 'memory_store', 'memory_recall', 'memory_update', 'memory_delete'.

User Request: "{message}"
"""

STUDY_EXTRACTION_PROMPT = """
Extract study details from the user's request.
If a detail is not explicitly mentioned in the request, you MUST look for it in the Background Context.

User Request: '{message}'
Background Context (Stored Memories): {memories}
"""

STUDY_PLAN_PROMPT = """
Create a personalized study plan for {subject}. 
The student has {days} days until the exam and can study {hours} hours daily.
Break it into specific manageable sessions with strategies.
"""

CAREER_EXTRACTION_PROMPT = """
Extract career details from the user's request.
If a detail is not explicitly mentioned in the request, you MUST look for it in the Background Context.

User Request: '{message}'
Background Context (Stored Memories): {memories}
"""

CAREER_PLAN_PROMPT = """
Act as a top-tier Career Coach. The student's goal is: {goal}.
Their current skills are: {skills}.
Analyze their skill gaps, provide a placement roadmap, and recommend resources.
Format exactly as the schema requires.
"""

ASSIGNMENT_EXTRACTION_PROMPT = """
Extract assignment details from the user's request.
If a detail is not explicitly mentioned in the request, you MUST look for it in the Background Context.

User Request: '{message}'
Background Context (Stored Memories): {memories}
"""

ATTENDANCE_EXTRACTION_PROMPT = """
Extract attendance data from the user's request. Look for total classes held, classes attended, or current percentage.
If a detail is not explicitly mentioned in the request, you MUST look for it in the Background Context.

User Request: '{message}'
Background Context (Stored Memories): {memories}
"""

MEMORY_STORE_EXTRACTION_PROMPT = "Extract memory detail to store: '{message}'"
MEMORY_RECALL_EXTRACTION_PROMPT = "Extract the key the user wants to recall: '{message}'"
MEMORY_DELETE_EXTRACTION_PROMPT = "Extract the key to delete: '{message}'"
