from google.adk.agents import Agent
from .callbacks import before_model_callback
from .tools import create_contact, update_contact
from google.genai import types
from pydantic import BaseModel

class AgentResponse(BaseModel):
    message: str        
    should_escalate: bool

root_agent = Agent(
    name="real_estate_agent",
    model="gemini-2.0-flash",
    description="real estate agent that qualifies leads using the BANT criteria in a few steps.",
    instruction="",
    before_model_callback=before_model_callback,
    tools=[create_contact, update_contact],
    # output_schema=AgentResponse,
    generate_content_config=types.GenerateContentConfig(temperature=0.7)
)