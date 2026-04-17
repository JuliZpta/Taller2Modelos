# Documento de Trazabilidad — Sistema de Evaluación de Riesgo Académico

## Institución Universitaria Pascual Bravo · Medellín, Colombia

---

## Sección 1: Trazabilidad Delphi → Variables Difusas

La siguiente tabla mapea cada Variable_Entrada del sistema difuso con su Factor Delphi de origen y los estadísticos de consenso obtenidos en la Ronda 3 del proceso Delphi.

| Variable_Entrada     | Factor Delphi        | Media  | CV     | % Aprobación | Aprobado |
|----------------------|----------------------|--------|--------|--------------|----------|
| promedio_academico   | promedio_academico   | 4.750  | 0.0912 | 100 %        | ✓        |
| inasistencia         | inasistencia         | 4.250  | 0.1019 | 100 %        | ✓        |
| horas_estudio        | horas_estudio        | 4.250  | 0.1019 | 100 %        | ✓        |
| motivacion_estres    | motivacion_estres    | 4.250  | 0.1019 | 100 %        | ✓        |

**Criterios de consenso aplicados:**
- Media ≥ 4.0 (escala Likert 1–5)
- Coeficiente de Variación (CV) ≤ 0.30
- Porcentaje de aprobación (puntuación ≥ 4) ≥ 70 %

Todas las variables candidatas superaron los tres criterios en la Ronda 3. No se registraron variables rechazadas.

---

## Sección 2: Trazabilidad Reglas Difusas → Consenso Experto

Las 12 reglas del sistema de inferencia Mamdani fueron derivadas directamente del consenso alcanzado por el panel de expertos (E1–E4) en la Ronda 3 del proceso Delphi.

| ID Regla | Descripción                                                                                      | Origen Delphi                                  |
|----------|--------------------------------------------------------------------------------------------------|------------------------------------------------|
| R01      | Si promedio_academico es **bajo** Y inasistencia es **alta** → riesgo es **alto**               | Consenso expertos E1, E2, E3, E4 — Ronda 3    |
| R02      | Si motivacion_estres es **bajo** Y horas_estudio es **pocas** → riesgo es **alto**              | Consenso expertos E1, E2, E3, E4 — Ronda 3    |
| R03      | Si promedio_academico es **bajo** Y horas_estudio es **pocas** → riesgo es **alto**             | Consenso expertos E1, E2, E3, E4 — Ronda 3    |
| R04      | Si promedio_academico es **alto** Y inasistencia es **baja** → riesgo es **bajo**               | Consenso expertos E1, E2, E3, E4 — Ronda 3    |
| R05      | Si promedio_academico es **alto** Y horas_estudio es **muchas** → riesgo es **bajo**            | Consenso expertos E1, E2, E3, E4 — Ronda 3    |
| R06      | Si motivacion_estres es **alto** Y promedio_academico es **alto** → riesgo es **bajo**          | Consenso expertos E1, E2, E3, E4 — Ronda 3    |
| R07      | Si promedio_academico es **medio** Y inasistencia es **media** → riesgo es **medio**            | Consenso expertos E1, E2, E3, E4 — Ronda 3    |
| R08      | Si horas_estudio es **moderadas** Y motivacion_estres es **medio** → riesgo es **medio**        | Consenso expertos E1, E2, E3, E4 — Ronda 3    |
| R09      | Si promedio_academico es **bajo** Y inasistencia es **media** → riesgo es **medio**             | Consenso expertos E1, E2, E3, E4 — Ronda 3    |
| R10      | Si inasistencia es **alta** Y horas_estudio es **pocas** → riesgo es **alto**                   | Consenso expertos E1, E2, E3, E4 — Ronda 3    |
| R11      | Si promedio_academico es **medio** Y horas_estudio es **pocas** → riesgo es **medio**           | Consenso expertos E1, E2, E3, E4 — Ronda 3    |
| R12      | Si motivacion_estres es **bajo** Y inasistencia es **alta** → riesgo es **alto**                | Consenso expertos E1, E2, E3, E4 — Ronda 3    |

**Distribución de reglas por nivel de riesgo:**
- Riesgo **alto**: R01, R02, R03, R10, R12 (5 reglas)
- Riesgo **bajo**: R04, R05, R06 (3 reglas)
- Riesgo **medio**: R07, R08, R09, R11 (4 reglas)

---

## Sección 3: Trazabilidad Variables → Modelos de Regresión

Las mismas 4 variables aprobadas en el proceso Delphi y utilizadas como Variables_Entrada del sistema difuso son las *features* de los modelos de regresión supervisada. No se introduce ninguna variable adicional ni se elimina ninguna variable aprobada.

| Variable_Entrada   | Sistema Difuso | Modelo KNN | Random Forest | Decision Tree |
|--------------------|:--------------:|:----------:|:-------------:|:-------------:|
| promedio_academico | ✓              | ✓          | ✓             | ✓             |
| inasistencia       | ✓              | ✓          | ✓             | ✓             |
| horas_estudio      | ✓              | ✓          | ✓             | ✓             |
| motivacion_estres  | ✓              | ✓          | ✓             | ✓             |

La variable objetivo (`riesgo`) en los modelos de regresión es el valor de salida del sistema difuso Mamdani, calculado mediante defuzzificación centroide. Esto garantiza la coherencia metodológica entre las Partes B, C y D del flujo.

---

## Sección 4: Flujo de Trazabilidad Completo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PROCESO DELPHI (Parte A)                           │
│                                                                             │
│  Panel de 4 expertos (E1–E4) · 3 rondas · Criterios: media≥4, CV≤0.30     │
│                                                                             │
│  Factores candidatos → Ronda 1 → Ronda 2 → Ronda 3 → Variables_Aprobadas  │
│                                                                             │
│  ✓ promedio_academico  ✓ inasistencia                                       │
│  ✓ horas_estudio       ✓ motivacion_estres                                  │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │  delphi_consenso.json
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SISTEMA DIFUSO MAMDANI (Parte B)                        │
│                                                                             │
│  Variables_Aprobadas → Funciones de pertenencia → 12 Reglas IF-THEN        │
│  Defuzzificación: centroide → evaluar_riesgo(dict) → float ∈ [0, 100]      │
│                                                                             │
│  Persistencia: fuzzy_variables.json · fuzzy_rules.json                     │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │  evaluar_riesgo()
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SIMULACIÓN MONTECARLO (Parte C)                         │
│                                                                             │
│  1000 escenarios aleatorios · Distribuciones estadísticas por variable     │
│  → base_simulada.csv (columnas: variables_entrada + riesgo)                │
│                                                                             │
│  Estadísticas: media, std, percentiles, P(riesgo ≥ 70)                     │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │  base_simulada.csv
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REGRESIÓN / PREDICCIÓN (Parte D)                        │
│                                                                             │
│  Features: mismas 4 Variables_Entrada · Target: riesgo (difuso)            │
│  Modelos: KNN (k=5) · Random Forest (100 árboles) · Decision Tree          │
│  Métricas: MAE · RMSE · R² · Correlación de Pearson                        │
└─────────────────────────────────────────────────────────────────────────────┘

Trazabilidad garantizada:
  Delphi ──► Variables_Aprobadas ──► Sistema Difuso ──► Montecarlo ──► Regresión
  Cada Variable_Entrada tiene un Factor Delphi con aprobado = True
  RANDOM_SEED = 42 garantiza reproducibilidad en todas las etapas
```

---

*Generado automáticamente como parte del flujo metodológico del Sistema de Evaluación de Riesgo de Bajo Rendimiento Académico — Institución Universitaria Pascual Bravo.*
