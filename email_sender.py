import base64
import os
import pickle
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.credentials import Credentials
import smtplib
import socket

# Reemplazá con tu cuenta
SMTP_USER = "lucas.ortiz@adaptiera.team"

# Scopes requeridos para enviar correo
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def obtener_token_oauth():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("./credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    
    return creds.token

def generar_oauth2_string(email, access_token):
    auth_string = f"user={email}\x01auth=Bearer {access_token}\x01\x01"
    return base64.b64encode(auth_string.encode()).decode()

def test_conexion_smtp():
    """Función para probar la conectividad SMTP"""
    try:
        # Probar conexión básica
        sock = socket.create_connection(("smtp.gmail.com", 587), timeout=10)
        sock.close()
        print("✅ Conexión a smtp.gmail.com:587 exitosa")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def enviar_correo_v1(destinatario, asunto, cuerpo):
    """Versión con OAuth2 y mejor manejo de errores"""
    try:
        # Probar conexión primero
        if not test_conexion_smtp():
            return False
            
        access_token = obtener_token_oauth()
        auth_string = generar_oauth2_string(SMTP_USER, access_token)
        
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = destinatario
        msg['Subject'] = asunto
        msg.attach(MIMEText(cuerpo, 'plain'))
        
        # Configurar servidor con timeout más largo
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.set_debuglevel(1)  # Para ver qué está pasando
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            # Autenticación OAuth2
            server.docmd("AUTH", "XOAUTH2 " + auth_string)
            server.sendmail(SMTP_USER, destinatario, msg.as_string())
        
        print("✅ Correo enviado correctamente")
        return True
        
    except Exception as e:
        print("❌ Error al enviar correo:", e)
        return False

def enviar_correo_v2_gmail_api(destinatario, asunto, cuerpo):
    """Alternativa usando Gmail API directamente (recomendado)"""
    try:
        from googleapiclient.discovery import build
        from email.mime.text import MIMEText
        import base64
        
        # Obtener credenciales
        creds = None
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("./credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)
        
        # Crear servicio Gmail API
        service = build('gmail', 'v1', credentials=creds)
        
        # Crear mensaje
        message = MIMEText(cuerpo)
        message['to'] = destinatario
        message['from'] = SMTP_USER
        message['subject'] = asunto
        
        # Codificar mensaje
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Enviar
        send_message = service.users().messages().send(
            userId="me", 
            body={'raw': raw_message}
        ).execute()
        
        print("✅ Correo enviado correctamente via Gmail API")
        return True
        
    except Exception as e:
        print("❌ Error al enviar correo via Gmail API:", e)
        return False

def enviar_correo_v3_password_app(destinatario, asunto, cuerpo, password_app):
    """Alternativa usando contraseña de aplicación (más simple)"""
    try:
        if not test_conexion_smtp():
            return False
            
        msg = MIMEMultipart()
        msg['From'] = 'Adaptiera Team' #SMTP_USER
        msg['To'] = destinatario
        msg['Subject'] = asunto
        msg.attach(MIMEText(cuerpo, 'plain'))
        
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.set_debuglevel(1)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, password_app)  # Usar contraseña de aplicación
            server.sendmail(SMTP_USER, destinatario, msg.as_string())
        
        print("✅ Correo enviado correctamente con contraseña de app")
        return True
        
    except Exception as e:
        print("❌ Error al enviar correo:", e)
        return False

# Función principal que prueba diferentes métodos
def enviar_correo(destinatario, asunto, cuerpo, password_app=None):
    """
    Función principal que intenta diferentes métodos de envío
    """
    print("🔄 Intentando enviar correo...")
    
    # Método 1: Gmail API (recomendado)
    print("📧 Intentando con Gmail API...")
    if enviar_correo_v2_gmail_api(destinatario, asunto, cuerpo):
        return True
    
    # Método 2: OAuth2 con SMTP
    print("📧 Intentando con OAuth2 + SMTP...")
    if enviar_correo_v1(destinatario, asunto, cuerpo):
        return True
    
    # Método 3: Contraseña de aplicación (si se proporciona)
    if password_app:
        print("📧 Intentando con contraseña de aplicación...")
        if enviar_correo_v3_password_app(destinatario, asunto, cuerpo, password_app):
            return True
    
    print("❌ Todos los métodos fallaron")
    return False

# Ejemplo de uso
if __name__ == "__main__":
    # Probar conexión
    test_conexion_smtp()
    
    # Enviar correo
    enviar_correo(
        destinatario="destinatario@email.com",
        asunto="Prueba",
        cuerpo="Este es un correo de prueba"
    )