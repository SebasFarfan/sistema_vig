import streamlit as st

from consultas import cargar_tabla, listar_tablas

st.title("🗂️ Datos")

tablas = listar_tablas()
if not tablas:
    st.warning("No hay tablas cargadas en la base de datos.")
    st.stop()

col_sel, col_btn = st.columns([4, 1], vertical_alignment="bottom")
tabla = col_sel.selectbox("Tabla", tablas)
if col_btn.button("🔄 Actualizar"):
    st.cache_data.clear()  # útil después de volver a correr el ETL
    st.rerun()

df = cargar_tabla(tabla)

texto = st.text_input("Buscar texto en la tabla")
if texto:
    mascara = (
        df.astype(str)
        .apply(lambda col: col.str.contains(texto, case=False, na=False))
        .any(axis=1)
    )
    df = df[mascara]

c1, c2 = st.columns(2)
c1.metric("Filas", f"{len(df):,}")
c2.metric("Columnas", df.shape[1])

st.dataframe(df, hide_index=True)

st.download_button(
    "⬇️ Descargar CSV",
    data=df.to_csv(index=False).encode("utf-8-sig"),
    file_name=f"{tabla}.csv",
    mime="text/csv",
)
