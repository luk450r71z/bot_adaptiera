import requests

# Estos endpoints deben apuntar a tus APIs reales
ENDPOINT_VACANTES = "https://api.ejemplo.com/vacantes"
ENDPOINT_MEDIOS = "https://api.ejemplo.com/medios"

def obtener_vacantes_extra():
    try:
        response = requests.get(ENDPOINT_VACANTES, timeout=5)
        if response.status_code == 200:
            return response.json().get("vacantes", [])
    except:
        pass
    return []

def obtener_medios_extra():
    try:
        response = requests.get(ENDPOINT_MEDIOS, timeout=5)
        if response.status_code == 200:
            return response.json().get("medios", [])
    except:
        pass
    return []
