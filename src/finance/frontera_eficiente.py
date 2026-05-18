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

from src.finance.markowitz import (
    calcular_metricas_mv,
    calcular_mu_sigma_anual,
    minimizar_varianza_retorno_objetivo,
    optimizar_max_sharpe_mv,
)
from src.finance.metricas import calcular_rendimientos
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


def _riesgo_rendimiento_mv(
    pesos: np.ndarray,
    mu: np.ndarray,
    sigma: np.ndarray,
) -> PuntoFrontera:
    ret, vol, _ = calcular_metricas_mv(pesos, mu, sigma, 0.0)
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
    mu, sigma = calcular_mu_sigma_anual(rendimientos)

    ret_min = float(mu.min())
    ret_max = float(mu.max())
    objetivos = np.linspace(ret_min, ret_max, n_puntos)

    frontera: list[PuntoFrontera] = []
    for ret_obj in objetivos:
        w = minimizar_varianza_retorno_objetivo(
            mu, sigma, float(ret_obj), activos, forzados
        )
        if w is not None:
            frontera.append(_riesgo_rendimiento_mv(w, mu, sigma))

    if not frontera:
        raise ValueError("No se generaron puntos para la frontera eficiente.")

    w_tang = optimizar_max_sharpe_mv(mu, sigma, tasa_libre_riesgo_anual, activos, forzados)
    w_tang, _ = filtrar_y_renormalizar_pesos(w_tang, activos, pesos_forzados=forzados)

    w_igual = pesos_iguales(activos, forzados)
    ret_i, vol_i, sharpe_igual = calcular_metricas_mv(
        w_igual, mu, sigma, tasa_libre_riesgo_anual
    )
    ret_o, vol_o, sharpe_opt = calcular_metricas_mv(
        w_tang, mu, sigma, tasa_libre_riesgo_anual
    )

    rf = tasa_libre_riesgo_anual
    if vol_o > 1e-8:
        pendiente = (ret_o - rf) / vol_o
    else:
        pendiente = 0.0

    vol_cml_max = max(vol_o * 2.0, 0.01)
    cml_sigmas = np.linspace(0.0, vol_cml_max, 100)
    cml_rendimientos = rf + pendiente * cml_sigmas

    return DatosFronteraEficiente(
        frontera=frontera,
        pesos_iguales_vol=vol_i,
        pesos_iguales_ret=ret_i,
        pesos_iguales_sharpe=sharpe_igual,
        optimizado_vol=vol_o,
        optimizado_ret=ret_o,
        optimizado_sharpe=sharpe_opt,
        tasa_libre_riesgo=rf,
        cml_sigmas=cml_sigmas,
        cml_rendimientos=cml_rendimientos,
    )
