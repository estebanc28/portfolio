"""
Resultados finales: tabla de pesos optimizados y evolución histórica acumulada.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.finance.metricas import calcular_rendimientos
from src.finance.portafolio import (
    filtrar_y_renormalizar_pesos,
    optimizar_max_sharpe,
    pesos_iguales,
)

VALOR_INICIAL_DEFECTO = 1000.0


@dataclass(frozen=True)
class DatosResultadosFinales:
    """Salidas para la Funcionalidad 4."""

    tabla_pesos: pd.DataFrame
    pesos_iguales: pd.Series
    pesos_optimizados: pd.Series
    activos_seleccionados: list[str]
    activos_no_utilizados: list[str]
    evolucion_igual: pd.Series
    evolucion_optimizado: pd.Series
    evolucion_benchmark: pd.Series | None


def _pesos_en_universo(
    activos_validos: list[str],
    activos_seleccionados: list[str],
    pesos_seleccionados: pd.Series,
) -> pd.Series:
    """Expande pesos del subconjunto seleccionado al universo completo (0 fuera de selección)."""
    seleccionados = set(activos_seleccionados)
    valores = {
        ticker: float(pesos_seleccionados.get(ticker, 0.0)) if ticker in seleccionados else 0.0
        for ticker in activos_validos
    }
    return pd.Series(valores, name="peso")


def construir_tabla_pesos_horizontal(
    activos_validos: list[str],
    activos_seleccionados: list[str],
    pesos_optimizados: pd.Series,
) -> pd.DataFrame:
    """
    Tabla horizontal: una fila solo con activos cuyo peso final es distinto de 0 %.
    """
    pesos_completos = _pesos_en_universo(
        activos_validos, activos_seleccionados, pesos_optimizados
    )
    fila = {
        ticker: f"{pesos_completos[ticker] * 100:.2f}%"
        for ticker in sorted(activos_validos)
        if pesos_completos[ticker] > 0
    }
    fila["Total"] = f"{pesos_completos.sum() * 100:.2f}%"
    return pd.DataFrame([fila], index=["Peso (%)"])


def calcular_evolucion_valor_acumulado(
    precios: pd.DataFrame,
    pesos: np.ndarray | pd.Series,
    activos: list[str],
    valor_inicial: float = VALOR_INICIAL_DEFECTO,
) -> pd.Series:
    """
    Valor acumulado del portafolio: V_t = V_0 * prod(1 + r_p,t).
    """
    columnas = [a for a in activos if a in precios.columns]
    if not columnas:
        raise ValueError("No hay precios para los activos indicados.")

    if isinstance(pesos, pd.Series):
        w = np.array([float(pesos[c]) for c in columnas], dtype=float)
    else:
        w = np.asarray(pesos, dtype=float)

    rendimientos = calcular_rendimientos(precios[columnas])
    retorno_portafolio = rendimientos.values @ w
    acumulado = valor_inicial * (1 + pd.Series(retorno_portafolio, index=rendimientos.index)).cumprod()
    acumulado.name = "valor_acumulado"
    return acumulado


def calcular_evolucion_benchmark(
    precios: pd.DataFrame,
    ticker_benchmark: str,
    valor_inicial: float = VALOR_INICIAL_DEFECTO,
) -> pd.Series | None:
    """Evolución acumulada del benchmark (p. ej. S&P 500)."""
    if ticker_benchmark not in precios.columns:
        return None

    rendimientos = calcular_rendimientos(precios[[ticker_benchmark]])
    serie_r = rendimientos[ticker_benchmark]
    evolucion = valor_inicial * (1 + serie_r).cumprod()
    evolucion.name = "valor_acumulado"
    return evolucion


def calcular_resultados_finales(
    precios: pd.DataFrame,
    activos_validos: list[str],
    activos_seleccionados: list[str],
    tasa_libre_riesgo_anual: float,
    pesos_forzados: dict[str, float] | None = None,
    ticker_benchmark: str = "^GSPC",
    valor_inicial: float = VALOR_INICIAL_DEFECTO,
) -> DatosResultadosFinales:
    """Calcula tabla de pesos y series de valor acumulado para la Funcionalidad 4."""
    seleccionados = [a for a in activos_seleccionados if a in precios.columns]
    if len(seleccionados) < 1:
        raise ValueError("Se requiere al menos un activo seleccionado con precios disponibles.")

    forzados = {k: v for k, v in (pesos_forzados or {}).items() if k in seleccionados}
    precios_sel = precios[seleccionados]
    rendimientos = calcular_rendimientos(precios_sel)

    w_igual = pesos_iguales(seleccionados, forzados)
    w_opt = optimizar_max_sharpe(rendimientos, tasa_libre_riesgo_anual, forzados)
    w_opt, no_utilizados = filtrar_y_renormalizar_pesos(
        w_opt, seleccionados, pesos_forzados=forzados
    )

    pesos_igual_serie = pd.Series(w_igual, index=seleccionados, name="peso")
    pesos_opt_serie = pd.Series(w_opt, index=seleccionados, name="peso")
    tabla = construir_tabla_pesos_horizontal(activos_validos, seleccionados, pesos_opt_serie)

    ev_igual = calcular_evolucion_valor_acumulado(precios_sel, w_igual, seleccionados, valor_inicial)
    ev_opt = calcular_evolucion_valor_acumulado(precios_sel, w_opt, seleccionados, valor_inicial)
    ev_bench = calcular_evolucion_benchmark(precios, ticker_benchmark, valor_inicial)

    return DatosResultadosFinales(
        tabla_pesos=tabla,
        pesos_iguales=pesos_igual_serie,
        pesos_optimizados=pesos_opt_serie,
        activos_seleccionados=seleccionados,
        activos_no_utilizados=no_utilizados,
        evolucion_igual=ev_igual,
        evolucion_optimizado=ev_opt,
        evolucion_benchmark=ev_bench,
    )
