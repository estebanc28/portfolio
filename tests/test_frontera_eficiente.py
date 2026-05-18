"""
Pruebas de la frontera eficiente.
"""

import numpy as np
import pandas as pd

from src.finance.frontera_eficiente import calcular_frontera_eficiente


def _precios_ejemplo() -> pd.DataFrame:
    fechas = pd.date_range("2020-01-01", periods=48, freq="MS")
    rng = np.random.default_rng(7)
    cols = {}
    for nombre in ("A", "B", "C"):
        r = rng.normal(0.009, 0.04, 48)
        cols[nombre] = 100 * np.cumprod(1 + r)
    return pd.DataFrame(cols, index=fechas)


def test_frontera_genera_puntos():
    datos = calcular_frontera_eficiente(_precios_ejemplo(), tasa_libre_riesgo_anual=0.04)
    assert len(datos.frontera) >= 5
    assert datos.optimizado_vol > 0
    assert len(datos.cml_sigmas) == len(datos.cml_rendimientos)


def test_cml_pasa_por_tasa_libre_riesgo():
    datos = calcular_frontera_eficiente(_precios_ejemplo(), 0.04)
    assert np.isclose(datos.cml_rendimientos[0], datos.tasa_libre_riesgo)


def test_cml_tangente_a_frontera_en_max_sharpe():
    datos = calcular_frontera_eficiente(_precios_ejemplo(), 0.04)
    rf = datos.tasa_libre_riesgo
    pendiente_cml = (datos.cml_rendimientos[-1] - rf) / datos.cml_sigmas[-1]
    pendiente_tang = (datos.optimizado_ret - rf) / datos.optimizado_vol
    assert np.isclose(pendiente_cml, pendiente_tang, rtol=1e-4)


def test_cml_extiende_hasta_doble_vol_tangente():
    datos = calcular_frontera_eficiente(_precios_ejemplo(), 0.04)
    assert np.isclose(datos.cml_sigmas[-1], datos.optimizado_vol * 2.0, rtol=1e-6)


def test_frontera_tiene_varios_puntos_ordenados_por_rendimiento():
    datos = calcular_frontera_eficiente(_precios_ejemplo(), 0.04)
    rets = [p.rendimiento for p in datos.frontera]
    assert rets == sorted(rets)
    assert len(datos.frontera) >= 10
