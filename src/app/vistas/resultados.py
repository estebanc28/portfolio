"""Funcionalidad 4: resultados finales y validación histórica."""

from __future__ import annotations

import streamlit as st

from src.finance.resultados import VALOR_INICIAL_DEFECTO
from src.visualization.resultados_cache import obtener_resultados_finales

COLOR_IGUAL = "#66bb6a"
COLOR_OPTIMIZADO = "#00e5ff"


def _texto_pesos_iguales(pesos: dict[str, float]) -> tuple[str, str]:
    """Genera el párrafo y la lista de tickers para el portafolio de pesos iguales."""
    tickers = sorted(pesos.keys())
    n = len(tickers)
    if n == 0:
        return "No hay activos en este escenario.", ""

    valores = [pesos[t] for t in tickers]
    peso_ref = valores[0]
    todos_iguales = all(abs(v - peso_ref) < 1e-6 for v in valores)

    if todos_iguales:
        pct = peso_ref * 100
        parrafo = (
            f"Se les asignó a cada una de las siguientes <strong>{n}</strong> empresas un peso "
            f"igual al 100 % dividido entre {n}, equivalente a <strong>{pct:.1f} %</strong> cada una:"
        )
    else:
        parrafo = (
            "Se asignaron pesos entre las empresas seleccionadas "
            "(pesos iguales en activos libres, respetando restricciones fijas si las hubo):"
        )

    lista = ", ".join(tickers)
    return parrafo, lista


def _texto_pesos_optimizados(pesos: dict[str, float]) -> str:
    """Lista TICKER: peso % para el portafolio optimizado."""
    if not pesos:
        return "*Sin posiciones con peso positivo.*"
    return ", ".join(
        f"<strong>{t}</strong>: {w * 100:.1f} %"
        for t, w in sorted(pesos.items(), key=lambda x: -x[1])
    )


def _mostrar_pregunta_inversion(
    final_igual: float,
    final_opt: float,
    final_bench: float | None,
) -> None:
    """Responde cuánto valdría hoy una inversión de $1,000 en el período de los datos."""
    st.markdown(
        f"""
        <div style="background-color: #1e3a8a; padding: 15px; border-radius: 10px; margin: 1rem 0;">
        <p style="color: white; margin: 0; font-size: 16px;">
        <strong>Este gráfico responde a la pregunta:</strong><br>
        <em>"Si hubieras invertido ${VALOR_INICIAL_DEFECTO:,.0f} en el periodo seleccionado,
        ¿cuánto tendrías hoy?"</em>
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    columnas = st.columns(3 if final_bench is not None else 2)
    escenarios = [
        ("Pesos iguales", final_igual),
        ("Portafolio optimizado", final_opt),
    ]
    if final_bench is not None:
        escenarios.append(("S&P 500 (Benchmark)", final_bench))

    for col, (etiqueta, valor) in zip(columnas, escenarios, strict=False):
        with col:
            st.metric(etiqueta, f"${valor:,.2f}")


def _mostrar_nota_explicativa(
    pesos_igual: dict[str, float],
    pesos_opt: dict[str, float],
) -> None:
    """Nota al pie del gráfico: composición de ambos portafolios comparados."""
    parrafo_igual, lista_igual = _texto_pesos_iguales(pesos_igual)
    texto_opt = _texto_pesos_optimizados(pesos_opt)

    st.markdown("#### 📝 Nota Explicativa")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div style="background-color: #1f1f1f; padding: 15px; border-radius: 10px;
            border-left: 4px solid {COLOR_IGUAL};">
            <p style="color: white; margin: 0 0 8px 0;">
            <strong>🟢 Portafolio de Pesos Iguales:</strong>
            </p>
            <p style="color: #e0e0e0; margin: 0 0 8px 0; line-height: 1.5;">{parrafo_igual}</p>
            <p style="color: white; margin: 0; line-height: 1.5;">{lista_igual}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style="background-color: #1f1f1f; padding: 15px; border-radius: 10px;
            border-left: 4px solid {COLOR_OPTIMIZADO};">
            <p style="color: white; margin: 0 0 8px 0;">
            <strong>🎯 Portafolio Optimizado:</strong>
            </p>
            <p style="color: white; margin: 0; line-height: 1.5;">{texto_opt}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def mostrar() -> None:
    st.markdown("### 📊 Resultados Finales y Validación Histórica")

    if not st.session_state.get("datos_cargados"):
        st.warning(
            "Primero complete la **Carga y Preparación de Datos** "
            "en el menú lateral."
        )
        return

    if not st.session_state.get("config_confirmada"):
        st.warning(
            "Debe confirmar la configuración en **Inputs y Configuración Inicial** "
            "antes de ver los resultados finales."
        )
        return

    precios = st.session_state.get("precios")
    activos_validos = list(st.session_state.get("activos_validos", []))
    activos_seleccionados = list(st.session_state.get("activos_seleccionados", []))

    if precios is None or not activos_validos:
        st.info("No hay datos de precios disponibles.")
        return

    if not activos_seleccionados:
        st.info("Seleccione al menos un activo en **Inputs y Configuración Inicial**.")
        return

    seleccionados_con_precio = [a for a in activos_seleccionados if a in precios.columns]
    if not seleccionados_con_precio:
        st.info("Ningún activo seleccionado tiene precios en el archivo cargado.")
        return

    pesos_forzados = st.session_state.get("pesos_forzados", {})
    tasa_anual = float(st.session_state.get("tasa_libre_riesgo_anual", 0.04))

    with st.spinner("Calculando pesos y evolución histórica..."):
        (
            tabla,
            figura,
            no_utilizados,
            pesos_igual,
            pesos_opt,
            final_igual,
            final_opt,
            final_bench,
        ) = obtener_resultados_finales(
            precios,
            tuple(sorted(activos_validos)),
            tuple(sorted(seleccionados_con_precio)),
            tuple(sorted(pesos_forzados.items())),
            tasa_anual,
        )

    # 1. Tabla horizontal de pesos (arriba)
    st.markdown(
        '<p class="titulo-seccion-grafico">Pesos del Portafolio Optimizado</p>',
        unsafe_allow_html=True,
    )
    st.dataframe(tabla, use_container_width=True, hide_index=True)

    if pesos_forzados:
        forzados_txt = ", ".join(
            f"**{t}**: {p * 100:.2f}%" for t, p in sorted(pesos_forzados.items())
        )
        st.caption(f"Pesos fijos respetados en la optimización: {forzados_txt}")

    st.caption(
        "Posiciones con peso inferior al **0,1 %** tras la optimización se tratan como "
        "**0 %** y no forman parte del portafolio final."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Activos considerados pero no utilizados en el portafolio óptimo")
        if no_utilizados:
            st.write(", ".join(sorted(no_utilizados)))
        else:
            st.write("*Ninguno*")
    with col_b:
        st.markdown("#### Activos excluidos por el usuario")
        excluidos = sorted(set(activos_validos) - set(seleccionados_con_precio))
        if excluidos:
            st.write(", ".join(excluidos))
        else:
            st.write("*Ninguno*")

    st.markdown("---")

    # 2. Gráfico comparativo (debajo)
    st.plotly_chart(figura, use_container_width=True)
    _mostrar_pregunta_inversion(final_igual, final_opt, final_bench)
    _mostrar_nota_explicativa(pesos_igual, pesos_opt)
