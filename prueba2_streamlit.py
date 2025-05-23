import streamlit as st
import groq
import os
import json
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cryptography.fernet import Fernet

import ast

from dotenv import load_dotenv
load_dotenv()  # Carga las variables de entorno desde el archivo .env

# Función para desencriptar texto
def desencriptar_texto(texto_encriptado, clave):
    f = Fernet(clave)

    try:
        # Intenta evaluar de forma segura (solo literales)
        b = ast.literal_eval(texto_encriptado)
        print(f"Texto evaluado: {b}")
        print(type(b))
    except Exception:
        # Si falla, intenta corregir
        texto_encriptado += "'"
        b = ast.literal_eval(texto_encriptado)
        print("Texto inválido, se agregó un apóstrofo.")
        print(f"Texto corregido: {texto_encriptado}")
    
    return f.decrypt(b).decode()

# Leer token cifrado en la URL
query_params = st.query_params
token = query_params.get("token", None)

if token:
    try:
        # La clave debe estar almacenada de forma segura, aquí la obtenemos de una variable de entorno
        clave = os.getenv("FERNET_KEY").encode()
        # Desencriptar el JSON
        json_desencriptado = desencriptar_texto(token, clave)
        print(f"Token desencriptado: {json_desencriptado}")
        # Convertir el JSON a diccionario
        datos_usuario = json.loads(json_desencriptado)
        nombre_usuario = datos_usuario.get("nombre", "Candidato")
        telefono_usuario = datos_usuario.get("phone")
        id_vacancy = datos_usuario.get("vacancy")
    except Exception as e:
        st.error(f"Error al procesar el token: {str(e)}")
        nombre_usuario = "Candidato"
        id_vacancy = None
else:
    # Leer parámetros GET desde la URL
    query_params = st.query_params
    nombre_usuario = query_params.get("nombre", "Candidato")
    telefono_usuario = query_params.get("phone")
    id_vacancy = query_params.get("vacancy")


# Configura tu API Key de Groq
client = groq.Groq(api_key=os.environ["GROQ_API_KEY"])

# Cargar preguntas desde archivo JSON
try:
    with open("preguntas.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        preguntas_data = data["preguntas"]
except Exception as e:
    st.error(f"Error al cargar preguntas: {str(e)}")
    preguntas_data = []

# Inicialización del estado de sesión
if "chat" not in st.session_state:
    st.session_state.chat = []
    st.session_state.respuestas = {}
    st.session_state.indice = 0
    st.session_state.finalizado = False

# Validación con LLM
def validar_respuesta(pregunta: str, respuesta: str) -> bool:
    prompt = f"""
Analiza la siguiente respuesta y determina si responde a la pregunta.
No seas tan estricto, la respuesta puede ser un poco vaga.

Pregunta: "{pregunta}"
Respuesta del candidato: "{respuesta}"

Responde solo con:
- sí: si la respuesta es clara y directamente relacionada con la pregunta.
- no: si la respuesta irrelevante o no responde a la pregunta.
"""
    try:
        response = client.chat.completions.create(
            model='llama3-70b-8192',
            messages=[{"role": "user", "content": prompt}]
        )
        resultado = response.choices[0].message.content.strip().lower()
        return "sí" in resultado
    except Exception as e:
        print("[ERROR EN VALIDACIÓN]:", e)
        return True

# Guardar archivo con respuestas
def guardar_respuestas(respuestas, nombre, id_vacancy):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"respuestas_{nombre or 'anonimo'}_{timestamp}.json"
    datos_guardar = {
        "fecha": timestamp,
        "nombre": nombre,
        "id_vacancy": id_vacancy,
        "respuestas": respuestas
    }
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(datos_guardar, f, ensure_ascii=False, indent=4)
    return nombre_archivo


def enviar_resumen_por_email(respuestas, preguntas_data, nombre, id_vacancy, destino_email):
    # Crear cuerpo del mensaje
    cuerpo = f"Entrevista de {nombre} (ID Vacante: {id_vacancy or 'N/A'})\n\n"

    for pregunta in preguntas_data:
        id_p = pregunta["id"]
        texto = pregunta["texto"]
        respuesta = respuestas.get(id_p, "[sin respuesta]")
        cuerpo += f"🔹 {texto}\n➡️ {respuesta}\n\n"

    # Configurar email
    remitente = "santiago.ferrero@adaptiera.team"
    contraseña = os.getenv("PASS_GMAIL")
    asunto = f"📝 Respuestas de entrevista - {nombre}"

    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = destino_email
    mensaje["Subject"] = asunto
    mensaje.attach(MIMEText(cuerpo, "plain", "utf-8"))

    try:
        # Conexión segura al servidor SMTP
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remitente, contraseña)
        servidor.send_message(mensaje)
        servidor.quit()
        return True
    except Exception as e:
        print(f"[ERROR AL ENVIAR EMAIL]: {e}")
        return False




# Mostrar el título y saludo personalizado
st.title("🧑‍💼 Chat de Entrevista RRHH")
st.markdown(f"**Bienvenido/a, {nombre_usuario}**")
if id_vacancy:
    st.markdown(f"ID de vacante: `{id_vacancy}`")

# Mostrar el historial del chat
chat_container = st.container()
with chat_container:
    for entrada in st.session_state.chat:
        with st.chat_message(entrada["rol"]):
            st.markdown(entrada["mensaje"])


# Flujo principal de la entrevista
if not st.session_state.finalizado:
    if st.session_state.indice < len(preguntas_data):
        pregunta_actual = preguntas_data[st.session_state.indice]
        clave, texto = pregunta_actual["id"], pregunta_actual["texto"]

        # Mostrar la pregunta si aún no fue hecha
        if len(st.session_state.chat) == 0 or st.session_state.chat[-1]["rol"] != "assistant":
            st.session_state.chat.append({"rol": "assistant", "mensaje": texto})
            st.rerun()

        user_input = st.chat_input("Tu respuesta...")
        if user_input:
            st.session_state.chat.append({"rol": "user", "mensaje": user_input})

            if validar_respuesta(texto, user_input):
                st.session_state.respuestas[clave] = user_input
                st.session_state.indice += 1
            else:
                st.session_state.chat.append({"rol": "assistant", "mensaje": "La respuesta no fue clara. Por favor intenta ser más preciso."})
                # Volver a mostrar la misma pregunta
                st.session_state.chat.append({"rol": "assistant", "mensaje": texto})

            st.rerun()

    else:
    # Al finalizar la entrevista
        nombre_archivo = guardar_respuestas(st.session_state.respuestas, nombre_usuario, id_vacancy)

        # Dirección de correo destino
        destino_email = "santiago.ferrero@adaptiera.team"

        exito_email = enviar_resumen_por_email(
            respuestas=st.session_state.respuestas,
            preguntas_data=preguntas_data,
            nombre=nombre_usuario,
            id_vacancy=id_vacancy,
            destino_email=destino_email
        )

        mensaje_final = f"¡Gracias por completar la entrevista! Tus respuestas fueron guardadas en `{nombre_archivo}`"
        if exito_email:
            mensaje_final += " y se han enviado por correo correctamente."
        else:
            mensaje_final += ". Sin embargo, hubo un error al enviar el correo."

        st.session_state.chat.append({"rol": "assistant", "mensaje": mensaje_final})
        st.session_state.finalizado = True
        st.rerun()
