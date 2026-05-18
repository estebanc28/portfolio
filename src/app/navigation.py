"""Menú lateral de navegación entre funcionalidades."""

from __future__ import annotations

import streamlit as st

from src.app.nav_styles import CSS_MENU_NAVEGACION

OPCIONES_MENU: list[str] = [
    "Inicio",
    "Carga y Preparación de Datos",
    "Inputs y Configuración Inicial",
    "Optimización y Frontera Eficiente",
    "Resultados Finales y Validación Histórica",
]

ICONOS_MENU: dict[str, str] = {
    "Inicio": "🏠",
    "Carga y Preparación de Datos": "📊",
    "Inputs y Configuración Inicial": "⚙️",
    "Optimización y Frontera Eficiente": "🎯",
    "Resultados Finales y Validación Histórica": "📋",
}

CLAVE_MENU_SESION = "menu_seleccionado"
CLAVE_RADIO_MENU = "radio_menu_navegacion"


def _etiqueta_menu(opcion: str) -> str:
    return f"{ICONOS_MENU[opcion]}  {opcion}"


def _inicializar_menu() -> None:
    if CLAVE_MENU_SESION not in st.session_state:
        st.session_state[CLAVE_MENU_SESION] = OPCIONES_MENU[0]
    if st.session_state[CLAVE_MENU_SESION] not in OPCIONES_MENU:
        st.session_state[CLAVE_MENU_SESION] = OPCIONES_MENU[0]
    if CLAVE_RADIO_MENU not in st.session_state:
        st.session_state[CLAVE_RADIO_MENU] = st.session_state[CLAVE_MENU_SESION]
    if st.session_state[CLAVE_RADIO_MENU] not in OPCIONES_MENU:
        st.session_state[CLAVE_RADIO_MENU] = OPCIONES_MENU[0]


def renderizar_menu() -> str:
    """Lista fija estilo imagen: panel blanco, ítem activo en gris, sin desplegable."""
    _inicializar_menu()

    with st.sidebar:
        st.markdown(
            """
            <p class="nav-titulo">🧭 Navegación</p>
            <p class="nav-subtitulo">Selecciona una funcionalidad:</p>
            """,
            unsafe_allow_html=True,
        )

        # CSS específico del menú (se aplica junto al widget radio)
        st.markdown(CSS_MENU_NAVEGACION, unsafe_allow_html=True)

        seleccion = st.radio(
            "Menú de navegación",
            OPCIONES_MENU,
            format_func=_etiqueta_menu,
            key=CLAVE_RADIO_MENU,
            label_visibility="collapsed",
        )

        st.session_state[CLAVE_MENU_SESION] = seleccion

    return st.session_state[CLAVE_MENU_SESION]
