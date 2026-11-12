import streamlit as st

with st.container(border=True):
    st.title(f"👋 ¡Bienvenido, {st.session_state['usuario']}!")
    st.markdown("Desde el menú lateral podés acceder a los reportes del sistema.")