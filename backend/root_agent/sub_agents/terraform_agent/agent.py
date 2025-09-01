from .instructions import instructions

from dotenv import load_dotenv
load_dotenv()

# From Google ADK
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# from .tools import saveTFCodeToDBSession

from google.genai import types

terraform_agent = LlmAgent(
    model='gemini-2.5-pro',
    name='terraform_agent',
    description='A helpful assistant for providing terraform code for given context.',
    instruction=instructions,
)

# a2a_app = to_a2a(architecture_validator_agent, port=8005)

# Command to run it
# uvicorn <path to this folder>.agent:a2a_app --host localhost --port 8005