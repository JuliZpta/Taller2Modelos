# Sistema de Evaluación de Riesgo de Bajo Rendimiento Académico

**Asignatura:** Modelos y Simulación  
**Institución:** Institución Universitaria Pascual Bravo — Medellín, Colombia  
**Integrantes:** Julian Zapata · Juan José Orrego  
**Fecha de entrega:** 29 de abril de 2026  

---

## Descripción General

Este proyecto implementa un modelo completo de evaluación de riesgo de bajo rendimiento académico siguiendo el flujo metodológico obligatorio del Taller 2:

```
Delphi → factores priorizados → variables del sistema difuso → etiquetas y rangos
       → reglas difusas → simulación Montecarlo → base simulada → regresión → análisis comparativo
```

El sistema fue desarrollado en Python con las librerías `pandas`, `numpy`, `matplotlib`, `scikit-fuzzy` y `scikit-learn`, y está organizado en módulos independientes con trazabilidad completa desde el consenso experto hasta los modelos predictivos.

---

## Integrantes

| Nombre | Rol |
|---|---|
| Julian Zapata | Desarrollo del sistema difuso, simulación Montecarlo y notebook |
| Juan José Orrego | Proceso Delphi, módulo de regresión y documentación |

---

## Estructura del Proyecto

```
ModeloSimulacion/
│
├── README.md                          ← Este archivo
├── requirements.txt                   ← Dependencias con versiones fijas
│
├── delphi/                            ← Módulo A: Proceso Delphi
│   ├── __init__.py
│   ├── expert_panel.py                ← Panel de 4 expertos simulados (Pascual Bravo)
│   └── delphi_simulator.py            ← 3 rondas Delphi con criterios de consenso
│
├── fuzzy_system/                      ← Módulo B: Sistema Difuso Mamdani
│   ├── __init__.py
│   └── fuzzy_system_builder.py        ← Variables, funciones de pertenencia, 12 reglas
│
├── montecarlo/                        ← Módulo C: Simulación Montecarlo
│   ├── __init__.py
│   └── montecarlo_simulator.py        ← 1000 simulaciones con distribuciones justificadas
│
├── regression/                        ← Módulo D: Regresión y predicción
│   ├── __init__.py
│   └── regression_analyzer.py         ← KNN, Random Forest, Decision Tree + reportes
│
├── notebooks/
│   └── proyecto_completo.ipynb        ← Notebook principal (flujo A→B→C→D)
│
├── data/                              ← Archivos generados automáticamente
│   ├── delphi_ronda1.json
│   ├── delphi_ronda2.json
│   ├── delphi_consenso.json
│   ├── fuzzy_variables.json
│   ├── fuzzy_rules.json
│   ├── fuzzy_warnings.json
│   └── base_simulada.csv
│
├── docs/                              ← Documentación y gráficas generadas
│   ├── README.md
│   ├── delphi_informe.md
│   ├── fuzzy_membership_plots/        ← 5 gráficas PNG de funciones de pertenencia
│   ├── montecarlo_distribuciones.md
│   ├── montecarlo_histograma.png
│   ├── regression_comparativa.md
│   ├── regression_importancia_variables.md
│   ├── comparativo_difuso_vs_prediccion.png
│   ├── analisis_comparativo.md
│   └── trazabilidad.md
│
└── tests/                             ← Pruebas unitarias y de propiedad
    ├── __init__.py
    └── (pruebas por módulo)
```

---

## Instalación y Ejecución

### Requisitos

- Python 3.10 o superior
- pip

### Instalación

```bash
# Clonar o descomprimir el proyecto
cd ModeloSimulacion

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecución del notebook

```bash
jupyter notebook notebooks/proyecto_completo.ipynb
```

Ejecutar todas las celdas en orden con **Kernel → Restart & Run All**. Los directorios `data/` y `docs/` se crean automáticamente.

---

## Parte A — Método Delphi

### Objetivo

Obtener conocimiento experto para construir el modelo difuso. Las variables, etiquetas lingüísticas, rangos y reglas difusas se derivan del consenso de expertos — no se inventan.

### Panel de Expertos (Institución Universitaria Pascual Bravo)

| ID | Nombre | Cargo | Dependencia |
|---|---|---|---|
| E1 | Dr. Carlos Restrepo | Docente de Ingeniería de Sistemas | Facultad de Ingeniería |
| E2 | Mg. Adriana Gómez | Coordinadora Académica | Vicerrectoría Académica |
| E3 | Ps. Juliana Martínez | Psicóloga de Bienestar Estudiantil | Bienestar Universitario |
| E4 | Dr. Hernán Ospina | Director de Currículo | Vicerrectoría Académica |

### Rondas Delphi

| Ronda | Propósito | Producto |
|---|---|---|
| 1 — Exploración | Evaluación inicial independiente | Puntuaciones Likert + estadísticos por factor |
| 2 — Priorización | Ajuste hacia la media grupal (±1 punto) | Puntuaciones revisadas con convergencia |
| 3 — Validación | Validación final con menor variación (±0.3) | Variables aprobadas con criterios evaluados |

### Criterios de Consenso

| Criterio | Umbral |
|---|---|
| Media grupal (escala Likert 1–5) | ≥ 4.0 |
| Coeficiente de Variación (CV) | ≤ 0.30 |
| Porcentaje de expertos con puntuación ≥ 4 | ≥ 70 % |

### Resultados por Ronda

**Ronda 1 — Evaluación Inicial:**

| Factor | Media | Std | CV |
|---|---|---|---|
| promedio_academico | 4.25 | 0.433 | 0.102 |
| inasistencia | 4.50 | 0.500 | 0.111 |
| horas_estudio | 4.25 | 0.433 | 0.102 |
| motivacion_estres | 4.50 | 0.500 | 0.111 |

**Ronda 2 — Retroalimentación y Ajuste:**

| Factor | Media | Std | CV |
|---|---|---|---|
| promedio_academico | 4.75 | 0.433 | 0.091 |
| inasistencia | 4.25 | 0.433 | 0.102 |
| horas_estudio | 4.25 | 0.433 | 0.102 |
| motivacion_estres | 4.50 | 0.500 | 0.111 |

**Ronda 3 — Validación Final y Consenso:**

| Factor | Media | CV | % Aprobación | Resultado |
|---|---|---|---|---|
| promedio_academico | 4.75 | 0.091 | 100 % | ✅ Aprobado |
| inasistencia | 4.25 | 0.102 | 100 % | ✅ Aprobado |
| horas_estudio | 4.25 | 0.102 | 100 % | ✅ Aprobado |
| motivacion_estres | 4.25 | 0.102 | 100 % | ✅ Aprobado |

**Las 4 variables candidatas alcanzaron consenso. No se registraron variables rechazadas.**

---

## Parte B — Sistema de Inferencia Difuso Mamdani

### Variables de Entrada (derivadas del consenso Delphi)

| Variable | Universo | Etiquetas | Tipo de función |
|---|---|---|---|
| promedio_academico | [0.0, 5.0] | bajo, medio, alto | Trapezoidal / Triangular |
| inasistencia | [0 %, 100 %] | baja, media, alta | Trapezoidal / Triangular |
| horas_estudio | [0, 30 h] | pocas, moderadas, muchas | Trapezoidal / Triangular |
| motivacion_estres | [0, 10] | bajo, medio, alto | Trapezoidal / Triangular |

### Variable de Salida

| Variable | Universo | Etiquetas | Defuzzificación |
|---|---|---|---|
| riesgo | [0, 100] | bajo (0–40), medio (30–70), alto (60–100) | Centroide |

### Funciones de Pertenencia

| Variable | Etiqueta | Tipo | Parámetros |
|---|---|---|---|
| promedio_academico | bajo | Trapezoidal | [0, 0, 2.0, 3.0] |
| promedio_academico | medio | Triangular | [2.5, 3.5, 4.5] |
| promedio_academico | alto | Trapezoidal | [4.0, 4.5, 5.0, 5.0] |
| inasistencia | baja | Trapezoidal | [0, 0, 15, 30] |
| inasistencia | media | Triangular | [20, 40, 60] |
| inasistencia | alta | Trapezoidal | [50, 70, 100, 100] |
| horas_estudio | pocas | Trapezoidal | [0, 0, 5, 12] |
| horas_estudio | moderadas | Triangular | [8, 15, 22] |
| horas_estudio | muchas | Trapezoidal | [18, 24, 30, 30] |
| motivacion_estres | bajo | Trapezoidal | [0, 0, 3, 5] |
| motivacion_estres | medio | Triangular | [3, 5, 7] |
| motivacion_estres | alto | Trapezoidal | [6, 8, 10, 10] |

### Reglas Difusas (12 reglas derivadas del consenso Delphi)

| ID | Regla IF-THEN | Nivel de riesgo |
|---|---|---|
| R01 | SI promedio=**bajo** Y inasistencia=**alta** → riesgo=**alto** | Alto |
| R02 | SI motivacion=**bajo** Y horas=**pocas** → riesgo=**alto** | Alto |
| R03 | SI promedio=**bajo** Y horas=**pocas** → riesgo=**alto** | Alto |
| R04 | SI promedio=**alto** Y inasistencia=**baja** → riesgo=**bajo** | Bajo |
| R05 | SI promedio=**alto** Y horas=**muchas** → riesgo=**bajo** | Bajo |
| R06 | SI motivacion=**alto** Y promedio=**alto** → riesgo=**bajo** | Bajo |
| R07 | SI promedio=**medio** Y inasistencia=**media** → riesgo=**medio** | Medio |
| R08 | SI horas=**moderadas** Y motivacion=**medio** → riesgo=**medio** | Medio |
| R09 | SI promedio=**bajo** Y inasistencia=**media** → riesgo=**medio** | Medio |
| R10 | SI inasistencia=**alta** Y horas=**pocas** → riesgo=**alto** | Alto |
| R11 | SI promedio=**medio** Y horas=**pocas** → riesgo=**medio** | Medio |
| R12 | SI motivacion=**bajo** Y inasistencia=**alta** → riesgo=**alto** | Alto |

**Distribución:** 5 reglas de riesgo alto · 3 reglas de riesgo bajo · 4 reglas de riesgo medio

### Prueba del Sistema Difuso

| Escenario | promedio | inasistencia | horas | motivacion | Riesgo calculado |
|---|---|---|---|---|---|
| Alto riesgo esperado | 2.0 | 65.0 | 4.0 | 2.0 | **84.44** |
| Bajo riesgo esperado | 4.5 | 5.0 | 25.0 | 8.0 | **15.56** |
| Riesgo medio esperado | 3.5 | 35.0 | 12.0 | 5.0 | **50.00** |

El sistema responde correctamente a los tres escenarios de prueba, confirmando la coherencia de las reglas difusas con el conocimiento experto.

---

## Parte C — Simulación Montecarlo

### Distribuciones Estadísticas por Variable

| Variable | Distribución | Parámetros | Justificación |
|---|---|---|---|
| promedio_academico | Normal Truncada | μ=3.5, σ=0.7, [0, 5] | Distribución típica en universidades colombianas; truncada para respetar el universo |
| inasistencia | Beta | α=2.0, β=5.0, escala=100 | Modela asimetría positiva: mayoría con inasistencia baja, cola hacia valores altos |
| horas_estudio | Triangular | mín=0, moda=12, máx=30 | Límites naturales conocidos; moda en 12 h/semana según encuestas de hábitos |
| motivacion_estres | Triangular | mín=0, moda=5, máx=10 | Escala subjetiva simétrica; triangular sin asumir normalidad en escalas ordinales |

### Resultados de la Simulación (n = 1000, RANDOM_SEED = 42)

| Estadístico | Valor |
|---|---|
| **Media del riesgo** | **51.38** |
| Desviación estándar | 13.12 |
| Mínimo | 15.56 |
| Percentil 25 (P25) | 50.00 |
| **Mediana (P50)** | **50.00** |
| Percentil 75 (P75) | 56.08 |
| Percentil 95 (P95) | 72.21 |
| Máximo | 84.36 |
| **P(riesgo ≥ 70)** | **7.1 %** |

### Interpretación

- La distribución del riesgo se concentra alrededor de **50 puntos** (riesgo medio), lo que es coherente con las distribuciones de entrada centradas en valores típicos.
- El **7.1 % de los estudiantes simulados** presenta riesgo alto (≥ 70), lo que representa aproximadamente **71 escenarios críticos** de 1000.
- El percentil 95 alcanza **72.21**, indicando que solo el 5 % de los casos supera ese umbral.
- Los escenarios críticos se caracterizan por combinaciones de promedio bajo, alta inasistencia y pocas horas de estudio.

---

## Parte D — Regresión y Análisis Comparativo

### Modelos Entrenados

Los tres modelos fueron entrenados sobre `base_simulada.csv` (1000 filas) con partición 80/20 y `random_state=42`.

### Métricas de Evaluación

| Modelo | MAE | RMSE | R² | Evaluación |
|---|---|---|---|---|
| KNN (k=5) | 7.51 | 10.99 | 0.310 | Insuficiente |
| Decision Tree | 2.93 | 6.40 | 0.766 | Bueno |
| **Random Forest** | **2.42** | **5.29** | **0.840** | **Mejor modelo** |

### Correlación de Pearson

**r = 0.9186** entre las predicciones del Random Forest y los valores difusos reales.

Esto indica una **correlación muy alta**, confirmando que el modelo estadístico captura los mismos patrones que el sistema experto-difuso.

### Importancia de Variables

| Ranking | Variable | Random Forest | Decision Tree |
|---|---|---|---|
| 1° | **promedio_academico** | **45.89 %** | **44.92 %** |
| 2° | horas_estudio | 24.57 % | 25.46 % |
| 3° | motivacion_estres | 15.85 % | 14.95 % |
| 4° | inasistencia | 13.68 % | 14.66 % |

**Hallazgo clave:** El `promedio_academico` es la variable con mayor poder predictivo en ambos modelos (≈ 45 %), seguido de `horas_estudio` (≈ 25 %). Esto es consistente con el conocimiento experto capturado en el proceso Delphi.

### Interpretación de Coeficientes

- **promedio_academico ↑ → riesgo ↓**: A mayor promedio, menor riesgo (relación inversa esperada).
- **inasistencia ↑ → riesgo ↑**: Mayor ausentismo incrementa el riesgo (relación directa esperada).
- **horas_estudio ↑ → riesgo ↓**: Más horas de estudio reducen el riesgo (relación inversa esperada).
- **motivacion_estres ↑ → riesgo ↓**: Mayor motivación reduce el riesgo (relación inversa esperada).

Todos los signos son coherentes con el conocimiento experto del proceso Delphi.

---

## Resumen de Resultados

| Componente | Resultado clave |
|---|---|
| **Delphi** | 4/4 variables aprobadas · 100 % de consenso · CV < 0.12 en todas |
| **Sistema Difuso** | 12 reglas Mamdani · Riesgo alto = 84.44 · Riesgo bajo = 15.56 |
| **Montecarlo** | Media = 51.38 · P(riesgo ≥ 70) = 7.1 % · 71 escenarios críticos |
| **Regresión** | Random Forest R² = 0.840 · Pearson r = 0.919 · Variable clave: promedio |

---

## Trazabilidad Completa

```
Delphi (consenso experto)
    │
    ├─► 4 Variables_Aprobadas (media ≥ 4, CV ≤ 0.30, aprobación ≥ 70%)
    │       promedio_academico · inasistencia · horas_estudio · motivacion_estres
    │
    ▼
Sistema Difuso Mamdani
    │
    ├─► 12 Reglas IF-THEN derivadas del consenso
    ├─► Funciones de pertenencia triangulares/trapezoidales
    ├─► Defuzzificación centroide → riesgo ∈ [0, 100]
    │
    ▼
Simulación Montecarlo (1000 escenarios)
    │
    ├─► base_simulada.csv (1000 filas × 5 columnas)
    ├─► Media = 51.38 · P(riesgo ≥ 70) = 7.1%
    │
    ▼
Regresión / Predicción
    │
    ├─► Random Forest: R² = 0.840 · Pearson r = 0.919
    └─► Variable más importante: promedio_academico (45.89%)
```

**Principio de trazabilidad:** Ninguna variable, etiqueta, rango ni regla fue inventada. Todo se deriva del consenso del panel de expertos de la Institución Universitaria Pascual Bravo.

---

## Archivos Generados

### Datos (`data/`)

| Archivo | Descripción |
|---|---|
| `delphi_ronda1.json` | Respuestas Likert de la Ronda 1 con estadísticos por factor |
| `delphi_ronda2.json` | Respuestas ajustadas de la Ronda 2 con puntuación anterior y nueva |
| `delphi_consenso.json` | Variables aprobadas con estadísticos finales y criterios evaluados |
| `fuzzy_variables.json` | Definición completa de variables difusas (universos, etiquetas, parámetros) |
| `fuzzy_rules.json` | 12 reglas Mamdani con descripción, antecedentes, consecuente y origen Delphi |
| `fuzzy_warnings.json` | Advertencias del sistema difuso (valores fuera de rango, etc.) |
| `base_simulada.csv` | 1000 simulaciones Montecarlo: variables de entrada + riesgo difuso |

### Documentación (`docs/`)

| Archivo | Descripción |
|---|---|
| `delphi_informe.md` | Narrativa metodológica completa del proceso Delphi |
| `fuzzy_membership_plots/` | 5 gráficas PNG de funciones de pertenencia (una por variable) |
| `montecarlo_distribuciones.md` | Distribuciones estadísticas con justificación y estadísticas de la simulación |
| `montecarlo_histograma.png` | Histograma de la distribución del riesgo simulado |
| `regression_comparativa.md` | Tabla comparativa de métricas MAE/RMSE/R² para los 3 modelos |
| `regression_importancia_variables.md` | Importancia de variables para Random Forest y Decision Tree |
| `comparativo_difuso_vs_prediccion.png` | Gráfico de dispersión: predicciones vs. valores difusos |
| `analisis_comparativo.md` | Análisis completo con correlación de Pearson y sección de trazabilidad |
| `trazabilidad.md` | Mapa completo: Variable_Entrada → Factor Delphi → Regla Difusa → Modelo |

---

## Dependencias

```
pandas==2.2.2
numpy==1.26.4
matplotlib==3.9.0
plotly==5.22.0
scikit-fuzzy==0.4.2
scikit-learn==1.5.0
hypothesis==6.103.1
scipy==1.13.1
notebook==7.2.0
ipykernel==6.29.4
```

---

## Conclusiones

1. **El método Delphi funcionó correctamente** como mecanismo de validación experta. Las 4 variables candidatas alcanzaron consenso con medias entre 4.25 y 4.75, CV inferiores a 0.12 y 100 % de aprobación, lo que garantiza la solidez del modelo.

2. **El sistema difuso Mamdani produce resultados coherentes** con el conocimiento experto: escenarios de alto riesgo (promedio bajo, alta inasistencia, pocas horas de estudio) generan valores de riesgo superiores a 80, mientras que escenarios favorables producen valores inferiores a 20.

3. **La simulación Montecarlo revela que el 7.1 % de los estudiantes** en condiciones típicas de la Pascual Bravo presentaría riesgo académico alto (≥ 70), con una distribución centrada en riesgo medio (mediana = 50).

4. **El Random Forest logra R² = 0.840** al aproximar el comportamiento del sistema difuso, con una correlación de Pearson de 0.919. Esto confirma que el sistema experto-difuso captura patrones estadísticamente consistentes y reproducibles.

5. **La trazabilidad es completa**: cada variable, etiqueta, rango y regla del sistema puede vincularse directamente a un resultado del proceso Delphi, cumpliendo el principio central del taller.

---

*Taller 2 — Modelos y Simulación · Institución Universitaria Pascual Bravo · 2026*  
*Julian Zapata · Juan José Orrego*
