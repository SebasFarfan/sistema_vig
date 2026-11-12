import streamlit as st

from auth import verificar_usuario

st.title("🔑 Iniciar sesión")

with st.form("login_form"):
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    submit = st.form_submit_button("Ingresar")

if submit:
    if verificar_usuario(username, password):
        st.session_state["autenticado"] = True
        st.session_state["usuario"] = username
        st.rerun()
    else:
        st.error("Usuario o contraseña incorrectos")