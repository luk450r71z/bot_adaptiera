from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables del archivo .env en el entorno

# Cargar variables de entorno o directamente del archivo credentials.json
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")  # Número de Twilio

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def enviar_sms(destinatario: str, mensaje: str) -> bool:
    mensaje = mensaje[:50]
    try:
        message = client.messages.create(
            body=mensaje,
            from_=TWILIO_PHONE_NUMBER,
            to=destinatario
        )
        print(f"SMS Enviado a : {destinatario}")
        return True
    except Exception as e:
        print(f"Error al enviar SMS: {e}")
        return False
