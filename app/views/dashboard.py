from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from consultas import (
    ESTADOS_HABILITADOS,
    cobertura_por_empresa,
    habilitados_a_fecha,
    objetivos_por_unidad,
    tramites_por_anio,
    vencimientos_empresas,
    vigiladores_por_estado,
)

st.title("📊 Dashboard")

tab_vig, tab_venc, tab_cob = st.tabs(
    ["Vigiladores", "Vencimientos de habilitación", "Dotación vs. objetivos"]
)

# ---------------------------------------------------------------- Vigiladores
with tab_vig:
    estados = vigiladores_por_estado()
    total = int(estados["cantidad"].sum())
    habilitados_hoy = int(
        estados.loc[
            estados["estado"].str.lower().isin(ESTADOS_HABILITADOS), "cantidad"
        ].sum()
    )

    fecha = st.date_input("Habilitados a la fecha", value=date.today())
    c1, c2, c3 = st.columns(3)
    c1.metric("Habilitados a la fecha", f"{habilitados_a_fecha(fecha):,}")
    c2.metric("Habilitados actualmente (Alta + Renovación)", f"{habilitados_hoy:,}")
    c3.metric("Total de vigiladores", f"{total:,}")
    st.caption(
        "Se consideran habilitados los vigiladores en estado Alta o Renovación. "
        "El conteo a una fecha es aproximado: usa el estado actual y la fecha del "
        "último trámite, no el historial completo (si un vigilador renovó después "
        "de esa fecha, no se cuenta)."
    )

    izq, der = st.columns(2)
    with izq:
        st.subheader("Vigiladores por estado")
        st.plotly_chart(px.bar(estados, x="estado", y="cantidad", text="cantidad"))
    with der:
        st.subheader("Trámites por año")
        st.plotly_chart(
            px.bar(tramites_por_anio(), x="anio", y="cantidad", color="estado")
        )

# ---------------------------------------------------------------- Vencimientos
with tab_venc:
    ORDEN = [
        "Vencida", "Vence en 30 días", "Vence en 60 días",
        "Vence en 90 días", "Vigente (+90 días)", "Inhabilitados",
    ]

    def clasificar(dias):
        if pd.isna(dias):
            return "Inhabilitados"
        if dias < 0:
            return "Vencida"
        if dias <= 30:
            return "Vence en 30 días"
        if dias <= 60:
            return "Vence en 60 días"
        if dias <= 90:
            return "Vence en 90 días"
        return "Vigente (+90 días)"

    df = vencimientos_empresas()
    df["hab_final"] = pd.to_datetime(df["hab_final"])
    hoy = pd.Timestamp.today().normalize()
    df["dias_restantes"] = (df["hab_final"] - hoy).dt.days
    df["situacion"] = df["dias_restantes"].apply(clasificar)

    resumen = (
        df["situacion"].value_counts()
        .reindex(ORDEN, fill_value=0)
        .rename_axis("situacion").reset_index(name="empresas")
    )

    cols = st.columns(len(ORDEN))
    for col, fila in zip(cols, resumen.itertuples()):
        col.metric(fila.situacion, fila.empresas)

    st.plotly_chart(px.bar(resumen, x="situacion", y="empresas", text="empresas"))

    filtro = st.multiselect("Filtrar por situación", ORDEN, default=ORDEN[1:4])
    detalle = df[df["situacion"].isin(filtro)].sort_values("dias_restantes")
    st.dataframe(
        detalle[["empresa", "hab_final", "dias_restantes", "situacion"]],
        hide_index=True,
    )

# ---------------------------------------------------------------- Cobertura
with tab_cob:
    cob = cobertura_por_empresa()

    c1, c2, c3 = st.columns(3)
    c1.metric("Empresas", len(cob))
    c2.metric("Objetivos", int(cob["objetivos"].sum()))
    c3.metric("Vigiladores habilitados", int(cob["vigiladores_habilitados"].sum()))

    cob["vigiladores_por_objetivo"] = (
        cob["vigiladores_habilitados"] / cob["objetivos"].where(cob["objetivos"] > 0)
    ).round(2)

    top = st.slider("Empresas a mostrar en los gráfico", 5, 40, 15)
    graf = (
        cob.sort_values("vigiladores_habilitados", ascending=False)
        .head(top)
        .melt(
            id_vars="empresa",
            value_vars=["vigiladores_habilitados", "objetivos"],
            var_name="indicador", value_name="cantidad",
        )
    )
    st.plotly_chart(
        px.bar(graf, x="empresa", y="cantidad", color="indicador", barmode="group")
    )
    
    # //=======-------------------------------------------
    st.subheader("Vigiladores asignados a objetivos por empresa")

    asig = cob.copy()
    asig["sin_asignar"] = (
        asig["vigiladores_habilitados"] - asig["vigiladores_asignados"]
    ).clip(lower=0)
    asig = (
        asig[asig["vigiladores_habilitados"] > 0]
        .sort_values("vigiladores_asignados", ascending=False)
        .head(top)
    )

    graf_asig = asig.melt(
        id_vars="empresa",
        value_vars=["vigiladores_asignados", "sin_asignar"],
        # value_vars=['vigiladores_asignados'],
        var_name="situacion",
        value_name="cantidad",
    )
    graf_asig["situacion"] = graf_asig["situacion"].replace(
        {"vigiladores_asignados": "Asignados a objetivos", "sin_asignar": "Sin asignar", "inhabilitados": "Inhabilitados"}
    )

    fig_asig = px.bar(
        graf_asig,
        x="cantidad",
        y="empresa",
        color="situacion",
        orientation="h",
        barmode="stack",
        text="cantidad",
    )
    fig_asig.update_layout(yaxis={"categoryorder": "total ascending"}, legend_title_text="")
    st.plotly_chart(fig_asig)
    st.caption(
        "Sin asignar = vigiladores habilitados de la empresa que no figuran "
        "asignados a ninguno de sus objetivos."
    )
    # ---------------------------------------------------

    st.subheader("Detalle por empresa")
    st.dataframe(cob.drop(columns="id_empresa"), hide_index=True)

    st.subheader("Objetivos por unidad regional")
    st.plotly_chart(
        px.bar(objetivos_por_unidad(), x="unidad_regional", y="objetivos", text="objetivos")
    )
