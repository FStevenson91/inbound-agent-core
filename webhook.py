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

# Webhook para recibir mensajes de WhatsApp, es un handler POST que procesa los datos del formulario, funciona de la siguiente manera: primero extrae los campos From, To, Body, MessageSid y AccountSid del formulario enviado por Twilio. Luego imprime el mensaje recibido en la consola. Después, llama a la función run_agent para procesar el mensaje y obtener una respuesta del agente. A continuación, imprime la respuesta del agente en la consola y envía la respuesta de vuelta al usuario de WhatsApp utilizando la función send_whatsapp_message. Si el agente indica que se debe escalar la conversación a un humano, también imprime un mensaje de advertencia en la consola. Finalmente, devuelve un JSON con el estado de la operación, el mensaje enviado y si se debe escalar o no.

# Basicamente un handler es una funcion que maneja una peticion HTTP, en este caso POST, y procesa los datos recibidos.
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
    
    # Ejecutar agente (ahora con await)
    response = await run_agent(phone, message)
    
    print(f"🤖 Respuesta del agente: {response['message']}")
    
    # Enviar respuesta por WhatsApp
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