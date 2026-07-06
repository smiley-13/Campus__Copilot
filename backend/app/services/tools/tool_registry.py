from typing import Dict, List, Any, Optional
from app.services.tools.base_tool import BaseTool
import logging

logger = logging.getLogger(__name__)

class ToolRegistry:
    _tools: Dict[str, BaseTool] = {}
    _failed_registrations: List[str] = []

    @classmethod
    def register_tool(cls, tool: BaseTool) -> None:
        try:
            if not isinstance(tool, BaseTool):
                raise TypeError(f"Tool {tool} must inherit from BaseTool.")
            cls._tools[tool.name] = tool
            logger.info(f"Registered tool: {tool.name}")
        except Exception as e:
            logger.error(f"Failed to register tool: {e}")
            cls._failed_registrations.append(str(tool))

    @classmethod
    def unregister_tool(cls, tool_name: str) -> bool:
        if tool_name in cls._tools:
            del cls._tools[tool_name]
            return True
        return False

    @classmethod
    def get_tool(cls, tool_name: str) -> Optional[BaseTool]:
        return cls._tools.get(tool_name)

    @classmethod
    def list_tools(cls, category: Optional[str] = None) -> List[str]:
        if category:
            return [name for name, tool in cls._tools.items() if tool.category == category]
        return list(cls._tools.keys())

    @classmethod
    def search_tools(cls, query: str) -> List[str]:
        query = query.lower()
        results = []
        for name, tool in cls._tools.items():
            if query in name.lower() or query in tool.description.lower():
                results.append(name)
        return results

    @classmethod
    def get_tool_metadata(cls, tool_name: str) -> Optional[Dict[str, Any]]:
        tool = cls.get_tool(tool_name)
        if not tool:
            return None
        return {
            "name": tool.name,
            "description": tool.description,
            "category": tool.category,
            "version": tool.version,
            "author": tool.author,
            "requires_llm": tool.requires_llm,
            "input_schema": tool.input_schema,
            "output_schema": tool.output_schema
        }

    @classmethod
    def health_check(cls) -> Dict[str, Any]:
        return {
            "registered_tool_count": len(cls._tools),
            "failed_registrations": cls._failed_registrations,
            "status": "healthy" if not cls._failed_registrations else "degraded",
            "categories": list(set(t.category for t in cls._tools.values()))
        }
