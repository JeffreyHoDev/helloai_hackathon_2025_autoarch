# from .instructions import instructions
# from .tools import validate_diagrams_import

from .instructions import instructions
from .tools import validate_diagrams_import

import os
import uvicorn


from dotenv import load_dotenv
load_dotenv()

# From Google ADK
from google.adk.agents import LlmAgent
from .custom_a2a import to_a2a
# from google.adk.a2a.utils.agent_to_a2a import to_a2a



root_agent = LlmAgent(
    model='gemini-2.5-pro',
    name='diagrams_code_builder_agent',
    description='A helpful assistant for creating code with python and Diagrams module.',
    instruction=instructions,
    before_agent_callback=validate_diagrams_import
)

# def create_agent() -> LlmAgent:
#     return root_agent




# This will auto create agent card
a2a_app = to_a2a(root_agent) 


# Command to run it
# uvicorn <path to this folder>.agent:a2a_app --host localhost --port 8001
# (if didnt use the to_a2a) adk api_server --a2a --port 8001 . --log_level debug
