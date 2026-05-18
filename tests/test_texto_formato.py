"""Pruebas de formato de texto para leyendas e interpretación."""

from src.app.texto_formato import capitalizar_palabras_largas


def test_capitaliza_solo_palabras_largas():
    assert capitalizar_palabras_largas("Frontera eficiente") == "Frontera Eficiente"
    assert capitalizar_palabras_largas("tasa libre de riesgo") == "tasa Libre de Riesgo"


def test_conserva_siglas():
    assert "CML" in capitalizar_palabras_largas("CML (Linea del Mercado de Capitales)")
