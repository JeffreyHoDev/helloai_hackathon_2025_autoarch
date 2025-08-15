from .instructions import instructions

from dotenv import load_dotenv
load_dotenv()

# From Google ADK
from google.adk.agents import LlmAgent
from google.adk.tools import google_search
# from google.adk.a2a.utils.agent_to_a2a import to_a2a
from .custom_a2a import to_a2a
from google.genai import types

root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='cloud_arch_proposal_agent',
    description='A helpful assistant for providing recommendation, recommend best practice on server and cloud architecture, including networking knowledge.',
    instruction=instructions,
    tools=[google_search]
)

a2a_app = to_a2a(root_agent)

# Command to run it
# uvicorn <path to this folder>.agent:a2a_app --host localhost --port 8002