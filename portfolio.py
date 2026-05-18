"""
Aplicación Streamlit — Portafolio de inversión (Markowitz).
Punto de entrada con navegación lateral por funcionalidades.
"""

import sys
from collections.abc import Callable
from pathlib import Path

import streamlit as st

# Permite importar src/ al ejecutar desde la raíz del proyecto
RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.app.navigation import renderizar_menu
from src.app.scroll import aplicar_scroll_al_entrar_vista
from src.app.theme import CSS_TEMA
from src.app.vistas import carga_datos, inicio, inputs, optimizacion, resultados

st.set_page_config(
    page_title="Portafolio Markowitz",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CSS_TEMA, unsafe_allow_html=True)

# Ocultar menú multipágina por defecto de Streamlit (usamos menú propio)
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

opcion = renderizar_menu()
aplicar_scroll_al_entrar_vista(opcion)

RUTAS: dict[str, Callable[[], None]] = {
    "Inicio": inicio.mostrar,
    "Carga y Preparación de Datos": carga_datos.mostrar,
    "Inputs y Configuración Inicial": inputs.mostrar,
    "Optimización y Frontera Eficiente": optimizacion.mostrar,
    "Resultados Finales y Validación Histórica": resultados.mostrar,
}

RUTAS[opcion]()
