"""Estilos globales de la aplicación (tema oscuro tipo terminal financiera)."""

from src.app.nav_styles import CSS_MENU_NAVEGACION

CSS_TEMA = (
    """
<style>
    /* Fondo negro en toda la app (incluida franja superior) */
    .stApp {
        background-color: #000000 !important;
        color: #f5f5f5;
    }
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stMainBlockContainer"],
    section.main > div {
        background-color: #000000 !important;
    }
    /* Barra superior de Streamlit (header / toolbar) */
    header[data-testid="stHeader"] {
        background-color: #000000 !important;
        border-bottom: 1px solid #1f1f1f;
    }
    [data-testid="stHeader"] > div {
        background-color: #000000 !important;
    }
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        background-color: #000000 !important;
    }
    /* Iconos de la barra superior visibles sobre fondo negro */
    [data-testid="stHeader"] button,
    [data-testid="stHeader"] span,
    [data-testid="stToolbar"] button {
        color: #e5e5e5 !important;
    }
    [data-testid="stHeader"] svg,
    [data-testid="stToolbar"] svg {
        fill: #e5e5e5 !important;
    }
    /* Área principal */
    [data-testid="stMain"] {
        background-color: #000000 !important;
    }
    .main .block-container {
        background-color: #000000 !important;
    }
    /* Título principal: más grande que subtítulos, en una sola línea */
    .titulo-principal {
        color: #ffffff !important;
        font-size: clamp(1.15rem, 2.1vw, 1.95rem) !important;
        font-weight: 700 !important;
        line-height: 1.15 !important;
        margin: 0 0 1rem 0 !important;
        padding: 0 !important;
        white-space: nowrap !important;
    }
    /* Mismo estilo que title de gráficos Plotly (frontera, correlación, etc.) */
    .titulo-seccion-grafico {
        color: #f0f0f0 !important;
        font-size: 16px !important;
        font-weight: bold !important;
        font-family: Arial, sans-serif !important;
        line-height: 1.2 !important;
        margin: 1.25rem 0 0.35rem 0 !important;
        padding: 0 !important;
        text-align: left !important;
    }
    /* Subtítulos de sección (Descripción General, etc.) */
    [data-testid="stMain"] h3 {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
    }
    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,

    [data-testid="stMain"] h3,
    [data-testid="stMain"] h4,
    [data-testid="stMain"] p,
    [data-testid="stMain"] li,
    [data-testid="stMain"] span,
    [data-testid="stMain"] label {
        color: #f0f0f0;
    }

    /* Caja de instrucciones — Funcionalidad 0 */
    .caja-opciones-carga {
        background-color: #141414;
        border: 1px solid #2d2d2d;
        border-radius: 10px;
        padding: 1rem 1.15rem;
        margin-bottom: 1rem;
        color: #e8e8e8;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    .caja-opciones-carga p {
        color: #e8e8e8 !important;
        margin: 0 0 0.65rem 0;
    }
    .caja-opciones-carga p:last-child {
        margin-bottom: 0;
    }

    /* Botón "Cargar Archivo Personalizado" y secundarios: texto oscuro */
    [data-testid="stMain"] .stButton > button[kind="secondary"],
    [data-testid="stMain"] .stButton > button[kind="secondary"] p,
    [data-testid="stMain"] .stButton > button[kind="secondary"] span,
    [data-testid="stMain"] .stButton > button[kind="secondary"] div,
    [data-testid="stMain"] [data-testid="baseButton-secondary"],
    [data-testid="stMain"] [data-testid="baseButton-secondary"] p,
    [data-testid="stMain"] [data-testid="baseButton-secondary"] span,
    [data-testid="stMain"] [data-testid="stBaseButton-secondary"],
    [data-testid="stMain"] [data-testid="stBaseButton-secondary"] p,
    [data-testid="stMain"] [data-testid="stBaseButton-secondary"] span {
        background-color: #ffffff !important;
        color: #1f2937 !important;
        border-color: #d1d5db !important;
    }
    [data-testid="stMain"] .stButton > button[kind="secondary"]:disabled,
    [data-testid="stMain"] .stButton > button[kind="secondary"]:disabled p,
    [data-testid="stMain"] .stButton > button[kind="secondary"]:disabled span,
    [data-testid="stMain"] [data-testid="baseButton-secondary"]:disabled,
    [data-testid="stMain"] [data-testid="baseButton-secondary"]:disabled p,
    [data-testid="stMain"] [data-testid="baseButton-secondary"]:disabled span {
        background-color: #f3f4f6 !important;
        color: #4b5563 !important;
    }
    [data-testid="stMain"] [data-testid="stFileUploader"] label,
    [data-testid="stMain"] [data-testid="stFileUploader"] small,
    [data-testid="stMain"] [data-testid="stFileUploader"] span,
    [data-testid="stMain"] [data-testid="stFileUploader"] p {
        color: #374151 !important;
    }
    [data-testid="stMain"] [data-testid="stFileUploader"] button,
    [data-testid="stMain"] [data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] {
        background-color: #ffffff !important;
        color: #1f2937 !important;
        border: 1px solid #d1d5db !important;
    }
    [data-testid="stMain"] section[data-testid="stFileUploaderDropzone"] {
        background-color: #f3f4f6 !important;
        border-color: #d1d5db !important;
    }
    [data-testid="stMain"] section[data-testid="stFileUploaderDropzone"] span,
    [data-testid="stMain"] section[data-testid="stFileUploaderDropzone"] small {
        color: #374151 !important;
    }

    /* Sidebar: fondo negro, ancho compacto */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #1f1f1f;
        min-width: 19.5rem;
        max-width: 19.5rem;
    }
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebarHeader"],
    [data-testid="stSidebarCollapsedControl"] {
        background-color: #000000 !important;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        padding-top: 1rem;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* Encabezado del menú */
    .nav-titulo {
        color: #ffffff !important;
        font-size: 1.05rem;
        font-weight: 700;
        margin: 0 0 0.15rem 0;
        padding: 0;
        text-align: left;
    }
    .nav-subtitulo {
        color: #e5e5e5 !important;
        font-size: 0.8rem;
        font-weight: 400;
        margin: 0 0 0.55rem 0;
        padding: 0;
        text-align: left;
    }
</style>
"""
    + CSS_MENU_NAVEGACION
)
