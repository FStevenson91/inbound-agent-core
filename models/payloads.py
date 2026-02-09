from pydantic import BaseModel
from typing import Optional

class TwilioWebhookPayload(BaseModel):
    """Payload que recibimos de Twilio cuando llega un mensaje de WhatsApp."""
    From: str                    # "whatsapp:+56912345678"
    To: str                      # "whatsapp:+14155238886"
    Body: str                    # "Hola, quiero comprar casa"
    MessageSid: str              # ID único del mensaje
    AccountSid: str              # ID de tu cuenta Twilio

class AgentResponse(BaseModel):
    """Respuesta del agente."""
    message: str
    should_escalate: bool = False

class WebhookResponse(BaseModel):
    """Respuesta que devuelve nuestro webhook."""
    status: str
    message_sent: Optional[str] = None
    should_escalate: bool = False