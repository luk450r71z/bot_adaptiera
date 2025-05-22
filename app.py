import streamlit as st
from utils import validar_email, validar_telefono
from api_client import obtener_vacantes_extra, obtener_medios_extra
from email_sender import enviar_correo

st.set_page_config(page_title="Formulario de Postulación", layout="centered")
st.title("Formulario de Postulación")

# Campos del formulario
with st.form("formulario_postulacion"):
    nombre = st.text_input("Apellidos y Nombres", placeholder="Ej. Juan Pérez")

    # Dropdown de Vacantes
    vacantes_base = ['Full Stack Developer', 'Datascience']
    vacantes_extra = obtener_vacantes_extra()
    opciones_vacantes = vacantes_base + vacantes_extra
    vacante = st.selectbox("Vacante", opciones_vacantes)

    correo = st.text_input("Correo", placeholder="ejemplo@dominio.com")
    telefono = st.text_input("Teléfono", placeholder="+52 123 456 7890")

    # Dropdown de Medio de Notificación
    medios_base = ['correo', 'telefono']
    medios_extra = obtener_medios_extra()
    opciones_medios = medios_base + medios_extra
    medio_notif = st.selectbox("Medio de Notificación", opciones_medios)

    submitted = st.form_submit_button("Enviar")

    if submitted:
        errores = []
        if not validar_email(correo):
            errores.append("Correo inválido.")
        if not validar_telefono(telefono):
            errores.append("Teléfono inválido (debe tener al menos 10 dígitos).")

        if errores:
            for error in errores:
                st.error(error)
        else:
            # Enviar correo
            enviado = enviar_correo(
                destinatario="lucas.ortiz@adaptiera.team",
                asunto="Nueva postulación recibida",
                cuerpo=f"""
                Apellidos y Nombres: {nombre}
                Vacante: {vacante}
                Correo: {correo}
                Teléfono: {telefono}
                Medio de Notificación: {medio_notif}
                """
            )
            if enviado:
                st.success("Formulario enviado correctamente.")
            else:
                st.error("Hubo un error al enviar el correo.")
