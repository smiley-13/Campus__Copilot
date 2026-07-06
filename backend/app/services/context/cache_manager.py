import time
from typing import Dict, Any, Optional

class CacheEntry:
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.expiry = time.time() + ttl if ttl else float('inf')
        
    def is_valid(self) -> bool:
        return time.time() < self.expiry

class IntelligentCache:
    _cache: Dict[str, Dict[str, CacheEntry]] = {
        "attendance": {},
        "assignment": {},
        "study": {},
        "career": {},
        "memory": {}
    }
    
    # Defaults in seconds
    TTLS = {
        "attendance": 5 * 60,
        "assignment": 10 * 60,
        "study": 30 * 60,
        "career": 60 * 60,
        "memory": 0 # Until modified
    }

    @classmethod
    def get(cls, category: str, key: str) -> Optional[Any]:
        if category not in cls._cache:
            return None
            
        entry = cls._cache[category].get(key)
        if entry:
            if entry.is_valid():
                return entry.value
            else:
                del cls._cache[category][key]
        return None

    @classmethod
    def set(cls, category: str, key: str, value: Any):
        if category not in cls._cache:
            cls._cache[category] = {}
            
        ttl = cls.TTLS.get(category, 5 * 60)
        cls._cache[category][key] = CacheEntry(value, ttl)

    @classmethod
    def invalidate(cls, category: str):
        if category in cls._cache:
            cls._cache[category].clear()
            
    @classmethod
    def invalidate_all(cls):
        for category in cls._cache:
            cls._cache[category].clear()
