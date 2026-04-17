# Plan de Implementación: Sistema de Evaluación de Riesgo de Bajo Rendimiento Académico

## Descripción general

Implementación incremental del flujo metodológico completo: Delphi → Sistema Difuso Mamdani → Simulación Montecarlo → Regresión/Predicción. Cada tarea construye sobre la anterior y termina con la integración en el notebook principal. Semilla global `RANDOM_SEED = 42` en todos los módulos.

## Tareas

- [x] 1. Estructura del proyecto y configuración del entorno
  - Crear los directorios: `data/`, `delphi/`, `fuzzy_system/`, `montecarlo/`, `regression/`, `notebooks/`, `docs/`, `tests/`
  - Crear `__init__.py` vacío en cada directorio que sea módulo Python: `delphi/`, `fuzzy_system/`, `montecarlo/`, `regression/`, `tests/`
  - Crear `requirements.txt` con versiones fijas: `pandas`, `numpy`, `matplotlib`, `plotly`, `scikit-fuzzy`, `scikit-learn`, `hypothesis`, `scipy`, `notebook`
  - Crear `docs/README.md` con descripción del proyecto, instrucciones de instalación (`pip install -r requirements.txt`), instrucciones de ejecución del notebook y descripción de cada entregable generado
  - _Requirements: 1.1, 1.2, 1.3, 12.3_

- [x] 2. Módulo Delphi — Panel de expertos y generación de respuestas
  - [x] 2.1 Implementar `Expert` dataclass y clase `ExpertPanel` en `delphi/expert_panel.py`
    - Definir `Expert` con campos: `id`, `nombre`, `cargo`, `dependencia`, `perfil`, `sesgo_base`
    - Implementar `ExpertPanel.__init__(seed=42)` con los 4 expertos simulados de la Pascual Bravo (E1–E4 según tabla del diseño)
    - Implementar `ExpertPanel.get_experts() -> list[Expert]`
    - Implementar `ExpertPanel.generate_likert_response(expert, factor, round_num, previous_score, group_mean) -> tuple[int, str]` con justificaciones textuales contextualizadas por perfil (docente referencia cursos, psicólogo menciona bienestar, etc.)
    - En ronda 2, ajustar puntuación hacia `group_mean` con variación aleatoria controlada ±0–1, manteniendo resultado en [1, 5]
    - _Requirements: 2.1, 2.3, 3.2_

  - [ ]* 2.2 Escribir prueba de propiedad para `generate_likert_response()`
    - **Property 1: Respuestas Likert siempre válidas**
    - **Validates: Requirements 2.3**
    - Usar `@given` con estrategias para experto, factor y ronda; verificar que la puntuación ∈ [1, 5] y la justificación no esté vacía

  - [ ]* 2.3 Escribir prueba de propiedad para convergencia en Ronda 2
    - **Property 4: Convergencia de puntuaciones en Ronda 2**
    - **Validates: Requirements 3.2**
    - Verificar que la nueva puntuación esté en `[max(1, ajustado-1), min(5, ajustado+1)]` para cualquier puntuación previa y media grupal

  - [x] 2.4 Implementar `DelphiSimulator` en `delphi/delphi_simulator.py`
    - Definir constantes `FACTORS` y `CONSENSUS_CRITERIA` según el diseño
    - Implementar `_calculate_stats(scores) -> dict` con media, std y CV
    - Implementar `_evaluate_consensus(stats, scores) -> dict` con los tres criterios (media ≥ 4, CV ≤ 0.30, aprobación ≥ 70 %)
    - Implementar `run_round1()`: genera respuestas para cada experto × factor, calcula estadísticos, persiste en `data/delphi_ronda1.json` con el esquema definido en el diseño
    - Implementar `run_round2(round1_results)`: genera respuestas ajustadas, incluye `puntuacion_anterior`, persiste en `data/delphi_ronda2.json`
    - Implementar `run_round3(round2_results)`: genera validación final, evalúa consenso, marca Variables_Aprobadas, registra criterio fallido si aplica, persiste en `data/delphi_consenso.json`
    - Implementar `_generate_report(all_rounds, consensus)`: genera `docs/delphi_informe.md` con narrativa metodológica, perfiles del panel, respuestas por ronda, estadísticos y justificación de Variables_Aprobadas
    - Crear `delphi/__init__.py` que exporte `Expert`, `ExpertPanel`, `DelphiSimulator`
    - _Requirements: 2.2, 2.4, 2.5, 3.1, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [ ]* 2.5 Escribir prueba de propiedad para `_calculate_stats()`
    - **Property 2: Corrección matemática de estadísticos Delphi**
    - **Validates: Requirements 2.4, 3.3**
    - Verificar `cv = std / mean` (cuando `mean > 0`), `std ≥ 0`, `1 ≤ mean ≤ 5`

  - [ ]* 2.6 Escribir prueba de propiedad para `_evaluate_consensus()`
    - **Property 3: Evaluación de consenso es correcta y completa**
    - **Validates: Requirements 4.2, 4.3, 4.4**
    - Verificar que `approved = True` si y solo si los tres criterios se cumplen simultáneamente; verificar que `criterio_fallido` identifica el criterio que falló

  - [ ]* 2.7 Escribir prueba de propiedad para round-trip de serialización JSON (módulo Delphi)
    - **Property 5: Round-trip de serialización JSON y CSV (Delphi)**
    - **Validates: Requirements 2.5, 3.4, 4.5**
    - Verificar que serializar y deserializar `delphi_ronda1.json`, `delphi_ronda2.json` y `delphi_consenso.json` produce datos equivalentes con todos los campos requeridos

  - [ ]* 2.8 Escribir pruebas unitarias para el módulo Delphi en `tests/test_delphi.py`
    - `test_panel_roles`: panel tiene entre 3–5 expertos con roles requeridos (docente, coordinador, psicólogo)
    - `test_factors_present`: los 4 factores candidatos están presentes en ronda 1
    - `test_consensus_json_structure`: `delphi_consenso.json` tiene todos los campos requeridos del esquema
    - _Requirements: 2.1, 2.2, 4.5_

- [ ] 3. Checkpoint — Verificar módulo Delphi
  - Ejecutar `python -m pytest tests/test_delphi.py -v` y confirmar que todas las pruebas pasan
  - Verificar que `data/delphi_ronda1.json`, `data/delphi_ronda2.json`, `data/delphi_consenso.json` y `docs/delphi_informe.md` se generan correctamente
  - Preguntar al usuario si hay ajustes antes de continuar

- [x] 4. Módulo Sistema Difuso — Variables y funciones de pertenencia
  - [x] 4.1 Implementar `FuzzySystemBuilder` en `fuzzy_system/fuzzy_system_builder.py`
    - Definir constante `UNIVERSES` con los universos de discurso del diseño
    - Implementar `__init__(consenso_path, data_dir, docs_dir)` que carga `delphi_consenso.json` y lanza `FileNotFoundError` si no existe
    - Implementar `_build_membership_functions()`: construir funciones triangulares y trapezoidales con `skfuzzy.membership.trimf` / `skfuzzy.membership.trapmf` según la tabla del diseño
    - Lanzar `ValueError` con mensaje descriptivo si las Variables_Aprobadas en el consenso no coinciden con las variables esperadas
    - Implementar `_plot_membership_functions()`: generar y guardar gráficas en `docs/fuzzy_membership_plots/` (una imagen por variable)
    - Persistir `data/fuzzy_variables.json` con el esquema definido en el diseño
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 11.3_

  - [ ]* 4.2 Escribir prueba de propiedad para tipos de funciones de pertenencia
    - **Property 8: Tipos de funciones de pertenencia son válidos**
    - **Validates: Requirements 5.4**
    - Verificar que todo tipo en `fuzzy_variables.json` pertenece a `{'triangular', 'trapezoidal', 'gaussiana'}`

  - [ ]* 4.3 Escribir prueba de propiedad para etiquetas lingüísticas
    - **Property 7: Cada Variable_Entrada tiene al menos tres etiquetas lingüísticas**
    - **Validates: Requirements 5.3**
    - Verificar que cada Variable_Entrada tiene ≥ 3 etiquetas con parámetros numéricos válidos

  - [x] 4.4 Implementar reglas Mamdani y motor de inferencia en `fuzzy_system/fuzzy_system_builder.py`
    - Implementar `_build_rules()`: construir reglas IF-THEN con `skfuzzy.control` derivadas del consenso Delphi (al menos una regla por nivel de riesgo: bajo, medio, alto)
    - Persistir `data/fuzzy_rules.json` con el esquema definido en el diseño (descripción, antecedentes, consecuente, operador, origen_delphi)
    - Registrar en `data/fuzzy_warnings.json` si alguna región del espacio de entrada no está cubierta
    - Implementar `_log_warning(message)`: acumular advertencias en `data/fuzzy_warnings.json` con timestamp
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [x] 4.5 Implementar `evaluar_riesgo()` y método `build()` en `fuzzy_system/fuzzy_system_builder.py`
    - Implementar `build()`: orquestar construcción de variables, funciones de pertenencia, reglas, persistencia y gráficas
    - Implementar `evaluar_riesgo(valores_entrada: dict) -> float`: fuzzificación → evaluación de reglas → agregación → defuzzificación centroide; recortar valores fuera del universo y registrar advertencia; retornar `float` en [0, 100]
    - Crear `fuzzy_system/__init__.py` que exporte `FuzzySystemBuilder`
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ]* 4.6 Escribir prueba de propiedad para `evaluar_riesgo()`
    - **Property 9: evaluar_riesgo() siempre retorna un valor en [0, 100]**
    - **Validates: Requirements 7.1, 7.3**
    - Usar `@given` con valores dentro de los universos de discurso; verificar que el resultado es `float` en [0.0, 100.0] sin excepciones ni NaN

  - [ ]* 4.7 Escribir prueba de propiedad para recorte de valores fuera del universo
    - **Property 10: Recorte de valores fuera del universo de discurso**
    - **Validates: Requirements 7.4**
    - Verificar que valores fuera del universo son recortados, el resultado sigue siendo válido y se registra advertencia en `fuzzy_warnings.json`

  - [ ]* 4.8 Escribir prueba de propiedad para trazabilidad Delphi → Difuso
    - **Property 6: Trazabilidad completa Delphi → Difuso → Regresión**
    - **Validates: Requirements 5.1, 11.1, 11.2**
    - Verificar que el conjunto de Variables_Entrada del sistema difuso es exactamente igual al conjunto de Variables_Aprobadas en `delphi_consenso.json`

  - [ ]* 4.9 Escribir prueba de propiedad para inconsistencia Delphi-Difuso
    - **Property 19: Inconsistencia Delphi-Difuso lanza error descriptivo**
    - **Validates: Requirements 11.3**
    - Verificar que `FuzzySystemBuilder.build()` lanza `ValueError` con mensaje descriptivo cuando las Variables_Aprobadas no coinciden con las variables esperadas

  - [ ]* 4.10 Escribir prueba de propiedad para round-trip de serialización JSON (módulo Difuso)
    - **Property 5: Round-trip de serialización JSON y CSV (Difuso)**
    - **Validates: Requirements 5.5, 6.3**
    - Verificar que `fuzzy_variables.json` y `fuzzy_rules.json` se pueden serializar y deserializar con todos los campos requeridos

  - [ ]* 4.11 Escribir pruebas unitarias para el módulo Difuso en `tests/test_fuzzy_system.py`
    - `test_fuzzy_output_variable`: variable de salida `riesgo` tiene universo [0, 100] y 3 etiquetas
    - `test_defuzzification_method`: el método de defuzzificación configurado es centroide
    - _Requirements: 5.2, 7.2_

- [ ] 5. Checkpoint — Verificar módulo Sistema Difuso
  - Ejecutar `python -m pytest tests/test_fuzzy_system.py -v` y confirmar que todas las pruebas pasan
  - Verificar que `data/fuzzy_variables.json`, `data/fuzzy_rules.json` y `docs/fuzzy_membership_plots/` se generan correctamente
  - Preguntar al usuario si hay ajustes antes de continuar

- [x] 6. Módulo Montecarlo — Simulación y estadísticas
  - [x] 6.1 Implementar `MontecarloSimulator` en `montecarlo/montecarlo_simulator.py`
    - Definir constante `DISTRIBUTIONS` con las distribuciones y justificaciones del diseño (normal truncada, beta, triangular)
    - Implementar `__init__(fuzzy_system, data_dir, docs_dir, seed=42)` con inicialización de semilla numpy
    - Implementar `_sample_inputs() -> dict`: muestrear cada Variable_Entrada según su distribución; usar `scipy.stats.truncnorm` para normal truncada, `numpy.random.beta` para beta, `numpy.random.triangular` para triangular
    - Implementar `_calculate_statistics(results: pd.Series) -> dict`: calcular media, std, min, max, percentiles 25/50/75/95 y P(riesgo ≥ 70)
    - Implementar `_identify_critical_scenarios(df) -> pd.DataFrame`: filtrar filas con `riesgo ≥ 70`
    - Implementar `_generate_histogram(results)`: generar y guardar `docs/montecarlo_histograma.png` con matplotlib
    - Implementar `_generate_distributions_doc()`: generar `docs/montecarlo_distribuciones.md` con distribución y justificación de cada variable
    - Implementar `run(n_simulaciones=1000) -> pd.DataFrame`: ejecutar simulaciones, persistir `data/base_simulada.csv`, generar histograma y documento de distribuciones; retornar DataFrame
    - Crear `montecarlo/__init__.py` que exporte `MontecarloSimulator`
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_

  - [ ]* 6.2 Escribir prueba de propiedad para valores muestreados en Montecarlo
    - **Property 11: Valores muestreados en Montecarlo respetan los universos de discurso**
    - **Validates: Requirements 8.3**
    - Verificar que para cualquier `n ≥ 1`, todos los valores muestreados están dentro de los universos: `promedio_academico ∈ [0,5]`, `inasistencia ∈ [0,100]`, `horas_estudio ∈ [0,30]`, `motivacion_estres ∈ [0,10]`

  - [ ]* 6.3 Escribir prueba de propiedad para orden de estadísticos Montecarlo
    - **Property 12: Orden correcto de estadísticos Montecarlo**
    - **Validates: Requirements 8.4**
    - Verificar que `min ≤ p25 ≤ p50 ≤ p75 ≤ p95 ≤ max` y todos los valores están en [0, 100]

  - [ ]* 6.4 Escribir prueba de propiedad para P(riesgo ≥ 70)
    - **Property 13: Probabilidad empírica P(riesgo ≥ 70) es correcta**
    - **Validates: Requirements 8.5, 8.6**
    - Verificar que `P(riesgo ≥ 70) = count(riesgo ≥ 70) / len(df)` y que los escenarios críticos son exactamente las filas con `riesgo ≥ 70`

  - [ ]* 6.5 Escribir prueba de propiedad para round-trip de serialización CSV (Montecarlo)
    - **Property 5: Round-trip de serialización JSON y CSV (Montecarlo)**
    - **Validates: Requirements 8.7**
    - Verificar que `base_simulada.csv` se puede leer con pandas y contiene las columnas esperadas con valores numéricos válidos

  - [ ]* 6.6 Escribir pruebas unitarias para el módulo Montecarlo en `tests/test_montecarlo.py`
    - `test_simulation_count`: `base_simulada.csv` tiene ≥ 1000 filas después de `run(1000)`
    - Verificar que el histograma y el documento de distribuciones se generan
    - _Requirements: 8.1, 8.8_

- [ ] 7. Checkpoint — Verificar módulo Montecarlo
  - Ejecutar `python -m pytest tests/test_montecarlo.py -v` y confirmar que todas las pruebas pasan
  - Verificar que `data/base_simulada.csv`, `docs/montecarlo_histograma.png` y `docs/montecarlo_distribuciones.md` se generan correctamente
  - Preguntar al usuario si hay ajustes antes de continuar

- [x] 8. Módulo Regresión — Entrenamiento, evaluación y análisis comparativo
  - [x] 8.1 Implementar `RegressionAnalyzer` en `regression/regression_analyzer.py`
    - Definir constantes `MODELS`, `TEST_SIZE = 0.20`, `RANDOM_STATE = 42`, `MIN_R2_THRESHOLD = 0.80`
    - Implementar `__init__(data_path, consenso_path, docs_dir)` que lanza `FileNotFoundError` si `base_simulada.csv` no existe y `ValueError` si faltan columnas
    - Implementar `load_data() -> tuple[pd.DataFrame, pd.Series]`: cargar CSV, separar features `X` y target `y = riesgo`
    - Implementar `train_and_evaluate() -> dict`: dividir 80/20 con `random_state=42`, entrenar KNN/RandomForest/DecisionTree, calcular MAE, RMSE y R² para cada modelo
    - Implementar `get_feature_importance() -> dict`: extraer importancias de RandomForest y DecisionTree
    - Implementar `calculate_pearson_correlation() -> float`: calcular correlación de Pearson entre predicciones del mejor modelo y valores difusos en el conjunto de prueba
    - Implementar `generate_scatter_plot()`: generar `docs/comparativo_difuso_vs_prediccion.png`
    - Implementar `generate_comparative_report(metrics)`: generar `docs/regression_comparativa.md` con tabla de métricas; incluir advertencia si todos los R² < 0.80
    - Implementar `generate_importance_report()`: generar `docs/regression_importancia_variables.md`
    - Implementar `generate_comparative_analysis(metrics, correlation)`: generar `docs/analisis_comparativo.md` con tabla, correlación, interpretación de importancias y sección de Trazabilidad que vincule cada Variable_Entrada a su Factor Delphi
    - Crear `regression/__init__.py` que exporte `RegressionAnalyzer`
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 10.1, 10.2, 10.3, 10.4_

  - [ ]* 8.2 Escribir prueba de propiedad para métricas de regresión
    - **Property 15: Métricas de regresión satisfacen invariantes matemáticos**
    - **Validates: Requirements 9.3**
    - Verificar que `MAE ≥ 0`, `RMSE ≥ 0`, `RMSE ≥ MAE` y `R² ≤ 1.0` para cualquier modelo entrenado

  - [ ]* 8.3 Escribir prueba de propiedad para importancias de variables
    - **Property 16: Importancias de variables suman 1.0**
    - **Validates: Requirements 9.5**
    - Verificar que la suma de importancias de RandomForest y DecisionTree es ≈ 1.0 (tolerancia `1e-6`) y ninguna importancia es negativa

  - [ ]* 8.4 Escribir prueba de propiedad para advertencia de R² bajo
    - **Property 17: Advertencia de R² bajo se genera correctamente**
    - **Validates: Requirements 9.6**
    - Verificar que la advertencia aparece en `regression_comparativa.md` si y solo si todos los modelos tienen R² < 0.80

  - [ ]* 8.5 Escribir prueba de propiedad para correlación de Pearson
    - **Property 18: Correlación de Pearson está en el rango válido**
    - **Validates: Requirements 10.1**
    - Verificar que la correlación calculada está en [-1.0, 1.0] para cualquier par de series de predicciones y valores difusos

  - [ ]* 8.6 Escribir prueba de propiedad para trazabilidad completa (Regresión)
    - **Property 6: Trazabilidad completa Delphi → Difuso → Regresión**
    - **Validates: Requirements 10.4, 11.1**
    - Verificar que cada Variable_Entrada en los modelos de regresión está presente en `delphi_consenso.json` con `aprobado = True`

  - [ ]* 8.7 Escribir pruebas unitarias para el módulo Regresión en `tests/test_regression.py`
    - `test_three_models_trained`: los tres modelos están entrenados después de `train_and_evaluate()`
    - `test_report_files_exist`: todos los archivos de documentación se generan (`regression_comparativa.md`, `regression_importancia_variables.md`, `analisis_comparativo.md`, `comparativo_difuso_vs_prediccion.png`)
    - _Requirements: 9.1, 9.4, 10.2, 10.3_

- [ ] 9. Checkpoint — Verificar módulo Regresión
  - Ejecutar `python -m pytest tests/test_regression.py -v` y confirmar que todas las pruebas pasan
  - Verificar que todos los archivos de documentación de regresión se generan correctamente
  - Preguntar al usuario si hay ajustes antes de continuar

- [x] 10. Documentación de trazabilidad
  - [x] 10.1 Generar `docs/trazabilidad.md`
    - Crear script o función en el módulo correspondiente que genere `docs/trazabilidad.md`
    - Incluir tabla que mapee cada Variable_Entrada del sistema difuso → Factor Delphi → estadísticos de consenso (media, CV, % aprobación)
    - Incluir tabla que mapee cada Regla_Difusa → justificación experta de origen (referenciando ronda y expertos del consenso)
    - _Requirements: 11.1, 11.2_

- [x] 11. Notebook principal `notebooks/proyecto_completo.ipynb`
  - [x] 11.1 Crear `notebooks/proyecto_completo.ipynb` con estructura completa
    - Celda 1 — Configuración global: importar módulos, fijar `RANDOM_SEED = 42` para `numpy.random.seed`, `random.seed` y verificar disponibilidad de paquetes (lanzar `ImportError` descriptivo si falta alguno)
    - Celda 2 — Verificación de trazabilidad: confirmar que todas las Variables_Entrada del sistema difuso están presentes en `data/delphi_consenso.json` con `aprobado = True`; mostrar resultado de verificación
    - Celda 3 — Parte A (Delphi): instanciar `ExpertPanel` y `DelphiSimulator`, ejecutar `run_round1()`, `run_round2()`, `run_round3()`, mostrar resumen de Variables_Aprobadas
    - Celda 4 — Parte B (Sistema Difuso): instanciar `FuzzySystemBuilder`, ejecutar `build()`, mostrar gráficas de funciones de pertenencia inline
    - Celda 5 — Parte C (Montecarlo): instanciar `MontecarloSimulator`, ejecutar `run(n_simulaciones=1000)`, mostrar histograma inline y estadísticas resumen
    - Celda 6 — Parte D (Regresión): instanciar `RegressionAnalyzer`, ejecutar `train_and_evaluate()`, `get_feature_importance()`, `calculate_pearson_correlation()`, generar todos los reportes, mostrar tabla comparativa inline
    - Celda 7 — Resumen final: mostrar rutas de todos los archivos generados y confirmar ejecución exitosa
    - _Requirements: 1.3, 1.4, 11.4, 12.1, 12.2, 12.4_

- [ ] 12. Pruebas de reproducibilidad e integración
  - [ ]* 12.1 Escribir prueba de propiedad para reproducibilidad con semilla fija
    - **Property 14: Reproducibilidad con semilla fija**
    - **Validates: Requirements 12.1**
    - Verificar que ejecutar cada módulo dos veces con `RANDOM_SEED = 42` produce resultados numéricamente idénticos (mismas puntuaciones Delphi, mismos valores muestreados, mismas métricas)

  - [ ]* 12.2 Escribir pruebas de integración en `tests/test_integration.py`
    - `test_full_pipeline`: ejecutar el flujo completo A→B→C→D y verificar que todos los archivos de salida existen (`delphi_ronda1.json`, `delphi_ronda2.json`, `delphi_consenso.json`, `delphi_informe.md`, `fuzzy_variables.json`, `fuzzy_rules.json`, `base_simulada.csv`, `montecarlo_histograma.png`, `regression_comparativa.md`, `analisis_comparativo.md`, `trazabilidad.md`)
    - `test_reproducibility`: ejecutar el flujo dos veces con `RANDOM_SEED = 42` y verificar resultados idénticos
    - `test_traceability_chain`: verificar que cada Variable_Entrada del modelo de regresión está en `delphi_consenso.json`
    - `test_traceability_cell_in_notebook`: verificar que el notebook contiene la celda de verificación de trazabilidad
    - _Requirements: 11.4, 12.1, 12.2_

- [ ] 13. Checkpoint final — Verificar flujo completo
  - Ejecutar `python -m pytest tests/ -v` y confirmar que todas las pruebas pasan
  - Verificar que el notebook se puede ejecutar de principio a fin sin errores
  - Confirmar que todos los archivos de `data/` y `docs/` se generan correctamente
  - Preguntar al usuario si hay ajustes finales antes de cerrar

## Notas

- Las subtareas marcadas con `*` son opcionales y pueden omitirse para una implementación MVP más rápida
- Cada tarea referencia los requisitos específicos para trazabilidad completa
- Los checkpoints garantizan validación incremental antes de avanzar a la siguiente etapa
- Las pruebas PBT usan Hypothesis con `@settings(max_examples=100)` como mínimo y el perfil `"ci"` definido en el diseño
- La semilla global `RANDOM_SEED = 42` debe fijarse en todos los módulos que usen aleatoriedad
- Los directorios `data/` y `docs/` se crean automáticamente con `os.makedirs(exist_ok=True)` si no existen
