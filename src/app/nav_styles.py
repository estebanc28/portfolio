"""Estilos del menú lateral fijo (lista blanca como en la referencia visual)."""

CSS_MENU_NAVEGACION = """
<style>
    /* Ocultar etiqueta por defecto del widget radio */
    [data-testid="stSidebar"] [data-testid="stRadio"] > label {
        display: none !important;
    }

    /* Panel blanco a ancho completo del sidebar */
    [data-testid="stSidebar"] [data-testid="stRadio"] {
        width: 100% !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        padding: 0.25rem 0 !important;
        width: 100% !important;
        gap: 0.06rem !important;
        border: none !important;
        box-sizing: border-box !important;
    }

    /* Cada ítem ocupa todo el ancho del panel (hasta el borde izquierdo) */
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label,
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] {
        background-color: #ffffff !important;
        color: #374151 !important;
        border: none !important;
        border-radius: 6px !important;
        margin: 0 !important;
        padding: 0.4rem 0.55rem !important;
        min-height: auto !important;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: flex-start !important;
        justify-content: flex-start !important;
        font-size: 0.72rem !important;
        font-weight: 500 !important;
        line-height: 1.25 !important;
        cursor: pointer !important;
        box-shadow: none !important;
    }

    /* Ocultar círculo del radio (sin punto rojo ni casilla) */
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label > div:first-child,
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {
        display: none !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] input[type="radio"],
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] input[type="radio"] {
        display: none !important;
        position: absolute !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] .element-container {
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Texto del ítem: fuente pequeña y texto completo visible */
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label > div,
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"] > div,
    [data-testid="stSidebar"] [data-testid="stRadio"] label p {
        color: #374151 !important;
        font-size: 0.72rem !important;
        line-height: 1.25 !important;
        overflow: visible !important;
        text-overflow: unset !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: anywhere !important;
    }

    /* Ítem seleccionado: fondo gris claro */
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked),
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
        background-color: #e4e7ee !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) > div,
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) > div {
        color: #1f2937 !important;
        font-weight: 600 !important;
    }

    /* Hover sutil en ítems no seleccionados */
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label:hover,
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:hover {
        background-color: #f5f6f8 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked):hover,
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked):hover {
        background-color: #e4e7ee !important;
    }
</style>
"""
