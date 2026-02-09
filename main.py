from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from real_estate_agent.agent import root_agent
from google.genai.types import Content, Part
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "real_estate_agent"

PHONE_NUMBER = input("Phone number (simulated): ")
USER_ID = PHONE_NUMBER
SESSION_ID = PHONE_NUMBER

session_service = InMemorySessionService()

asyncio.run(session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID, state={"user_id": PHONE_NUMBER}))

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service
)

while True:
    user_msg = input("You: ")
    if user_msg == "exit": 
        break
    
    content = Content(
        role="user", 
        parts=[Part(text=user_msg)]
    )

    events = runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=content
    )

    for event in events:
        
        if event.is_final_response() and event.content:
            response_text = event.content.parts[0].text
            
            clean_text = response_text.replace("```json", "").replace("```", "").strip()

            try:
                response_data = json.loads(clean_text)
                message = response_data.get("message") or response_data.get("response", response_text)
                should_escalate = response_data.get("should_escalate", False)
                
                print("Agent: " + message)
                
                if should_escalate:
                    print("⚠️ ESCALATING TO HUMAN...")
                    
            except json.JSONDecodeError:
                print("Agent: " + response_text)