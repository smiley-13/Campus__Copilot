from typing import Dict, List, Any, Optional
from app.services.skills.base_skill import BaseSkill
import logging

logger = logging.getLogger(__name__)

class SkillRegistry:
    _skills: Dict[str, BaseSkill] = {}
    _failed_registrations: List[str] = []

    @classmethod
    def register_skill(cls, skill: BaseSkill) -> None:
        try:
            if not isinstance(skill, BaseSkill):
                raise TypeError(f"Skill {skill} must inherit from BaseSkill.")
            cls._skills[skill.name] = skill
            logger.info(f"Registered skill: {skill.name}")
        except Exception as e:
            logger.error(f"Failed to register skill: {e}")
            cls._failed_registrations.append(str(skill))

    @classmethod
    def get_skill(cls, skill_name: str) -> Optional[BaseSkill]:
        return cls._skills.get(skill_name)

    @classmethod
    def list_skills(cls) -> List[str]:
        return list(cls._skills.keys())

    @classmethod
    def get_skill_metadata(cls, skill_name: str) -> Optional[Dict[str, Any]]:
        skill = cls.get_skill(skill_name)
        if not skill:
            return None
        return {
            "name": skill.name,
            "description": skill.description
        }
        
    @classmethod
    def health_check(cls) -> Dict[str, Any]:
        return {
            "registered_skill_count": len(cls._skills),
            "failed_registrations": cls._failed_registrations,
            "status": "healthy" if not cls._failed_registrations else "degraded"
        }
