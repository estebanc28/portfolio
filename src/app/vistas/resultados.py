"""Funcionalidad 4: resultados finales y validación histórica."""

from src.app.vistas.placeholder import mostrar as _placeholder


def mostrar() -> None:
    _placeholder(
        titulo="Resultados Finales y Validación Histórica",
        icono="📊",
        descripcion=(
            "Muestra los pesos del portafolio optimizado y compara su desempeño "
            "histórico frente al portafolio de pesos iguales y el S&P 500."
        ),
        acciones=[
            "Tabla de pesos porcentuales del portafolio optimizado.",
            "Gráfico base 100: igual peso, optimizado y benchmark.",
            'Respuesta a: "Si hubieras invertido $1,000 hace 5 años, ¿cuánto tendrías hoy?"',
        ],
    )
