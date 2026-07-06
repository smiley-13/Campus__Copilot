# Expose the modules so they are loaded when app starts
from app.mcp.registry import MCPToolRegistry
from app.mcp.client import MCPClient
import app.mcp.tools # This ensures tools are registered
