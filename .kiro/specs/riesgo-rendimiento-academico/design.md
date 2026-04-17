# Design Document — Sistema de Evaluación de Riesgo de Bajo Rendimiento Académico

**Institución Universitaria Pascual Bravo · Medellín, Colombia**

---

## Overview

El sistema implementa un flujo metodológico de cuatro etapas para evaluar el riesgo de bajo rendimiento académico estudiantil:

1. **Delphi** — Priorización y validación de factores mediante panel de expertos simulado.
2. **Sistema Difuso Mamdani** — Inferencia del nivel de riesgo a partir de los factores validados.
3. **Simulación Montecarlo** — Estimación de la distribución de probabilidad del riesgo.
4. **Regresión/Predicción** — Comparación entre el enfoque difuso y modelos estadísticos.

El diseño prioriza tres atributos de calidad: **trazabilidad** (cada decisión de diseño se vincula a un resultado Delphi documentado), **reproducibilidad** (semilla global fija `RANDOM_SEED = 42`) y **modularidad** (cada etapa es un módulo Python independiente con interfaz pública bien definida).

### Decisiones de diseño globales

| Decisión | Justificación |
|---|---|
| Semilla global `RANDOM_SEED = 42` | Garantiza reproducibilidad completa en todas las etapas |
| Persistencia en JSON para metadatos | Legibilidad humana, trazabilidad y portabilidad entre módulos |
| Persistencia en CSV para datos tabulares | Compatibilidad directa con pandas y scikit-learn |
| scikit-fuzzy para el motor difuso | Biblioteca madura, compatible con NumPy, implementa Mamdani nativo |
| Defuzzificación centroide | Método estándar para Mamdani; produce valores continuos y estables; ampliamente documentado en literatura de control difuso |
| Distribuciones estadísticas por variable | Modelan la realidad observada en poblaciones estudiantiles (ver Parte C) |

---

## Architecture

### Diagrama de arquitectura de módulos

```
┌─────────────────────────────────────────────────────────────────────┐
│                    notebooks/proyecto_completo.ipynb                │
│  (orquestador principal — RANDOM_SEED = 42 — ejecución secuencial) │
└──────────┬──────────────┬──────────────┬──────────────┬────────────┘
           │              │              │              │
           ▼              ▼              ▼              ▼
    ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │  delphi/    │ │ fuzzy_system/│ │ montecarlo/  │ │ regression/  │
    │             │ │              │ │              │ │              │
    │ ExpertPanel │ │FuzzySystem   │ │Montecarlo    │ │Regression    │
    │ Delphi      │ │Builder       │ │Simulator     │ │Analyzer      │
    │ Simulator   │ │              │ │              │ │              │
    └──────┬──────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │              │              │              │
           ▼              ▼              ▼              ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                          data/                                  │
    │  delphi_ronda1.json   fuzzy_variables.json   base_simulada.csv  │
    │  delphi_ronda2.json   fuzzy_rules.json                          │
    │  delphi_consenso.json fuzzy_warnings.json                       │
    └─────────────────────────────────────────────────────────────────┘
           │              │              │              │
           ▼              ▼              ▼              ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                          docs/                                  │
    │  delphi_informe.md          montecarlo_distribuciones.md        │
    │  fuzzy_membership_plots/    montecarlo_histograma.png           │
    │  regression_comparativa.md  analisis_comparativo.md             │
    │  regression_importancia_variables.md                            │
    │  comparativo_difuso_vs_prediccion.png                           │
    │  trazabilidad.md            README.md                           │
    └─────────────────────────────────────────────────────────────────┘
```

### Diagrama de flujo de datos entre módulos

```
┌──────────────────────────────────────────────────────────────────────┐
│  PARTE A — Delphi                                                    │
│                                                                      │
│  ExpertPanel ──► DelphiSimulator.run_round1() ──► delphi_ronda1.json │
│                         │                                            │
│                         ▼                                            │
│               DelphiSimulator.run_round2() ──► delphi_ronda2.json   │
│                         │                                            │
│                         ▼                                            │
│               DelphiSimulator.run_round3() ──► delphi_consenso.json │
│                                            ──► delphi_informe.md    │
└──────────────────────────┬───────────────────────────────────────────┘
                           │ lee delphi_consenso.json
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  PARTE B — Sistema Difuso                                            │
│                                                                      │
│  FuzzySystemBuilder ──► fuzzy_variables.json                        │
│                     ──► fuzzy_rules.json                            │
│                     ──► fuzzy_membership_plots/                     │
│                     ──► evaluar_riesgo(dict) -> float               │
└──────────────────────────┬───────────────────────────────────────────┘
                           │ usa evaluar_riesgo()
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  PARTE C — Montecarlo                                                │
│                                                                      │
│  MontecarloSimulator.run(n=1000) ──► base_simulada.csv              │
│                                  ──► montecarlo_histograma.png      │
│                                  ──► montecarlo_distribuciones.md   │
└──────────────────────────┬───────────────────────────────────────────┘
                           │ lee base_simulada.csv
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  PARTE D — Regresión                                                 │
│                                                                      │
│  RegressionAnalyzer ──► regression_comparativa.md                  │
│                     ──► regression_importancia_variables.md         │
│                     ──► comparativo_difuso_vs_prediccion.png        │
│                     ──► analisis_comparativo.md                     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Components and Interfaces

### Parte A — Módulo Delphi (`delphi/`)

#### Clase `ExpertPanel`

Encapsula la definición del panel de expertos simulados de la Institución Universitaria Pascual Bravo.

```python
@dataclass
class Expert:
    id: str                  # identificador único, e.g. "E1"
    nombre: str              # nombre ficticio
    cargo: str               # e.g. "Docente de Ingeniería de Sistemas"
    dependencia: str         # e.g. "Facultad de Ingeniería"
    perfil: str              # "docente" | "coordinador" | "psicologo" | "directivo"
    sesgo_base: float        # puntuación base Likert (3.5–5.0) según perfil

class ExpertPanel:
    """
    Define y gestiona el panel de 4 expertos simulados de la Pascual Bravo.
    Los perfiles cubren: docente universitario, coordinador académico,
    psicólogo de bienestar estudiantil y directivo académico.
    """

    def __init__(self, seed: int = 42) -> None: ...

    def get_experts(self) -> list[Expert]: ...

    def generate_likert_response(
        self,
        expert: Expert,
        factor: str,
        round_num: int,
        previous_score: float | None = None,
        group_mean: float | None = None,
    ) -> tuple[int, str]:
        """
        Genera una puntuación Likert (1–5) y justificación textual
        coherente con el perfil del experto y el contexto institucional.
        En ronda 2, ajusta hacia group_mean con variación ±0–1.
        Retorna (puntuacion: int, justificacion: str).
        """
        ...
```

**Perfiles de expertos simulados:**

| ID | Nombre | Cargo | Dependencia | Perfil |
|---|---|---|---|---|
| E1 | Dr. Carlos Restrepo | Docente de Ingeniería de Sistemas | Facultad de Ingeniería | docente |
| E2 | Mg. Adriana Gómez | Coordinadora Académica | Vicerrectoría Académica | coordinador |
| E3 | Ps. Juliana Martínez | Psicóloga de Bienestar Estudiantil | Bienestar Universitario | psicologo |
| E4 | Dr. Hernán Ospina | Director de Currículo | Vicerrectoría Académica | directivo |

#### Clase `DelphiSimulator`

Orquesta las tres rondas del proceso Delphi.

```python
class DelphiSimulator:
    """
    Ejecuta el proceso Delphi de tres rondas sobre los factores candidatos.
    Persiste resultados en data/ y genera el informe en docs/.
    """

    FACTORS: list[str] = [
        "promedio_academico",
        "inasistencia",
        "horas_estudio",
        "motivacion_estres",
    ]

    CONSENSUS_CRITERIA = {
        "min_mean": 4.0,
        "max_cv": 0.30,
        "min_approval_pct": 70.0,  # % de expertos con puntuación >= 4
    }

    def __init__(self, panel: ExpertPanel, data_dir: str = "data/") -> None: ...

    def run_round1(self) -> dict:
        """
        Genera respuestas Likert iniciales para cada experto × factor.
        Calcula media, std y CV por factor.
        Persiste en data/delphi_ronda1.json.
        Retorna el diccionario de resultados.
        """
        ...

    def run_round2(self, round1_results: dict) -> dict:
        """
        Genera respuestas ajustadas hacia la media grupal de ronda 1
        con variación aleatoria controlada (±0–1).
        Persiste en data/delphi_ronda2.json.
        Retorna el diccionario de resultados.
        """
        ...

    def run_round3(self, round2_results: dict) -> dict:
        """
        Genera validación final. Evalúa criterios de consenso.
        Persiste en data/delphi_consenso.json y docs/delphi_informe.md.
        Retorna diccionario con Variables_Aprobadas y sus estadísticos.
        """
        ...

    def _calculate_stats(self, scores: list[float]) -> dict:
        """Calcula media, std y CV. Retorna {'mean': float, 'std': float, 'cv': float}."""
        ...

    def _evaluate_consensus(self, stats: dict, scores: list[float]) -> dict:
        """
        Evalúa los tres criterios de consenso.
        Retorna {'approved': bool, 'criteria': {mean_ok, cv_ok, approval_ok}}.
        """
        ...

    def _generate_report(self, all_rounds: dict, consensus: dict) -> None:
        """Genera docs/delphi_informe.md con narrativa metodológica completa."""
        ...
```

---

### Parte B — Módulo Difuso (`fuzzy_system/`)

#### Clase `FuzzySystemBuilder`

```python
class FuzzySystemBuilder:
    """
    Construye el sistema de inferencia difuso Mamdani usando scikit-fuzzy.
    Lee las Variables_Aprobadas de data/delphi_consenso.json.
    Expone evaluar_riesgo() como interfaz pública para otros módulos.
    """

    # Universos de discurso fijos por variable
    UNIVERSES = {
        "promedio_academico": (0.0, 5.0, 0.01),   # step 0.01
        "inasistencia":       (0.0, 100.0, 0.5),
        "horas_estudio":      (0.0, 30.0, 0.1),
        "motivacion_estres":  (0.0, 10.0, 0.1),
        "riesgo":             (0.0, 100.0, 0.5),
    }

    def __init__(
        self,
        consenso_path: str = "data/delphi_consenso.json",
        data_dir: str = "data/",
        docs_dir: str = "docs/",
    ) -> None: ...

    def build(self) -> None:
        """
        Construye variables difusas, funciones de pertenencia y reglas.
        Persiste fuzzy_variables.json y fuzzy_rules.json.
        Genera gráficas en docs/fuzzy_membership_plots/.
        """
        ...

    def evaluar_riesgo(self, valores_entrada: dict) -> float:
        """
        Interfaz pública. Recibe dict con claves = nombres de Variables_Entrada.
        Ejecuta fuzzificación → evaluación de reglas → agregación → defuzzificación centroide.
        Recorta valores fuera del universo y registra advertencia en fuzzy_warnings.json.
        Retorna float en [0, 100].
        """
        ...

    def _build_membership_functions(self) -> dict:
        """Construye funciones de pertenencia triangulares/trapezoidales con skfuzzy."""
        ...

    def _build_rules(self) -> list:
        """Construye reglas Mamdani derivadas del consenso Delphi."""
        ...

    def _plot_membership_functions(self) -> None:
        """Genera y guarda gráficas en docs/fuzzy_membership_plots/."""
        ...

    def _log_warning(self, message: str) -> None:
        """Agrega advertencia a data/fuzzy_warnings.json."""
        ...
```

**Funciones de pertenencia por variable:**

| Variable | Etiqueta | Tipo | Parámetros |
|---|---|---|---|
| promedio_academico | bajo | trapezoidal | [0, 0, 2.0, 3.0] |
| promedio_academico | medio | triangular | [2.5, 3.5, 4.5] |
| promedio_academico | alto | trapezoidal | [4.0, 4.5, 5.0, 5.0] |
| inasistencia | baja | trapezoidal | [0, 0, 15, 30] |
| inasistencia | media | triangular | [20, 40, 60] |
| inasistencia | alta | trapezoidal | [50, 70, 100, 100] |
| horas_estudio | pocas | trapezoidal | [0, 0, 5, 12] |
| horas_estudio | moderadas | triangular | [8, 15, 22] |
| horas_estudio | muchas | trapezoidal | [18, 24, 30, 30] |
| motivacion_estres | bajo | trapezoidal | [0, 0, 3, 5] |
| motivacion_estres | medio | triangular | [3, 5, 7] |
| motivacion_estres | alto | trapezoidal | [6, 8, 10, 10] |
| riesgo | bajo | trapezoidal | [0, 0, 20, 40] |
| riesgo | medio | triangular | [30, 50, 70] |
| riesgo | alto | trapezoidal | [60, 80, 100, 100] |

**Justificación de la defuzzificación centroide:** El método centroide (centro de gravedad) es el estándar de facto para sistemas Mamdani porque produce un valor continuo y suave que refleja el "peso" de todas las reglas activas. Alternativas como bisector o mom (mean of maximum) son más sensibles a la forma del área agregada y producen discontinuidades. Para un índice de riesgo que alimenta análisis estadísticos posteriores, la continuidad es esencial.

---

### Parte C — Módulo Montecarlo (`montecarlo/`)

#### Clase `MontecarloSimulator`

```python
class MontecarloSimulator:
    """
    Ejecuta simulación Montecarlo sobre el sistema difuso.
    Muestrea cada Variable_Entrada según su distribución estadística justificada.
    """

    DISTRIBUTIONS = {
        "promedio_academico": {
            "type": "truncated_normal",
            "params": {"mean": 3.5, "std": 0.7, "low": 0.0, "high": 5.0},
            "justification": (
                "El promedio académico en poblaciones universitarias sigue una "
                "distribución aproximadamente normal. Se trunca en [0,5] para "
                "respetar el universo de discurso. Media 3.5 y std 0.7 reflejan "
                "la distribución típica observada en instituciones colombianas."
            ),
        },
        "inasistencia": {
            "type": "beta",
            "params": {"alpha": 2.0, "beta": 5.0, "scale": 100.0},
            "justification": (
                "La inasistencia es una proporción en [0,100]. La distribución "
                "Beta(2,5) modela la asimetría positiva observada: la mayoría de "
                "estudiantes tiene inasistencia baja, con cola hacia valores altos."
            ),
        },
        "horas_estudio": {
            "type": "triangular",
            "params": {"low": 0.0, "mode": 12.0, "high": 30.0},
            "justification": (
                "Las horas de estudio tienen límites naturales claros (0–30 h/semana). "
                "La distribución triangular es apropiada cuando se conocen mínimo, "
                "máximo y valor más probable. Moda en 12 h refleja el promedio "
                "reportado en encuestas de hábitos de estudio universitario."
            ),
        },
        "motivacion_estres": {
            "type": "triangular",
            "params": {"low": 0.0, "mode": 5.0, "high": 10.0},
            "justification": (
                "Escala subjetiva [0–10] con distribución simétrica alrededor del "
                "punto medio. La triangular con moda=5 modela la tendencia central "
                "sin asumir normalidad en escalas ordinales."
            ),
        },
    }

    def __init__(
        self,
        fuzzy_system: FuzzySystemBuilder,
        data_dir: str = "data/",
        docs_dir: str = "docs/",
        seed: int = 42,
    ) -> None: ...

    def run(self, n_simulaciones: int = 1000) -> pd.DataFrame:
        """
        Ejecuta n_simulaciones del sistema difuso.
        Persiste base_simulada.csv, montecarlo_histograma.png
        y montecarlo_distribuciones.md.
        Retorna DataFrame con columnas [variables_entrada..., riesgo].
        """
        ...

    def _sample_inputs(self) -> dict:
        """Muestrea un conjunto de valores de entrada según las distribuciones definidas."""
        ...

    def _calculate_statistics(self, results: pd.Series) -> dict:
        """
        Calcula: mean, std, min, max, p25, p50, p75, p95, P(riesgo>=70).
        Retorna dict con todas las estadísticas.
        """
        ...

    def _identify_critical_scenarios(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filtra filas con riesgo >= 70. Retorna sub-DataFrame de escenarios críticos."""
        ...

    def _generate_histogram(self, results: pd.Series) -> None:
        """Genera y guarda docs/montecarlo_histograma.png."""
        ...

    def _generate_distributions_doc(self) -> None:
        """Genera docs/montecarlo_distribuciones.md con justificaciones estadísticas."""
        ...
```

---

### Parte D — Módulo Regresión (`regression/`)

#### Clase `RegressionAnalyzer`

```python
class RegressionAnalyzer:
    """
    Entrena y evalúa KNN, RandomForest y DecisionTree sobre base_simulada.csv.
    Genera análisis comparativo y documentación de trazabilidad.
    """

    MODELS = {
        "knn": KNeighborsRegressor(n_neighbors=5),
        "random_forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "decision_tree": DecisionTreeRegressor(random_state=42),
    }

    TEST_SIZE = 0.20
    RANDOM_STATE = 42
    MIN_R2_THRESHOLD = 0.80

    def __init__(
        self,
        data_path: str = "data/base_simulada.csv",
        consenso_path: str = "data/delphi_consenso.json",
        docs_dir: str = "docs/",
    ) -> None: ...

    def load_data(self) -> tuple[pd.DataFrame, pd.Series]:
        """Carga base_simulada.csv. Retorna (X, y) donde y = columna 'riesgo'."""
        ...

    def train_and_evaluate(self) -> dict:
        """
        Divide datos 80/20, entrena los tres modelos, calcula MAE/RMSE/R².
        Retorna dict con métricas por modelo.
        """
        ...

    def get_feature_importance(self) -> dict:
        """
        Extrae importancia de variables para RandomForest y DecisionTree.
        Retorna dict {'random_forest': Series, 'decision_tree': Series}.
        """
        ...

    def calculate_pearson_correlation(self) -> float:
        """
        Calcula correlación de Pearson entre predicciones del mejor modelo
        y valores difusos en el conjunto de prueba.
        Retorna coeficiente r.
        """
        ...

    def generate_scatter_plot(self) -> None:
        """Genera docs/comparativo_difuso_vs_prediccion.png."""
        ...

    def generate_comparative_report(self, metrics: dict) -> None:
        """
        Genera docs/regression_comparativa.md con tabla de métricas.
        Incluye advertencia si R² < 0.80 para todos los modelos.
        """
        ...

    def generate_importance_report(self) -> None:
        """Genera docs/regression_importancia_variables.md."""
        ...

    def generate_comparative_analysis(self, metrics: dict, correlation: float) -> None:
        """
        Genera docs/analisis_comparativo.md con tabla, correlación,
        interpretación de importancia de variables y sección de Trazabilidad.
        """
        ...
```

---

## Data Models

### Esquema `data/delphi_ronda1.json` y `data/delphi_ronda2.json`

```json
{
  "ronda": 1,
  "timestamp": "2024-01-15T10:30:00",
  "factores": [
    {
      "factor": "promedio_academico",
      "respuestas": [
        {
          "experto_id": "E1",
          "nombre": "Dr. Carlos Restrepo",
          "cargo": "Docente de Ingeniería de Sistemas",
          "dependencia": "Facultad de Ingeniería",
          "puntuacion": 5,
          "puntuacion_anterior": null,
          "justificacion": "En mis cursos de Ingeniería de Sistemas observo que..."
        }
      ],
      "estadisticos": {
        "media": 4.75,
        "std": 0.43,
        "cv": 0.091
      }
    }
  ]
}
```

*Nota: En `delphi_ronda2.json`, el campo `puntuacion_anterior` contiene la puntuación de ronda 1 para evidenciar el ajuste.*

### Esquema `data/delphi_consenso.json`

```json
{
  "timestamp": "2024-01-15T11:00:00",
  "variables_aprobadas": [
    {
      "factor": "promedio_academico",
      "estadisticos_finales": {
        "media": 4.75,
        "std": 0.43,
        "cv": 0.091
      },
      "criterios": {
        "mean_ok": true,
        "cv_ok": true,
        "approval_ok": true,
        "approval_pct": 100.0
      },
      "aprobado": true,
      "criterio_fallido": null
    }
  ],
  "variables_rechazadas": []
}
```

### Esquema `data/fuzzy_variables.json`

```json
{
  "variables_entrada": [
    {
      "nombre": "promedio_academico",
      "universo": [0.0, 5.0],
      "step": 0.01,
      "etiquetas": [
        {
          "nombre": "bajo",
          "tipo": "trapezoidal",
          "parametros": [0, 0, 2.0, 3.0]
        },
        {
          "nombre": "medio",
          "tipo": "triangular",
          "parametros": [2.5, 3.5, 4.5]
        },
        {
          "nombre": "alto",
          "tipo": "trapezoidal",
          "parametros": [4.0, 4.5, 5.0, 5.0]
        }
      ],
      "origen_delphi": "promedio_academico"
    }
  ],
  "variable_salida": {
    "nombre": "riesgo",
    "universo": [0.0, 100.0],
    "step": 0.5,
    "etiquetas": [
      {"nombre": "bajo",  "tipo": "trapezoidal", "parametros": [0, 0, 20, 40]},
      {"nombre": "medio", "tipo": "triangular",  "parametros": [30, 50, 70]},
      {"nombre": "alto",  "tipo": "trapezoidal", "parametros": [60, 80, 100, 100]}
    ]
  }
}
```

### Esquema `data/fuzzy_rules.json`

```json
{
  "reglas": [
    {
      "id": "R01",
      "descripcion": "Si promedio es bajo Y inasistencia es alta ENTONCES riesgo es alto",
      "antecedentes": [
        {"variable": "promedio_academico", "etiqueta": "bajo"},
        {"variable": "inasistencia", "etiqueta": "alta"}
      ],
      "consecuente": {"variable": "riesgo", "etiqueta": "alto"},
      "operador": "AND",
      "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3"
    }
  ]
}
```

### Esquema `data/base_simulada.csv`

```
promedio_academico,inasistencia,horas_estudio,motivacion_estres,riesgo
3.82,12.4,14.2,6.1,28.5
2.10,55.3,5.8,3.2,74.1
...
```

### Esquema `data/fuzzy_warnings.json`

```json
{
  "warnings": [
    {
      "timestamp": "2024-01-15T12:00:00",
      "tipo": "valor_fuera_universo",
      "variable": "inasistencia",
      "valor_original": 105.0,
      "valor_recortado": 100.0,
      "mensaje": "Valor 105.0 recortado al límite superior 100.0"
    }
  ]
}
```

---

## Correctness Properties

*Una propiedad es una característica o comportamiento que debe mantenerse verdadero en todas las ejecuciones válidas del sistema — esencialmente, un enunciado formal sobre lo que el sistema debe hacer. Las propiedades sirven como puente entre especificaciones legibles por humanos y garantías de corrección verificables automáticamente.*


### Property 1: Respuestas Likert siempre válidas

*Para cualquier* experto del panel y cualquier factor candidato, la respuesta generada por `generate_likert_response()` debe producir una puntuación entera en el rango [1, 5] y una justificación textual no vacía, independientemente del perfil del experto, la ronda o los estadísticos grupales previos.

**Validates: Requirements 2.3**

---

### Property 2: Corrección matemática de estadísticos Delphi

*Para cualquier* lista de puntuaciones Likert válidas (valores en [1, 5]), `_calculate_stats()` debe producir estadísticos que satisfagan: `cv = std / mean` (cuando `mean > 0`), `0 ≤ std`, y `1 ≤ mean ≤ 5`.

**Validates: Requirements 2.4, 3.3**

---

### Property 3: Evaluación de consenso es correcta y completa

*Para cualquier* combinación de valores de media, CV y porcentaje de aprobación, `_evaluate_consensus()` debe retornar `approved = True` si y solo si los tres criterios se cumplen simultáneamente: `media ≥ 4.0 AND cv ≤ 0.30 AND approval_pct ≥ 70.0`. Si algún criterio falla, `approved = False` y el campo `criterio_fallido` debe identificar cuál criterio no se cumplió.

**Validates: Requirements 4.2, 4.3, 4.4**

---

### Property 4: Convergencia de puntuaciones en Ronda 2

*Para cualquier* puntuación previa de un experto y media grupal de Ronda 1, la nueva puntuación generada en Ronda 2 debe estar dentro del rango `[max(1, ajustado - 1), min(5, ajustado + 1)]`, donde `ajustado` es el valor movido un paso hacia la media grupal. La puntuación siempre debe permanecer en [1, 5].

**Validates: Requirements 3.2**

---

### Property 5: Round-trip de serialización JSON y CSV

*Para cualquier* estructura de datos producida por los módulos (resultados Delphi, variables difusas, reglas difusas, base simulada), serializar a JSON/CSV y deserializar debe producir datos equivalentes con todos los campos requeridos presentes y con los mismos valores numéricos (dentro de tolerancia de punto flotante).

**Validates: Requirements 2.5, 3.4, 4.5, 5.5, 6.3, 8.7**

---

### Property 6: Trazabilidad completa Delphi → Difuso → Regresión

*Para cualquier* Variable_Entrada presente en el sistema difuso o en los modelos de regresión, debe existir un Factor correspondiente en `data/delphi_consenso.json` con `aprobado = True`. El conjunto de Variables_Entrada del sistema difuso debe ser exactamente igual al conjunto de Variables_Aprobadas en el consenso — ni más ni menos.

**Validates: Requirements 5.1, 10.4, 11.1, 11.2**

---

### Property 7: Cada Variable_Entrada tiene al menos tres etiquetas lingüísticas

*Para cualquier* Variable_Entrada definida en el sistema difuso, debe tener al menos tres etiquetas lingüísticas (bajo, medio, alto), y cada etiqueta debe tener parámetros numéricos válidos para su tipo de función de pertenencia.

**Validates: Requirements 5.3**

---

### Property 8: Tipos de funciones de pertenencia son válidos

*Para cualquier* función de pertenencia definida en `data/fuzzy_variables.json`, su tipo debe pertenecer al conjunto `{'triangular', 'trapezoidal', 'gaussiana'}`. No debe existir ninguna función de pertenencia con tipo fuera de este conjunto.

**Validates: Requirements 5.4**

---

### Property 9: evaluar_riesgo() siempre retorna un valor en [0, 100]

*Para cualquier* conjunto de valores de entrada dentro de los universos de discurso de las Variables_Entrada, `evaluar_riesgo()` debe retornar un `float` en el rango `[0.0, 100.0]` sin lanzar excepciones. La función nunca debe retornar `NaN`, `None` o un valor fuera del rango.

**Validates: Requirements 7.1, 7.3**

---

### Property 10: Recorte de valores fuera del universo de discurso

*Para cualquier* valor de entrada que exceda los límites del universo de discurso de su Variable_Entrada, `evaluar_riesgo()` debe: (a) recortar el valor al límite más cercano, (b) retornar un resultado válido en [0, 100] sin lanzar excepción, y (c) registrar una advertencia en `data/fuzzy_warnings.json` con el valor original y el valor recortado.

**Validates: Requirements 7.4**

---

### Property 11: Valores muestreados en Montecarlo respetan los universos de discurso

*Para cualquier* número de simulaciones `n ≥ 1`, todos los valores muestreados por `_sample_inputs()` para cada Variable_Entrada deben estar dentro del universo de discurso de esa variable: `promedio_academico ∈ [0, 5]`, `inasistencia ∈ [0, 100]`, `horas_estudio ∈ [0, 30]`, `motivacion_estres ∈ [0, 10]`.

**Validates: Requirements 8.3**

---

### Property 12: Orden correcto de estadísticos Montecarlo

*Para cualquier* conjunto de resultados de simulación, los estadísticos calculados por `_calculate_statistics()` deben satisfacer el orden: `min ≤ p25 ≤ p50 ≤ p75 ≤ p95 ≤ max`, y todos los valores deben estar en `[0, 100]`.

**Validates: Requirements 8.4**

---

### Property 13: Probabilidad empírica P(riesgo ≥ 70) es correcta

*Para cualquier* DataFrame de simulaciones, `P(riesgo ≥ 70)` calculado por el módulo debe ser igual a `count(riesgo ≥ 70) / len(df)`. Los escenarios críticos identificados deben ser exactamente las filas donde `riesgo ≥ 70` — ni más ni menos.

**Validates: Requirements 8.5, 8.6**

---

### Property 14: Reproducibilidad con semilla fija

*Para cualquier* módulo que use aleatoriedad (Delphi, Montecarlo, Regresión), ejecutar el módulo dos veces con la misma semilla `RANDOM_SEED = 42` debe producir resultados numéricamente idénticos: mismas puntuaciones Delphi, mismos valores muestreados, mismas particiones de datos, mismas métricas de modelos.

**Validates: Requirements 12.1**

---

### Property 15: Métricas de regresión satisfacen invariantes matemáticos

*Para cualquier* modelo de regresión entrenado y evaluado sobre el conjunto de prueba, las métricas deben satisfacer: `MAE ≥ 0`, `RMSE ≥ 0`, `RMSE ≥ MAE` (por la desigualdad cuadrática), y `R² ≤ 1.0`. Si el modelo predice perfectamente, `MAE = RMSE = 0` y `R² = 1.0`.

**Validates: Requirements 9.3**

---

### Property 16: Importancias de variables suman 1.0

*Para cualquier* modelo RandomForest o DecisionTree entrenado, la suma de las importancias de todas las Variables_Entrada debe ser aproximadamente `1.0` (dentro de tolerancia numérica `1e-6`). Ninguna importancia individual puede ser negativa.

**Validates: Requirements 9.5**

---

### Property 17: Advertencia de R² bajo se genera correctamente

*Para cualquier* conjunto de métricas donde todos los modelos tienen `R² < 0.80`, el archivo `docs/regression_comparativa.md` generado debe contener la advertencia de poder predictivo insuficiente. Si al menos un modelo tiene `R² ≥ 0.80`, la advertencia no debe aparecer.

**Validates: Requirements 9.6**

---

### Property 18: Correlación de Pearson está en el rango válido

*Para cualquier* par de series de predicciones del modelo y valores difusos de la base simulada, la correlación de Pearson calculada debe estar en el rango `[-1.0, 1.0]`.

**Validates: Requirements 10.1**

---

### Property 19: Inconsistencia Delphi-Difuso lanza error descriptivo

*Para cualquier* archivo `data/delphi_consenso.json` cuyas Variables_Aprobadas no coincidan con las variables esperadas por el sistema difuso, `FuzzySystemBuilder.build()` debe lanzar una excepción con un mensaje descriptivo que identifique la variable inconsistente. El sistema nunca debe continuar silenciosamente con una inconsistencia de trazabilidad.

**Validates: Requirements 11.3**

---

## Error Handling

### Estrategia general

El sistema usa un enfoque de **fallo rápido y explícito**: los errores de configuración o trazabilidad lanzan excepciones inmediatamente con mensajes descriptivos. Los errores de datos (valores fuera de rango) se manejan con recorte y registro de advertencias para no interrumpir el flujo de simulación.

### Tabla de errores por módulo

| Módulo | Condición de error | Comportamiento |
|---|---|---|
| Todos | Paquete Python no disponible | `ImportError` con nombre del paquete y comando `pip install` |
| `DelphiSimulator` | `delphi_ronda1.json` no existe al iniciar ronda 2 | `FileNotFoundError` con ruta esperada |
| `FuzzySystemBuilder` | `delphi_consenso.json` no existe | `FileNotFoundError` con ruta esperada |
| `FuzzySystemBuilder` | Variables en consenso ≠ variables esperadas | `ValueError` con nombre de variable inconsistente |
| `FuzzySystemBuilder` | Valor de entrada fuera del universo | Recorte silencioso + registro en `fuzzy_warnings.json` |
| `MontecarloSimulator` | Sistema difuso no construido | `RuntimeError` indicando que `build()` debe llamarse primero |
| `RegressionAnalyzer` | `base_simulada.csv` no existe | `FileNotFoundError` con ruta esperada |
| `RegressionAnalyzer` | Columnas faltantes en CSV | `ValueError` con lista de columnas faltantes |
| Todos | Directorio `docs/` o `data/` no existe | Creación automática con `os.makedirs(exist_ok=True)` |

### Manejo de advertencias no fatales

Las advertencias no fatales se acumulan en `data/fuzzy_warnings.json` con timestamp, tipo, variable afectada y descripción. El módulo continúa operando después de registrar la advertencia.

---

## Testing Strategy

### Enfoque dual: pruebas unitarias + pruebas basadas en propiedades

El sistema usa dos capas complementarias de pruebas:

- **Pruebas unitarias**: verifican ejemplos concretos, casos de borde y condiciones de error.
- **Pruebas basadas en propiedades (PBT)**: verifican propiedades universales sobre espacios de entrada amplios.

Las pruebas unitarias capturan bugs concretos; las pruebas de propiedades verifican corrección general. Ambas son necesarias.

### Biblioteca de PBT

Se usa **[Hypothesis](https://hypothesis.readthedocs.io/)** para Python, la biblioteca de PBT más madura del ecosistema. Cada prueba de propiedad se configura con `@settings(max_examples=100)` como mínimo.

### Organización de pruebas

```
tests/
├── test_delphi.py          # Pruebas del módulo Delphi
├── test_fuzzy_system.py    # Pruebas del sistema difuso
├── test_montecarlo.py      # Pruebas del módulo Montecarlo
├── test_regression.py      # Pruebas del módulo Regresión
└── test_integration.py     # Pruebas de integración end-to-end
```

### Pruebas de propiedades (PBT)

Cada propiedad del diseño se implementa como una prueba Hypothesis con el tag correspondiente:

```python
# Ejemplo de implementación de Property 2
from hypothesis import given, settings
from hypothesis import strategies as st

@given(
    scores=st.lists(
        st.integers(min_value=1, max_value=5),
        min_size=2, max_size=10
    )
)
@settings(max_examples=100)
def test_property_2_estadisticos_correctos(scores):
    """
    Feature: riesgo-rendimiento-academico,
    Property 2: Corrección matemática de estadísticos Delphi
    """
    stats = simulator._calculate_stats(scores)
    mean = stats['mean']
    std = stats['std']
    cv = stats['cv']

    assert 1.0 <= mean <= 5.0
    assert std >= 0
    if mean > 0:
        assert abs(cv - std / mean) < 1e-9
```

### Pruebas unitarias prioritarias

| Prueba | Tipo | Descripción |
|---|---|---|
| `test_panel_roles` | SMOKE | Panel tiene entre 3–5 expertos con roles requeridos |
| `test_factors_present` | SMOKE | Los 4 factores candidatos están en ronda 1 |
| `test_consensus_json_structure` | EXAMPLE | `delphi_consenso.json` tiene todos los campos requeridos |
| `test_fuzzy_output_variable` | SMOKE | Variable de salida `riesgo` tiene universo [0,100] y 3 etiquetas |
| `test_defuzzification_method` | SMOKE | Método de defuzzificación es centroide |
| `test_simulation_count` | EXAMPLE | `base_simulada.csv` tiene ≥ 1000 filas |
| `test_three_models_trained` | EXAMPLE | Los tres modelos están entrenados después de `train_and_evaluate()` |
| `test_report_files_exist` | EXAMPLE | Todos los archivos de documentación se generan |
| `test_traceability_cell_in_notebook` | SMOKE | El notebook contiene la celda de verificación de trazabilidad |

### Pruebas de integración

| Prueba | Descripción |
|---|---|
| `test_full_pipeline` | Ejecuta el flujo completo A→B→C→D y verifica que todos los archivos de salida existen |
| `test_reproducibility` | Ejecuta el flujo dos veces con `RANDOM_SEED = 42` y verifica resultados idénticos |
| `test_traceability_chain` | Verifica que cada Variable_Entrada del modelo de regresión está en `delphi_consenso.json` |

### Tag format para PBT

```
Feature: riesgo-rendimiento-academico, Property {N}: {texto_de_la_propiedad}
```

### Configuración mínima de Hypothesis

```python
from hypothesis import settings, HealthCheck

settings.register_profile(
    "ci",
    max_examples=100,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile("ci")
```
