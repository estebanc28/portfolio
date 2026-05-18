 # 📄 Documento de Funcionalidades del Proyecto 

### **Portafolio de Inversión con Optimización de Markowitz** 

**Fecha:** Mayo 2026 

**Tecnologías:** Python + Streamlit + Plotly + Pandas + NumPy + SciPy 



---



## 🎯 Descripción General



Este proyecto tiene como objetivo construir una aplicación interactiva que permita analizar y optimizar un portafolio de inversión a partir de datos históricos de precios de **20 empresas** y del índice **S&P 500**.



A diferencia de otros enfoques tradicionales, **no se utilizaran bibliotecas externas como PyPortfolioOpt**. 

En su lugar, se implementaran todos los cálculos de riesgo, rendimiento y optimización directamente en **Python puro** (NumPy + SciPy), para no depender de librerías de terceros que puedan quedar obsoletas.



La aplicación contará con dos decisiones de diseño globales:



1. **Tema oscuro (fondo negro):** 

   Diseño inspirado en terminales financieras tipo Bloomberg, con colores de contraste (azul, verde, rojo, morado, blanco). 

2. **Navegación por menú lateral en Streamlit:** 

   Cada funcionalidad principal tendrá su propia sección: 

   - Inputs y Configuración Inicial 

   - Análisis de Riesgos y Dependencias 

   - Optimización y Frontera Eficiente 

   - Resultados Finales y Validación Histórica 



---



## 🛠 Funcionalidad 0: Carga y Preparación de Datos



**Objetivo:** Garantizar que el análisis se realice únicamente con datos consistentes y completos.



### Acciones:

- Cargar automáticamente el archivo CSV con datos históricos (fechas + 20 empresas + S&P 500). 

- Validar si existen datos faltantes en alguna empresa. 

- **Excluir automáticamente** los activos con datos incompletos. 

- Generar un mensaje informativo al usuario, por ejemplo: 

  *“Se omitió la empresa XYZ por datos incompletos.”* 

- Continuar a la Funcionalidad 1 únicamente con los activos válidos.



---



## 🧩 Funcionalidad 1: Inputs y Configuración Inicial



**Objetivo:** Definir el universo de inversión y los supuestos principales del modelo.



### Acciones:

- Mostrar un listado de empresas disponibles (ya filtradas en la Funcionalidad 0). 

- Permitir que el usuario **deseleccione** activos que no quiere incluir. 

- Permitir que el usuario **fuerce pesos específicos** para ciertos activos (ejemplo: Visa = 15%). 

- Input para ingresar la **tasa libre de riesgo** (valor por defecto ≈ Treasury 10 años ≈ 4% anual). 

  - Internamente, esta tasa se convierte a **mensual** para los cálculos. 

- Botón de confirmación para fijar el universo de activos y avanzar al análisis.



---



## 📉 Funcionalidad 2: Análisis de Riesgos y Dependencias



**Objetivo:** Comprender cómo interactúan los activos y qué implicaciones tiene la diversificación.



### Acciones:

- Mostrar la **matriz de correlaciones / covarianzas** como un **mapa de calor** sobre fondo negro. 

   - Rojo → correlaciones negativas 

   - Verde/Azul → correlaciones positivas 

- Generar una **tabla comparativa** entre: 

   - Portafolio de **pesos iguales** 

   - Portafolio **optimizado** (cálculo en Python puro) 

- Mostrar métricas **anualizadas** para ambos escenarios: 

   - Rendimiento esperado 

   - Volatilidad (riesgo) 

   - Ratio de Sharpe 



---



## 📈 Funcionalidad 3: Optimización y Frontera Eficiente



**Objetivo:** Visualizar la lógica de la optimización de Markowitz y el impacto de la tasa libre de riesgo.



### Acciones:

- Cálculo de la **frontera eficiente** mediante **optimización cuadrática con SciPy**. 

- Gráfico sobre fondo negro que muestre: 

   - Curva completa de la frontera eficiente (riesgo vs. rendimiento). 

   - Punto del **portafolio de pesos iguales**. 

   - Punto del **portafolio optimizado** (máxima razón de Sharpe). 

- Inclusión de la **Línea del Mercado de Capitales (CML)** utilizando la tasa libre de riesgo definida en la Funcionalidad 1.

- Bloque **Interpretación del Gráfico** debajo del gráfico (dos tarjetas): frontera eficiente y CML, con viñetas explicativas y capitalización fija según el diseño de referencia (no aplica la regla de la leyenda).

- En la **leyenda** del gráfico, capitalizar la primera letra de cada palabra con más de 4 letras (siglas como CML se conservan).



---



## 📊 Funcionalidad 4: Resultados Finales y Validación Histórica



**Objetivo:** Mostrar los resultados del portafolio optimizado y compararlos con el mercado.



### Acciones:

- Tabla con los **pesos porcentuales del portafolio optimizado**: 

   - Solo se muestran los activos seleccionados. 

   - Los activos no elegidos quedan con peso 0. 

- Tabla **horizontal** de pesos del portafolio optimizado (solo columnas con peso **&gt; 0 %**; respeta pesos fijos).

   - Tras optimizar, activos con peso **&lt; 0,1 %** se eliminan del portafolio final (se muestran como **0 %**), se renormalizan los restantes y se listan como *no utilizados*.

- Gráfico de evolución histórica (valor inicial **$1,000**, ventana del CSV) con fondo negro, ejes *Tiempo* y *Valor Acumulado*, para: 

   - Portafolio de pesos iguales (entre activos seleccionados) 

   - Portafolio optimizado (con restricciones si las hubiera) 

   - S&P 500 como **benchmark** 

- La tabla va **arriba** y el gráfico **debajo**.

- Responder explícitamente la pregunta: 

  > **“Si hubieras invertido $1,000 en el periodo seleccionado, ¿cuánto tendrías hoy?”**

- **Nota explicativa** al final del gráfico (dos columnas): composición del portafolio de pesos iguales y del optimizado.



---



## 🧭 Propósito del Documento



Este documento funciona como la guía estructural del proyecto y permite:



- Pensar antes de programar. 

- Definir claramente qué se quiere construir. 

- Comunicar la visión a la Inteligencia Artificial para que genere código de forma precisa. 

- Asegurar que todas las funcionalidades se integren de manera coherente.



---

