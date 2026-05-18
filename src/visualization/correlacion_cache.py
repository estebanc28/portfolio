"""
Caché del mapa de calor de correlaciones (evita recálculo al cambiar de hoja).
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.finance.metricas import calcular_matriz_correlacion, calcular_rendimientos
from src.visualization.correlacion import crear_mapa_calor_correlacion


@st.cache_data(show_spinner=False)
def obtener_mapa_correlacion(
    precios: pd.DataFrame,
    activos: tuple[str, ...],
) -> tuple[object, int]:
    """
    Calcula y cachea el mapa de calor. Solo se vuelve a ejecutar si cambian
    los precios o la lista de activos seleccionados.
    """
    columnas = [a for a in activos if a in precios.columns]
    sub = precios[columnas]
    rendimientos = calcular_rendimientos(sub)
    matriz_corr = calcular_matriz_correlacion(rendimientos)
    figura = crear_mapa_calor_correlacion(matriz_corr)
    return figura, len(rendimientos)


def invalidar_cache_correlacion() -> None:
    """Limpia la caché al cargar nuevos datos o cambiar la configuración."""
    from src.visualization.frontera_cache import invalidar_cache_frontera
    from src.visualization.resultados_cache import invalidar_cache_resultados
    from src.visualization.tabla_comparativa_cache import invalidar_cache_tabla_comparativa

    obtener_mapa_correlacion.clear()
    invalidar_cache_tabla_comparativa()
    invalidar_cache_frontera()
    invalidar_cache_resultados()
