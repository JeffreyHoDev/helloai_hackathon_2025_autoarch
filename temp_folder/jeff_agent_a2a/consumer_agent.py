from google.adk.agents import Agent

from .instructions import instructions

from .sub_agents.diagram_code_builder_agent.agent import diagrams_code_builder_agent

from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH

jeff_agent = RemoteA2aAgent(
    name="jeff_agent",
    description="Agent that answer jeff.",
    agent_card=(
        f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}"
    )
)


root_agent = Agent(
    model='gemini-2.5-flash',
    name='cloud_arch_diagram_agent',
    description='A helpful assistant for user questions.',
    instruction=instructions,
    sub_agents=[jeff_agent]
)
