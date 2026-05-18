"""
Caché del gráfico de frontera eficiente y CML.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.finance.frontera_eficiente import calcular_frontera_eficiente
from src.visualization.frontera import crear_grafico_frontera_cml


@st.cache_data(show_spinner=False)
def obtener_grafico_frontera(
    precios: pd.DataFrame,
    activos: tuple[str, ...],
    pesos_forzados: tuple[tuple[str, float], ...],
    tasa_libre_riesgo_anual: float,
    _version: int = 11,
) -> object:
    """Calcula y cachea la figura de frontera eficiente + CML."""
    columnas = [a for a in activos if a in precios.columns]
    sub = precios[columnas]
    forzados = dict(pesos_forzados)

    datos = calcular_frontera_eficiente(sub, tasa_libre_riesgo_anual, forzados)
    return crear_grafico_frontera_cml(datos)


def invalidar_cache_frontera() -> None:
    obtener_grafico_frontera.clear()
