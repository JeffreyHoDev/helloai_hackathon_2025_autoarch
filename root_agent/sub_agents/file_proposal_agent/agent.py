from google.adk.agents import Agent

from .instruction import agent_instructions

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
import os

from .tools import generate_docx_from_markdown, generate_pdf_from_markdown


file_proposal_agent = Agent(
    model='gemini-2.5-flash',
    name='file_proposal_agent',
    description='A helpful agent for creating and editing specific file type.',
    instruction=agent_instructions,
    tools=[generate_docx_from_markdown, generate_pdf_from_markdown]
)
