from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.agent_tool import AgentTool
from .instructions import instructions

# from .tools import saveJSONToDBSession

from dotenv import load_dotenv
load_dotenv()

diagrams_code_builder_agent = RemoteA2aAgent(
    name="diagrams_code_builder_agent",
    description="A helpful assistant for creating code with python and Diagrams module.",
    agent_card=(
        f"https://diagrams-code-builder-service-945869404169.us-central1.run.app{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
    # agent_card=(
    #     f"http://localhost:8002{AGENT_CARD_WELL_KNOWN_PATH}"
    # )
)


cloud_arch_diagram_agent = Agent(
    model='gemini-2.5-flash',
    name='cloud_arch_diagram_agent',
    description='A helpful assistant for helping to generate cloud architecture diagram at the end.',
    instruction=instructions,
    # sub_agents=[diagrams_code_builder_agent],
    tools=[AgentTool(diagrams_code_builder_agent)]
)
