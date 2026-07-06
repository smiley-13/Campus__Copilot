from typing import Any, Dict
from app.services.tools.base_tool import BaseTool
from app.services.memory_service import MemoryService
from app.schemas.memory import MemoryCreate

class StoreMemoryTool(BaseTool):
    @property
    def name(self) -> str:
        return "store_memory_tool"
        
    @property
    def description(self) -> str:
        return "Stores or updates a memory key-value pair."
        
    @property
    def category(self) -> str:
        return "Memory"
        
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "key": {"type": "string"},
                "value": {"type": "string"},
                "category": {"type": "string"},
                "priority": {"type": "string"},
                "confidence": {"type": "number"}
            },
            "required": ["user_id", "key", "value"]
        }
        
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "key": {"type": "string"},
                "value": {"type": "string"}
            }
        }
        
    def execute(self, user_id: str, key: str, value: str, category: str = "general", priority: str = "low", confidence: float = 1.0, **kwargs) -> Dict[str, Any]:
        mem_create = MemoryCreate(
            key=key.lower(),
            value=value,
            category=category,
            priority=priority,
            source="chat",
            confidence=confidence
        )
        saved_mem = MemoryService.store_memory(user_id, mem_create)
        return {"success": True, "key": saved_mem.key, "value": saved_mem.value}


class SearchMemoryTool(BaseTool):
    @property
    def name(self) -> str:
        return "recall_memory_tool"
        
    @property
    def description(self) -> str:
        return "Searches for a memory based on a query."
        
    @property
    def category(self) -> str:
        return "Memory"
        
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "query": {"type": "string"}
            },
            "required": ["user_id", "query"]
        }
        
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "found": {"type": "boolean"},
                "key": {"type": "string"},
                "value": {"type": "string"}
            }
        }
        
    def execute(self, user_id: str, query: str, **kwargs) -> Dict[str, Any]:
        results = MemoryService.search_memory(user_id, query)
        if results:
            return {"found": True, "key": results[0].key, "value": results[0].value}
        return {"found": False, "key": "", "value": ""}


class DeleteMemoryTool(BaseTool):
    @property
    def name(self) -> str:
        return "delete_memory_tool"
        
    @property
    def description(self) -> str:
        return "Deletes a specific memory by exact key."
        
    @property
    def category(self) -> str:
        return "Memory"
        
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"},
                "key": {"type": "string"}
            },
            "required": ["user_id", "key"]
        }
        
    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"}
            }
        }
        
    def execute(self, user_id: str, key: str, **kwargs) -> Dict[str, Any]:
        success = MemoryService.delete_memory(user_id, key)
        return {"success": success}

MEMORY_TOOLS = [StoreMemoryTool(), SearchMemoryTool(), DeleteMemoryTool()]
