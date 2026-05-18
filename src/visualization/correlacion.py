"""
Visualización de la matriz de correlaciones (Funcionalidad 3 — sección A).

Solo mapa de calor; sin optimización de portafolio ni tablas comparativas.
"""

from __future__ import annotations

import plotly.graph_objects as go
import pandas as pd

# Escala divergente: rojo oscuro (-1) → rojo claro → gris (0) → azul claro → azul oscuro (+1)
ESCALA_CORRELACION = [
    [0.0, "#7B0000"],    # -1.0: rojo más oscuro
    [0.15, "#B71C1C"],   # correlación negativa fuerte
    [0.30, "#E53935"],   # negativa moderada
    [0.42, "#FF8A80"],   # negativa débil, acercándose a 0
    [0.5, "#D5D5D5"],    # 0: gris claro
    [0.58, "#90CAF9"],   # positiva débil, alejándose de 0
    [0.70, "#42A5F5"],   # positiva moderada
    [0.85, "#1565C0"],   # positiva fuerte
    [1.0, "#0A2E5C"],    # +1.0: azul más oscuro
]

COLOR_FONDO = "#000000"
COLOR_TEXTO = "#f0f0f0"


def _color_texto_celda(valor: float) -> str:
    """Contraste legible según la intensidad de la correlación."""
    if abs(valor) >= 0.55:
        return "#ffffff"
    if abs(valor) <= 0.15:
        return "#2a2a2a"
    return "#1a1a1a"


def crear_mapa_calor_correlacion(matriz: pd.DataFrame) -> go.Figure:
    """
    Crea un mapa de calor de correlaciones con fondo negro y etiquetas legibles.

    Parámetros
    ----------
    matriz : pd.DataFrame
        Matriz de correlaciones simétrica (activos × activos).

    Retorna
    -------
    plotly.graph_objects.Figure
    """
    if matriz.empty:
        raise ValueError("La matriz de correlación está vacía.")

    # Eje Y: primer activo arriba. Eje X: orden inverso (abajo→arriba respecto a Y)
    # para que la diagonal principal una mismo activo en ambos ejes (corr = 1, azul).
    etiquetas_y = list(matriz.index)
    etiquetas_x = list(reversed(etiquetas_y))
    valores = matriz.loc[etiquetas_y, etiquetas_x].values
    n = len(etiquetas_y)

    # Altura dinámica para que los nombres en ambos ejes se lean con claridad
    altura = max(520, 36 * n + 180)

    fig = go.Figure(
        data=go.Heatmap(
            z=valores,
            x=etiquetas_x,
            y=etiquetas_y,
            zmin=-1.0,
            zmax=1.0,
            colorscale=ESCALA_CORRELACION,
            colorbar=dict(
                title=dict(text="Correlación", font=dict(color=COLOR_TEXTO, size=12)),
                tickfont=dict(color=COLOR_TEXTO, size=11),
                outlinewidth=0,
                len=0.75,
                thickness=18,
            ),
            hovertemplate=(
                "Activo X: %{x}<br>"
                "Activo Y: %{y}<br>"
                "Correlación: %{z:.3f}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=dict(
            text="Matriz de Correlaciones entre Activos Seleccionados",
            font=dict(size=16, color=COLOR_TEXTO),
            x=0.02,
            xanchor="left",
        ),
        plot_bgcolor=COLOR_FONDO,
        paper_bgcolor=COLOR_FONDO,
        font=dict(color=COLOR_TEXTO, family="Arial, sans-serif"),
        height=altura,
        margin=dict(l=90, r=60, t=70, b=130),
        xaxis=dict(
            side="bottom",
            tickangle=-45,
            tickfont=dict(size=11, color=COLOR_TEXTO),
            showgrid=False,
            linewidth=0,
        ),
        yaxis=dict(
            tickfont=dict(size=11, color=COLOR_TEXTO),
            autorange="reversed",
            showgrid=False,
            linewidth=0,
        ),
    )

    # Valor de correlación en cada casilla (máximo 3 decimales)
    tamano_fuente = max(7, min(10, 14 - n // 2))
    for fila in etiquetas_y:
        for col in etiquetas_x:
            valor = float(matriz.loc[fila, col])
            fig.add_annotation(
                x=col,
                y=fila,
                text=f"{valor:.3f}",
                showarrow=False,
                font=dict(size=tamano_fuente, color=_color_texto_celda(valor)),
            )

    return fig
