from fastapi import FastAPI, Form
from dotenv import load_dotenv
from services.agent_runner import run_agent
from services.whatsapp import send_whatsapp_message

load_dotenv()

app = FastAPI(title="Inbound Agent Core")


@app.get("/")
def health_check():
    """Endpoint de salud para verificar que el servidor está activo."""
    return {"status": "ok", "message": "Inbound Agent Core is running"}

@app.post("/webhook")
async def webhook(
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...),
    AccountSid: str = Form(...)
):
    """
    Recibe mensajes de WhatsApp desde Twilio.
    """
    phone = From.replace("whatsapp:", "")
    message = Body
    
    print(f"📩 Mensaje recibido de {phone}: {message}")
    
    response = await run_agent(phone, message)
    
    print(f"🤖 Respuesta del agente: {response['message']}")
    
    result = send_whatsapp_message(to=From, body=response["message"])
    
    if response["should_escalate"]:
        print(f"⚠️ ESCALANDO: Usuario {phone} necesita atención humana")
    
    return {
        "status": "ok",
        "message_sent": response["message"],
        "should_escalate": response["should_escalate"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)