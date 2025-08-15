from google.adk.agents import Agent

from .instruction import agent_instructions
from .tools import list_gcp_project_resources

gcp_agent = Agent(
    model='gemini-2.5-flash',
    name='gcp_agent',
    description='A helpful assistant for interacting with Google Cloud Platform project.',
    instruction=agent_instructions,
    tools=[list_gcp_project_resources]
)
