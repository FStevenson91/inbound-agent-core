# Inbound Agent Core

Agente conversacional para WhatsApp que califica leads inmobiliarios usando la metodología BANT (Budget, Authority, Need, Timeline). Construido con Google ADK y Gemini.

## Qué hace

El agente recibe mensajes de WhatsApp vía Twilio, mantiene una conversación natural con el usuario, y va recopilando información para calificar el lead. Detecta el país del usuario para adaptar el idioma y el tono.

Cuando termina la conversación, guarda el contacto en el CRM con toda la info BANT recopilada.

## Stack

- **Google ADK** - Framework para agentes con Gemini
- **Gemini 2.0 Flash** - Modelo de lenguaje
- **FastAPI** - Servidor para el webhook
- **Twilio** - Integración con WhatsApp
- **Supabase** - Persistencia de sesiones

## Estructura

```
├── webhook.py              # Servidor FastAPI (producción)
├── main.py                 # Modo consola (pruebas locales)
├── services/
│   ├── agent_runner.py     # Ejecuta el agente con contexto
│   ├── supabase_session.py # Manejo de sesiones
│   └── whatsapp.py         # Envío de mensajes
└── real_estate_agent/
    ├── agent.py            # Configuración del agente
    ├── prompt.py           # Prompt del sistema
    ├── callbacks.py        # Inyección de contexto dinámico
    └── tools/
        ├── crm.py          # create_contact, update_contact
        └── location.py     # Detección de país
```

## Setup

### 1. Clonar y crear entorno

```bash
git clone <repo>
cd inbound-agent-core
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Crear un archivo `.env` en la raíz:

```env
# Google
GOOGLE_API_KEY=tu_api_key

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=tu_service_key

# Twilio
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_WHATSAPP_NUMBER=+14155238886

# App
TENANT_ID=uuid-del-tenant
```

### 3. Crear tabla en Supabase

```sql
create table sessions (
  id uuid default gen_random_uuid() primary key,
  phone text not null,
  history jsonb default '[]',
  state jsonb default '{}',
  tenant_id uuid not null,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

create index idx_sessions_phone_tenant on sessions(phone, tenant_id);
```

## Uso

### Desarrollo (con WhatsApp)

```bash
# Terminal 1 - Servidor
python webhook.py

# Terminal 2 - Exponer con ngrok
ngrok http 8000
```

Luego configurar el webhook en Twilio:
`https://tu-url.ngrok.io/webhook`

### Pruebas locales (sin WhatsApp)

```bash
python main.py
```

Te pide un número de teléfono simulado y podés chatear directo en la terminal.

## Cómo funciona

1. Usuario envía mensaje por WhatsApp
2. Twilio hace POST al webhook con el mensaje
3. El servidor busca/crea la sesión del usuario en Supabase
4. Se ejecuta el agente con el historial de la conversación
5. El agente responde siguiendo el flujo BANT
6. Se guarda el historial actualizado
7. Se envía la respuesta por WhatsApp

El agente tiene acceso a dos tools:
- `create_contact`: Crea el contacto en el CRM al final
- `update_contact`: Actualiza info BANT durante la conversación

## Configuración del agente

El comportamiento del agente se puede modificar en `real_estate_agent/prompt.py`. Ahí están las reglas de conversación, el flujo BANT, y los ejemplos.

En `real_estate_agent/callbacks.py` se inyecta el contexto dinámico (nombre de empresa, personalidad, etc.) antes de cada llamada al modelo.

## Notas

- El número de Twilio `+14155238886` es el sandbox. Los usuarios deben enviar "join <several-forward>" primero.
- Para producción hay que agregar validación de firma de Twilio, rate limiting, y logging.
- El agente usa temperatura 0.7 para respuestas más naturales.
