import re
from typing import Optional, Tuple, Dict, Any
from app.schemas.agent import PlannerClassification

class DecisionEngine:
    @staticmethod
    def classify(message: str) -> Tuple[Optional[PlannerClassification], Dict[str, Any], float]:
        """
        Uses keywords and regex to determine intent.
        Returns: (Classification or None, extracted_params, confidence_score)
        If confidence < 0.90, it will return (None, {}, score) so Gemini can take over.
        """
        msg_lower = message.lower().strip()
        
        # 1. Memory Rules
        # "remember my branch is aiml" -> memory_store
        store_match = re.search(r"remember my ([\w\s]+) is ([\w\s]+)", msg_lower)
        if store_match:
            params = {"key": store_match.group(1).strip(), "value": store_match.group(2).strip()}
            return (PlannerClassification(intents=["memory_store"], target_agents=["memory_agent"]), params, 0.95)
            
        update_match = re.search(r"update my ([\w\s]+) to ([\w\s]+)", msg_lower)
        if update_match:
            params = {"key": update_match.group(1).strip(), "value": update_match.group(2).strip()}
            return (PlannerClassification(intents=["memory_update"], target_agents=["memory_agent"]), params, 0.95)

        recall_match = re.search(r"what'?s my ([\w\s\?]+)", msg_lower)
        if recall_match:
            key = recall_match.group(1).replace("?", "").strip()
            params = {"key": key}
            return (PlannerClassification(intents=["memory_recall"], target_agents=["memory_agent"]), params, 0.95)

        delete_match = re.search(r"forget my ([\w\s]+)", msg_lower)
        if delete_match:
            params = {"key": delete_match.group(1).strip()}
            return (PlannerClassification(intents=["memory_delete"], target_agents=["memory_agent"]), params, 0.95)

        # 2. Attendance Rules
        att_match = re.search(r"attended (\d+) out of (\d+) classes", msg_lower)
        if att_match:
            params = {"classes_attended": int(att_match.group(1)), "total_classes": int(att_match.group(2))}
            return (PlannerClassification(intents=["attendance_tracking"], target_agents=["attendance_agent"]), params, 0.95)
            
        if "attendance" in msg_lower or "miss class" in msg_lower or "bunk" in msg_lower:
            return (PlannerClassification(intents=["attendance_tracking"], target_agents=["attendance_agent"]), {}, 0.90)

        # 3. Assignment Rules
        if "assignment" in msg_lower or "homework" in msg_lower or "deadline" in msg_lower or "due" in msg_lower:
            return (PlannerClassification(intents=["assignment_tracking"], target_agents=["assignment_agent"]), {}, 0.90)

        # 4. Study Rules
        if "study plan" in msg_lower or "exam" in msg_lower or "revision" in msg_lower:
            return (PlannerClassification(intents=["study_planning"], target_agents=["study_agent"]), {}, 0.90)

        # 5. Career Rules
        if "career roadmap" in msg_lower or "resume" in msg_lower or "placement" in msg_lower or "interview" in msg_lower:
            return (PlannerClassification(intents=["career_planning"], target_agents=["career_agent"]), {}, 0.90)

        # 6. General Rules
        if msg_lower in ["hello", "hi", "hey", "good morning", "good evening"]:
            return (PlannerClassification(intents=["general_conversation"], target_agents=["general_agent"]), {}, 0.99)

        # Could not confidently determine
        return (None, {}, 0.0)
