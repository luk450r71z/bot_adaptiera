import re

def validar_email(email: str) -> bool:
    patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(patron, email) is not None

def validar_telefono(telefono: str) -> bool:
    numeros = re.sub(r"\D", "", telefono)
    return len(numeros) >= 10
