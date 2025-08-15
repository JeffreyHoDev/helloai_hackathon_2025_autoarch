# from .instructions import instructions
# from .tools import validate_diagrams_import

from .instructions import instructions


import os
import uvicorn


from dotenv import load_dotenv
load_dotenv()

# From Google ADK
from google.adk.agents import LlmAgent
from .custom_a2a import to_a2a
# from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import google_search


root_agent = LlmAgent(
    model='gemini-2.5-pro',
    name='cloud_cost_analysis_agent',
    description='A helpful assistant for performing cost analysis or compare price from different cloud providers given the architecture setup.',
    instruction=instructions,
    tools=[google_search]
)

# def create_agent() -> LlmAgent:
#     return root_agent




# This will auto create agent card
a2a_app = to_a2a(root_agent) 


# Command to run it
# uvicorn <path to this folder>.agent:a2a_app --host localhost --port 8001
# (if didnt use the to_a2a) adk api_server --a2a --port 8001 . --log_level debug
