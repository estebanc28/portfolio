"""Coherencia del Sharpe entre tabla comparativa y frontera eficiente."""

import numpy as np
import pandas as pd

from src.finance.frontera_eficiente import calcular_frontera_eficiente
from src.finance.portafolio import construir_tabla_comparativa


def _precios_ejemplo() -> pd.DataFrame:
    fechas = pd.date_range("2020-01-01", periods=60, freq="MS")
    rng = np.random.default_rng(99)
    columnas = {}
    for i, ticker in enumerate(["A", "B", "C", "D", "E"]):
        r = rng.normal(0.008 + i * 0.001, 0.04, 60)
        columnas[ticker] = 100 * np.cumprod(1 + r)
    return pd.DataFrame(columnas, index=fechas)


def test_sharpe_tabla_coincide_con_frontera():
    precios = _precios_ejemplo()
    tasa = 0.04

    tabla, m_igual, m_opt = construir_tabla_comparativa(precios, tasa)
    datos_frontera = calcular_frontera_eficiente(precios, tasa)

    assert np.isclose(m_igual.sharpe, datos_frontera.pesos_iguales_sharpe, rtol=1e-4)
    assert np.isclose(m_opt.sharpe, datos_frontera.optimizado_sharpe, rtol=1e-4)
