from .instructions import instructions

from dotenv import load_dotenv
load_dotenv()

# From Google ADK
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from .sub_agents.report_creation_agent.agent import report_creation_agent
from google.genai import types

architecture_validator_agent = LlmAgent(
    model='gemini-2.5-pro',
    name='architecture_validator_agent',
    description='A helpful assistant for providing recommendation, validation, and best practices on server and cloud architecture, including networking knowledge.',
    instruction=instructions,
    sub_agents=[report_creation_agent]
)

# a2a_app = to_a2a(architecture_validator_agent, port=8005)

# Command to run it
# uvicorn <path to this folder>.agent:a2a_app --host localhost --port 8005