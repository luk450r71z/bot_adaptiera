import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Usa variables de entorno o archivo seguro para las credenciales
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "tu_correo@gmail.com"
SMTP_PASS = "tu_contraseña_o_token"

def enviar_correo(destinatario, asunto, cuerpo):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = destinatario
        msg['Subject'] = asunto
        msg.attach(MIMEText(cuerpo, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("Error al enviar correo:", e)
        return False
