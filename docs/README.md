# Sistema de Evaluación de Riesgo de Bajo Rendimiento Académico

## Institución Universitaria Pascual Bravo — Medellín, Colombia

---

## Descripción del proyecto

Este sistema implementa un flujo metodológico de cuatro etapas para evaluar el riesgo de bajo rendimiento académico estudiantil en la Institución Universitaria Pascual Bravo (Medellín, Colombia):

1. **Delphi** — Priorización y validación de factores mediante un panel de expertos simulado (docente universitario, coordinador académico, psicóloga de bienestar estudiantil y directivo académico). Se ejecutan tres rondas: exploración, priorización y validación con consenso.

2. **Sistema Difuso Mamdani** — Inferencia del nivel de riesgo a partir de los factores validados por el proceso Delphi. Utiliza funciones de pertenencia triangulares y trapezoidales, reglas IF-THEN derivadas del consenso experto y defuzzificación por centroide.

3. **Simulación Montecarlo** — Estimación de la distribución de probabilidad del riesgo académico mediante 1 000 simulaciones del sistema difuso con valores muestreados según distribuciones estadísticas justificadas (normal truncada, beta, triangular).

4. **Regresión/Predicción** — Comparación entre el enfoque difuso y modelos estadísticos (KNN, Random Forest, Árbol de Decisión) entrenados sobre la base simulada. Incluye análisis de importancia de variables y correlación de Pearson.

El diseño prioriza **trazabilidad** (cada decisión se vincula a un resultado Delphi documentado), **reproducibilidad** (semilla global `RANDOM_SEED = 42`) y **modularidad** (cada etapa es un módulo Python independiente).

---

## Instalación

Requiere Python 3.10 o superior. Se recomienda usar un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

---

## Ejecución

Abrir y ejecutar el notebook principal en orden secuencial desde la primera celda:

```bash
jupyter notebook notebooks/proyecto_completo.ipynb
```

O con JupyterLab:

```bash
jupyter lab notebooks/proyecto_completo.ipynb
```

**Importante:** ejecutar todas las celdas en orden (Kernel → Restart & Run All) para garantizar la reproducibilidad completa del flujo. Los directorios `data/` y `docs/` se crean automáticamente durante la ejecución.

---

## Entregables

### Archivos generados en `data/`

| Archivo | Descripción |
|---|---|
| `delphi_ronda1.json` | Respuestas Likert de la Ronda 1 (exploración) con estadísticos por factor |
| `delphi_ronda2.json` | Respuestas ajustadas de la Ronda 2 (priorización) con puntuación anterior y nueva |
| `delphi_consenso.json` | Variables aprobadas con estadísticos finales y criterios de consenso evaluados |
| `fuzzy_variables.json` | Definición completa de variables difusas: universos, etiquetas y parámetros de funciones de pertenencia |
| `fuzzy_rules.json` | Reglas Mamdani IF-THEN con descripción, antecedentes, consecuente y origen Delphi |
| `fuzzy_warnings.json` | Advertencias del sistema difuso (valores fuera del universo, regiones no cubiertas) |
| `base_simulada.csv` | Base de datos con 1 000 simulaciones Montecarlo: variables de entrada y riesgo difuso |

### Archivos generados en `docs/`

| Archivo | Descripción |
|---|---|
| `delphi_informe.md` | Narrativa metodológica del proceso Delphi: perfiles del panel, respuestas por ronda, estadísticos y justificación de variables aprobadas |
| `fuzzy_membership_plots/` | Gráficas de funciones de pertenencia para cada variable difusa (una imagen por variable) |
| `montecarlo_distribuciones.md` | Distribuciones estadísticas utilizadas en el muestreo Montecarlo con justificación por variable |
| `montecarlo_histograma.png` | Histograma de la distribución del riesgo simulado |
| `regression_comparativa.md` | Tabla comparativa de métricas (MAE, RMSE, R²) para los tres modelos de predicción |
| `regression_importancia_variables.md` | Importancia de variables para Random Forest y Árbol de Decisión |
| `comparativo_difuso_vs_prediccion.png` | Gráfico de dispersión: predicciones del mejor modelo vs. valores difusos |
| `analisis_comparativo.md` | Análisis comparativo completo: métricas, correlación de Pearson, interpretación de importancias y sección de trazabilidad |
| `trazabilidad.md` | Mapa completo de trazabilidad: Variable_Entrada → Factor Delphi → estadísticos de consenso; Regla_Difusa → justificación experta |
| `README.md` | Este archivo |

---

## Estructura del proyecto

```
ModeloSimulacion/
│
├── data/                          # Archivos de datos generados (JSON, CSV)
│   ├── delphi_ronda1.json
│   ├── delphi_ronda2.json
│   ├── delphi_consenso.json
│   ├── fuzzy_variables.json
│   ├── fuzzy_rules.json
│   ├── fuzzy_warnings.json
│   └── base_simulada.csv
│
├── delphi/                        # Módulo Delphi
│   ├── __init__.py
│   ├── expert_panel.py            # ExpertPanel y dataclass Expert
│   └── delphi_simulator.py        # DelphiSimulator (3 rondas)
│
├── fuzzy_system/                  # Módulo Sistema Difuso Mamdani
│   ├── __init__.py
│   └── fuzzy_system_builder.py    # FuzzySystemBuilder + evaluar_riesgo()
│
├── montecarlo/                    # Módulo Simulación Montecarlo
│   ├── __init__.py
│   └── montecarlo_simulator.py    # MontecarloSimulator
│
├── regression/                    # Módulo Regresión/Predicción
│   ├── __init__.py
│   └── regression_analyzer.py     # RegressionAnalyzer
│
├── notebooks/                     # Notebook principal
│   └── proyecto_completo.ipynb    # Orquestador del flujo completo
│
├── docs/                          # Documentación y gráficas generadas
│   ├── README.md
│   ├── delphi_informe.md
│   ├── fuzzy_membership_plots/
│   ├── montecarlo_distribuciones.md
│   ├── montecarlo_histograma.png
│   ├── regression_comparativa.md
│   ├── regression_importancia_variables.md
│   ├── comparativo_difuso_vs_prediccion.png
│   ├── analisis_comparativo.md
│   └── trazabilidad.md
│
├── tests/                         # Pruebas unitarias y de propiedad
│   ├── __init__.py
│   ├── test_delphi.py
│   ├── test_fuzzy_system.py
│   ├── test_montecarlo.py
│   ├── test_regression.py
│   └── test_integration.py
│
└── requirements.txt               # Dependencias con versiones fijas
```
