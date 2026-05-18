"""
Cálculo de pesos y métricas de portafolio (pesos iguales y optimización Markowitz).

Optimización de máxima razón de Sharpe con SciPy, respetando pesos forzados del usuario.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.finance.markowitz import (
    calcular_metricas_mv,
    calcular_mu_sigma_anual,
    optimizar_max_sharpe_mv,
)
from src.finance.metricas import (
    MESES_POR_ANIO,
    calcular_rendimiento_esperado_anualizado,
    calcular_rendimientos,
    calcular_volatilidad_anualizada,
)

# Pesos menores a este umbral (0,1 %) se tratan como 0 en el portafolio final
UMBRAL_PESO_MINIMO = 0.001


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


def optimizar_max_sharpe(
    rendimientos: pd.DataFrame,
    tasa_libre_riesgo_anual: float,
    pesos_forzados: dict[str, float] | None = None,
) -> np.ndarray:
    """
    Maximiza la razón de Sharpe (anual) en espacio μ–Σ (misma lógica que la frontera).
    """
    activos = list(rendimientos.columns)
    if not activos:
        raise ValueError("No hay activos para optimizar.")

    forzados = {k: v for k, v in (pesos_forzados or {}).items() if k in activos}
    if sum(forzados.values()) > 1.0 + 1e-9:
        raise ValueError("La suma de pesos forzados supera el 100%.")

    mu, sigma = calcular_mu_sigma_anual(rendimientos)
    return optimizar_max_sharpe_mv(mu, sigma, tasa_libre_riesgo_anual, activos, forzados)


def filtrar_y_renormalizar_pesos(
    pesos: np.ndarray | pd.Series,
    activos: list[str],
    umbral: float = UMBRAL_PESO_MINIMO,
    pesos_forzados: dict[str, float] | None = None,
) -> tuple[np.ndarray, list[str]]:
    """
    Elimina posiciones con peso < umbral (salvo pesos fijos del usuario) y renormaliza a 1.

    Retorna el vector de pesos ajustado y la lista de tickers descartados por umbral.
    """
    forzados = pesos_forzados or {}
    forzados_set = set(forzados.keys())
    n = len(activos)

    if isinstance(pesos, pd.Series):
        w = np.array([float(pesos.get(t, 0.0)) for t in activos], dtype=float)
    else:
        w = np.asarray(pesos, dtype=float).copy()

    if len(w) != n:
        raise ValueError("La longitud de pesos no coincide con la lista de activos.")

    descartados: list[str] = []
    for i, ticker in enumerate(activos):
        if ticker in forzados_set:
            w[i] = float(forzados[ticker])
            continue
        if w[i] < umbral:
            if w[i] > 1e-12:
                descartados.append(ticker)
            w[i] = 0.0

    suma_forzada = sum(w[i] for i, t in enumerate(activos) if t in forzados_set)
    indices_libres = [
        i for i, t in enumerate(activos) if t not in forzados_set and w[i] >= umbral
    ]
    suma_libre = float(w[indices_libres].sum()) if indices_libres else 0.0

    restante = max(0.0, 1.0 - suma_forzada)
    if indices_libres and suma_libre > 0:
        w[indices_libres] = w[indices_libres] * (restante / suma_libre)
    elif w.sum() > 0:
        w = w / w.sum()

    if w.sum() <= 0:
        raise ValueError("Tras aplicar el umbral mínimo no quedó ningún activo en el portafolio.")

    return w, descartados


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

    mu, sigma = calcular_mu_sigma_anual(rendimientos)

    w_igual = pesos_iguales(activos, forzados)
    w_opt = optimizar_max_sharpe(rendimientos, tasa_libre_riesgo_anual, forzados)
    w_opt, _ = filtrar_y_renormalizar_pesos(w_opt, activos, pesos_forzados=forzados)

    ret_i, vol_i, sharpe_i = calcular_metricas_mv(
        w_igual, mu, sigma, tasa_libre_riesgo_anual
    )
    ret_o, vol_o, sharpe_o = calcular_metricas_mv(
        w_opt, mu, sigma, tasa_libre_riesgo_anual
    )

    m_igual = MetricasPortafolio(
        rendimiento_anual=ret_i,
        volatilidad_anual=vol_i,
        sharpe=sharpe_i,
        pesos=pd.Series(w_igual, index=activos, name="peso"),
    )
    m_opt = MetricasPortafolio(
        rendimiento_anual=ret_o,
        volatilidad_anual=vol_o,
        sharpe=sharpe_o,
        pesos=pd.Series(w_opt, index=activos, name="peso"),
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
