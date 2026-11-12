import streamlit as st

from database import inicializar_base_datos

st.set_page_config(page_title="Sistema VIG", page_icon="🛡️", layout="wide")


@st.cache_resource
def _inicializar():
    inicializar_base_datos()   # se ejecuta una vez por proceso, no en cada interacción


_inicializar()

# --- Estado de sesión ---
st.session_state.setdefault("autenticado", False)
st.session_state.setdefault("usuario", None)


def cerrar_sesion():
    st.session_state.clear()
    st.rerun()


# --- Navegación según autenticación ---
if not st.session_state["autenticado"]:
    pagina = st.navigation(
        [st.Page("views/login.py", title="Iniciar sesión", icon="🔑")]
    )
else:
    pagina = st.navigation(
        {
            "General": [
                st.Page("views/inicio.py", title="Inicio", icon="🏠", default=True),
            ],
            "Información": [
                st.Page("views/datos.py", title="Datos", icon="🗂️"),
                st.Page("views/dashboard.py", title="Dashboard", icon="📊"),
            ],
        }
    )

    with st.sidebar:
        st.write("---")
        st.subheader(f"👤 Perfil: {st.session_state['usuario']}")
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            cerrar_sesion()

pagina.run()