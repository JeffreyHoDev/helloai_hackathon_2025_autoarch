from .instructions import instructions
from .tools import save_weightage, analyze_and_visualize_migration_path_graphviz


from dotenv import load_dotenv
load_dotenv()

# From Google ADK
from google.adk.agents import LlmAgent

discovery_and_assessment_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='discovery_and_assessment_agent',
    description='A helpful assistant understanding the environment of provided cloud architecture design, and create detailed inventory of all assets.',
    instruction=instructions,
    tools=[save_weightage, analyze_and_visualize_migration_path_graphviz]
)

# a2a_app = to_a2a(architecture_validator_agent, port=8005)

# Command to run it
# uvicorn <path to this folder>.agent:a2a_app --host localhost --port 8005