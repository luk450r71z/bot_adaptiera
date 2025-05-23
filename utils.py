import re

def validar_email(email: str) -> bool:
    patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(patron, email) is not None

def validar_telefono(telefono: str) -> bool:
    numeros = re.sub(r"\D", "", telefono)
    return len(numeros) >= 10

def validar_telefono(numero):
    # Formato E.164: + seguido de 10 a 15 dígitos
    return re.match(r'^\+\d{10,15}$', numero) is not None
