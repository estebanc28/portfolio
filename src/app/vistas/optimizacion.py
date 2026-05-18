"""
Funcionalidad 3: optimización y frontera eficiente.

Matriz de correlaciones, tabla comparativa y gráfico de frontera eficiente + CML.
"""

from __future__ import annotations

import streamlit as st

from src.app.scroll import scroll_al_inicio
from src.visualization.correlacion_cache import obtener_mapa_correlacion
from src.visualization.frontera_cache import obtener_grafico_frontera
from src.visualization.tabla_comparativa_cache import obtener_tabla_comparativa

COLOR_FRONTERA = "#00e5ff"
COLOR_CML = "#ffd54f"


def _precios_activos_seleccionados():
    """Precios históricos solo de los activos confirmados en la Funcionalidad 1."""
    if not st.session_state.get("config_confirmada"):
        return None

    activos = list(st.session_state.get("activos_seleccionados", []))
    precios = st.session_state.get("precios")

    if precios is None or not activos:
        return None

    columnas = [t for t in activos if t in precios.columns]
    if not columnas:
        return None

    return precios[columnas]


def _mostrar_tabla_comparativa(precios, activos_clave: tuple[str, ...]) -> None:
    """Tabla de métricas anualizadas: pesos iguales vs portafolio optimizado."""
    pesos_forzados = st.session_state.get("pesos_forzados", {})
    tasa_anual = float(st.session_state.get("tasa_libre_riesgo_anual", 0.04))
    forzados_clave = tuple(sorted(pesos_forzados.items()))

    tabla, pesos_igual, pesos_opt = obtener_tabla_comparativa(
        precios,
        activos_clave,
        forzados_clave,
        tasa_anual,
    )

    st.session_state["pesos_portafolio_igual"] = pesos_igual
    st.session_state["pesos_portafolio_optimizado"] = pesos_opt

    st.markdown(
        '<p class="titulo-seccion-grafico">'
        "Comparación de Portafolios: Pesos Iguales vs Optimizado"
        "</p>",
        unsafe_allow_html=True,
    )
    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True,
    )


def _mostrar_frontera_eficiente(precios, activos_clave: tuple[str, ...]) -> None:
    """Gráfico de frontera eficiente y CML debajo de la tabla comparativa."""
    pesos_forzados = st.session_state.get("pesos_forzados", {})
    tasa_anual = float(st.session_state.get("tasa_libre_riesgo_anual", 0.04))
    forzados_clave = tuple(sorted(pesos_forzados.items()))

    figura = obtener_grafico_frontera(
        precios,
        activos_clave,
        forzados_clave,
        tasa_anual,
    )
    st.plotly_chart(figura, use_container_width=True)
    _mostrar_interpretacion_grafico()


def _mostrar_interpretacion_grafico() -> None:
    """Tarjetas de ayuda bajo el gráfico de frontera eficiente y CML."""
    st.markdown("#### 📖 Interpretación del Gráfico")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div style="background-color: #1f1f1f; padding: 15px; border-radius: 10px;
            border-left: 4px solid {COLOR_FRONTERA};">
            <p style="color: white; margin: 0;"><strong>🔵 Frontera Eficiente (Azul):</strong></p>
            <ul style="color: white; margin: 8px 0 0 18px; line-height: 1.5;">
            <li>Representa todos los portafolios óptimos</li>
            <li>Máximo rendimiento para cada nivel de riesgo</li>
            <li>Calculada mediante optimización cuadrática</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style="background-color: #1f1f1f; padding: 15px; border-radius: 10px;
            border-left: 4px solid {COLOR_CML};">
            <p style="color: white; margin: 0;"><strong>🟡 CML (Amarilla):</strong></p>
            <ul style="color: white; margin: 8px 0 0 18px; line-height: 1.5;">
            <li>Línea del Mercado de Capitales</li>
            <li>Combina activo libre de riesgo con portafolio de mercado</li>
            <li>Pendiente = Ratio de Sharpe del mercado</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


def mostrar() -> None:
    st.markdown("### 🎯 Optimización y Frontera Eficiente")

    if not st.session_state.get("datos_cargados"):
        st.warning(
            "Primero complete la **Carga y Preparación de Datos** "
            "en el menú lateral."
        )
        return

    if not st.session_state.get("config_confirmada"):
        st.warning(
            "Debe confirmar la configuración en **Inputs y Configuración Inicial** "
            "antes de visualizar las correlaciones."
        )
        return

    precios = _precios_activos_seleccionados()
    if precios is None or precios.shape[1] < 2:
        st.info(
            "Se requieren al menos **dos activos seleccionados** "
            "para calcular la matriz de correlaciones."
        )
        return

    activos_clave = tuple(sorted(precios.columns.tolist()))
    figura, _ = obtener_mapa_correlacion(precios, activos_clave)
    st.plotly_chart(figura, use_container_width=True)

    _mostrar_tabla_comparativa(precios, activos_clave)
    _mostrar_frontera_eficiente(precios, activos_clave)
    scroll_al_inicio(tras_graficos=True)
