# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import logging
import sys

try:
  from a2a.server.apps import A2AStarletteApplication
  from a2a.server.request_handlers import DefaultRequestHandler
  from a2a.server.tasks import InMemoryTaskStore
except ImportError as e:
  if sys.version_info < (3, 10):
    raise ImportError(
        "A2A requires Python 3.10 or above. Please upgrade your Python version."
    ) from e
  else:
    raise e

from starlette.applications import Starlette

from google.adk.agents.base_agent import BaseAgent
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from google.adk.cli.utils.logs import setup_adk_logger
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.a2a.executor.a2a_agent_executor import A2aAgentExecutor
from google.adk.a2a.utils.agent_card_builder import AgentCardBuilder


# Custom add
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

def to_a2a(
    agent: BaseAgent, *, host: str = "localhost", port: int = 8080
) -> Starlette:
  """Convert an ADK agent to a A2A Starlette application.

  Args:
      agent: The ADK agent to convert
      host: The host for the A2A RPC URL (default: "localhost")
      port: The port for the A2A RPC URL (default: 8000)

  Returns:
      A Starlette application that can be run with uvicorn

  Example:
      agent = MyAgent()
      app = to_a2a(agent, host="localhost", port=8000)
      # Then run with: uvicorn module:app --host localhost --port 8000
  """
  # Set up ADK logging to ensure logs are visible when using uvicorn directly
  setup_adk_logger(logging.INFO)

  async def create_runner() -> Runner:
    """Create a runner for the agent."""
    return Runner(
        app_name=agent.name or "adk_agent",
        agent=agent,
        # Use minimal services - in a real implementation these could be configured
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
        credential_service=InMemoryCredentialService(),
    )

  # Create A2A components
  task_store = InMemoryTaskStore()

  agent_executor = A2aAgentExecutor(
      runner=create_runner,
  )

  request_handler = DefaultRequestHandler(
      agent_executor=agent_executor, task_store=task_store
  )

  # Build agent card
  rpc_url = "https://cloud-arch-proposal-agent-service-945869404169.us-central1.run.app"

  capabilities = AgentCapabilities(streaming=True)
  skill = AgentSkill(
    id="server_cloud_proposal_helper",
    name="Server Cloud IT Proposal",
    description="expertise in Information Technology, Infrastructure, Server and Cloud that can provide proposal on server and cloud architecture, including networking knowledge.",
    tags=["Server Architecture", "Information Technology", "Infrastructure", "Networking", "Cloud Architecture", "Proposal"],
  )
  agent_card = AgentCard(
    name="cloud_arch_proposal_agent",
    description="An agent specialized in providing proposal about cloud architecture",
    url=rpc_url,
    version="1.0.0",
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    capabilities=capabilities,
    skills=[skill],
  )

  # Create a Starlette app that will be configured during startup
  app = Starlette()

  # Add startup handler to build the agent card and configure A2A routes
  async def setup_a2a():
    # Build the agent card asynchronously [Removed]
    

    # Create the A2A Starlette application
    a2a_app = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    # Add A2A routes to the main app
    a2a_app.add_routes_to_app(
        app,
    )

  # Store the setup function to be called during startup
  app.add_event_handler("startup", setup_a2a)

  return app
