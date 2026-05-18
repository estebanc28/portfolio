"""Pruebas de resultados finales (pesos y evolución histórica)."""

import numpy as np
import pandas as pd

from src.finance.resultados import (
    VALOR_INICIAL_DEFECTO,
    calcular_evolucion_valor_acumulado,
    calcular_resultados_finales,
    construir_tabla_pesos_horizontal,
)
from src.finance.portafolio import UMBRAL_PESO_MINIMO, filtrar_y_renormalizar_pesos, pesos_iguales


def _precios_ejemplo() -> pd.DataFrame:
    fechas = pd.date_range("2020-01-01", periods=24, freq="MS")
    rng = np.random.default_rng(7)
    datos = {
        "A": 100 * np.cumprod(1 + rng.normal(0.01, 0.04, 24)),
        "B": 90 * np.cumprod(1 + rng.normal(0.008, 0.03, 24)),
        "C": 110 * np.cumprod(1 + rng.normal(0.012, 0.05, 24)),
        "^GSPC": 4000 * np.cumprod(1 + rng.normal(0.009, 0.02, 24)),
    }
    return pd.DataFrame(datos, index=fechas)


def test_tabla_omite_activos_con_peso_cero():
    pesos = pd.Series({"A": 0.6, "B": 0.4})
    tabla = construir_tabla_pesos_horizontal(["A", "B", "C"], ["A", "B"], pesos)
    assert "C" not in tabla.columns
    assert tabla.loc["Peso (%)", "A"] == "60.00%"
    assert tabla.loc["Peso (%)", "Total"] == "100.00%"


def test_evolucion_inicia_en_valor_inicial():
    precios = _precios_ejemplo()
    w = pesos_iguales(["A", "B"])
    serie = calcular_evolucion_valor_acumulado(precios, w, ["A", "B"], valor_inicial=1000.0)
    assert len(serie) == len(precios) - 1
    assert serie.iloc[0] != 0


def test_tabla_muestra_cero_si_peso_bajo_umbral():
    pesos = pd.Series({"A": 0.7, "B": 0.2997, "C": UMBRAL_PESO_MINIMO / 2})
    w_filtrado, _ = filtrar_y_renormalizar_pesos(
        pesos.values, ["A", "B", "C"], umbral=UMBRAL_PESO_MINIMO
    )
    pesos_filtrados = pd.Series(w_filtrado, index=["A", "B", "C"])
    tabla = construir_tabla_pesos_horizontal(["A", "B", "C"], ["A", "B", "C"], pesos_filtrados)
    assert "C" not in tabla.columns
    assert tabla.loc["Peso (%)", "Total"] == "100.00%"


def test_resultados_finales_tres_series():
    precios = _precios_ejemplo()
    datos = calcular_resultados_finales(
        precios,
        activos_validos=["A", "B", "C"],
        activos_seleccionados=["A", "B"],
        tasa_libre_riesgo_anual=0.04,
        valor_inicial=VALOR_INICIAL_DEFECTO,
    )
    assert datos.evolucion_benchmark is not None
    assert len(datos.evolucion_igual) == len(datos.evolucion_optimizado)
