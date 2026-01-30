import os
import requests
from datetime import datetime
from urllib.parse import quote


def get_headers():
    supabase_key = os.getenv("SUPABASE_KEY")
    return {
        "apikey": supabase_key,
        "Authorization": "Bearer " + supabase_key,
        "Content-Type": "application/json"
    }


def get_supabase_url():
    return os.getenv("SUPABASE_URL")

def get_tenant_id():
    return os.getenv("TENANT_ID")


class SupabaseSessionService:
    
    async def get_session(self, phone: str):
        encoded_phone = quote(phone, safe='')
        tenant_id = get_tenant_id()
        url = get_supabase_url() + "/rest/v1/sessions?phone=eq." + encoded_phone + "&tenant_id=eq." + tenant_id
        response = requests.get(url, headers=get_headers())
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                return data[0]
        return None
    
    async def create_session(self, phone: str, state: dict = None):
        url = get_supabase_url() + "/rest/v1/sessions"
        data = {
            "phone": phone,
            "history": [],
            "state": state or {},
            "tenant_id": get_tenant_id(),
        }
        headers = get_headers()
        headers["Prefer"] = "return=representation"
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            result = response.json()
            return result[0] if result else None
        return None
    
    async def update_history(self, phone: str, history: list):
        encoded_phone = quote(phone, safe='')
        tenant_id = get_tenant_id()
        url = get_supabase_url() + "/rest/v1/sessions?phone=eq." + encoded_phone + "&tenant_id=eq." + tenant_id
        data = {
            "history": history,
            "updated_at": datetime.utcnow().isoformat()
        }
        requests.patch(url, headers=get_headers(), json=data)
    
    async def get_or_create_session(self, phone: str):
        session = await self.get_session(phone)
        if session:
            print("📂 Sesión existente para " + phone)
            return session
        
        print("📁 Creando nueva sesión para " + phone)
        return await self.create_session(phone)