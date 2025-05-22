# import streamlit as st
# from utils import validar_email, validar_telefono
# from api_client import obtener_vacantes_extra, obtener_medios_extra
# from email_sender import enviar_correo
# # Importar el generador de templates
# from email_templates import generar_asunto_y_cuerpo_simple

# st.set_page_config(page_title="Adaptiera - Formulario de Invitación a Postulación", layout="centered")

# st.title("Adaptiera - Formulario de Invitación a Postulación")

# # Campos del formulario
# with st.form("formulario_invitacion_postulacion"):
#     nombre = st.text_input("Apellidos y Nombres", placeholder="Ej. Juan Pérez")

#     # Dropdown de Vacantes
#     vacantes_base = ['Full Stack Developer', 'Datascience']
#     vacantes_extra = obtener_vacantes_extra()
#     opciones_vacantes = vacantes_base + vacantes_extra

#     # Crear diccionario con índices
#     vacantes_con_indices = {f"{i}: {vacante}": vacante for i, vacante in enumerate(opciones_vacantes)}

#     # Mostrar las opciones con índices en el selectbox
#     vacante_seleccionada = st.selectbox("Vacante", list(vacantes_con_indices.keys()))

#     correo = st.text_input("Correo", placeholder="ejemplo@dominio.com")
#     telefono = st.text_input("Teléfono", placeholder="+52 123 456 7890")

#     # Dropdown de Medio de Notificación
#     medios_base = ['correo', 'telefono']
#     medios_extra = obtener_medios_extra()
#     opciones_medios = medios_base + medios_extra
#     medio_notif = st.selectbox("Medio de Notificación", opciones_medios)

#     submitted = st.form_submit_button("Enviar")

#     if submitted:
#         errores = []
#         if not validar_email(correo):
#             errores.append("Correo inválido.")
#         if not validar_telefono(telefono):
#             errores.append("Teléfono inválido (debe tener al menos 10 dígitos).")

#         if errores:
#             for error in errores:
#                 st.error(error)
#         else:
#             # Extraer el nombre de vacante sin índice
#             vacante = vacantes_con_indices[vacante_seleccionada]
            
#             # 1. Enviar correo interno (como ya lo tienes)
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
            
#             # 2. Enviar correo de reclutamiento al candidato (NUEVO)
#             correo_candidato_enviado = False
#             if correo_interno_enviado and medio_notif == 'correo':
#                 try:
#                     # Generar contenido del correo de reclutamiento
#                     asunto_reclutamiento, cuerpo_reclutamiento = generar_asunto_y_cuerpo_simple(
#                         nombre_candidato=nombre,
#                         puesto=vacante,
#                         empresa="Adaptiera",
#                         enlace_entrevista="https://forms.google.com/d/tu-formulario-entrevista"  # Cambiar por tu enlace real
#                     )
                    
#                     # Enviar correo al candidato usando tu función existente
#                     correo_candidato_enviado = enviar_correo(
#                         destinatario=correo,  # Email del candidato
#                         asunto=asunto_reclutamiento,
#                         cuerpo=cuerpo_reclutamiento
#                     )
                    
#                 except Exception as e:
#                     st.error(f"Error al generar correo de reclutamiento: {e}")
            
#             # Mostrar resultados
#             if correo_interno_enviado:
#                 st.success("✅ Formulario enviado correctamente.")
                
#                 if medio_notif == 'correo':
#                     if correo_candidato_enviado:
#                         st.success("✅ Correo de reclutamiento enviado al candidato.")
#                     else:
#                         st.warning("⚠️ No se pudo enviar el correo de reclutamiento al candidato.")
#                 elif medio_notif == 'telefono':
#                     st.info("📞 El candidato será contactado por teléfono.")
#                 else:
#                     st.info(f"📋 Notificación configurada vía: {medio_notif}")
#             else:
#                 st.error("❌ Hubo un error al enviar el correo interno.")

import streamlit as st
from utils import validar_email, validar_telefono
from api_client import obtener_vacantes_extra, obtener_medios_extra
from email_sender import enviar_correo
from email_templates import generar_asunto_y_cuerpo_simple

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

    # Dropdown de Medio de Notificación
    medios_base = ['correo', 'telefono']
    medios_extra = obtener_medios_extra()
    opciones_medios = medios_base + medios_extra
    medio_notif = st.selectbox("Medio de Notificación", opciones_medios)

    submitted = st.form_submit_button("Enviar", disabled=st.session_state["enviando"])

# Lógica de envío
if submitted:
    st.session_state["enviando"] = True
    errores = []
    if not validar_email(correo):
        errores.append("Correo inválido.")
    if not validar_telefono(telefono):
        errores.append("Teléfono inválido (debe tener al menos 10 dígitos).")

    if errores:
        for error in errores:
            st.error(error)
        st.session_state["enviando"] = False
    else:
        vacante = vacantes_con_indices[vacante_seleccionada]

        with st.spinner("📤 Enviando correos..."):
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

            # 2. Enviar correo al candidato si corresponde
            correo_candidato_enviado = False
            if correo_interno_enviado and medio_notif == 'correo':
                try:
                    asunto_reclutamiento, cuerpo_reclutamiento = generar_asunto_y_cuerpo_simple(
                        nombre_candidato=nombre,
                        puesto=vacante,
                        empresa="Adaptiera",
                        enlace_entrevista="https://forms.google.com/d/tu-formulario-entrevista"  # Cambiar por el real
                    )
                    correo_candidato_enviado = enviar_correo(
                        destinatario=correo,
                        asunto=asunto_reclutamiento,
                        cuerpo=cuerpo_reclutamiento
                    )
                except Exception as e:
                    st.error(f"Error al generar correo de reclutamiento: {e}")

        # Mostrar resultados
        if correo_interno_enviado:
            st.success("✅ Formulario enviado correctamente.")
            if medio_notif == 'correo':
                if correo_candidato_enviado:
                    st.success("✅ Correo de reclutamiento enviado al candidato.")
                else:
                    st.warning("⚠️ No se pudo enviar el correo de reclutamiento al candidato.")
            elif medio_notif == 'telefono':
                st.info("📞 El candidato será contactado por teléfono.")
            else:
                st.info(f"📋 Notificación configurada vía: {medio_notif}")
        else:
            st.error("❌ Hubo un error al enviar el correo interno.")

        st.session_state["enviando"] = False
