"""
Configuración del portafolio (Funcionalidad 1): validación y conversión de tasas.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.config import TASA_LIBRE_RIESGO_DEFAULT_ANUAL


@dataclass(frozen=True)
class ConfiguracionPortafolio:
    """Parámetros confirmados por el usuario para el análisis."""

    activos_seleccionados: list[str]
    pesos_forzados: dict[str, float]
    tasa_libre_riesgo_anual: float
    tasa_libre_riesgo_mensual: float


def anual_a_mensual(tasa_anual: float) -> float:
    """
    Convierte una tasa anual efectiva a tasa mensual equivalente.

    Fórmula: (1 + r_anual)^(1/12) - 1
    """
    return (1.0 + tasa_anual) ** (1.0 / 12.0) - 1.0


def validar_configuracion(
    activos_disponibles: list[str],
    activos_seleccionados: list[str],
    pesos_forzados: dict[str, float],
    tasa_libre_riesgo_anual: float,
) -> tuple[bool, str]:
    """
    Valida el universo de activos, pesos forzados y tasa libre de riesgo.

    Retorna (es_valida, mensaje_error).
    """
    if not activos_disponibles:
        return False, "No hay activos disponibles. Complete primero la carga de datos."

    if not activos_seleccionados:
        return False, "Debe incluir al menos un activo en el portafolio."

    disponibles = set(activos_disponibles)
    seleccionados = set(activos_seleccionados)

    if not seleccionados.issubset(disponibles):
        extra = seleccionados - disponibles
        return False, f"Activos no válidos: {', '.join(sorted(extra))}."

    if tasa_libre_riesgo_anual < 0 or tasa_libre_riesgo_anual > 1:
        return False, "La tasa libre de riesgo anual debe estar entre 0% y 100%."

    for ticker, peso in pesos_forzados.items():
        if ticker not in seleccionados:
            return (
                False,
                f"El peso forzado de {ticker} no aplica: el activo no está seleccionado.",
            )
        if peso <= 0 or peso > 1:
            return False, f"El peso forzado de {ticker} debe estar entre 0% y 100%."

    suma_pesos = sum(pesos_forzados.values())
    if suma_pesos > 1.0 + 1e-9:
        return (
            False,
            f"La suma de pesos forzados ({suma_pesos * 100:.2f}%) no puede superar el 100%.",
        )

    return True, ""


def construir_configuracion(
    activos_seleccionados: list[str],
    pesos_forzados: dict[str, float],
    tasa_libre_riesgo_anual: float | None = None,
) -> ConfiguracionPortafolio:
    """Crea la configuración con tasa mensual calculada automáticamente."""
    tasa_anual = (
        tasa_libre_riesgo_anual
        if tasa_libre_riesgo_anual is not None
        else TASA_LIBRE_RIESGO_DEFAULT_ANUAL
    )
    return ConfiguracionPortafolio(
        activos_seleccionados=list(activos_seleccionados),
        pesos_forzados=dict(pesos_forzados),
        tasa_libre_riesgo_anual=tasa_anual,
        tasa_libre_riesgo_mensual=anual_a_mensual(tasa_anual),
    )
