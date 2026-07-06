from typing import Any, Dict
from datetime import datetime, timedelta
from app.services.tools.base_tool import BaseTool

class TodayTool(BaseTool):
    @property
    def name(self) -> str: return "today"
    @property
    def description(self) -> str: return "Returns today's date."
    @property
    def category(self) -> str: return "Utility"
    @property
    def input_schema(self) -> Dict[str, Any]: return {"type": "object", "properties": {}}
    @property
    def output_schema(self) -> Dict[str, Any]: return {"type": "object", "properties": {"date": {"type": "string"}}}
    def execute(self, **kwargs) -> Dict[str, Any]:
        return {"date": datetime.utcnow().strftime("%Y-%m-%d")}

UTILITY_TOOLS = [TodayTool()]
