"""
Frontera eficiente (Markowitz) mediante optimización cuadrática con SciPy.

Alineado con el proyecto de referencia del curso:
- μ anual = (1 + promedio mensual)^12 - 1
- Frontera: minimizar varianza para cada rendimiento entre min(μ) y max(μ)
- CML: extensión hasta 2× la volatilidad del portafolio tangente
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from src.finance.metricas import (
    MESES_POR_ANIO,
    calcular_matriz_covarianza,
    calcular_rendimientos,
)
from src.finance.portafolio import filtrar_y_renormalizar_pesos, pesos_iguales


@dataclass(frozen=True)
class PuntoFrontera:
    """Punto riesgo–rendimiento sobre la frontera eficiente."""

    volatilidad: float
    rendimiento: float


@dataclass(frozen=True)
class DatosFronteraEficiente:
    """Resultados para graficar frontera, portafolios clave y CML."""

    frontera: list[PuntoFrontera]
    pesos_iguales_vol: float
    pesos_iguales_ret: float
    pesos_iguales_sharpe: float
    optimizado_vol: float
    optimizado_ret: float
    optimizado_sharpe: float
    tasa_libre_riesgo: float
    cml_sigmas: np.ndarray
    cml_rendimientos: np.ndarray


def _mu_sigma_grafico(rendimientos: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """
    μ y Σ para el gráfico (misma convención que el proyecto de referencia del curso).
    """
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


def _minimizar_varianza_retorno_objetivo(
    mu: np.ndarray,
    sigma: np.ndarray,
    retorno_objetivo: float,
    activos: list[str],
    pesos_forzados: dict[str, float],
) -> np.ndarray | None:
    """Portafolio de mínima varianza para un rendimiento esperado dado."""
    n = len(activos)
    indices_libres, forzados, suma_forzada = _indices_libres_forzados(activos, pesos_forzados)
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


def _optimizar_max_sharpe_mv(
    mu: np.ndarray,
    sigma: np.ndarray,
    tasa_libre_riesgo: float,
    activos: list[str],
    pesos_forzados: dict[str, float],
) -> np.ndarray | None:
    """Portafolio tangente: máxima razón de Sharpe en espacio Markowitz."""
    indices_libres, forzados, _ = _indices_libres_forzados(activos, pesos_forzados)
    restante = max(0.0, 1.0 - sum(forzados.values()))

    if not indices_libres:
        return _pesos_desde_libres(activos, np.array([]), [], forzados)

    x0 = np.full(len(indices_libres), restante / len(indices_libres))

    def neg_sharpe(x: np.ndarray) -> float:
        w = _pesos_desde_libres(activos, x, indices_libres, forzados)
        vol = float(np.sqrt(max(w @ sigma @ w, 0.0)))
        if vol < 1e-10:
            return 1e6
        return -(float(w @ mu) - tasa_libre_riesgo) / vol

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
        w_igual = pesos_iguales(activos, forzados)
        return w_igual

    return _pesos_desde_libres(activos, resultado.x, indices_libres, forzados)


def _riesgo_rendimiento_mv(
    pesos: np.ndarray,
    mu: np.ndarray,
    sigma: np.ndarray,
) -> PuntoFrontera:
    ret = float(pesos @ mu)
    vol = float(np.sqrt(max(pesos @ sigma @ pesos, 0.0)))
    return PuntoFrontera(volatilidad=vol, rendimiento=ret)


def calcular_frontera_eficiente(
    precios: pd.DataFrame,
    tasa_libre_riesgo_anual: float,
    pesos_forzados: dict[str, float] | None = None,
    n_puntos: int = 100,
) -> DatosFronteraEficiente:
    """
    Calcula la frontera (μ–Σ) y la CML tangente al máximo Sharpe.
    """
    rendimientos = calcular_rendimientos(precios)
    activos = list(rendimientos.columns)
    forzados = pesos_forzados or {}
    mu, sigma = _mu_sigma_grafico(rendimientos)

    # Mismo criterio que el proyecto de referencia: de min(μ) a max(μ) por activo
    ret_min = float(mu.min())
    ret_max = float(mu.max())
    objetivos = np.linspace(ret_min, ret_max, n_puntos)

    frontera: list[PuntoFrontera] = []
    for ret_obj in objetivos:
        w = _minimizar_varianza_retorno_objetivo(mu, sigma, float(ret_obj), activos, forzados)
        if w is not None:
            frontera.append(_riesgo_rendimiento_mv(w, mu, sigma))

    if not frontera:
        raise ValueError("No se generaron puntos para la frontera eficiente.")

    w_tang = _optimizar_max_sharpe_mv(mu, sigma, tasa_libre_riesgo_anual, activos, forzados)
    if w_tang is None:
        raise ValueError("No se pudo calcular el portafolio de máximo Sharpe.")

    w_tang, _ = filtrar_y_renormalizar_pesos(w_tang, activos, pesos_forzados=forzados)

    w_igual = pesos_iguales(activos, forzados)
    p_igual = _riesgo_rendimiento_mv(w_igual, mu, sigma)
    p_tang = _riesgo_rendimiento_mv(w_tang, mu, sigma)

    rf = tasa_libre_riesgo_anual
    sigma_t = p_tang.volatilidad
    ret_t = p_tang.rendimiento

    def _sharpe_mv(ret: float, vol: float) -> float:
        if vol > 1e-10:
            return (ret - rf) / vol
        return float("nan")

    sharpe_igual = _sharpe_mv(p_igual.rendimiento, p_igual.volatilidad)
    sharpe_opt = _sharpe_mv(p_tang.rendimiento, p_tang.volatilidad)

    if sigma_t > 1e-8:
        pendiente = (ret_t - rf) / sigma_t
    else:
        pendiente = 0.0

    # CML extendida como en el proyecto de referencia (2× vol del portafolio tangente)
    vol_cml_max = max(sigma_t * 2.0, 0.01)
    cml_sigmas = np.linspace(0.0, vol_cml_max, 100)
    cml_rendimientos = rf + pendiente * cml_sigmas

    return DatosFronteraEficiente(
        frontera=frontera,
        pesos_iguales_vol=p_igual.volatilidad,
        pesos_iguales_ret=p_igual.rendimiento,
        pesos_iguales_sharpe=sharpe_igual,
        optimizado_vol=p_tang.volatilidad,
        optimizado_ret=p_tang.rendimiento,
        optimizado_sharpe=sharpe_opt,
        tasa_libre_riesgo=rf,
        cml_sigmas=cml_sigmas,
        cml_rendimientos=cml_rendimientos,
    )
