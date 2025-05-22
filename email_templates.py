# email_templates.py
"""
Módulo independiente para generar templates de correo de reclutamiento
No modifica ni interfiere con el script de envío existente
"""

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generar_cuerpo_correo_html(nombre_candidato, puesto, empresa="Adaptiera", enlace_entrevista="#"):
    """
    Genera el cuerpo del correo en formato HTML similar al de la imagen
    """
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .emoji {{
                font-size: 24px;
                margin-right: 8px;
            }}
            .highlight {{
                font-weight: bold;
                color: #1a73e8;
            }}
            .button {{
                display: inline-block;
                background-color: #1a73e8;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .button:hover {{
                background-color: #1557b0;
            }}
            .footer {{
                margin-top: 30px;
                font-style: italic;
                color: #666;
                font-size: 14px;
                border-top: 1px solid #eee;
                padding-top: 15px;
            }}
            .signature {{
                margin-top: 20px;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <p><span class="emoji">👋</span>¡Hola{f' {nombre_candidato}' if nombre_candidato else ''}!</p>
        
        <p>Somos de <span class="highlight">{empresa}</span> y vimos tu postulación para el puesto de <span class="highlight">{puesto}</span>.</p>
        
        <p>Estamos muy interesados en tu perfil y queremos conocerte un poco más.</p>
        
        <p>Cuando tengas un momento, te invitamos a participar de la primera etapa de entrevistas. Solo tenés que ingresar al siguiente enlace, donde te haremos algunas preguntas:</p>
        
        <div style="text-align: center;">
            <a href="{enlace_entrevista}" class="button">Ir a entrevista</a>
        </div>
        
        <p>Muchas gracias por tu tiempo.</p>
        
        <div class="signature">
            <p>Saludos,<br>
            <span class="highlight">Equipo de {empresa}</span></p>
        </div>
        
        <div class="footer">
            <p>Este correo fue generado automáticamente. Si no estás interesado, simplemente podés ignorarlo.</p>
        </div>
    </body>
    </html>
    """
    return html_template

def generar_cuerpo_correo_texto(nombre_candidato, puesto, empresa="Adaptiera", enlace_entrevista="#"):
    """
    Genera el cuerpo del correo en formato texto plano
    """
    texto_template = f"""👋 ¡Hola{f' {nombre_candidato}' if nombre_candidato else ''}!

Somos de {empresa} y vimos tu postulación para el puesto de {puesto}.

Estamos muy interesados en tu perfil y queremos conocerte un poco más.

Cuando tengas un momento, te invitamos a participar de la primera etapa de entrevistas. Solo tenés que ingresar al siguiente enlace, donde te haremos algunas preguntas:

{enlace_entrevista}

Muchas gracias por tu tiempo.

Saludos,
Equipo de {empresa}

---
Este correo fue generado automáticamente. Si no estás interesado, simplemente podés ignorarlo.
"""
    return texto_template

def crear_mensaje_multipart(destinatario, nombre_candidato, puesto, empresa="Adaptiera", 
                          enlace_entrevista="#", remitente="santiago.ferrero@adaptiera.team"):
    """
    Crea un mensaje multipart (HTML + texto) listo para enviar
    Retorna el objeto mensaje completo
    """
    # Crear mensaje multipart
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"👋 Te estamos buscando para el puesto de {puesto}"
    msg['From'] = remitente
    msg['To'] = destinatario
    
    # Crear versiones del correo
    texto_plano = generar_cuerpo_correo_texto(nombre_candidato, puesto, empresa, enlace_entrevista)
    texto_html = generar_cuerpo_correo_html(nombre_candidato, puesto, empresa, enlace_entrevista)
    
    # Convertir a objetos MIMEText
    parte_texto = MIMEText(texto_plano, 'plain', 'utf-8')
    parte_html = MIMEText(texto_html, 'html', 'utf-8')
    
    # Adjuntar partes al mensaje
    msg.attach(parte_texto)
    msg.attach(parte_html)
    
    return msg

def generar_asunto_y_cuerpo_simple(nombre_candidato, puesto, empresa="Adaptiera", enlace_entrevista="#"):
    """
    Genera asunto y cuerpo en texto plano para usar con tu script existente
    Retorna: (asunto, cuerpo_texto)
    """
    asunto = f"👋 Te estamos buscando para el puesto de {puesto}"
    cuerpo = generar_cuerpo_correo_texto(nombre_candidato, puesto, empresa, enlace_entrevista)
    
    return asunto, cuerpo

# Ejemplos de uso:
if __name__ == "__main__":
    # Ejemplo 1: Generar solo HTML
    html = generar_cuerpo_correo_html("Juan Pérez", "Data Scientist", enlace_entrevista="https://forms.google.com/123")
    print("=== HTML GENERADO ===")
    print(html[:200] + "...")

    # Ejemplo 2: Generar asunto y cuerpo simple para usar con script existente
    asunto, cuerpo = generar_asunto_y_cuerpo_simple(
        nombre_candidato="María González",
        puesto="Full Stack Developer",
        enlace_entrevista="https://forms.google.com/entrevista-456"
    )
    print("\n=== PARA SCRIPT EXISTENTE ===")
    print(f"Asunto: {asunto}")
    print(f"Cuerpo: {cuerpo[:100]}...")
    
    # Ejemplo 3: Crear mensaje completo multipart
    mensaje = crear_mensaje_multipart(
        destinatario="candidato@email.com",
        nombre_candidato="Carlos López", 
        puesto="Data Scientist",
        enlace_entrevista="https://forms.google.com/789"
    )
    print(f"\n=== MENSAJE MULTIPART ===")
    print(f"Asunto: {mensaje['Subject']}")
    print(f"Para: {mensaje['To']}")
    print(f"De: {mensaje['From']}")