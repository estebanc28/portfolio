"""
Pruebas del backend cuantitativo — Fase 2 (sin optimización).
"""

import numpy as np
import pandas as pd

from src.finance.metricas import (
    calcular_matriz_correlacion,
    calcular_matriz_covarianza,
    calcular_rendimiento_esperado_anualizado,
    calcular_rendimientos,
    calcular_volatilidad_anualizada,
)


def _precios_ejemplo() -> pd.DataFrame:
    fechas = pd.date_range("2020-01-01", periods=24, freq="MS")
    return pd.DataFrame(
        {
            "A": 100 * (1.01 ** np.arange(24)),
            "B": 50 * (1.005 ** np.arange(24)),
        },
        index=fechas,
    )


def test_calcular_rendimientos():
    rend = calcular_rendimientos(_precios_ejemplo())
    assert rend.shape[0] == 23
    assert list(rend.columns) == ["A", "B"]


def test_rendimiento_anualizado_no_es_promedio_por_12():
    precios = _precios_ejemplo()
    rend = calcular_rendimientos(precios)
    anual = calcular_rendimiento_esperado_anualizado(rend["A"])
    naive = rend["A"].mean() * 12
  # Con capitalización, el valor anualizado difiere del "× 12" ingenuo
    assert not np.isclose(anual, naive, rtol=1e-6)


def test_volatilidad_anualizada_usa_raiz_12():
    rend = calcular_rendimientos(_precios_ejemplo())
    vol_anual = calcular_volatilidad_anualizada(rend["A"])
    vol_mensual = rend["A"].std(ddof=1)
    assert np.isclose(vol_anual, vol_mensual * np.sqrt(12))


def test_matrices_covarianza_y_correlacion():
    rend = calcular_rendimientos(_precios_ejemplo())
    cov = calcular_matriz_covarianza(rend)
    corr = calcular_matriz_correlacion(rend)
    assert cov.shape == (2, 2)
    assert corr.shape == (2, 2)
    assert np.allclose(np.diag(corr), 1.0)
