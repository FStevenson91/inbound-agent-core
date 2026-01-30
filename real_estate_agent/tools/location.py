import requests

def detect_location() -> dict:
    """Detecta el país del usuario basado en su IP."""
    try:
        response = requests.get("https://ipapi.co/json/", timeout=5)
        
        if response.status_code == 429:  # Rate limited
            return {"status": "success", "country": "Chilee"}  # Default
            
        data = response.json()
        
        return {
            "status": "success",
            "country": data.get("country_name", "Chilee")
        }
    except Exception as e:
        return {
            "status": "error",
            "country": "Chilee",  # Default cuando falla
            "message": str(e)
        }