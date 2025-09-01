from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# from .models import CustomerInquiryRequest, CustomerInquiryResponse
from google.adk.sessions import DatabaseSessionService
from google.adk.artifacts import GcsArtifactService
from google.adk.runners import Runner
# from .agents.customer_agent import CustomerAgentOrchestrator
from .root_agent.agent import root_agent
from google.genai import types
import json
import re
import uuid
import os
from contextlib import asynccontextmanager

from google.adk.sessions.in_memory_session_service import InMemorySessionService


from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


db_pw = os.environ.get('DB_PASSWORD')
db_port = os.environ.get('DB_PORT')
db_user = os.environ.get('DB_USER')

# Define the structure for the inner "request_body"
class UserRequestBody(BaseModel):
    role: str
    question: str

# Define the full request body structure
class ChatRequest(BaseModel):
    app_name: str
    user_id: str
    session_id: str
    request_body: UserRequestBody  # This field will be the Pydantic model
    streaming: bool

class ChatResponse(BaseModel):
    response: str
    session_id: str
    user_id: str

class ListSessionRequest(BaseModel):
    user_id: str

class CreateSessionRequest(BaseModel):
    user_id: str
    session_id: str


artifact_service = GcsArtifactService(bucket_name="helloaihackathon_2025_autoarch_backend_specific")


# SQLlite DB init
# DB_URL = "sqlite:///./autoarch_sessions.db"
# DB_URL = "postgresql+psycopg2://postgres:Ue.{<Edlg$D5%DAZ@34.123.21.88:5432/customUIAutoarch"
DB_URL = f"postgresql://postgres.hmzranakwmrrimcxylhy:{db_pw}@aws-0-ap-southeast-1.pooler.supabase.com:{db_port}/{db_user}"
APP_NAME = "autoarch"

# Create a lifespan event to initialize and clean up the session service
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    print("Application starting up...")    
    # Initialize the DatabaseSessionService instance and store it in app.state
    try:
        app.state.session_service =DatabaseSessionService(db_url=DB_URL)
        print("Database session service initialized successfully.")
    except Exception as e:
        print("Database session service initialized failed.")
        print(e)
    
    yield # This is where the application runs, handling requests
    # Shutdown code
    print("Application shutting down...")
    
# FastAPI application setup
app = FastAPI(
    title="AutoArch Agent Service",
    description="Multi-agent system service for accepting user request on cloud architecture design, proposal, validation",
    version="1.0.0",
    lifespan=lifespan,
)
# Initializing the Orchestrator
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "https://autoarch-custom-ui-945869404169.us-central1.run.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def process_question(
    request: ChatRequest
):
    """
    Endpoint to interact with the multi-agent ADK system.
    request: {"question": "What can you do"}
    """
    # Extract customer inquiry from request
    question = request.request_body.question
    
    # Generate unique IDs for this processing session
    unique_id = str(uuid.uuid4())
    session_id = request.session_id
    user_id = request.user_id

    try:
         # Get database session service from application state
        session_service: DatabaseSessionService = app.state.session_service
        
        # Try to get existing session or create new one
        current_session = None
        try:
            current_session = await session_service.get_session(
                app_name=APP_NAME,
                user_id = user_id,
                session_id=session_id,
            )
        except Exception as e:
            print(f"Existing Session retrieval failed for session_id='{session_id}' "
                    f"and user_uid='{user_id}': {e}")
        
        # If no session found, creating new session
        if current_session is None:
            current_session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id,
            )
        else:
            print(f"Existing session '{session_id}'has been found. Resuming session.")

        # Initialize the ADK Runner with our multi-agent pipeline
        runner = Runner(
            app_name=APP_NAME,
            agent=root_agent,
            session_service = session_service,
            artifact_service=artifact_service
        )


         # Format the user query as a structured message using the google genais content types
        user_message = types.Content(
            role="user", parts=[types.Part.from_text(text=question)]
        )
        
        # Run the agent asynchronously
        events = runner.run_async(
            user_id = user_id,
            session_id = session_id,
            new_message = user_message,
        )

        # Process events to find the final response 
        final_response = None
        # In a multi-agent system, the final action of a parent agent might be a
        # tool call (delegation) which has no text. The actual user-facing text
        # comes from the sub-agent. Therefore, we iterate through all events and
        # find the last one that contains displayable text.
        # async for event in events:
            
        #     if event.content and event.content.parts:
        #         # Concatenate all text parts from the current event.
        #         # print(event.content.parts)
        #         current_event_text = "".join(
        #             [part.text for part in event.content.parts if part.text]
        #         )
        #         # If we found text, store it. The loop will naturally leave us
        #         # with the text from the last event that had any.
        #         if current_event_text:
        #             final_response = current_event_text

        last_event_content = None
        async for event in events:
            if event.is_final_response():
                if event.content and event.content.parts:
                    last_event_content = event.content.parts[0].text

        if last_event_content:
            final_response = last_event_content
        else:
            print("No final response event found from the Sequential Agent.")
        # Parse the JSON response from agents
        if final_response is None:
            print("No event with text content found from the Agent.")
            raise HTTPException(status_code=500, detail="No text response received from agent.")
        
        # Clean up Markdown code block if it exists
        # This handles responses like: ```json\n{ ... }\n```
        cleaned_response = re.sub(r"^```(?:json)?\n|```$", "", final_response.strip(), flags=re.IGNORECASE)
        
        result = ChatResponse(
            response=cleaned_response,
            session_id=session_id,
            user_id=user_id
        )
        
        # Return the structured response using your Pydantic model
        return result
               
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process agent query: {e}")

@router.post("/list_sessions")
async def list_sessions(
    request: ListSessionRequest
):
    """
    Endpoint to get all the sessions
    request: {"user_id": "user123"}
    """
    # Extract customer inquiry from request
    user_id = request.user_id
    try:
         # Get database session service from application state
        session_service: DatabaseSessionService = app.state.session_service



        list_of_sessions = await session_service.list_sessions(
            app_name=APP_NAME,
            user_id = user_id,
        )

        return list_of_sessions
    except Exception as e:
        print(f"Existing Session retrieval failed for {user_id}. Error: {str(e)}")

@router.post("/create_session")
async def create_session(
    request: CreateSessionRequest
):
    """
    Endpoint to get all the sessions
    request: {"user_id": "user123"}
    """
    # Extract customer inquiry from request
    user_id = request.user_id
    session_id = request.session_id
    try:
         # Get database session service from application state
        session_service: DatabaseSessionService = app.state.session_service

        current_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id = user_id,
            session_id=session_id,
        )

        if current_session is None:
            current_session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id,
            )
        return current_session
    except Exception as e:
        print(f"Existing Session retrieval failed for {user_id}. Error: {str(e)}")

@router.post("/get_session")
async def get_session(
    request: CreateSessionRequest
):
    """
    Endpoint to get all the sessions
    request: {"user_id": "user123", "session_id": "session_123"}
    """
    # Extract customer inquiry from request
    user_id = request.user_id
    session_id = request.session_id
    try:
         # Get database session service from application state
        session_service: DatabaseSessionService = app.state.session_service

        current_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        return current_session
    except Exception as e:
        print(f"Existing Session retrieval failed for {user_id}. Error: {str(e)}")

@router.post("/delete_session")
async def delete_session(
    request: CreateSessionRequest
):
    """
    Endpoint to get all the sessions
    request: {"user_id": "user123"}
    """
    # Extract customer inquiry from request
    user_id = request.user_id
    session_id = request.session_id
    try:
         # Get database session service from application state
        session_service: DatabaseSessionService = app.state.session_service

        current_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id = user_id,
            session_id=session_id,
        )

        if current_session is not None:
            current_session = await session_service.delete_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id,
            )
        return current_session
    except Exception as e:
        print(f"Existing Session retrieval failed for {user_id}. Error: {str(e)}")


# Include the router in the FastAPI app
app.include_router(router, prefix="/api", tags=["Cloud architecture"])

# fastapi run main2.py