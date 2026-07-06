from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, update
from datetime import datetime
from app.core.database import SessionLocal
from app.models.memory import Memory
from app.schemas.memory import MemoryCreate, MemoryRead

import logging
from app.core.config import settings

logger = logging.getLogger("memory_pipeline_debug")
logger.setLevel(logging.DEBUG)

class MemoryService:
    @staticmethod
    def _get_session() -> Session:
        logger.debug(f"DEBUG: SQLite Database URL: {settings.DATABASE_URL}")
        return SessionLocal()

    @staticmethod
    def store_memory(user_id: str, memory_data: MemoryCreate) -> MemoryRead:
        with MemoryService._get_session() as db:
            # Check if exists to update instead of insert (upsert logic)
            existing = db.query(Memory).filter(
                Memory.user_id == user_id, 
                Memory.key == memory_data.key
            ).first()

            if existing:
                existing.value = memory_data.value
                existing.category = memory_data.category or existing.category
                existing.priority = memory_data.priority or existing.priority
                existing.source = memory_data.source or existing.source
                existing.confidence = memory_data.confidence or existing.confidence
                if memory_data.metadata_json is not None:
                    existing.metadata_json = memory_data.metadata_json
                existing.last_accessed = datetime.utcnow()
                db.commit()
                db.refresh(existing)
                logger.debug(f"DEBUG (Store-Update): user_id={user_id}, key={existing.key}, value={existing.value}, SQL Result: {existing}")
                return MemoryRead.model_validate(existing)
            else:
                new_memory = Memory(
                    user_id=user_id,
                    **memory_data.model_dump()
                )
                db.add(new_memory)
                db.commit()
                db.refresh(new_memory)
                logger.debug(f"DEBUG (Store-Insert): user_id={user_id}, key={new_memory.key}, value={new_memory.value}, SQL Result: {new_memory}")
                return MemoryRead.model_validate(new_memory)

    @staticmethod
    def update_memory(user_id: str, key: str, value: str, **kwargs) -> Optional[MemoryRead]:
        with MemoryService._get_session() as db:
            mem = db.query(Memory).filter(Memory.user_id == user_id, Memory.key == key).first()
            if not mem:
                # If not exists, we can treat update as store
                create_data = MemoryCreate(key=key, value=value, **kwargs)
                return MemoryService.store_memory(user_id, create_data)
            
            mem.value = value
            for k, v in kwargs.items():
                if hasattr(mem, k) and v is not None:
                    setattr(mem, k, v)
            mem.last_accessed = datetime.utcnow()
            db.commit()
            db.refresh(mem)
            return MemoryRead.model_validate(mem)

    @staticmethod
    def get_memory(user_id: str, key: str) -> Optional[MemoryRead]:
        with MemoryService._get_session() as db:
            mem = db.query(Memory).filter(Memory.user_id == user_id, Memory.key == key).first()
            if mem:
                mem.last_accessed = datetime.utcnow()
                db.commit()
                db.refresh(mem)
                return MemoryRead.model_validate(mem)
            return None

    @staticmethod
    def delete_memory(user_id: str, key: str) -> bool:
        with MemoryService._get_session() as db:
            mem = db.query(Memory).filter(Memory.user_id == user_id, Memory.key == key).first()
            if mem:
                db.delete(mem)
                db.commit()
                return True
            return False

    @staticmethod
    def clear_memory(user_id: str) -> int:
        with MemoryService._get_session() as db:
            deleted_count = db.query(Memory).filter(Memory.user_id == user_id).delete()
            db.commit()
            return deleted_count

    @staticmethod
    def get_all_memories(user_id: str) -> List[MemoryRead]:
        with MemoryService._get_session() as db:
            mems = db.query(Memory).filter(Memory.user_id == user_id).all()
            return [MemoryRead.model_validate(m) for m in mems]

    @staticmethod
    def get_relevant_memories(user_id: str) -> List[MemoryRead]:
        # For now, just return all memories. In the future this can filter by priority or context.
        return MemoryService.get_all_memories(user_id)

    @staticmethod
    def search_memory(user_id: str, query: str) -> List[MemoryRead]:
        """Fuzzy recall using SQL LIKE and simple synonym mapping"""
        # Basic synonym mapping for common academic terms
        synonyms = {
            "department": "branch",
            "course": "branch",
            "degree": "branch",
            "major": "branch",
            "name": "name",
            "goal": "goal",
            "career": "goal",
            "semester": "semester",
            "year": "semester"
        }
        
        normalized_query = query.lower().strip()
        # Check if the query contains a known synonym
        for k, v in synonyms.items():
            if k in normalized_query:
                normalized_query = v
                break
                
        with MemoryService._get_session() as db:
            search_term = f"%{normalized_query}%"
            # We search across key, value, and category
            mems = db.query(Memory).filter(
                Memory.user_id == user_id,
                or_(
                    Memory.key.ilike(search_term),
                    Memory.value.ilike(search_term),
                    Memory.category.ilike(search_term)
                )
            ).all()
            
            # Update last accessed for matches
            if mems:
                for m in mems:
                    m.last_accessed = datetime.utcnow()
                db.commit()
                
            logger.debug(f"DEBUG (Recall): user_id={user_id}, search_query='{normalized_query}', SQL Results Count: {len(mems)}")
            for idx, m in enumerate(mems):
                logger.debug(f"DEBUG (Recall Match {idx}): key={m.key}, value={m.value}, SQL Result: {m}")
                
            return [MemoryRead.model_validate(m) for m in mems]
