from pathlib import Path

# Raíz del proyecto (carpeta que contiene src/, documentos/, portfolio.py)
RAIZ_PROYECTO = Path(__file__).resolve().parent.parent

# Archivo CSV por defecto según documentación del proyecto
RUTA_CSV_DEFECTO = RAIZ_PROYECTO / "documentos" / "portafolio_21_activos.csv"

# Columna de fechas y ticker del benchmark (S&P 500)
COLUMNA_FECHA = "Date"
TICKER_BENCHMARK = "^GSPC"

# Tasa libre de riesgo por defecto (Treasury 10 años ≈ 4% anual)
TASA_LIBRE_RIESGO_DEFAULT_ANUAL = 0.04
