import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

# 
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")


def send_whatsapp_message(to: str, body: str) -> dict:
    """
    Envía un mensaje de WhatsApp usando Twilio.
    
    Args:
        to: Número destino con formato "whatsapp:+56912345678"
        body: Texto del mensaje
    
    Returns:
        dict con status y message_sid o error
    """
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
        
        data = {
            "From": f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            "To": to,
            "Body": body
        }
        
        response = requests.post(
            url,
            data=data,
            auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=10
        )
        
        if response.status_code == 201:
            return {"status": "success", "message_sid": response.json().get("sid")}
        
        return {"status": "error", "message": response.text}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}