from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part
from real_estate_agent.agent import root_agent
from services.supabase_session import SupabaseSessionService
import json

APP_NAME = "real_estate_agent"

supabase_sessions = SupabaseSessionService()
memory_session_service = InMemorySessionService()


def format_history_for_prompt(history: list) -> str:
    """Formatea el historial para inyectar en el contexto."""
    if not history:
        return ""
    
    formatted = "CONVERSACIÓN PREVIA CON ESTE USUARIO:\n"
    for msg in history:
        role = "Usuario" if msg.get("role") == "user" else "Agente"
        content = msg.get("content", "")
        formatted = formatted + role + ": " + content + "\n"
    
    formatted = formatted + "\nCONTINÚA LA CONVERSACIÓN (no repitas preguntas ya respondidas):\n"
    return formatted


async def run_agent(phone: str, message: str) -> dict:
    """Ejecuta el agente con un mensaje y devuelve la respuesta."""
   
    db_session = await supabase_sessions.get_or_create_session(phone)
    history = db_session.get("history", []) if db_session else []
    
    try:
        session = await memory_session_service.get_session(
            app_name=APP_NAME,
            user_id=phone,
            session_id=phone
        )
        if not session:
            await memory_session_service.create_session(
                app_name=APP_NAME,
                user_id=phone,
                session_id=phone,
                state={"user_id": phone}
            )
    except Exception:
        await memory_session_service.create_session(
            app_name=APP_NAME,
            user_id=phone,
            session_id=phone,
            state={"user_id": phone}
        )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=memory_session_service
    )
    
    # Preparar mensaje con contexto del historial
    history_context = format_history_for_prompt(history)
    message_with_context = history_context + "Usuario: " + message if history else message
    
    content = Content(
        role="user",
        parts=[Part(text=message_with_context)]
    )
    
    async for event in runner.run_async(
        user_id=phone,
        session_id=phone,
        new_message=content
    ):
        if event.is_final_response() and event.content:
            response_text = event.content.parts[0].text
            
            # Guardar en historial (solo el mensaje original, no el contexto)
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": response_text})
            await supabase_sessions.update_history(phone, history)
            
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            
            try:
                response_data = json.loads(clean_text)
                return {
                    "message": response_data.get("message") or response_data.get("response", response_text),
                    "should_escalate": response_data.get("should_escalate", False)
                }
            except json.JSONDecodeError:
                return {
                    "message": response_text,
                    "should_escalate": False
                }
    
    return {
        "message": "Lo siento, hubo un error. ¿Podrías repetir?",
        "should_escalate": False
    }