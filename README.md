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
| Media del riesgo | ~50 |
| Desviación estándar | ~25 |
| P(riesgo ≥ 70) | ~30 % |
| Distribución | Aproximadamente uniforme entre 10 y 90 |

> Con distribuciones uniformes de entrada, la distribución de salida refleja la cobertura del sistema difuso. El ~30% de escenarios críticos indica que el sistema diferencia bien entre situaciones de riesgo.

---

## Parte D — Regresión y Análisis Comparativo

### Métricas de Evaluación

| Modelo | MAE | RMSE | R² |
|---|---|---|---|
| KNN (k=5) | ~7.5 | ~11.0 | ~0.31 |
| Decision Tree | ~2.9 | ~6.4 | ~0.77 |
| **Random Forest** | **~2.4** | **~5.3** | **~0.84** |

### Correlación de Pearson

**r ≈ 0.92** — correlación muy alta entre Random Forest y sistema difuso.

### Importancia de Variables (Random Forest)

| Ranking | Variable | Importancia |
|---|---|---|
| 1° | **promedio_academico** | **~46 %** |
| 2° | horas_estudio | ~25 % |
| 3° | motivacion_estres | ~16 % |
| 4° | inasistencia | ~14 % |

---

## Resumen de Resultados

| Componente | Resultado clave |
|---|---|
| **Delphi** | 4/4 variables aprobadas · 100% consenso · CV < 0.12 |
| **Sistema Difuso** | 27 reglas · 5 niveles · Riesgo muy alto ≈ 82 · Muy bajo ≈ 16 |
| **Montecarlo** | Distribución uniforme · P(riesgo ≥ 70) ≈ 30% con entradas uniformes |
| **Regresión** | Random Forest R² ≈ 0.84 · Pearson r ≈ 0.92 · Variable clave: promedio |

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
Regresión (KNN / Random Forest / Decision Tree)
    │
    └─► R² ≈ 0.84 · Pearson r ≈ 0.92
```

**Principio central:** Ninguna variable, etiqueta, rango ni regla fue inventada. Todo se deriva del consenso del panel de expertos.

---

## Conclusiones

1. **El Delphi garantiza respaldo experto real** — las 4 variables tienen media ≥ 4.0, CV ≤ 0.12 y 100% de aprobación.

2. **El sistema difuso captura comportamiento no lineal** — 27 reglas con 5 niveles de salida producen una distribución continua y diferenciada del riesgo.

3. **La simulación Montecarlo explora todo el espacio de estados** — con distribuciones uniformes, el histograma refleja el comportamiento real del sistema difuso sin sesgos.

4. **El Random Forest valida la coherencia del sistema difuso** — R² ≈ 0.84 y r ≈ 0.92 confirman que el sistema difuso es estadísticamente consistente.

5. **La metodología es transferible** — el mismo flujo se aplicó exitosamente al caso de streaming (Parte E) con adaptaciones mínimas.

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
