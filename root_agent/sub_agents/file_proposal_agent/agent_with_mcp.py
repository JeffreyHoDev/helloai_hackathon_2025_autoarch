from google.adk.agents import Agent

from .instruction import agent_instructions

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
import os

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)

file_proposal_agent = Agent(
    model='gemini-2.5-flash',
    name='file_proposal_agent',
    description='A helpful agent for creating and editing specific file type.',
    instruction=agent_instructions,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                    url="http://localhost:8084/mcp"
                )
        )
    ]
)
