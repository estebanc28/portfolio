"""
Desplazamiento al inicio de la vista principal en Streamlit.
"""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

# Vistas con mucho contenido vertical (gráficos Plotly)
VISTAS_SCROLL_INICIO: frozenset[str] = frozenset(
    {
        "Optimización y Frontera Eficiente",
        "Resultados Finales y Validación Histórica",
    }
)

CLAVE_NAV_ANTERIOR = "nav_opcion_anterior"


def scroll_al_inicio(*, tras_graficos: bool = False) -> None:
    """
    Lleva el scroll de la zona principal al tope.

    Si tras_graficos es True, repite el scroll con retardo para contrarrestar
    el salto que provocan los gráficos Plotly al renderizarse.
    """
    delays = [0, 120, 350, 700, 1200] if tras_graficos else [0, 80]
    delays_js = ", ".join(str(d) for d in delays)

    components.html(
        f"""
        <script>
        (function() {{
            function irArriba() {{
                const doc = window.parent.document;
                const selectores = [
                    'section[data-testid="stMain"]',
                    '[data-testid="stAppViewContainer"]',
                    '.main',
                ];
                selectores.forEach(function(sel) {{
                    const el = doc.querySelector(sel);
                    if (el) el.scrollTop = 0;
                }});
                try {{
                    window.parent.scrollTo({{ top: 0, left: 0, behavior: 'instant' }});
                }} catch (e) {{
                    window.parent.scrollTo(0, 0);
                }}
            }}
            [{delays_js}].forEach(function(ms) {{
                setTimeout(irArriba, ms);
            }});
        }})();
        </script>
        """,
        height=0,
    )


def aplicar_scroll_al_entrar_vista(opcion_actual: str) -> None:
    """Scroll al tope cuando el usuario cambia a una vista de resultados."""
    if opcion_actual not in VISTAS_SCROLL_INICIO:
        st.session_state[CLAVE_NAV_ANTERIOR] = opcion_actual
        return

    anterior = st.session_state.get(CLAVE_NAV_ANTERIOR)
    st.session_state[CLAVE_NAV_ANTERIOR] = opcion_actual

    if anterior != opcion_actual:
        scroll_al_inicio(tras_graficos=False)
