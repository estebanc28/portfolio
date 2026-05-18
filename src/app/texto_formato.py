"""
Utilidades de formato de texto para la interfaz.
"""

from __future__ import annotations

import re


def capitalizar_palabras_largas(texto: str, umbral: int = 4) -> str:
    """
    Pone en mayúscula la primera letra de cada palabra con más de `umbral` letras.

    Palabras cortas (≤ umbral) quedan en minúsculas. Siglas en mayúsculas (p. ej. CML)
    se conservan.
    """

    def _reemplazar(match: re.Match[str]) -> str:
        palabra = match.group(0)
        if palabra.isupper() and len(palabra) <= 5:
            return palabra
        if len(palabra) > umbral:
            return palabra[0].upper() + palabra[1:].lower()
        return palabra.lower()

    return re.sub(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ]+\b", _reemplazar, texto, flags=re.UNICODE)
