# Parte E — Simulación de Plataforma de Streaming

**Asignatura:** Modelos y Simulación  
**Taller:** Taller 2 — Método Delphi, Sistema Difuso, Montecarlo y Regresión  
**Institución:** Institución Universitaria Pascual Bravo — Medellín, Colombia  
**Integrantes:** Julian Zapata · Juan José Orrego  
**Fecha:** Abril 2026

---

## Descripción del Sistema

El sistema modela una **plataforma de streaming de video** (similar a Netflix, YouTube o Twitch) donde múltiples usuarios compiten por recursos limitados del servidor. Cuando la demanda excede la capacidad, se producen retardos, degradación de calidad y desconexiones.

**Variable de salida:** `riesgo_qos` (0–100) — índice de riesgo de degradación del servicio.

### Tipo de modelo

| Característica | Clasificación |
|---|---|
| Tipo | Difuso / Estocástico / Eventos discretos |
| Temporalidad | Dinámico |
| Linealidad | No lineal |
| Apertura | Abierto |

---

## Ejecución

```bash
# Desde la raíz del proyecto principal
pip install -r requirements.txt

# Notebook
jupyter notebook trabajo_final/notebooks/streaming_completo.ipynb

# O desde la app Streamlit (sección Parte E)
streamlit run app.py
```

---

## Flujo Metodológico

```
Delphi (4 expertos sector tecnológico)
    │
    ├─► 4 variables aprobadas (media ≥ 4, CV ≤ 0.30, aprobación ≥ 70%)
    │       usuarios_concurrentes · uso_ancho_banda · latencia_red · capacidad_servidor
    │
    ▼
Sistema Difuso Mamdani (27 reglas, 5 niveles de salida)
    │
    ├─► evaluar_riesgo(dict) → riesgo_qos ∈ [0, 100]
    │
    ▼
Simulación Montecarlo (5000 escenarios, RANDOM_SEED = 42)
    │
    ├─► base_simulada_streaming.csv (5000 filas × 5 columnas)
    │
    ▼
Regresión (KNN / Random Forest / Decision Tree)
    │
    └─► Random Forest R² = 0.966 · Pearson r = 0.983
```

---

## Parte A — Método Delphi

### Panel de Expertos (Sector Tecnológico)

| ID | Nombre | Cargo | Área |
|---|---|---|---|
| E1 | Ing. Santiago Vargas | Arquitecto de Infraestructura Cloud | Plataformas Digitales |
| E2 | Mg. Valentina Torres | Analista de QoS y Redes | Operaciones de Red |
| E3 | Dr. Felipe Morales | Investigador en Sistemas Distribuidos | I+D |
| E4 | Ing. Camila Ríos | Especialista en Experiencia de Usuario (UX) | Área de Producto |

### Resultados — Ronda 3 (Validación Final)

| Factor | Media | CV | % Aprobación | Resultado |
|---|---|---|---|---|
| usuarios_concurrentes | 4.75 | 0.091 | 100 % | ✅ Aprobado |
| uso_ancho_banda | 4.25 | 0.102 | 100 % | ✅ Aprobado |
| latencia_red | 4.25 | 0.102 | 100 % | ✅ Aprobado |
| capacidad_servidor | 4.25 | 0.102 | 100 % | ✅ Aprobado |

**4/4 variables aprobadas · 100% consenso · 0 variables rechazadas**

### Justificaciones clave

- **E1 (Arquitecto Cloud):** *"Los usuarios concurrentes son el principal driver de escalado. Superado el 70% de capacidad, activamos auto-scaling."*
- **E2 (Analista QoS):** *"La latencia superior a 150ms genera buffering visible que impacta la retención de usuarios."*
- **E3 (Investigador):** *"Los modelos de carga muestran comportamiento no lineal cuando la concurrencia supera el 75% de la capacidad nominal."*
- **E4 (UX):** *"Por encima de 200ms de latencia, la tasa de abandono aumenta un 40%."*

---

## Parte B — Sistema Difuso Mamdani

### Variables de Entrada

| Variable | Universo | Etiquetas |
|---|---|---|
| usuarios_concurrentes | [0, 100] | bajo, medio, alto |
| uso_ancho_banda | [0, 100 %] | bajo, medio, alto |
| latencia_red | [0, 10 ms] | baja, media, alta |
| capacidad_servidor | [0, 100 %] | baja, media, alta |

### Variable de Salida — 5 niveles

| Variable | Universo | Etiquetas | Defuzzificación |
|---|---|---|---|
| riesgo_qos | [0, 100] | muy_bajo · bajo · medio · alto · muy_alto | Centroide |

Las funciones de pertenencia de salida son **asimétricas** con solapamiento amplio para producir una distribución continua en el Montecarlo.

### Reglas Difusas — 27 reglas con cobertura completa

| Grupo | Reglas | Consecuente |
|---|---|---|
| usuarios=alto + banda=alta + latencia=alta | R01–R02 | muy_alto |
| usuarios=alto + otras combinaciones | R03–R09 | alto / medio / bajo |
| usuarios=medio + todas combinaciones | R10–R20 | alto / medio / muy_bajo |
| usuarios=bajo + todas combinaciones | R21–R27 | medio / bajo / muy_bajo |

### Prueba del Sistema

| Escenario | Usuarios | Banda | Latencia | Capacidad | Riesgo QoS |
|---|---|---|---|---|---|
| Carga máxima | 85 | 90 % | 8.0 ms | 88 % | **~82** |
| Carga mínima | 10 | 15 % | 1.0 ms | 20 % | **~16** |
| Carga normal | 55 | 60 % | 5.0 ms | 60 % | **~47** |

---

## Parte C — Simulación Montecarlo

### Distribuciones (5000 simulaciones, RANDOM_SEED = 42)

| Variable | Distribución | Parámetros | Justificación |
|---|---|---|---|
| usuarios_concurrentes | Beta(α=2, β=3) × 100 | α=2, β=3 | Mayoría del tiempo con carga media-baja; picos ocasionales |
| uso_ancho_banda | Normal Truncada | μ=55, σ=20, [0,100] | Uso promedio del 55% con alta variabilidad en horas pico |
| latencia_red | Triangular | mín=0, moda=3, máx=10 | Latencia típica baja con cola hacia valores altos en congestión |
| capacidad_servidor | Beta(α=3, β=2) × 100 | α=3, β=2 | Servidores operan típicamente a alta capacidad |

### Resultados (n = 5000, RANDOM_SEED = 42)

| Estadístico | Valor | Interpretación |
|---|---|---|
| **Media riesgo_qos** | **~40** | Riesgo promedio moderado-bajo |
| Desviación estándar | ~20 | Alta variabilidad entre escenarios |
| P(riesgo_qos ≥ 70) | **~5–10 %** | Escenarios críticos — requieren intervención |
| Percentil 95 | ~70 | Solo el 5% supera el umbral crítico |

### Dataset sintético: `data/base_simulada_streaming.csv`

| Columna | Tipo | Rango | Distribución |
|---|---|---|---|
| usuarios_concurrentes | float | [0, 100] | Beta(α=2, β=3) × 100 |
| uso_ancho_banda | float | [0, 100] | Normal Truncada(μ=55, σ=20) |
| latencia_red | float | [0, 10] | Triangular(mín=0, moda=3, máx=10) |
| capacidad_servidor | float | [0, 100] | Beta(α=3, β=2) × 100 |
| riesgo_qos | float | [0, 100] | Calculado por sistema difuso |

- **5000 filas** · `RANDOM_SEED = 42` · Reproducible

---

## Parte D — Regresión y Análisis Comparativo

### Métricas de Evaluación

| Modelo | MAE | RMSE | R² | Evaluación |
|---|---|---|---|---|
| KNN (k=5) | 7.26 | 10.55 | 0.638 | Aceptable |
| Decision Tree | 1.69 | 4.43 | 0.936 | Muy bueno |
| **Random Forest** | **1.40** | **3.22** | **0.966** | **Excelente** |

### Correlación de Pearson

**r = 0.9832** — correlación muy alta entre Random Forest y sistema difuso.

### Importancia de Variables (Random Forest)

| Ranking | Variable | Importancia |
|---|---|---|
| 1° | **usuarios_concurrentes** | **~30 %** |
| 2° | **latencia_red** | **~29 %** |
| 3° | uso_ancho_banda | ~20 % |
| 4° | capacidad_servidor | ~20 % |

Las 4 variables tienen importancias equilibradas — coherente con el conocimiento experto del Delphi.

---

## Resumen Ejecutivo

| Componente | Resultado clave | Significado |
|---|---|---|
| **Delphi** | 4/4 aprobadas · 100% consenso | Validación experta sólida |
| **Sistema Difuso** | 27 reglas · 5 niveles · Riesgo alto ≈ 82 | Sistema coherente y diferenciado |
| **Montecarlo** | 5000 sims · P(≥70) ≈ 5–10% | Plataforma estable en condiciones típicas |
| **Regresión** | R² = 0.966 · r = 0.983 | Alta consistencia difuso-estadístico |

---

## Comparación con Caso Base

| Aspecto | Caso Base (Académico) | Proyecto Final (Streaming) |
|---|---|---|
| Variables | promedio, inasistencia, horas, motivacion | usuarios, banda, latencia, capacidad |
| Reglas | 27 | 27 |
| Niveles de salida | 5 | 5 |
| Simulaciones | 1000 | 5000 |
| Mejor R² | ~0.84 | **0.966** |
| Pearson r | ~0.92 | **0.983** |
| Variable clave | promedio_academico (~46%) | usuarios_concurrentes (~30%) |

---

## Trazabilidad

| Variable | Aprobada en Delphi | Media | CV | En Difuso | En Regresión |
|---|---|---|---|---|---|
| usuarios_concurrentes | ✅ | 4.75 | 0.091 | ✅ | ✅ |
| uso_ancho_banda | ✅ | 4.25 | 0.102 | ✅ | ✅ |
| latencia_red | ✅ | 4.25 | 0.102 | ✅ | ✅ |
| capacidad_servidor | ✅ | 4.25 | 0.102 | ✅ | ✅ |

---

## Conclusiones

1. **El Delphi validó los factores correctos** — los 4 factores de red tienen respaldo experto del sector tecnológico con 100% de consenso.

2. **El sistema difuso captura la no linealidad del streaming** — 27 reglas con 5 niveles producen una distribución continua y diferenciada del riesgo QoS.

3. **La plataforma es estable en condiciones típicas** — solo el 5–10% de los escenarios supera el umbral crítico de 70.

4. **El Random Forest valida la coherencia** — R² = 0.966 y r = 0.983 son los mejores resultados del taller, gracias a 5000 simulaciones y reglas más determinísticas.

5. **Usuarios concurrentes y latencia son los factores más críticos** — ambos con ~30% de importancia, coherente con la literatura de sistemas distribuidos.

6. **La metodología es completamente transferible** — el mismo flujo del caso académico se aplicó al streaming con adaptaciones mínimas.

---

## Estructura del Proyecto

```
trabajo_final/
│
├── README.md                              ← Este archivo
│
├── data/                                  ← Datos generados (RANDOM_SEED = 42)
│   ├── base_simulada_streaming.csv        ← 5000 filas × 5 columnas ⭐
│   ├── delphi_ronda1.json
│   ├── delphi_ronda2.json
│   ├── delphi_consenso.json
│   ├── fuzzy_variables.json
│   └── fuzzy_rules.json
│
├── delphi/
│   ├── expert_panel.py                    ← 4 expertos del sector streaming
│   └── delphi_simulator.py
│
├── fuzzy_system/
│   └── fuzzy_system_builder.py            ← 27 reglas, 5 niveles de salida
│
├── montecarlo/
│   └── montecarlo_simulator.py            ← 5000 simulaciones
│
├── regression/
│   └── regression_analyzer.py
│
├── notebooks/
│   └── streaming_completo.ipynb           ← Notebook principal
│
└── docs/
    ├── delphi_informe.md
    ├── fuzzy_membership_plots/
    ├── montecarlo_histograma_streaming.png
    ├── montecarlo_distribuciones_streaming.md
    ├── regression_comparativa_streaming.md
    ├── regression_importancia_streaming.md
    ├── analisis_comparativo_streaming.md
    └── comparativo_difuso_vs_prediccion_streaming.png
```

---

*Taller 2 — Modelos y Simulación · Institución Universitaria Pascual Bravo · 2026*  
*Julian Zapata · Juan José Orrego*
