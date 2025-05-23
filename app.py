import streamlit as st
from utils import validar_email, validar_telefono
from api_client import obtener_vacantes_extra, obtener_medios_extra
from email_sender import enviar_correo
from email_templates import generar_asunto_y_cuerpo_simple
from sms_sender import enviar_sms
#Cryptography
import json
from cryptography.fernet import Fernet


st.set_page_config(page_title="Adaptiera - Formulario de Invitación a Postulación", layout="centered")

st.title("Adaptiera - Formulario de Invitación a Postulación")

# Estado del botón para evitar múltiples envíos simultáneos
if "enviando" not in st.session_state:
    st.session_state["enviando"] = False

# Campos del formulario
with st.form("formulario_invitacion_postulacion"):
    nombre = st.text_input("Apellidos y Nombres", placeholder="Ej. Juan Pérez")

    # Dropdown de Vacantes
    vacantes_base = ['Full Stack Developer', 'Datascience']
    vacantes_extra = obtener_vacantes_extra()
    opciones_vacantes = vacantes_base + vacantes_extra

    # Crear diccionario con índices
    vacantes_con_indices = {f"{i}: {vacante}": vacante for i, vacante in enumerate(opciones_vacantes)}
    vacante_seleccionada = st.selectbox("Vacante", list(vacantes_con_indices.keys()))

    correo = st.text_input("Correo", placeholder="ejemplo@dominio.com")
    telefono = st.text_input("Teléfono", placeholder="+52 123 456 7890")
    telefono = telefono.replace(" ", "")  # Limpia espacios antes de validación

    # Dropdown de Medio de Notificación
    medios_base = ['correo', 'telefono']
    medios_extra = obtener_medios_extra()
    opciones_medios = medios_base + medios_extra
    medio_notif = st.selectbox("Medio de Notificación", opciones_medios)

    submitted = st.form_submit_button("Enviar", disabled=st.session_state["enviando"])

# # Lógica de envío
if submitted:
    st.session_state["enviando"] = True
    errores = []

    # Validaciones según el medio
    if medio_notif == 'correo' and not validar_email(correo):
        errores.append("Correo inválido.")
    if medio_notif == 'telefono' and not validar_telefono(telefono):
        errores.append("Teléfono inválido (debe tener al menos 10 dígitos en formato internacional).")

    if errores:
        for error in errores:
            st.error(error)
        st.session_state["enviando"] = False
    else:
        vacante = vacantes_con_indices[vacante_seleccionada]

        # Generar una clave de cifrado
        key = Fernet.generate_key()
        cipher = Fernet(b'8_ATnSijn7ooUv-VekfQDQUvk-FM13Sp9X43ws_mdi8=')
        
        # Ejemplo de objeto JSON
        objeto_json = {
            "nombre": nombre,
            "phone": telefono,
            "vacancy": 1
        }

        # Convertir el objeto JSON a string
        json_string = json.dumps(objeto_json)

        # Encriptar el string
        json_encriptado = cipher.encrypt(json_string.encode())

        with st.spinner("📤 Enviando notificación..."):
            notificacion_enviada = False

            if medio_notif == 'correo':
                # 1. Enviar correo interno
                correo_interno_enviado = enviar_correo(
                    destinatario=correo,
                    asunto="👋 Te estamos buscando para el puesto de Data scientist",
                    cuerpo=f"""
                    Apellidos y Nombres: {nombre}
                    Vacante: {vacante}
                    Correo: {correo}
                    Teléfono: {telefono}
                    Medio de Notificación: {medio_notif}
                    """
                )

                # 2. Enviar correo al candidato
                if correo_interno_enviado:
                    try:
                        asunto_reclutamiento, cuerpo_reclutamiento = generar_asunto_y_cuerpo_simple(
                            nombre_candidato=nombre,
                            puesto=vacante,
                            empresa="Adaptiera",
                            enlace_entrevista=f"https://chatbot-adaptiera.streamlit.app/?token={json_encriptado}"
                        )
                        notificacion_enviada = enviar_correo(
                            destinatario=correo,
                            asunto=asunto_reclutamiento,
                            cuerpo=cuerpo_reclutamiento
                        )
                    except Exception as e:
                        st.error(f"Error al generar o enviar correo de reclutamiento: {e}")

                # Mostrar resultados de notificación por correo
                if correo_interno_enviado:
                    st.success("✅ Formulario enviado correctamente.")
                    if notificacion_enviada:
                        st.success("✅ Correo de reclutamiento enviado al candidato.")
                    else:
                        st.warning("⚠️ No se pudo enviar el correo de reclutamiento al candidato.")
                else:
                    st.error("❌ Hubo un error al enviar el correo interno.")

            elif medio_notif == 'telefono':
                try:
                    mensaje_sms = f"Hola {nombre}, en Adaptiera queremos invitarte a postular al puesto de {vacante}. Ingresa aquí: https://chatbot-adaptiera.streamlit.app/?token=aquiToken"
                    notificacion_enviada = enviar_sms(telefono, mensaje_sms)
                    st.success("✅ SMS enviado correctamente al candidato.")
                except Exception as e:
                    st.error(f"❌ Error al enviar SMS: {e}")

            else:
                st.info(f"📋 Medio de notificación no manejado: {medio_notif}")

        st.session_state["enviando"] = False


# if submitted:
#     st.session_state["enviando"] = True
#     errores = []
#     if not validar_email(correo):
#         errores.append("Correo inválido.")
#     if not validar_telefono(telefono):
#         errores.append("Teléfono inválido (debe tener al menos 10 dígitos).")

#     if errores:
#         for error in errores:
#             st.error(error)
#         st.session_state["enviando"] = False
#     else:
#         vacante = vacantes_con_indices[vacante_seleccionada]

#         with st.spinner("📤 Enviando correos..."):
#             # 1. Enviar correo interno
#             correo_interno_enviado = enviar_correo(
#                 destinatario=correo,
#                 asunto="👋 Te estamos buscando para el puesto de Data scientist",
#                 cuerpo=f"""
#                 Apellidos y Nombres: {nombre}
#                 Vacante: {vacante}
#                 Correo: {correo}
#                 Teléfono: {telefono}
#                 Medio de Notificación: {medio_notif}
#                 """
#             )

#             # 2. Enviar correo al candidato si corresponde
#             correo_candidato_enviado = False
#             if correo_interno_enviado and medio_notif == 'correo':
#                 try:
#                     asunto_reclutamiento, cuerpo_reclutamiento = generar_asunto_y_cuerpo_simple(
#                         nombre_candidato=nombre,
#                         puesto=vacante,
#                         empresa="Adaptiera",
#                         enlace_entrevista="https://forms.google.com/d/tu-formulario-entrevista"  # Cambiar por el real
#                     )
#                     correo_candidato_enviado = enviar_correo(
#                         destinatario=correo,
#                         asunto=asunto_reclutamiento,
#                         cuerpo=cuerpo_reclutamiento
#                     )
#                 except Exception as e:
#                     st.error(f"Error al generar correo de reclutamiento: {e}")

#         # Mostrar resultados
#         if correo_interno_enviado:
#             st.success("✅ Formulario enviado correctamente.")
#             if medio_notif == 'correo':
#                 if correo_candidato_enviado:
#                     st.success("✅ Correo de reclutamiento enviado al candidato.")
#                 else:
#                     st.warning("⚠️ No se pudo enviar el correo de reclutamiento al candidato.")
#             elif medio_notif == 'telefono':
#                 st.info("📞 El candidato será contactado por teléfono.")
#             else:
#                 st.info(f"📋 Notificación configurada vía: {medio_notif}")
#         else:
#             st.error("❌ Hubo un error al enviar el correo interno.")

#         st.session_state["enviando"] = False
