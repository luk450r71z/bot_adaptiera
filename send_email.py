import os.path
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle

# Permisos necesarios para enviar correos
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def login_gmail():
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def send_email(service, to, subject, body_text):
    message = EmailMessage()
    message.set_content(body_text)
    message['To'] = to
    message['From'] = "me"
    message['Subject'] = subject

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {
        'raw': encoded_message
    }

    send_message = service.users().messages().send(userId="me", body=create_message).execute()
    print(f'✅ Correo enviado. ID del mensaje: {send_message["id"]}')

if __name__ == '__main__':
    gmail_service = login_gmail()
    send_email(gmail_service, "destinatario@gmail.com", "Asunto de prueba", "Este es un mensaje enviado con Gmail API y OAuth 2.0")
