"""Funcionalidad 0: carga y preparación de datos."""

from __future__ import annotations

import streamlit as st

from src.config import RUTA_CSV_DEFECTO, TICKER_BENCHMARK
from src.data.loader import ResultadoCargaDatos, cargar_y_validar_datos
from src.visualization.correlacion_cache import invalidar_cache_correlacion

CLAVE_ARCHIVO_SUBIDO = "csv_subido_bytes"
CLAVE_NOMBRE_ARCHIVO = "csv_subido_nombre"


def _limpiar_configuracion_posterior() -> None:
    """Reinicia la configuración del usuario si se cargan datos nuevos."""
    claves = [
        "config_confirmada",
        "activos_seleccionados",
        "pesos_forzados",
        "tasa_libre_riesgo_anual",
        "tasa_libre_riesgo_mensual",
    ]
    for clave in claves:
        st.session_state.pop(clave, None)


def _inicializar_sesion(resultado: ResultadoCargaDatos) -> None:
    st.session_state["datos_cargados"] = True
    st.session_state["precios"] = resultado.precios
    st.session_state["activos_validos"] = resultado.activos_validos
    st.session_state["benchmark"] = resultado.benchmark
    st.session_state["activos_excluidos"] = resultado.activos_excluidos
    st.session_state["mensajes_carga"] = resultado.mensajes
    st.session_state["nombre_archivo_datos"] = resultado.nombre_archivo
    _limpiar_configuracion_posterior()
    invalidar_cache_correlacion()


def _procesar_carga(resultado: ResultadoCargaDatos) -> None:
    _inicializar_sesion(resultado)
    st.rerun()


def _mostrar_resultados(resultado: ResultadoCargaDatos) -> None:
    if resultado.mensajes:
        for mensaje in resultado.mensajes:
            if mensaje.startswith("Advertencia"):
                st.warning(mensaje)
            else:
                st.warning(mensaje)
    else:
        st.success(
            "Todos los activos del archivo tienen datos completos. "
            "Puede continuar con la configuración inicial."
        )

    col_resumen, col_detalle = st.columns([1, 2])

    with col_resumen:
        st.subheader("Resumen")
        st.metric("Empresas válidas", len(resultado.activos_validos))
        st.metric("Empresas excluidas", len(resultado.activos_excluidos))
        st.metric("Observaciones (meses)", len(resultado.precios))
        st.write(f"**Benchmark:** `{resultado.benchmark}`")
        st.write(f"**Archivo:** `{resultado.nombre_archivo}`")

    with col_detalle:
        st.subheader("Empresas disponibles para el análisis")
        st.write(", ".join(resultado.activos_validos))

        if resultado.activos_excluidos:
            st.subheader("Empresas excluidas")
            st.write(", ".join(resultado.activos_excluidos))

    st.subheader("Vista previa de precios (primeras filas)")
    st.dataframe(resultado.precios.head(10), use_container_width=True)

    st.subheader("Rango de fechas")
    fecha_min = resultado.precios.index.min().strftime("%Y-%m-%d")
    fecha_max = resultado.precios.index.max().strftime("%Y-%m-%d")
    st.info(f"Datos desde **{fecha_min}** hasta **{fecha_max}**.")

    if TICKER_BENCHMARK in resultado.precios.columns:
        st.caption(
            f"La columna `{TICKER_BENCHMARK}` se conserva como benchmark "
            "y no forma parte del universo de optimización."
        )


def _mostrar_opciones_carga() -> tuple[bool, bool]:
    """Muestra instrucciones, uploader y botones. Retorna flags de acción."""
    st.markdown(
        """
        <div class="caja-opciones-carga">
            <p><strong>🔹 Opciones de Carga de Datos</strong></p>
            <p><strong>1. Usar el archivo por defecto:</strong><br>
            El archivo ya está incluido en la aplicación. Contiene precios mensuales
            de 20 empresas más el índice S&amp;P 500.</p>
            <p><strong>2. Subir un archivo CSV personalizado:</strong><br>
            • La primera columna debe contener las fechas<br>
            • Las siguientes 20 columnas deben contener precios mensuales de empresas<br>
            • La última columna debe corresponder al índice S&amp;P 500<br>
            • El archivo debe tener exactamente 60 registros mensuales</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### 📁 Selecciona tu Opción")
    st.caption("📁 Cargar archivo CSV personalizado")

    archivo = st.file_uploader(
        "Selecciona tu archivo CSV",
        type=["csv"],
        help="Formato: fechas + 20 empresas + S&P 500 (^GSPC), 60 filas mensuales.",
    )

    if archivo is not None:
        st.session_state[CLAVE_ARCHIVO_SUBIDO] = archivo.getvalue()
        st.session_state[CLAVE_NOMBRE_ARCHIVO] = archivo.name
    elif CLAVE_ARCHIVO_SUBIDO not in st.session_state:
        st.session_state[CLAVE_ARCHIVO_SUBIDO] = None

    hay_archivo = bool(st.session_state.get(CLAVE_ARCHIVO_SUBIDO))

    st.markdown(
        """
        <style>
        /* Botón "Cargar Archivo Personalizado" — texto oscuro legible */
        [data-testid="stFileUploader"] ~ div [data-testid="column"]:first-child .stButton > button,
        [data-testid="stFileUploader"] ~ div [data-testid="column"]:first-child .stButton > button * {
            color: #1f2937 !important;
            -webkit-text-fill-color: #1f2937 !important;
        }
        [data-testid="stFileUploader"] ~ div [data-testid="column"]:first-child .stButton > button:disabled,
        [data-testid="stFileUploader"] ~ div [data-testid="column"]:first-child .stButton > button:disabled * {
            color: #4b5563 !important;
            -webkit-text-fill-color: #4b5563 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_personalizado, col_defecto = st.columns(2)

    with col_personalizado:
        cargar_personalizado = st.button(
            "Cargar Archivo Personalizado",
            type="secondary",
            use_container_width=True,
            disabled=not hay_archivo,
            key="btn_cargar_archivo_personalizado",
            help="Primero seleccione un archivo CSV en el control superior.",
        )

    with col_defecto:
        cargar_defecto = st.button(
            "📄 Usar Archivo por Defecto",
            type="primary",
            use_container_width=True,
        )

    return cargar_personalizado, cargar_defecto


def mostrar() -> None:
    st.markdown("### 📊 Carga y Preparación de Datos")

    # Resultados si ya hay datos cargados en sesión
    if st.session_state.get("datos_cargados"):
        st.success(
            f"Datos cargados: **{st.session_state.get('nombre_archivo_datos', '—')}**. "
            "Puede volver a cargar otro archivo si lo desea."
        )
        if st.session_state.get("precios") is not None:
            _mostrar_resultados(
                ResultadoCargaDatos(
                    precios=st.session_state["precios"],
                    activos_validos=st.session_state["activos_validos"],
                    benchmark=st.session_state["benchmark"],
                    activos_excluidos=st.session_state.get("activos_excluidos", []),
                    mensajes=st.session_state.get("mensajes_carga", []),
                    ruta_csv=RUTA_CSV_DEFECTO,
                    nombre_archivo=st.session_state.get(
                        "nombre_archivo_datos", "datos.csv"
                    ),
                )
            )
        st.divider()

    cargar_personalizado, cargar_defecto = _mostrar_opciones_carga()

    if cargar_defecto:
        try:
            resultado = cargar_y_validar_datos(ruta_csv=RUTA_CSV_DEFECTO)
            _procesar_carga(resultado)
        except (FileNotFoundError, ValueError) as error:
            st.error(str(error))

    if cargar_personalizado:
        contenido = st.session_state.get(CLAVE_ARCHIVO_SUBIDO)
        nombre = st.session_state.get(CLAVE_NOMBRE_ARCHIVO, "archivo_subido.csv")
        if not contenido:
            st.error("Seleccione un archivo CSV antes de continuar.")
            return
        try:
            resultado = cargar_y_validar_datos(
                contenido_csv=contenido,
                nombre_archivo=nombre,
            )
            _procesar_carga(resultado)
        except ValueError as error:
            st.error(str(error))
