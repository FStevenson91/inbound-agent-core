import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": "Bearer " + SUPABASE_KEY,
    "Content-Type": "application/json"
}

def get_tenant_id():
    return os.getenv("TENANT_ID")

def get_contact(phone: str) -> dict:
    """Busca un contacto por teléfono."""
    try:
        tenant_id = get_tenant_id()
        url = SUPABASE_URL + "/rest/v1/contacts?phone=eq." + phone + "&tenant_id=eq." + tenant_id
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        
        if data and len(data) > 0:
            return {"status": "success", "contact": data[0]}
        return {"status": "not_found", "contact": None}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


def create_contact(name: str, email: str, phone_number: str) -> dict:
    """Crea un contacto nuevo en el CRM."""
    try:
        url = SUPABASE_URL + "/rest/v1/contacts"
        body = {
            "name": name, 
            "phone": phone_number,
            "tenant_id": get_tenant_id()
        }
        if email:
            body["email"] = email
            
        response = requests.post(url, headers=HEADERS, json=body, timeout=10)
        
        if response.status_code == 201:
            return {"status": "success", "message": "Contact created"}
        return {"status": "error", "message": response.text}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


def update_contact(phone: str, **kwargs) -> dict:
    """Actualiza un contacto por teléfono."""
    try:
        tenant_id = get_tenant_id()
        url = SUPABASE_URL + "/rest/v1/contacts?phone=eq." + phone + "&tenant_id=eq." + tenant_id
        response = requests.patch(url, headers=HEADERS, json=kwargs, timeout=10)
        
        if response.status_code == 200:
            return {"status": "success", "message": "Contact updated"}
        return {"status": "error", "message": response.text}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}