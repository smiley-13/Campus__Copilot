import logging
import time
from typing import Dict, Any
from app.mcp.registry import MCPToolRegistry

logger = logging.getLogger(__name__)

class MCPClient:
    """
    Local MCP Client abstraction.
    Agents use this to interact with MCP tools seamlessly.
    Handles metrics, logging, and execution.
    """
    
    @staticmethod
    def get_tool_schemas() -> list:
        """Returns schemas for Gemini function calling."""
        schemas = []
        for tool in MCPToolRegistry.get_all_tools().values():
            schemas.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.input_schema
            })
        return schemas
        
    @staticmethod
    def get_tools_for_agent(agent_prefix: str) -> list:
        """Returns tools relevant to a specific agent prefix (e.g. 'attendance_')."""
        schemas = []
        for name, tool in MCPToolRegistry.get_all_tools().items():
            if name.startswith(agent_prefix) or agent_prefix == "all":
                schemas.append({
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema
                })
        return schemas

    @staticmethod
    def call_tool(agent_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes an MCP tool with full logging and metrics.
        """
        logger.info(f"[{agent_name}] -> [MCP Tool] Invoking '{tool_name}' with args: {arguments}")
        
        tool = MCPToolRegistry.get_tool(tool_name)
        if not tool:
            logger.error(f"[MCP Tool] Tool '{tool_name}' not found.")
            raise ValueError(f"Tool {tool_name} not found.")

        start_time = time.perf_counter()
        success = False
        result = None
        error_msg = None
        
        try:
            # Execute handler
            result = tool.handler(**arguments)
            success = True
            logger.info(f"[MCP Tool] '{tool_name}' execution successful.")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[MCP Tool] '{tool_name}' execution failed: {error_msg}", exc_info=True)
            raise e
        finally:
            execution_time = (time.perf_counter() - start_time) * 1000
            # Execution Metrics
            metrics = {
                "name": tool_name,
                "execution_time_ms": round(execution_time, 2),
                "success": success,
                "error": error_msg
            }
            logger.info(f"[MCP Metrics] {metrics}")
            
        logger.info(f"[{agent_name}] <- [MCP Tool] Result: {result}")
        return result, metrics
