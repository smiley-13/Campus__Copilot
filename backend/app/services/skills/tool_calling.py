import logging
import time
import uuid
from typing import Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from datetime import datetime

from app.services.skills.base_skill import BaseSkill
from app.services.tools.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

class ToolExecutionError(Exception):
    pass

class ToolCallingSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "ToolCallingSkill"
        
    @property
    def description(self) -> str:
        return "Executes deterministic tools from the ToolRegistry with retry logic, metrics, and chaining."

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, OSError))
    )
    def _execute_single_tool(self, agent_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a single tool with automatic retries for transient failures."""
        tool = ToolRegistry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found in ToolRegistry.")
            
        execution_id = str(uuid.uuid4())
        start_time = time.perf_counter()
        success = False
        result = None
        error_msg = None
        
        logger.info(f"[{agent_name}] -> [Tool:{tool_name}] ExecID:{execution_id} args: {arguments}")
        
        try:
            result = tool.execute(**arguments)
            success = True
            logger.info(f"[{agent_name}] <- [Tool:{tool_name}] ExecID:{execution_id} Success")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[{agent_name}] <- [Tool:{tool_name}] ExecID:{execution_id} Failed: {error_msg}")
            raise e
        finally:
            execution_time_ms = (time.perf_counter() - start_time) * 1000
            metrics = {
                "execution_id": execution_id,
                "tool_name": tool_name,
                "agent_name": agent_name,
                "execution_time_ms": round(execution_time_ms, 2),
                "success": success,
                "error_message": error_msg,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "input_summary": str(arguments)[:100],
                "output_summary": str(result)[:100] if result else None
            }
            # Attach metrics to result dict if possible, or return as tuple
            
        return {"result": result, "metrics": metrics}

    def execute(self, agent_name: str, tool_chain: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Executes a chain of tools. 
        tool_chain format: [{"tool_name": "...", "arguments": {...}}, ...]
        """
        results = []
        for step in tool_chain:
            tool_name = step.get("tool_name")
            arguments = step.get("arguments", {})
            try:
                out = self._execute_single_tool(agent_name, tool_name, arguments)
                results.append(out)
            except Exception as e:
                # Append failure and stop chain
                results.append({
                    "result": None, 
                    "metrics": {
                        "execution_id": str(uuid.uuid4()),
                        "tool_name": tool_name,
                        "agent_name": agent_name,
                        "success": False,
                        "error_message": str(e)
                    }
                })
                break
        return results

