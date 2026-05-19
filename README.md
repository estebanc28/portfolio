# Portafolio de Inversión con Optimización de Markowitz

Aplicación web interactiva para analizar, optimizar y validar portafolios de inversión a partir de precios históricos mensuales. Desarrollada en **Python** con **Streamlit**, implementa la teoría de Markowitz **sin depender de bibliotecas de optimización de terceros** (por ejemplo, PyPortfolioOpt): los cálculos de riesgo, rendimiento y frontera eficiente se realizan con **NumPy**, **Pandas** y **SciPy**.

El diseño visual sigue un **tema oscuro** inspirado en terminales financieras, con navegación por menú lateral entre las distintas etapas del análisis.

---

## Tabla de contenidos

- [Características principales](#características-principales)
- [Capturas y flujo de uso](#capturas-y-flujo-de-uso)
- [Stack tecnológico](#stack-tecnológico)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos e instalación](#requisitos-e-instalación)
- [Ejecución](#ejecución)
- [Formato del archivo CSV](#formato-del-archivo-csv)
- [Metodología financiera](#metodología-financiera)
- [Pruebas](#pruebas)
- [Documentación adicional](#documentación-adicional)
- [Autor y contexto](#autor-y-contexto)

---

## Características principales

| Sección | Descripción |
|--------|-------------|
| **Inicio** | Presentación del proyecto y guía para comenzar. |
| **Carga y preparación de datos** | Carga del CSV (por defecto o archivo propio), validación de datos faltantes y exclusión automática de activos incompletos. |
| **Inputs y configuración inicial** | Selección de activos, pesos forzados opcionales y tasa libre de riesgo anual (≈ 4 % por defecto). |
| **Optimización y frontera eficiente** | Mapa de calor de correlaciones, tabla comparativa (pesos iguales vs optimizado), gráfico de frontera eficiente + CML e interpretación del gráfico. |
| **Resultados finales y validación histórica** | Tabla de pesos del portafolio optimizado, gráfico de evolución con base $1,000 y comparación con el S&P 500. |

### Detalles relevantes del modelo

- **Optimización de máximo Sharpe** con restricciones long-only y suma de pesos = 100 %.
- **Pesos forzados** respetados en optimización, frontera y resultados finales.
- **Umbral mínimo de peso (0,1 %):** posiciones por debajo se tratan como 0 %, se renormalizan los restantes y se listan como *no utilizadas*.
- **Métricas coherentes:** tabla comparativa, tooltip del gráfico de frontera y punto del portafolio optimizado usan la misma formulación **μ–Σ** de Markowitz.
- **Caché de cálculos** en Streamlit para evitar recálculos al cambiar de sección.
- **Scroll al inicio** al entrar en las secciones con gráficos extensos.

---

## Capturas y flujo de uso

Flujo recomendado en el menú lateral:

```
Inicio
  → Carga y Preparación de Datos
  → Inputs y Configuración Inicial (confirmar configuración)
  → Optimización y Frontera Eficiente
  → Resultados Finales y Validación Histórica
```

1. Cargar y validar el CSV.
2. Elegir empresas, opcionalmente fijar pesos y definir la tasa libre de riesgo; confirmar.
3. Revisar correlaciones, métricas comparativas y frontera eficiente con CML.
4. Consultar pesos finales, evolución histórica ($1,000 inicial) y benchmark S&P 500.

---

## Stack tecnológico

| Tecnología | Uso |
|------------|-----|
| **Python 3.10+** | Lenguaje base (probado con 3.11–3.14) |
| **Streamlit** | Interfaz web y estado de sesión |
| **Plotly** | Gráficos interactivos (correlación, frontera, evolución) |
| **Pandas / NumPy** | Datos y álgebra lineal |
| **SciPy** | Optimización cuadrática (frontera y máximo Sharpe) |

---

## Estructura del proyecto

```
portafolio/
├── portfolio.py              # Punto de entrada de la aplicación Streamlit
├── requirements.txt          # Dependencias
├── README.md
├── documentos/
│   ├── funcionalidades_proyecto.md   # Especificación funcional detallada
│   └── portafolio_21_activos.csv     # Dataset por defecto (60 meses)
├── src/
│   ├── config.py             # Rutas, benchmark, tasa por defecto
│   ├── app/
│   │   ├── navigation.py     # Menú lateral
│   │   ├── theme.py          # Estilos globales (tema oscuro)
│   │   ├── scroll.py         # Scroll al inicio en vistas largas
│   │   └── vistas/           # Pantallas por funcionalidad
│   ├── data/
│   │   └── loader.py         # Carga y validación del CSV
│   ├── finance/
│   │   ├── metricas.py       # Rendimientos, volatilidad, correlación
│   │   ├── markowitz.py      # μ, Σ, optimización MV, métricas unificadas
│   │   ├── portafolio.py     # Pesos iguales, max Sharpe, tabla comparativa
│   │   ├── frontera_eficiente.py
│   │   └── resultados.py     # Pesos finales y evolución histórica
│   └── visualization/        # Figuras Plotly y caché Streamlit
└── tests/                    # Pruebas unitarias
```

---

## Requisitos e instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd portafolio
```

### 2. Crear y activar un entorno virtual (recomendado)

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

> **Nota:** Si ejecutas `streamlit` con un Python distinto al del entorno virtual, instala las dependencias en ese mismo intérprete (`python -m pip install -r requirements.txt`).

---

## Ejecución

Desde la raíz del proyecto:

```bash
streamlit run portfolio.py
```

La aplicación se abrirá en el navegador (por defecto `http://localhost:8501`).

---

## Formato del archivo CSV

El archivo debe incluir:

| Requisito | Detalle |
|-----------|---------|
| **Columna de fechas** | `Date` (formato interpretable por Pandas) |
| **Activos** | Hasta 20 tickers de empresas con precios mensuales |
| **Benchmark** | Columna `^GSPC` (S&P 500) |
| **Frecuencia** | Datos **mensuales** (el proyecto espera ~60 observaciones) |
| **Calidad** | Sin valores faltantes por columna; las columnas incompletas se excluyen automáticamente |

Ejemplo de encabezado:

```text
Date,AAPL,AMZN,...,XOM,^GSPC
```

Puedes usar el archivo incluido en `documentos/portafolio_21_activos.csv` o subir tu propio CSV en la sección de carga.

---

## Metodología financiera

### Rendimientos y anualización

- Rendimientos mensuales simples: \( r_t = P_t / P_{t-1} - 1 \).
- Rendimiento anual esperado (enfoque compuesto para series): capitalización sobre la ventana histórica.
- Volatilidad anual: desviación mensual × \( \sqrt{12} \).

### Espacio Markowitz (μ–Σ)

Usado de forma consistente en frontera, tabla comparativa y tooltips:

- \( \mu_i = (1 + \bar{r}_{i,\text{mensual}})^{12} - 1 \)
- \( \Sigma \) anual = matriz de covarianza mensual × 12
- Rendimiento del portafolio: \( \mu_p = w^\top \mu \)
- Volatilidad: \( \sigma_p = \sqrt{w^\top \Sigma w} \)
- **Sharpe:** \( (\mu_p - r_f) / \sigma_p \)

### Frontera eficiente

- 100 puntos entre \( \min(\mu) \) y \( \max(\mu) \) por activo.
- Para cada rendimiento objetivo se minimiza la varianza (SciPy, SLSQP).
- **CML:** recta tangente al portafolio de máximo Sharpe, extendida hasta \( 2 \times \sigma \) del portafolio tangente.

### Portafolio optimizado final

1. Maximización de Sharpe con restricciones y pesos forzados.
2. Eliminación de pesos &lt; 0,1 % (salvo pesos fijos del usuario).
3. Renormalización a 100 %.

### Validación histórica

Simulación con **$1,000** al inicio del período del CSV:

- Portafolio de pesos iguales (entre activos seleccionados).
- Portafolio optimizado (con restricciones).
- S&P 500 (`^GSPC`) como benchmark.

---

## Pruebas

Ejecutar desde la raíz del proyecto:

```bash
python -m pytest tests/ -q
```

Incluye pruebas de métricas, portafolio, frontera eficiente, resultados, formato de texto y coherencia del Sharpe entre tabla y gráfico.

---

## Documentación adicional

La especificación funcional completa (objetivos, acciones por pantalla y criterios de diseño) está en:

**[`documentos/funcionalidades_proyecto.md`](documentos/funcionalidades_proyecto.md)**

---

## Autor y contexto

Proyecto educativo desarrollado en el marco de formación en **Python aplicado a finanzas** (análisis de datos, optimización de portafolios y visualización interactiva).

Si utilizas este repositorio, ten presente que:

- Los resultados se basan en **datos históricos** y no constituyen asesoría financiera.
- La optimización asume rendimientos y covarianzas estimados a partir del pasado; el desempeño futuro puede diferir.

---

## Licencia

Consulta el archivo `LICENSE` del repositorio si está disponible. En su ausencia, asume uso académico y referencia al autor original del proyecto.
