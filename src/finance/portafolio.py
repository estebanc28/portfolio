"""
Cálculo de pesos y métricas de portafolio (pesos iguales y optimización Markowitz).

Optimización de máxima razón de Sharpe con SciPy, respetando pesos forzados del usuario.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from src.finance.metricas import (
    MESES_POR_ANIO,
    calcular_rendimiento_esperado_anualizado,
    calcular_rendimientos,
    calcular_volatilidad_anualizada,
)


@dataclass(frozen=True)
class MetricasPortafolio:
    """Métricas anualizadas de un portafolio con pesos fijos."""

    rendimiento_anual: float
    volatilidad_anual: float
    sharpe: float
    pesos: pd.Series


def pesos_iguales(
    activos: list[str],
    pesos_forzados: dict[str, float] | None = None,
) -> np.ndarray:
    """
    Asigna pesos iguales entre activos libres; respeta pesos forzados previos.
    """
    forzados = pesos_forzados or {}
    n = len(activos)
    pesos = np.zeros(n, dtype=float)

    for i, ticker in enumerate(activos):
        if ticker in forzados:
            pesos[i] = forzados[ticker]

    suma_forzada = float(pesos.sum())
    libres = [i for i, ticker in enumerate(activos) if ticker not in forzados]

    if libres:
        restante = max(0.0, 1.0 - suma_forzada)
        pesos[libres] = restante / len(libres)

    total = pesos.sum()
    if total > 0 and not np.isclose(total, 1.0):
        pesos = pesos / total

    return pesos


def _rendimientos_portafolio(
    rendimientos: pd.DataFrame,
    pesos: np.ndarray,
) -> pd.Series:
    """Serie mensual de rendimientos del portafolio."""
    return pd.Series(rendimientos.values @ pesos, index=rendimientos.index, name="portafolio")


def calcular_metricas_portafolio(
    rendimientos: pd.DataFrame,
    pesos: np.ndarray,
    tasa_libre_riesgo_anual: float,
    activos: list[str] | None = None,
) -> MetricasPortafolio:
    """Calcula rendimiento, volatilidad y Sharpe anualizados del portafolio."""
    etiquetas = activos if activos is not None else list(rendimientos.columns)
    serie = _rendimientos_portafolio(rendimientos, pesos)

    rendimiento = float(calcular_rendimiento_esperado_anualizado(serie))
    volatilidad = float(calcular_volatilidad_anualizada(serie))

    if volatilidad > 0:
        sharpe = (rendimiento - tasa_libre_riesgo_anual) / volatilidad
    else:
        sharpe = float("nan")

    return MetricasPortafolio(
        rendimiento_anual=rendimiento,
        volatilidad_anual=volatilidad,
        sharpe=sharpe,
        pesos=pd.Series(pesos, index=etiquetas, name="peso"),
    )


def _construir_pesos_completos(
    activos: list[str],
    pesos_libres: np.ndarray,
    indices_libres: list[int],
    pesos_forzados: dict[str, float],
) -> np.ndarray:
    n = len(activos)
    pesos = np.zeros(n, dtype=float)
    for ticker, valor in pesos_forzados.items():
        if ticker in activos:
            pesos[activos.index(ticker)] = valor
    for j, idx in enumerate(indices_libres):
        pesos[idx] = pesos_libres[j]
    return pesos


def optimizar_max_sharpe(
    rendimientos: pd.DataFrame,
    tasa_libre_riesgo_anual: float,
    pesos_forzados: dict[str, float] | None = None,
) -> np.ndarray:
    """
    Maximiza la razón de Sharpe (anual) con restricciones long-only y suma = 1.
    """
    activos = list(rendimientos.columns)
    forzados = {k: v for k, v in (pesos_forzados or {}).items() if k in activos}
    n = len(activos)

    if n == 0:
        raise ValueError("No hay activos para optimizar.")

    indices_forzados = {activos.index(t) for t in forzados}
    indices_libres = [i for i in range(n) if i not in indices_forzados]
    suma_forzada = sum(forzados.values())

    if suma_forzada > 1.0 + 1e-9:
        raise ValueError("La suma de pesos forzados supera el 100%.")

    # Sin grados de libertad: solo retornar los pesos forzados normalizados
    if not indices_libres:
        pesos = np.array([forzados.get(a, 0.0) for a in activos])
        total = pesos.sum()
        return pesos / total if total > 0 else pesos

    if len(indices_libres) == 1:
        pesos = np.zeros(n)
        for t, v in forzados.items():
            pesos[activos.index(t)] = v
        pesos[indices_libres[0]] = max(0.0, 1.0 - suma_forzada)
        return pesos

    restante = max(0.0, 1.0 - suma_forzada)
    x0 = np.full(len(indices_libres), restante / len(indices_libres))
    bounds = [(0.0, 1.0)] * len(indices_libres)

    def objetivo(x: np.ndarray) -> float:
        w = _construir_pesos_completos(activos, x, indices_libres, forzados)
        metricas = calcular_metricas_portafolio(
            rendimientos, w, tasa_libre_riesgo_anual, activos=activos
        )
        if np.isnan(metricas.sharpe):
            return 1e6
        return -metricas.sharpe

    restricciones = [
        {"type": "eq", "fun": lambda x: float(np.sum(x) - restante)},
    ]

    resultado = minimize(
        objetivo,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=restricciones,
        options={"maxiter": 500, "ftol": 1e-9},
    )

    if not resultado.success:
        # Respaldo: pesos iguales entre activos libres
        return pesos_iguales(activos, forzados)

    return _construir_pesos_completos(activos, resultado.x, indices_libres, forzados)


def construir_tabla_comparativa(
    precios: pd.DataFrame,
    tasa_libre_riesgo_anual: float,
    pesos_forzados: dict[str, float] | None = None,
) -> tuple[pd.DataFrame, MetricasPortafolio, MetricasPortafolio]:
    """
    Genera la tabla comparativa entre portafolio de pesos iguales y optimizado.

    Retorna (tabla_formateada, metricas_iguales, metricas_optimizado).
    """
    rendimientos = calcular_rendimientos(precios)
    activos = list(rendimientos.columns)
    forzados = pesos_forzados or {}

    w_igual = pesos_iguales(activos, forzados)
    w_opt = optimizar_max_sharpe(rendimientos, tasa_libre_riesgo_anual, forzados)

    m_igual = calcular_metricas_portafolio(
        rendimientos, w_igual, tasa_libre_riesgo_anual, activos=activos
    )
    m_opt = calcular_metricas_portafolio(
        rendimientos, w_opt, tasa_libre_riesgo_anual, activos=activos
    )

    tabla = pd.DataFrame(
        {
            "Métrica": [
                "Rendimiento Esperado (Anual)",
                "Volatilidad (Anual)",
                "Ratio de Sharpe",
            ],
            "Pesos Iguales": [
                _formatear_porcentaje(m_igual.rendimiento_anual),
                _formatear_porcentaje(m_igual.volatilidad_anual),
                _formatear_sharpe(m_igual.sharpe),
            ],
            "Portafolio Optimizado": [
                _formatear_porcentaje(m_opt.rendimiento_anual),
                _formatear_porcentaje(m_opt.volatilidad_anual),
                _formatear_sharpe(m_opt.sharpe),
            ],
        }
    )

    return tabla, m_igual, m_opt


def _formatear_porcentaje(valor: float) -> str:
    return f"{valor * 100:.2f}%"


def _formatear_sharpe(valor: float) -> str:
    if np.isnan(valor):
        return "—"
    return f"{valor:.3f}"
