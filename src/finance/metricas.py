"""
Fase 2 — Backend de cálculos cuantitativos (métricas auxiliares).

Este módulo prepara las fórmulas de riesgo y rendimiento necesarias para el análisis
de portafolios. Corresponde a la Fase 2 del proyecto.

Importante: en esta fase NO se implementa optimización de Markowitz ni frontera eficiente.
Eso corresponde a una fase posterior (Fase 3).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Periodicidad de los datos del proyecto (precios mensuales)
MESES_POR_ANIO = 12


def calcular_rendimientos(precios: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula rendimientos históricos mensuales a partir de precios.

    Usa rendimientos simples: r_t = P_t / P_{t-1} - 1

    Parámetros
    ----------
    precios : pd.DataFrame
        Precios históricos con índice temporal (fechas) y una columna por activo.

    Retorna
    -------
    pd.DataFrame
        Rendimientos mensuales (sin la primera fila NaN).
    """
    if precios.empty:
        raise ValueError("El DataFrame de precios está vacío.")

    rendimientos = precios.pct_change()
    return rendimientos.dropna(how="all")


def _anualizar_rendimiento_multiplicativo(
    rendimientos_mensuales: pd.Series,
    meses_por_anio: int = MESES_POR_ANIO,
) -> float:
    """
    Anualiza el rendimiento esperado con capitalización compuesta.

    Fórmula (NO es multiplicar el promedio mensual por 12):
        r_anual = [ Π (1 + r_mensual) ]^(12 / n) - 1

    donde n es el número de observaciones mensuales.
    """
    if rendimientos_mensuales.empty:
        raise ValueError("La serie de rendimientos está vacía.")

    n = len(rendimientos_mensuales)
    producto_uno_mas_r = float((1.0 + rendimientos_mensuales).prod())
    return producto_uno_mas_r ** (meses_por_anio / n) - 1.0


def calcular_rendimiento_esperado_anualizado(
    rendimientos: pd.DataFrame | pd.Series,
    meses_por_anio: int = MESES_POR_ANIO,
) -> pd.Series | float:
    """
    Calcula el rendimiento esperado anualizado por activo (fórmula multiplicativa).

    Parámetros
    ----------
    rendimientos : pd.DataFrame | pd.Series
        Rendimientos mensuales históricos.
    meses_por_anio : int
        Factor de anualización (12 para datos mensuales).

    Retorna
    -------
    pd.Series | float
        Rendimiento anualizado por columna, o escalar si la entrada es una Serie.
    """
    if isinstance(rendimientos, pd.Series):
        return _anualizar_rendimiento_multiplicativo(rendimientos, meses_por_anio)

    if rendimientos.empty:
        raise ValueError("El DataFrame de rendimientos está vacío.")

    return rendimientos.apply(
        _anualizar_rendimiento_multiplicativo,
        meses_por_anio=meses_por_anio,
    )


def calcular_volatilidad_anualizada(
    rendimientos: pd.DataFrame | pd.Series,
    meses_por_anio: int = MESES_POR_ANIO,
    grados_libertad: int = 1,
) -> pd.Series | float:
    """
    Calcula la volatilidad anualizada (fórmula multiplicativa estándar).

    La volatilidad NO se obtiene multiplicando por 12, sino escalando con la raíz
    del número de periodos al año (supuesto de independencia mensual):

        σ_anual = σ_mensual × √(12)

    Parámetros
    ----------
    rendimientos : pd.DataFrame | pd.Series
        Rendimientos mensuales históricos.
    meses_por_anio : int
        Número de meses por año (12 en este proyecto).
    grados_libertad : int
        Grados de libertad para la desviación estándar muestral (default 1).

    Retorna
    -------
    pd.Series | float
        Volatilidad anualizada por activo, o escalar si la entrada es una Serie.
    """
    factor = float(np.sqrt(meses_por_anio))
    vol_mensual = rendimientos.std(ddof=grados_libertad)
    return vol_mensual * factor


def calcular_matriz_covarianza(
    rendimientos: pd.DataFrame,
    grados_libertad: int = 1,
) -> pd.DataFrame:
    """
    Calcula la matriz de covarianzas entre activos (base mensual).

    Parámetros
    ----------
    rendimientos : pd.DataFrame
        Rendimientos mensuales históricos.
    grados_libertad : int
        Grados de libertad para la covarianza muestral.

    Retorna
    -------
    pd.DataFrame
        Matriz de covarianzas (activos × activos).
    """
    if rendimientos.empty:
        raise ValueError("El DataFrame de rendimientos está vacío.")

    return rendimientos.cov()


def calcular_matriz_correlacion(rendimientos: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula la matriz de correlaciones entre activos.

    Parámetros
    ----------
    rendimientos : pd.DataFrame
        Rendimientos mensuales históricos.

    Retorna
    -------
    pd.DataFrame
        Matriz de correlaciones (activos × activos), valores entre -1 y 1.
    """
    if rendimientos.empty:
        raise ValueError("El DataFrame de rendimientos está vacío.")

    return rendimientos.corr()


def calcular_metricas_activos(
    precios: pd.DataFrame,
    meses_por_anio: int = MESES_POR_ANIO,
) -> pd.DataFrame:
    """
    Pipeline auxiliar de Fase 2: rendimientos y métricas anualizadas por activo.

    No incluye optimización. Útil para validar el backend antes de la Fase 3.

    Retorna un DataFrame con columnas:
        rendimiento_esperado_anual, volatilidad_anual
    """
    rendimientos = calcular_rendimientos(precios)
    retorno_anual = calcular_rendimiento_esperado_anualizado(rendimientos, meses_por_anio)
    vol_anual = calcular_volatilidad_anualizada(rendimientos, meses_por_anio)

    return pd.DataFrame(
        {
            "rendimiento_esperado_anual": retorno_anual,
            "volatilidad_anual": vol_anual,
        }
    )
