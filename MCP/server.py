import sys
from pathlib import Path

# Add parent directory to path so we can import from tools/
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from dotenv import load_dotenv
load_dotenv()

# Import all tool functions
from tools.topics_extraction import TopicExtraction
from tools.topic_clustering import TopicClustering
from tools.cluster_labelling import ClusterLabelling
from tools.business_insight import businessInsight


mcp = FastMCP("SurveyInsight MCP Server")

# Register tools
mcp.tool(TopicExtraction)
mcp.tool(TopicClustering)
mcp.tool(ClusterLabelling)
mcp.tool(businessInsight)


if __name__ == "__main__":
    mcp.run()