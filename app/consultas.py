from typing import Optional

import pandas as pd
import streamlit as st
from sqlalchemy import inspect, text

from database import engine

# Tablas que no se muestran en la página "Datos"
TABLAS_EXCLUIDAS = {"usuarios"}

# Estados que cuentan como "habilitado" (en minúsculas, sin espacios)
ESTADOS_HABILITADOS = ("alta", "renovacion")
_IN_HAB = ", ".join(f"'{e}'" for e in ESTADOS_HABILITADOS)


# ------------------------------------------------------------------ Genéricas
@st.cache_data(ttl=300)
def listar_tablas() -> list[str]:
    tablas = inspect(engine).get_table_names()
    return sorted(t for t in tablas if t not in TABLAS_EXCLUIDAS)


@st.cache_data(ttl=300)
def cargar_tabla(nombre: str) -> pd.DataFrame:
    if nombre not in listar_tablas():
        raise ValueError(f"Tabla no permitida: {nombre}")
    return pd.read_sql_table(nombre, con=engine)


@st.cache_data(ttl=300)
def consultar(sql: str, params: Optional[dict] = None) -> pd.DataFrame:
    """Ejecuta una consulta SQL con parámetros (:nombre) y devuelve un DataFrame."""
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


# ----------------------------------------------------------------- Vigiladores
@st.cache_data(ttl=300)
def vigiladores_por_estado() -> pd.DataFrame:
    return consultar("""
        SELECT TRIM(estado) AS estado, COUNT(*) AS cantidad
        FROM vigilante
        GROUP BY TRIM(estado)
        ORDER BY cantidad DESC
    """)


@st.cache_data(ttl=300)
def habilitados_a_fecha(fecha) -> int:
    df = consultar(f"""
        SELECT COUNT(*) AS n
        FROM vigilante
        WHERE LOWER(TRIM(estado)) IN ({_IN_HAB})
          AND fecha_tramite <= :fecha
    """, {"fecha": fecha})
    return int(df["n"][0])


@st.cache_data(ttl=300)
def tramites_por_anio() -> pd.DataFrame:
    return consultar("""
        SELECT YEAR(fecha_tramite) AS anio,
               TRIM(estado)        AS estado,
               COUNT(*)            AS cantidad
        FROM vigilante
        WHERE fecha_tramite IS NOT NULL
        GROUP BY YEAR(fecha_tramite), TRIM(estado)
        ORDER BY anio
    """)


# ------------------------------------------------------------ Habilitaciones
@st.cache_data(ttl=300)
def vencimientos_empresas() -> pd.DataFrame:
    """Última fecha de fin de habilitación registrada por empresa."""
    return consultar("""
        SELECT e.id_empresa,
               e.nombre_empresa AS empresa,
               MAX(s.hab_final) AS hab_final
        FROM empresa e
        LEFT JOIN salida s ON s.id_empresa = e.id_empresa
        GROUP BY e.id_empresa, e.nombre_empresa
    """)


# ------------------------------------------------------- Dotación y objetivos
@st.cache_data(ttl=300)
def cobertura_por_empresa() -> pd.DataFrame:
    return consultar(f"""
        SELECT e.id_empresa,
               e.nombre_empresa           AS empresa,
               COALESCE(v.vigiladores, 0) AS vigiladores_habilitados,
               COALESCE(o.objetivos, 0)   AS objetivos,
               COALESCE(a.asignados, 0)   AS vigiladores_asignados
        FROM empresa e
        LEFT JOIN (
            SELECT id_empresa, COUNT(*) AS vigiladores
            FROM vigilante
            WHERE LOWER(TRIM(estado)) IN ({_IN_HAB})
            GROUP BY id_empresa
        ) v ON v.id_empresa = e.id_empresa
        LEFT JOIN (
            SELECT id_empresa, COUNT(*) AS objetivos
            FROM objetivo
            GROUP BY id_empresa
        ) o ON o.id_empresa = e.id_empresa
        LEFT JOIN (
            SELECT ob.id_empresa, COUNT(DISTINCT ov.dni_vigilante) AS asignados
            FROM objetivo_vigilante ov
            JOIN objetivo   ob ON ob.id_objetivo = ov.id_objetivo
            JOIN vigilante  vi ON vi.dni = ov.dni_vigilante
            WHERE LOWER(TRIM(vi.estado)) IN ({_IN_HAB})
            GROUP BY ob.id_empresa
        ) a ON a.id_empresa = e.id_empresa
        ORDER BY vigiladores_habilitados DESC
    """)


@st.cache_data(ttl=300)
def objetivos_por_unidad() -> pd.DataFrame:
    return consultar("""
        SELECT `unidad regional` AS unidad_regional, COUNT(*) AS objetivos
        FROM objetivo
        GROUP BY `unidad regional`
        ORDER BY unidad_regional
    """)
