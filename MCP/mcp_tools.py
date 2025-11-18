from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from pathlib import Path

# Dynamically compute the absolute path to MCP server
PATH_TO_MCP_SERVER_SCRIPT = str((Path(__file__).parent / "server.py").resolve())



async def get_SurveyInsight_mcp_tools():
    params = StdioServerParams(
        command='python3',
        args=[PATH_TO_MCP_SERVER_SCRIPT],
        read_timeout_seconds=400
      
    )
    mcp_tools = await mcp_server_tools(server_params=params)
    return mcp_tools