from .instructions import instructions

from dotenv import load_dotenv
load_dotenv()

# From Google ADK
from google.adk.agents import LlmAgent

migration_planner_agent = LlmAgent(
    model='gemini-2.5-pro',
    name='migration_planner_agent',
    description='A helpful assistant for providing migration planner.',
    instruction=instructions,
)

# a2a_app = to_a2a(architecture_validator_agent, port=8005)

# Command to run it
# uvicorn <path to this folder>.agent:a2a_app --host localhost --port 8005