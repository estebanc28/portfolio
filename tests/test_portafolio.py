"""
Pruebas de pesos y métricas de portafolio.
"""

import numpy as np
import pandas as pd

from src.finance.portafolio import (
    calcular_metricas_portafolio,
    construir_tabla_comparativa,
    optimizar_max_sharpe,
    pesos_iguales,
)
from src.finance.metricas import calcular_rendimientos


def _precios_ejemplo() -> pd.DataFrame:
    fechas = pd.date_range("2020-01-01", periods=36, freq="MS")
    rng = np.random.default_rng(42)
    r_a = rng.normal(0.01, 0.05, 36)
    r_b = rng.normal(0.008, 0.04, 36)
    precios_a = 100 * np.cumprod(1 + r_a)
    precios_b = 80 * np.cumprod(1 + r_b)
    return pd.DataFrame({"A": precios_a, "B": precios_b}, index=fechas)


def test_pesos_iguales_suman_uno():
    activos = ["A", "B", "C"]
    w = pesos_iguales(activos, {"A": 0.2})
    assert np.isclose(w.sum(), 1.0)
    assert np.isclose(w[0], 0.2)
    assert np.isclose(w[1], 0.4)
    assert np.isclose(w[2], 0.4)


def test_pesos_iguales_sin_forzados():
    w = pesos_iguales(["A", "B"])
    assert np.allclose(w, [0.5, 0.5])


def test_optimizar_respeta_pesos_forzados():
    precios = _precios_ejemplo()
    rend = calcular_rendimientos(precios)
    w = optimizar_max_sharpe(rend, tasa_libre_riesgo_anual=0.04, pesos_forzados={"A": 0.3})
    assert np.isclose(w.sum(), 1.0)
    assert np.isclose(w[0], 0.3)
    assert w[1] >= 0


def test_metricas_portafolio_sharpe():
    precios = _precios_ejemplo()
    rend = calcular_rendimientos(precios)
    w = np.array([0.5, 0.5])
    m = calcular_metricas_portafolio(rend, w, tasa_libre_riesgo_anual=0.04)
    esperado = (m.rendimiento_anual - 0.04) / m.volatilidad_anual
    assert np.isclose(m.sharpe, esperado)


def test_tabla_comparativa_tiene_filas_esperadas():
    tabla, _, _ = construir_tabla_comparativa(_precios_ejemplo(), 0.04)
    assert len(tabla) == 3
    assert "Pesos Iguales" in tabla.columns
    assert "Portafolio Optimizado" in tabla.columns
