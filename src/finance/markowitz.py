"""
Métricas y optimización en espacio μ–Σ (Markowitz).

Convención alineada con la frontera eficiente del curso:
- μ anual por activo: (1 + promedio mensual)^12 - 1
- Σ anual: covarianza mensual × 12
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from src.finance.metricas import MESES_POR_ANIO, calcular_matriz_covarianza


def calcular_mu_sigma_anual(rendimientos: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Vectores μ y matriz Σ anualizados para optimización y métricas."""
    media_mensual = rendimientos.mean()
    mu = ((1.0 + media_mensual) ** MESES_POR_ANIO - 1.0).values.astype(float)
    cov_mensual = calcular_matriz_covarianza(rendimientos).values.astype(float)
    sigma = cov_mensual * MESES_POR_ANIO
    return mu, sigma


def _indices_libres_forzados(
    activos: list[str],
    pesos_forzados: dict[str, float],
) -> tuple[list[int], dict[str, float], float]:
    forzados = {k: v for k, v in pesos_forzados.items() if k in activos}
    indices_libres = [i for i in range(len(activos)) if activos[i] not in forzados]
    suma_forzada = float(sum(forzados.values()))
    return indices_libres, forzados, suma_forzada


def _pesos_desde_libres(
    activos: list[str],
    x: np.ndarray,
    indices_libres: list[int],
    forzados: dict[str, float],
) -> np.ndarray:
    n = len(activos)
    pesos = np.zeros(n, dtype=float)
    for ticker, valor in forzados.items():
        pesos[activos.index(ticker)] = valor
    for j, idx in enumerate(indices_libres):
        pesos[idx] = x[j]
    return pesos


def calcular_metricas_mv(
    pesos: np.ndarray,
    mu: np.ndarray,
    sigma: np.ndarray,
    tasa_libre_riesgo_anual: float,
) -> tuple[float, float, float]:
    """Rendimiento, volatilidad y Sharpe anualizados en espacio μ–Σ."""
    rendimiento = float(pesos @ mu)
    volatilidad = float(np.sqrt(max(pesos @ sigma @ pesos, 0.0)))
    if volatilidad > 1e-10:
        sharpe = (rendimiento - tasa_libre_riesgo_anual) / volatilidad
    else:
        sharpe = float("nan")
    return rendimiento, volatilidad, sharpe


def optimizar_max_sharpe_mv(
    mu: np.ndarray,
    sigma: np.ndarray,
    tasa_libre_riesgo_anual: float,
    activos: list[str],
    pesos_forzados: dict[str, float] | None = None,
) -> np.ndarray:
    """Portafolio de máxima razón de Sharpe (Markowitz)."""
    forzados = pesos_forzados or {}
    indices_libres, forzados, _ = _indices_libres_forzados(activos, forzados)
    restante = max(0.0, 1.0 - sum(forzados.values()))

    if not indices_libres:
        return _pesos_desde_libres(activos, np.array([]), [], forzados)

    x0 = np.full(len(indices_libres), restante / len(indices_libres))

    def neg_sharpe(x: np.ndarray) -> float:
        w = _pesos_desde_libres(activos, x, indices_libres, forzados)
        vol = float(np.sqrt(max(w @ sigma @ w, 0.0)))
        if vol < 1e-10:
            return 1e6
        return -(float(w @ mu) - tasa_libre_riesgo_anual) / vol

    restricciones = [{"type": "eq", "fun": lambda x: float(np.sum(x) - restante)}]
    bounds = [(0.0, 1.0)] * len(indices_libres)

    resultado = minimize(
        neg_sharpe,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=restricciones,
        options={"maxiter": 600, "ftol": 1e-10},
    )

    if not resultado.success:
        from src.finance.portafolio import pesos_iguales

        return pesos_iguales(activos, forzados)

    return _pesos_desde_libres(activos, resultado.x, indices_libres, forzados)


def minimizar_varianza_retorno_objetivo(
    mu: np.ndarray,
    sigma: np.ndarray,
    retorno_objetivo: float,
    activos: list[str],
    pesos_forzados: dict[str, float] | None = None,
) -> np.ndarray | None:
    """Portafolio de mínima varianza para un rendimiento esperado dado."""
    forzados = pesos_forzados or {}
    indices_libres, forzados, suma_forzada = _indices_libres_forzados(activos, forzados)
    restante = max(0.0, 1.0 - suma_forzada)

    if not indices_libres:
        w = _pesos_desde_libres(activos, np.array([]), [], forzados)
        if abs(float(w @ mu) - retorno_objetivo) < 1e-6:
            return w
        return None

    x0 = np.full(len(indices_libres), restante / len(indices_libres))

    def varianza(x: np.ndarray) -> float:
        w = _pesos_desde_libres(activos, x, indices_libres, forzados)
        return float(w @ sigma @ w)

    restricciones = [
        {"type": "eq", "fun": lambda x: float(np.sum(x) - restante)},
        {
            "type": "eq",
            "fun": lambda x, target=retorno_objetivo: float(
                _pesos_desde_libres(activos, x, indices_libres, forzados) @ mu - target
            ),
        },
    ]
    bounds = [(0.0, 1.0)] * len(indices_libres)

    resultado = minimize(
        varianza,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=restricciones,
        options={"maxiter": 600, "ftol": 1e-10},
    )

    if not resultado.success:
        return None

    return _pesos_desde_libres(activos, resultado.x, indices_libres, forzados)
