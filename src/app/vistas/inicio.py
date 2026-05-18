"""Vista de inicio con descripción general del proyecto."""

import streamlit as st


def mostrar() -> None:
    st.markdown(
        '<h1 class="titulo-principal">'
        "📊 Portafolio de Inversión con Optimización de Markowitz"
        "</h1>",
        unsafe_allow_html=True,
    )

    st.markdown("### 🎯 Descripción General")
    st.write(
        "Este proyecto tiene como objetivo construir una aplicación interactiva que "
        "permita analizar y optimizar un portafolio de inversión a partir de datos "
        "históricos de precios de **20 empresas** y del índice **S&P 500**."
    )

    st.markdown("### 📋 Funcionalidades Disponibles")
    funcionalidades = [
        ("🏠", "Inicio"),
        ("📊", "Carga y Preparación de Datos"),
        ("⚙️", "Inputs y Configuración Inicial"),
        ("🎯", "Optimización y Frontera Eficiente"),
        ("📋", "Resultados Finales y Validación Histórica"),
    ]
    for icono, nombre in funcionalidades:
        st.markdown(f"{icono} {nombre}")

    st.markdown("### 🚀 Comenzar")
    st.info(
        "Selecciona **Carga y Preparación de Datos** en el menú lateral para validar "
        "el archivo CSV y preparar el universo de activos. Luego avanza por cada "
        "sección en orden hasta llegar a los resultados finales."
    )
