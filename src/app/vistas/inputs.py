"""Funcionalidad 1: inputs y configuración inicial."""

from __future__ import annotations

import streamlit as st

from src.config import TASA_LIBRE_RIESGO_DEFAULT_ANUAL
from src.finance.configuracion import (
    anual_a_mensual,
    construir_configuracion,
    validar_configuracion,
)
from src.visualization.correlacion_cache import invalidar_cache_correlacion

# Claves de session_state usadas por el resto de funcionalidades
CLAVE_CONFIG_CONFIRMADA = "config_confirmada"
CLAVE_ACTIVOS_SELECCIONADOS = "activos_seleccionados"
CLAVE_PESOS_FORZADOS = "pesos_forzados"
CLAVE_TASA_ANUAL = "tasa_libre_riesgo_anual"
CLAVE_TASA_MENSUAL = "tasa_libre_riesgo_mensual"


def _datos_listos() -> bool:
    return bool(st.session_state.get("datos_cargados"))


def _inicializar_valores_por_defecto(activos_disponibles: list[str]) -> None:
    if CLAVE_ACTIVOS_SELECCIONADOS not in st.session_state:
        st.session_state[CLAVE_ACTIVOS_SELECCIONADOS] = list(activos_disponibles)
    if CLAVE_PESOS_FORZADOS not in st.session_state:
        st.session_state[CLAVE_PESOS_FORZADOS] = {}
    if CLAVE_TASA_ANUAL not in st.session_state:
        st.session_state[CLAVE_TASA_ANUAL] = TASA_LIBRE_RIESGO_DEFAULT_ANUAL


def _guardar_configuracion_en_sesion(
    activos_seleccionados: list[str],
    pesos_forzados: dict[str, float],
    tasa_anual: float,
) -> None:
    config = construir_configuracion(activos_seleccionados, pesos_forzados, tasa_anual)
    st.session_state[CLAVE_CONFIG_CONFIRMADA] = True
    st.session_state[CLAVE_ACTIVOS_SELECCIONADOS] = config.activos_seleccionados
    st.session_state[CLAVE_PESOS_FORZADOS] = config.pesos_forzados
    st.session_state[CLAVE_TASA_ANUAL] = config.tasa_libre_riesgo_anual
    st.session_state[CLAVE_TASA_MENSUAL] = config.tasa_libre_riesgo_mensual
    invalidar_cache_correlacion()


def _obtener_rango_fechas() -> str:
    """Obtiene el período de los datos cargados en la Funcionalidad 0."""
    precios = st.session_state.get("precios")
    if precios is None or getattr(precios, "empty", True):
        return "No disponible (cargue los datos primero)"
    fecha_min = precios.index.min().strftime("%Y-%m-%d")
    fecha_max = precios.index.max().strftime("%Y-%m-%d")
    meses = len(precios)
    return f"{fecha_min} → {fecha_max} ({meses} meses)"


def _mostrar_resumen_final(
    activos_seleccionados: list[str],
    pesos_forzados: dict[str, float],
    tasa_anual: float,
    confirmada: bool,
) -> None:
    """Resumen al final del formulario con los datos elegidos por el usuario."""
    st.divider()
    st.subheader("Resumen de su configuración")

    if confirmada:
        st.success("Configuración confirmada. Puede continuar con la optimización.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Cantidad de acciones", len(activos_seleccionados))
    with col2:
        st.metric("Tasa libre de riesgo", f"{tasa_anual * 100:.2f}%")
    with col3:
        st.metric("Pesos fijos", len(pesos_forzados))

    st.markdown(f"**Período de los datos:** {_obtener_rango_fechas()}")

    if activos_seleccionados:
        st.markdown(
            "**Acciones seleccionadas:** " + ", ".join(sorted(activos_seleccionados))
        )
    else:
        st.markdown("**Acciones seleccionadas:** ninguna")

    if pesos_forzados:
        lineas_pesos = [
            f"- **{ticker}:** {peso * 100:.2f}%"
            for ticker, peso in sorted(pesos_forzados.items())
        ]
        st.markdown("**Pesos fijos:**\n" + "\n".join(lineas_pesos))
    else:
        st.markdown("**Pesos fijos:** ninguno definido")


def mostrar() -> None:
    st.markdown("### ⚙️ Inputs y Configuración Inicial")

    if not _datos_listos():
        st.warning(
            "Primero debe completar la **Carga y Preparación de Datos** "
            "para disponer del universo de activos válidos."
        )
        return

    activos_disponibles: list[str] = list(st.session_state.get("activos_validos", []))
    _inicializar_valores_por_defecto(activos_disponibles)

    st.markdown(
        "Seleccione las empresas a incluir, opcionalmente fije pesos objetivo "
        "y defina la tasa libre de riesgo antes de confirmar."
    )

    # --- Selección de activos ---
    st.subheader("Universo de activos")
    st.caption(
        f"Empresas disponibles tras la validación de datos ({len(activos_disponibles)})."
    )

    activos_previos = [
        a
        for a in st.session_state.get(CLAVE_ACTIVOS_SELECCIONADOS, activos_disponibles)
        if a in activos_disponibles
    ]
    if not activos_previos:
        activos_previos = list(activos_disponibles)

    activos_seleccionados = st.multiselect(
        "Empresas a incluir en el portafolio",
        options=activos_disponibles,
        default=activos_previos,
        help="Retire del listado las empresas que no desea analizar.",
    )

    if not activos_seleccionados:
        st.info("Seleccione al menos un activo para continuar.")

    # --- Pesos forzados ---
    st.subheader("Pesos forzados (opcional)")
    st.caption(
        "Asigne un porcentaje fijo a activos específicos (ejemplo: V = 15%). "
        "La suma de todos los pesos forzados no puede superar el 100%."
    )

    pesos_previos: dict[str, float] = dict(st.session_state.get(CLAVE_PESOS_FORZADOS, {}))
    pesos_forzados: dict[str, float] = {}

    if activos_seleccionados:
        cols = st.columns(2)
        for i, ticker in enumerate(sorted(activos_seleccionados)):
            peso_pct_previo = pesos_previos.get(ticker, 0.0) * 100.0
            with cols[i % 2]:
                peso_pct = st.number_input(
                    f"{ticker} (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(peso_pct_previo),
                    step=0.5,
                    format="%.2f",
                    key=f"peso_forzado_{ticker}",
                    help="0% = sin peso forzado; el optimizador asignará el resto.",
                )
            if peso_pct > 0:
                pesos_forzados[ticker] = peso_pct / 100.0

        suma_forzada = sum(pesos_forzados.values())
        if pesos_forzados:
            st.write(f"**Suma de pesos forzados:** {suma_forzada * 100:.2f}%")
            if suma_forzada > 1.0:
                st.error("La suma de pesos forzados supera el 100%. Ajuste los valores.")
    else:
        st.caption("Seleccione activos para definir pesos forzados.")

    # --- Tasa libre de riesgo ---
    st.subheader("Tasa libre de riesgo")
    tasa_anual_previa = float(
        st.session_state.get(CLAVE_TASA_ANUAL, TASA_LIBRE_RIESGO_DEFAULT_ANUAL)
    )
    tasa_pct = st.number_input(
        "Tasa anual (%) — referencia Treasury 10 años",
        min_value=0.0,
        max_value=100.0,
        value=tasa_anual_previa * 100.0,
        step=0.1,
        format="%.2f",
        help="Se convertirá automáticamente a tasa mensual para los cálculos internos.",
    )
    tasa_anual = tasa_pct / 100.0
    tasa_mensual_vista = anual_a_mensual(tasa_anual)
    st.caption(
        f"Equivalente mensual para cálculos: **{tasa_mensual_vista * 100:.4f}%** "
        f"(fórmula: (1 + r_anual)^(1/12) − 1)"
    )

    # --- Confirmación ---
    st.divider()
    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        confirmar = st.button(
            "Confirmar configuración",
            type="primary",
            use_container_width=True,
        )
    with col_info:
        st.caption(
            "Al confirmar, se fijan el universo de activos y los supuestos "
            "para las funcionalidades de análisis y optimización."
        )

    if confirmar:
        es_valida, mensaje = validar_configuracion(
            activos_disponibles=activos_disponibles,
            activos_seleccionados=activos_seleccionados,
            pesos_forzados=pesos_forzados,
            tasa_libre_riesgo_anual=tasa_anual,
        )
        if not es_valida:
            st.error(mensaje)
        else:
            _guardar_configuracion_en_sesion(
                activos_seleccionados=activos_seleccionados,
                pesos_forzados=pesos_forzados,
                tasa_anual=tasa_anual,
            )
            st.rerun()

    _mostrar_resumen_final(
        activos_seleccionados=activos_seleccionados,
        pesos_forzados=pesos_forzados,
        tasa_anual=tasa_anual,
        confirmada=bool(st.session_state.get(CLAVE_CONFIG_CONFIRMADA)),
    )
