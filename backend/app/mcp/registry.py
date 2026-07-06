import logging
import time
from typing import Dict, Any, Callable, Type
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class MCPTool(BaseModel):
    name: str
    description: str
    version: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    handler: Callable

class MCPToolRegistry:
    """
    Registry for MCP Tools. Maintains tool definitions and their handlers.
    """
    _tools: Dict[str, MCPTool] = {}

    @classmethod
    def register(cls, name: str, description: str, version: str, input_schema: Type[BaseModel], output_schema: Type[BaseModel], handler: Callable):
        tool = MCPTool(
            name=name,
            description=description,
            version=version,
            input_schema=input_schema.model_json_schema(),
            output_schema=output_schema.model_json_schema(),
            handler=handler
        )
        cls._tools[name] = tool
        logger.info(f"[MCPRegistry] Registered tool: {name} (v{version})")

    @classmethod
    def get_tool(cls, name: str) -> MCPTool:
        return cls._tools.get(name)

    @classmethod
    def get_all_tools(cls) -> Dict[str, MCPTool]:
        return cls._tools
