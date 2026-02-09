from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from .config import AGENT_NAME, COMPANY, PERSONALITY, BANT_QUESTIONS, CONVERSATION_EXAMPLES, DEFAULTS
from .prompt import agent_prompt_template
from .tools import get_contact, detect_location


def get_contact_context(phone_number: str = None) -> dict:
    """
    Get contact info from CRM
    Returns context and greeting instruction
    """
    if phone_number:
        result = get_contact(phone_number)

        if result["status"] == "success" and result.get("contact"):
            contact = result["contact"]
            name = contact.get("name", "")
            contact_context = "Existing contact. Name: " + name
            greeting_instruction = "This is a returning contact named " + name + ". Greet them by name. Do NOT ask for their name again."
            return {
                "contact_context": contact_context, 
                "greeting_instruction": greeting_instruction,
                "is_new": False,
                "phone_number": phone_number
            }
    
    contact_context = "New contact. Not in CRM yet."
    greeting_instruction = "This is a new contact. Say: '¡Hola! Soy [your name], asesor inmobiliario de [company]. ¿Cuál es tu nombre y cómo puedo ayudarte?' Before scheduling, you MUST ask for their email. After scheduling, use create_contact tool with their full name, email, and phone number: " + str(phone_number) + "."
    return {
        "contact_context": contact_context, 
        "greeting_instruction": greeting_instruction,
        "is_new": True,
        "phone_number": phone_number
    }

    
def get_location_context() -> dict:
    """
    Detects user location.
    """
    result = detect_location()
    
    if result["status"] == "success":
        return {
            "detected_country": result.get("country", "Unknown")
        }
    
    return {
        "detected_country": "Unknown"
    }


def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest):
    """Runs before sending the request to the LLM. Hydrates the template"""

    phone_number = callback_context.state.get("user_id", None)

    crm_data = get_contact_context(phone_number)

    location_data = get_location_context()


    # GET BANT questions (or default config)
    bant = BANT_QUESTIONS or DEFAULTS.get("bant_questions", {})

    # Get conversation examples (or default config)
    examples = CONVERSATION_EXAMPLES or DEFAULTS.get("conversation_examples", "")

    final_instruction = agent_prompt_template.format(
        agent_name=AGENT_NAME or DEFAULTS["agent_name"],
        company=COMPANY or DEFAULTS["company"],
        personality=PERSONALITY or DEFAULTS["personality"],
        contact_context=crm_data["contact_context"],
        greeting_instruction=crm_data["greeting_instruction"],
        detected_country=location_data["detected_country"],
        # BANT variables
        bant_need=bant.get("need", "what they need"),
        bant_timeline=bant.get("timeline", "when they need it"),
        bant_budget=bant.get("budget", "their budget"),
        bant_authority=bant.get("authority", "who decides"),
        # conversation examples
        conversation_examples=examples
    )

    if llm_request.config:
        llm_request.config.system_instruction = final_instruction

    return None