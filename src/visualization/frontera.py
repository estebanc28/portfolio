"""
Gráfico de frontera eficiente y línea del mercado de capitales (CML).
"""

from __future__ import annotations

import math

import plotly.graph_objects as go

from src.app.texto_formato import capitalizar_palabras_largas
from src.finance.frontera_eficiente import DatosFronteraEficiente

_CAP = capitalizar_palabras_largas

COLOR_FONDO = "#000000"
COLOR_TEXTO = "#f0f0f0"
COLOR_FRONTERA = "#00e5ff"
COLOR_CML = "#ffd54f"
COLOR_IGUAL = "#ff6b9d"
COLOR_OPTIMIZADO = "#00e5ff"
COLOR_RF = "#ffffff"

PASO_EJE_Y = 0.20
PASO_EJE_X = 0.10
TOPE_EJE_Y = 1.0


def _limite_superior_eje(paso: float, valor_max: float, margen: float = 1.08) -> float:
    """Redondea hacia arriba al múltiplo del paso."""
    return max(paso, math.ceil(valor_max * margen / paso) * paso)


def _formatear_sharpe(valor: float) -> str:
    if valor != valor:
        return "—"
    return f"{valor:.3f}"


def crear_grafico_frontera_cml(datos: DatosFronteraEficiente) -> go.Figure:
    """Construye el gráfico interactivo riesgo vs rendimiento."""
    fig = go.Figure()
    puntos = datos.frontera

    if len(puntos) >= 2:
        fig.add_trace(
            go.Scatter(
                x=[p.volatilidad for p in puntos],
                y=[p.rendimiento for p in puntos],
                mode="lines",
                name=_CAP("Frontera eficiente"),
                line=dict(color=COLOR_FRONTERA, width=2.5),
                hovertemplate=(
                    "<b>Frontera Eficiente</b><br>"
                    "Volatilidad: %{x:.2%}<br>"
                    "Rendimiento: %{y:.2%}<extra></extra>"
                ),
            )
        )

    fig.add_trace(
        go.Scatter(
            x=datos.cml_sigmas,
            y=datos.cml_rendimientos,
            mode="lines",
            name=_CAP("CML (Linea del Mercado de Capitales)"),
            # Guion corto en leyenda (~2 rayitas) con itemwidth reducido
            line=dict(color=COLOR_CML, width=2, dash="5px,4px"),
            hovertemplate=(
                "<b>CML</b><br>"
                "Volatilidad: %{x:.2%}<br>"
                "Rendimiento: %{y:.2%}<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[0.0],
            y=[datos.tasa_libre_riesgo],
            mode="markers",
            name=_CAP("Tasa libre de riesgo"),
            cliponaxis=False,
            marker=dict(color=COLOR_RF, size=10, symbol="diamond"),
            hovertemplate=(
                "<b>Tasa Libre De Riesgo</b><br>"
                "Volatilidad: 0.00%<br>"
                "Rendimiento: %{y:.2%}<extra></extra>"
            ),
        )
    )

    sharpe_igual_txt = _formatear_sharpe(datos.pesos_iguales_sharpe)
    fig.add_trace(
        go.Scatter(
            x=[datos.pesos_iguales_vol],
            y=[datos.pesos_iguales_ret],
            mode="markers",
            name=_CAP("Pesos iguales"),
            cliponaxis=False,
            marker=dict(color=COLOR_IGUAL, size=10, symbol="circle"),
            hovertemplate=(
                "<b>Pesos Iguales</b><br>"
                "Volatilidad: %{x:.2%}<br>"
                "Rendimiento: %{y:.2%}<br>"
                f"Sharpe: {sharpe_igual_txt}<extra></extra>"
            ),
        )
    )

    sharpe_opt_txt = _formatear_sharpe(datos.optimizado_sharpe)
    fig.add_trace(
        go.Scatter(
            x=[datos.optimizado_vol],
            y=[datos.optimizado_ret],
            mode="markers",
            name=_CAP("Portafolio optimizado"),
            cliponaxis=False,
            marker=dict(
                color=COLOR_OPTIMIZADO,
                size=12,
                symbol="star",
                line=dict(width=1, color="#ffffff"),
            ),
            hovertemplate=(
                "<b>Portafolio Optimizado</b><br>"
                "Volatilidad: %{x:.2%}<br>"
                "Rendimiento: %{y:.2%}<br>"
                f"Sharpe: {sharpe_opt_txt}<extra></extra>"
            ),
        )
    )

    ret_max_datos = max(
        max((p.rendimiento for p in puntos), default=0.0),
        datos.optimizado_ret,
        datos.pesos_iguales_ret,
        datos.tasa_libre_riesgo,
        float(max(datos.cml_rendimientos)) if len(datos.cml_rendimientos) else 0.0,
    )
    vol_max_datos = max(
        max((p.volatilidad for p in puntos), default=0.0),
        datos.optimizado_vol,
        datos.pesos_iguales_vol,
        float(max(datos.cml_sigmas)) if len(datos.cml_sigmas) else 0.05,
    )

    y_auto = _limite_superior_eje(PASO_EJE_Y, ret_max_datos)
    y_max = min(TOPE_EJE_Y, y_auto)
    x_max = _limite_superior_eje(PASO_EJE_X, vol_max_datos)

    fig.update_layout(
        title=dict(
            text="Frontera Eficiente y Línea del Mercado de Capitales (CML)",
            font=dict(size=16, color=COLOR_TEXTO),
            x=0.02,
            xanchor="left",
        ),
        xaxis=dict(
            title="Volatilidad (Riesgo)",
            tickformat=".0%",
            tickfont=dict(color=COLOR_TEXTO),
            gridcolor="#2a2a2a",
            zerolinecolor="#444444",
            range=[0, x_max],
            dtick=PASO_EJE_X,
            tick0=0,
        ),
        yaxis=dict(
            title="Rendimiento Esperado",
            tickformat=".0%",
            tickfont=dict(color=COLOR_TEXTO),
            gridcolor="#2a2a2a",
            zerolinecolor="#444444",
            range=[0, y_max],
            dtick=PASO_EJE_Y,
            tick0=0,
        ),
        plot_bgcolor=COLOR_FONDO,
        paper_bgcolor=COLOR_FONDO,
        font=dict(color=COLOR_TEXTO, family="Arial, sans-serif"),
        legend=dict(
            bgcolor="rgba(0,0,0,0.6)",
            bordercolor="#444444",
            borderwidth=1,
            font=dict(size=9, color=COLOR_TEXTO),
            y=0.98,
            yanchor="top",
            itemsizing="constant",
            itemwidth=38,
            tracegroupgap=4,
            itemclick=False,
            itemdoubleclick=False,
        ),
        height=600,
        width=1000,
        margin=dict(l=80, r=80, t=80, b=80),
        hovermode="closest",
    )

    return fig
