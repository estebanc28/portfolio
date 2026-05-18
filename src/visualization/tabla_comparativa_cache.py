"""
Caché de la tabla comparativa de portafolios.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.finance.portafolio import construir_tabla_comparativa


@st.cache_data(show_spinner=False)
def obtener_tabla_comparativa(
    precios: pd.DataFrame,
    activos: tuple[str, ...],
    pesos_forzados: tuple[tuple[str, float], ...],
    tasa_libre_riesgo_anual: float,
    _version: int = 2,
) -> tuple[pd.DataFrame, dict[str, float], dict[str, float]]:
    """
    Calcula y cachea la tabla comparativa y los pesos de ambos escenarios.
    """
    columnas = [a for a in activos if a in precios.columns]
    sub = precios[columnas]
    forzados = dict(pesos_forzados)

    tabla, m_igual, m_opt = construir_tabla_comparativa(
        sub,
        tasa_libre_riesgo_anual,
        forzados,
    )

    return (
        tabla,
        m_igual.pesos.to_dict(),
        m_opt.pesos.to_dict(),
    )


def invalidar_cache_tabla_comparativa() -> None:
    obtener_tabla_comparativa.clear()
