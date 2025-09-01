from google.adk.agents import Agent

from .instructions import root_agent_instructions

from .sub_agents.gcp_agent.agent import gcp_agent
from .sub_agents.cloud_arch_diagram_agent.agent import cloud_arch_diagram_agent
from .sub_agents.architecture_validator_agent.agent import architecture_validator_agent
from .sub_agents.terraform_agent.agent import terraform_agent


from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

from google.adk.tools.agent_tool import AgentTool





cloud_arch_proposal_agent = RemoteA2aAgent(
    name="cloud_arch_proposal_agent",
    description="A helpful expert to provide proposal on cloud architecture design.",
    agent_card=(
        f"https://for-custom-ui-cloud-arch-proposal-agent-service-945869404169.us-central1.run.app{AGENT_CARD_WELL_KNOWN_PATH}"
        # f"http://localhost:8002{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)


cloud_cost_analysis_agent = RemoteA2aAgent(
    name="cloud_cost_analysis_agent",
    description="A helpful expert to compare price between different cloud providers for given cloud architecture resources, and perform cost analysis.",
    agent_card=(
        f"https://for-custom-ui-cloud-cost-analysis-agent-945869404169.us-central1.run.app{AGENT_CARD_WELL_KNOWN_PATH}"
        # f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}"
    ),
)

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction=root_agent_instructions,
    sub_agents=[gcp_agent, cloud_arch_diagram_agent, cloud_arch_proposal_agent, architecture_validator_agent, terraform_agent, cloud_cost_analysis_agent]
    
)
