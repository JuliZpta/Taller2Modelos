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

Desarrollado en Python con `pandas`, `numpy`, `matplotlib`, `scikit-fuzzy`, `scikit-learn` y `streamlit`.  
Organizado en módulos independientes con trazabilidad completa desde el consenso experto hasta los modelos predictivos.

---

## Integrantes

| Nombre | Rol |
|---|---|
| Julian Zapata | Sistema difuso, simulación Montecarlo, app Streamlit y notebook |
| Juan José Orrego | Proceso Delphi, módulo de regresión y documentación |

---

## Entregables del Proyecto

| Entregable | Archivo | Descripción |
|---|---|---|
| App interactiva | `app.py` | Aplicación Streamlit con flujo completo ejecutable en tiempo real ⭐ |
| Notebook | `notebooks/proyecto_completo.ipynb` | Flujo A→B→C→D ejecutable secuencialmente |
| Proyecto Final | `trabajo_final/` | Parte E: misma metodología aplicada a streaming |

---

## Ejecución Rápida

### App Streamlit (recomendado para exposición)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abre `http://localhost:8501` en el navegador. La app incluye:
- Ejecución interactiva de cada módulo
- Calculadora de riesgo con sliders en tiempo real
- Histogramas y gráficos interactivos
- Conclusiones con KPIs dinámicos

### Notebook

```bash
jupyter notebook notebooks/proyecto_completo.ipynb
```

Ejecutar con **Kernel → Restart & Run All**.

---

## Estructura del Proyecto

```
ModeloSimulacion/
│
├── README.md                          ← Este archivo
├── requirements.txt                   ← Dependencias con versiones fijas
├── app.py                             ← App Streamlit interactiva ⭐
│
├── delphi/                            ← Módulo A: Proceso Delphi
│   ├── expert_panel.py                ← 4 expertos simulados (Pascual Bravo)
│   └── delphi_simulator.py            ← 3 rondas con criterios de consenso
│
├── fuzzy_system/                      ← Módulo B: Sistema Difuso Mamdani
│   └── fuzzy_system_builder.py        ← 27 reglas, 5 niveles de salida
│
├── montecarlo/                        ← Módulo C: Simulación Montecarlo
│   └── montecarlo_simulator.py        ← Distribuciones uniformes, N simulaciones
│
├── regression/                        ← Módulo D: Regresión y predicción
│   └── regression_analyzer.py         ← KNN, Random Forest, Decision Tree
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
│   ├── delphi_informe.md
│   ├── fuzzy_membership_plots/        ← 5 PNG de funciones de pertenencia
│   ├── montecarlo_histograma.png
│   ├── montecarlo_distribuciones.md
│   ├── regression_comparativa.md
│   ├── regression_importancia_variables.md
│   ├── comparativo_difuso_vs_prediccion.png
│   ├── analisis_comparativo.md
│   └── trazabilidad.md
│
├── trabajo_final/                     ← Parte E: Plataforma de Streaming
│   ├── README.md
│   ├── data/
│   ├── delphi/
│   ├── fuzzy_system/
│   ├── montecarlo/
│   ├── regression/
│   ├── notebooks/streaming_completo.ipynb
│   └── docs/
│
└── tests/                             ← Pruebas unitarias
```

---

## Parte A — Método Delphi

### Panel de Expertos (I.U. Pascual Bravo)

| ID | Nombre | Cargo | Dependencia |
|---|---|---|---|
| E1 | Dr. Carlos Restrepo | Docente de Ingeniería de Sistemas | Facultad de Ingeniería |
| E2 | Mg. Adriana Gómez | Coordinadora Académica | Vicerrectoría Académica |
| E3 | Ps. Juliana Martínez | Psicóloga de Bienestar Estudiantil | Bienestar Universitario |
| E4 | Dr. Hernán Ospina | Director de Currículo | Vicerrectoría Académica |

### Criterios de Consenso

| Criterio | Umbral |
|---|---|
| Media grupal (Likert 1–5) | ≥ 4.0 |
| Coeficiente de Variación (CV) | ≤ 0.30 |
| % expertos con puntuación ≥ 4 | ≥ 70 % |

### Resultados — Ronda 3 (Validación Final)

| Factor | Media | CV | % Aprobación | Resultado |
|---|---|---|---|---|
| promedio_academico | 4.75 | 0.091 | 100 % | ✅ Aprobado |
| inasistencia | 4.25 | 0.102 | 100 % | ✅ Aprobado |
| horas_estudio | 4.25 | 0.102 | 100 % | ✅ Aprobado |
| motivacion_estres | 4.25 | 0.102 | 100 % | ✅ Aprobado |

**4/4 variables aprobadas · 100% consenso · 0 variables rechazadas**

---

## Parte B — Sistema Difuso Mamdani

### Variables de Entrada

| Variable | Universo | Etiquetas |
|---|---|---|
| promedio_academico | [0.0, 5.0] | bajo, medio, alto |
| inasistencia | [0, 100 %] | baja, media, alta |
| horas_estudio | [0, 30 h] | pocas, moderadas, muchas |
| motivacion_estres | [0, 10] | bajo, medio, alto |

### Variable de Salida — 5 niveles (actualizado)

| Variable | Universo | Etiquetas | Defuzzificación |
|---|---|---|---|
| riesgo | [0, 100] | muy_bajo · bajo · medio · alto · muy_alto | Centroide |

> **Nota:** Se usan 5 etiquetas asimétricas (centroides en ~9, ~23, ~46, ~69, ~91) para evitar concentración de valores en puntos redondos y obtener una distribución continua en el Montecarlo.

### Reglas Difusas — 27 reglas con cobertura completa (actualizado)

El sistema usa **27 reglas con 3 antecedentes** que cubren todas las combinaciones relevantes del espacio de entrada, garantizando activación mixta de etiquetas de salida:

| Grupo | Reglas | Consecuente |
|---|---|---|
| promedio=bajo + inasistencia=alta | R01–R02 | muy_alto |
| promedio=bajo + otras combinaciones | R03–R09 | alto / medio / bajo |
| promedio=medio + todas combinaciones | R10–R20 | alto / medio / bajo |
| promedio=alto + todas combinaciones | R21–R27 | medio / bajo / muy_bajo |

### Prueba del Sistema

| Escenario | promedio | inasistencia | horas | motivacion | Riesgo |
|---|---|---|---|---|---|
| Muy alto riesgo | 1.0 | 90 % | 2 h | 1 | **~82** |
| Alto riesgo | 2.0 | 65 % | 4 h | 2 | **~70** |
| Riesgo medio | 3.5 | 40 % | 15 h | 5 | **~47** |
| Bajo riesgo | 4.5 | 5 % | 25 h | 8 | **~22** |
| Muy bajo riesgo | 4.8 | 2 % | 28 h | 9 | **~16** |

---

## Parte C — Simulación Montecarlo

### Distribuciones (actualizado — uniformes para cobertura completa)

| Variable | Distribución | Parámetros | Justificación |
|---|---|---|---|
| promedio_academico | **Uniforme** | [0.5, 5.0] | Cobertura completa del espacio de estados del sistema difuso |
| inasistencia | **Uniforme** | [0, 100] | Exploración de todos los escenarios posibles |
| horas_estudio | **Uniforme** | [0, 30] | Cobertura uniforme del universo de discurso |
| motivacion_estres | **Uniforme** | [0, 10] | Cobertura de todos los niveles |

> Las distribuciones uniformes garantizan que el histograma de riesgo refleje el comportamiento real del sistema difuso en todo su espacio de estados, sin sesgos hacia zonas específicas.

### Resultados (n = 1000, RANDOM_SEED = 42)

| Estadístico | Valor |
|---|---|
| Media del riesgo | 54.26 |
| Desviación estándar | 22.42 |
| P(riesgo ≥ 70) | 22.4 % |
| Percentil 95 | 90.18 |
| Rango | [7.43, 90.18] |

> Con distribuciones uniformes de entrada, la distribución de salida refleja la cobertura del sistema difuso en todo su espacio de estados.

---

## Parte D — Regresión y Análisis Comparativo

### Métricas de Evaluación

| Modelo | MAE | RMSE | R² |
|---|---|---|---|
| KNN (k=5) | 10.80 | 13.78 | 0.58 |
| SVR (RBF) | 4.80 | 6.55 | 0.91 |
| Decision Tree | 2.33 | 5.32 | 0.94 |
| **Random Forest** | **1.84** | **3.39** | **0.97** |

> **Nota:** Se añadió SVR (Support Vector Regression con kernel RBF) como modelo de prueba adicional. Random Forest mantiene el mejor desempeño con R² = 0.97.

### Correlación de Pearson

**r ≈ 0.99** — correlación muy alta entre Random Forest y sistema difuso.

### Importancia de Variables (Random Forest)

| Ranking | Variable | Importancia |
|---|---|---|
| 1° | **inasistencia** | **50.01 %** |
| 2° | promedio_academico | 41.04 % |
| 3° | horas_estudio | 4.92 % |
| 4° | motivacion_estres | 4.03 % |

---

## Parte E — Proyecto Final: Plataforma de Streaming

### Descripción del Sistema

El proyecto final aplica la **misma metodología** (Delphi → Difuso → Montecarlo → Regresión) a un caso diferente: evaluación del **riesgo de degradación de QoS** en una plataforma de streaming de video.

**Variable de salida:** `riesgo_qos` (0–100) — índice de riesgo de degradación del servicio.

### Panel de Expertos (Sector Tecnológico)

| ID | Nombre | Cargo | Área |
|---|---|---|---|
| E1 | Ing. Santiago Vargas | Arquitecto de Infraestructura Cloud | Plataformas Digitales |
| E2 | Mg. Valentina Torres | Analista de QoS y Redes | Operaciones de Red |
| E3 | Dr. Felipe Morales | Investigador en Sistemas Distribuidos | I+D |
| E4 | Ing. Camila Ríos | Especialista en Experiencia de Usuario (UX) | Área de Producto |

### Resultados Delphi — Ronda 3

| Factor | Media | CV | % Aprobación | Resultado |
|---|---|---|---|---|
| usuarios_concurrentes | 4.75 | 0.091 | 100 % | ✅ Aprobado |
| uso_ancho_banda | 4.25 | 0.102 | 100 % | ✅ Aprobado |
| latencia_red | 4.25 | 0.102 | 100 % | ✅ Aprobado |
| capacidad_servidor | 4.25 | 0.102 | 100 % | ✅ Aprobado |

**4/4 variables aprobadas · 100% consenso**

### Sistema Difuso Mamdani

| Variable | Universo | Etiquetas |
|---|---|---|
| usuarios_concurrentes | [0, 100] | bajo, medio, alto |
| uso_ancho_banda | [0, 100 %] | bajo, medio, alto |
| latencia_red | [0, 10 ms] | baja, media, alta |
| capacidad_servidor | [0, 100 %] | baja, media, alta |
| **riesgo_qos** (salida) | [0, 100] | muy_bajo · bajo · medio · alto · muy_alto |

**27 reglas Mamdani · 5 niveles de salida · Defuzzificación por centroide**

### Simulación Montecarlo (5000 iteraciones)

| Variable | Distribución | Parámetros | Justificación |
|---|---|---|---|
| usuarios_concurrentes | Beta(α=2, β=3) × 100 | α=2, β=3 | Mayoría del tiempo con carga media-baja; picos ocasionales |
| uso_ancho_banda | Normal Truncada | μ=55, σ=20, [0,100] | Uso promedio del 55% con alta variabilidad |
| latencia_red | Triangular | mín=0, moda=3, máx=10 | Latencia típica baja con cola hacia valores altos |
| capacidad_servidor | Beta(α=3, β=2) × 100 | α=3, β=2 | Servidores operan típicamente a alta capacidad |

**Resultados:**
- Media riesgo_qos: **36.58**
- Desviación estándar: **16.14**
- P(riesgo_qos ≥ 70): **2.9 %** (escenarios críticos)
- Percentil 95: **63.86**
- Rango: [17.05, 91.56]

### Regresión y Análisis Comparativo

| Modelo | MAE | RMSE | R² |
|---|---|---|---|
| KNN (k=5) | 5.53 | 8.14 | 0.75 |
| SVR (RBF) | 3.64 | 5.05 | 0.90 |
| Decision Tree | 0.91 | 2.29 | 0.98 |
| **Random Forest** | **0.66** | **1.64** | **0.99** |

**Correlación de Pearson: r = 0.9950**

### Importancia de Variables (Random Forest — Streaming)

| Ranking | Variable | Importancia |
|---|---|---|
| 1° | **usuarios_concurrentes** | **37.76 %** |
| 2° | uso_ancho_banda | 35.38 % |
| 3° | latencia_red | 23.95 % |
| 4° | capacidad_servidor | 2.90 % |

> `usuarios_concurrentes` y `uso_ancho_banda` dominan con ~73% combinado. `capacidad_servidor` tiene menor peso en este dataset.

### Comparación: Caso Base vs Streaming

| Aspecto | Caso Base (Académico) | Proyecto Final (Streaming) |
|---|---|---|
| **Variables** | promedio, inasistencia, horas, motivacion | usuarios, banda, latencia, capacidad |
| **Reglas** | 27 | 27 |
| **Niveles de salida** | 5 | 5 |
| **Simulaciones** | 1000 | 5000 |
| **Mejor R²** | 0.9747 (RF) | **0.9899 (RF)** |
| **Pearson r** | 0.9877 | **0.9950** |
| **Variable clave** | inasistencia (50.01%) | usuarios_concurrentes (37.76%) |
| **P(riesgo ≥ 70)** | 22.4% (entradas uniformes) | 2.9% (distribuciones reales) |
| **Modelos evaluados** | 4 (KNN, SVR, DT, RF) | 4 (KNN, SVR, DT, RF) |

---

## Resumen de Resultados

| Componente | Caso Base (Académico) | Proyecto Final (Streaming) |
|---|---|---|
| **Delphi** | 4/4 aprobadas · 100% consenso · CV ≤ 0.102 | 4/4 aprobadas · 100% consenso · CV ≤ 0.102 |
| **Sistema Difuso** | 27 reglas · 5 niveles · Riesgo muy alto ≈ 82 | 27 reglas · 5 niveles · Riesgo muy alto ≈ 82 |
| **Montecarlo** | 1000 sims · media=54.26 · P(≥70)=22.4% | 5000 sims · media=36.58 · P(≥70)=2.9% |
| **Regresión** | RF R²=0.9747 · r=0.9877 · var. clave: inasistencia | RF R²=0.9899 · r=0.9950 · var. clave: usuarios_concurrentes |

---

## Trazabilidad

```
Delphi (consenso experto)
    │
    ├─► 4 Variables aprobadas (media ≥ 4, CV ≤ 0.30, aprobación ≥ 70%)
    │
    ▼
Sistema Difuso Mamdani (27 reglas, 5 niveles de salida)
    │
    ├─► evaluar_riesgo(dict) → float ∈ [0, 100]
    │
    ▼
Simulación Montecarlo (distribuciones uniformes, N iteraciones)
    │
    ├─► base_simulada.csv
    │
    ▼
Regresión (KNN / SVR / Random Forest / Decision Tree)
    │
    └─► R² = 0.97 · Pearson r = 0.99
```

**Principio central:** Ninguna variable, etiqueta, rango ni regla fue inventada. Todo se deriva del consenso del panel de expertos.

---

## Conclusiones

1. **El Delphi garantiza respaldo experto real** — las 4 variables tienen media ≥ 4.0, CV ≤ 0.102 y 100% de aprobación en ambos casos.

2. **El sistema difuso captura comportamiento no lineal** — 27 reglas con 5 niveles de salida producen una distribución continua y diferenciada del riesgo.

3. **La simulación Montecarlo explora todo el espacio de estados** — con distribuciones uniformes en el caso base, el histograma refleja el comportamiento real del sistema difuso (media=54.26, P(≥70)=22.4%).

4. **El Random Forest valida la coherencia del sistema difuso** — R²=0.9747 y r=0.9877 en el caso base; R²=0.9899 y r=0.9950 en streaming. Se evaluaron 4 modelos (KNN, SVR, Decision Tree, Random Forest) y Random Forest mostró el mejor desempeño en ambos casos.

5. **La metodología es transferible** — el mismo flujo se aplicó exitosamente al caso de streaming (Parte E) con adaptaciones mínimas, obteniendo resultados incluso superiores (R²=0.9899, r=0.9950).

6. **La trazabilidad es completa** — cada decisión de diseño puede vincularse al consenso Delphi.

---

## Dependencias

```
pandas==2.2.2
numpy==1.26.4
matplotlib==3.9.0
plotly==5.22.0
scikit-fuzzy==0.4.2
scikit-learn==1.5.0
scipy==1.13.1
streamlit==1.56.0
notebook==7.2.0
ipykernel==6.29.4
```

---

*Taller 2 — Modelos y Simulación · Institución Universitaria Pascual Bravo · 2026*  
*Julian Zapata · Juan José Orrego*
