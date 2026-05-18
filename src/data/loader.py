"""
Funcionalidad 0: carga y preparación de datos del portafolio.
"""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.config import COLUMNA_FECHA, RUTA_CSV_DEFECTO, TICKER_BENCHMARK

# Registros mensuales esperados según el dataset del proyecto
REGISTROS_MENSUALES_ESPERADOS = 60


@dataclass(frozen=True)
class ResultadoCargaDatos:
    """Resultado de la carga y validación del CSV de precios."""

    precios: pd.DataFrame
    activos_validos: list[str]
    benchmark: str
    activos_excluidos: list[str]
    mensajes: list[str]
    ruta_csv: Path
    nombre_archivo: str


def _mensaje_activo_omitido(ticker: str) -> str:
    return f"Se omitió la empresa {ticker} por datos incompletos."


def _validar_dataframe(
    df: pd.DataFrame,
    ruta_referencia: Path,
    nombre_archivo: str | None = None,
) -> ResultadoCargaDatos:
    """Valida y limpia un DataFrame de precios ya leído desde CSV."""
    if COLUMNA_FECHA not in df.columns:
        raise ValueError(
            f"El CSV debe incluir la columna '{COLUMNA_FECHA}' con las fechas."
        )

    df = df.copy()
    df[COLUMNA_FECHA] = pd.to_datetime(df[COLUMNA_FECHA])
    df = df.sort_values(COLUMNA_FECHA).set_index(COLUMNA_FECHA)
    df.index.name = "fecha"

    mensajes: list[str] = []
    if len(df) != REGISTROS_MENSUALES_ESPERADOS:
        mensajes.append(
            f"Advertencia: se esperaban {REGISTROS_MENSUALES_ESPERADOS} registros "
            f"mensuales; el archivo contiene {len(df)}."
        )

    columnas_precio = list(df.columns)
    if TICKER_BENCHMARK not in columnas_precio:
        raise ValueError(
            f"El CSV debe incluir la columna del benchmark '{TICKER_BENCHMARK}'."
        )

    activos_candidatos = [c for c in columnas_precio if c != TICKER_BENCHMARK]
    activos_excluidos: list[str] = []
    activos_validos: list[str] = []

    for ticker in activos_candidatos:
        if df[ticker].isna().any():
            activos_excluidos.append(ticker)
            mensajes.append(_mensaje_activo_omitido(ticker))
        else:
            activos_validos.append(ticker)

    columnas_finales = list(activos_validos)
    if df[TICKER_BENCHMARK].isna().any():
        mensajes.append(
            f"Se omitió el benchmark {TICKER_BENCHMARK} por datos incompletos."
        )
    else:
        columnas_finales.append(TICKER_BENCHMARK)

    if not activos_validos:
        raise ValueError(
            "No quedó ninguna empresa con datos completos tras la validación."
        )

    precios = df[columnas_finales].copy()

    return ResultadoCargaDatos(
        precios=precios,
        activos_validos=activos_validos,
        benchmark=TICKER_BENCHMARK,
        activos_excluidos=activos_excluidos,
        mensajes=mensajes,
        ruta_csv=ruta_referencia,
        nombre_archivo=nombre_archivo or ruta_referencia.name,
    )


def cargar_y_validar_datos(
    ruta_csv: Path | str | None = None,
    contenido_csv: bytes | None = None,
    nombre_archivo: str | None = None,
) -> ResultadoCargaDatos:
    """
    Carga el CSV de precios, valida datos faltantes y excluye activos incompletos.

    Parámetros
    ----------
    ruta_csv : Path | str | None
        Ruta al archivo en disco. Si es None y no hay contenido_csv, usa el CSV por defecto.
    contenido_csv : bytes | None
        Contenido binario de un CSV subido por el usuario.
    nombre_archivo : str | None
        Nombre del archivo subido (solo con contenido_csv).

    Raises
    ------
    FileNotFoundError
        Si la ruta indicada no existe.
    ValueError
        Si el formato del CSV no es válido.
    """
    if contenido_csv is not None:
        df = pd.read_csv(io.BytesIO(contenido_csv))
        nombre = nombre_archivo or "archivo_subido.csv"
        ruta = Path(nombre)
    else:
        ruta = Path(ruta_csv) if ruta_csv is not None else RUTA_CSV_DEFECTO
        if not ruta.is_file():
            raise FileNotFoundError(f"No se encontró el archivo de datos: {ruta}")
        df = pd.read_csv(ruta)
        nombre = ruta.name

    return _validar_dataframe(df, ruta, nombre_archivo=nombre)
