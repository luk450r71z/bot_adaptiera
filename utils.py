import re
import requests


def validar_email(email: str) -> bool:
    patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(patron, email) is not None

def validar_telefono(telefono: str) -> bool:
    numeros = re.sub(r"\D", "", telefono)
    return len(numeros) >= 10

def validar_telefono(numero):
    # Formato E.164: + seguido de 10 a 15 dígitos
    return re.match(r'^\+\d{10,15}$', numero) is not None

def acortar_url(url_larga):
    endpoint = "http://tinyurl.com/api-create.php"
    respuesta = requests.get(endpoint, params={"url": url_larga})
    if respuesta.status_code == 200:
        return respuesta.text
    else:
        raise Exception("Error al acortar la URL")