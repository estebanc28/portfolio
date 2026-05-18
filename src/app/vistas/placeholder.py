"""Plantilla para secciones aún no implementadas."""

import streamlit as st


def mostrar(titulo: str, icono: str, descripcion: str, acciones: list[str]) -> None:
    st.title(f"{icono} {titulo}")
    st.markdown(descripcion)
    st.markdown("**Acciones previstas:**")
    for accion in acciones:
        st.markdown(f"- {accion}")
    st.warning("Esta sección se implementará en una siguiente iteración del proyecto.")
