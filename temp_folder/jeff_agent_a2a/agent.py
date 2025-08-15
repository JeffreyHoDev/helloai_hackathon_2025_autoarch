from dotenv import load_dotenv
from google.adk.agents import Agent

# Load environment variables from a .env file in the same directory.
# This should be at the top of your file.
load_dotenv()
from .instructions import instructions
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Make your agent A2A-compatible



root_agent = Agent(
    model='gemini-2.5-flash',
    name='jeff_agent_a2a',
    description='A helpful assistant that only answer I am Jeff.',
    instruction=instructions
)

a2a_app = to_a2a(root_agent, port=8001)