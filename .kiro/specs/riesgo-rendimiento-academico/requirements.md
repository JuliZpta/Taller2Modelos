# Requirements Document

## Introduction

Sistema académico de evaluación de riesgo de bajo rendimiento estudiantil desarrollado en el contexto de la **Institución Universitaria Pascual Bravo** (Medellín, Colombia). El sistema sigue un flujo metodológico riguroso y trazable: método Delphi para priorización de factores → sistema de inferencia difuso Mamdani → simulación Montecarlo → modelos de regresión/predicción. El panel de expertos simulado está compuesto por perfiles reales de la Pascual Bravo (docente, coordinador académico y psicólogo de bienestar), cuyas respuestas se generan de forma programática con justificaciones contextualizadas a la institución. El sistema produce resultados reproducibles, documentados y comparables entre enfoques. El alcance cubre las Partes A, B, C y D; la Parte E queda fuera del alcance.

## Glossary

- **Sistema**: el conjunto de módulos Python que implementan el flujo metodológico completo.
- **Delphi_Module**: módulo que estructura y ejecuta el proceso Delphi con paneles de expertos simulados.
- **Panel_Expertos**: conjunto de 3 a 5 perfiles expertos simulados con identidad, cargo y dependencia institucional de la Institución Universitaria Pascual Bravo (Medellín), incluyendo al menos: docente universitario, coordinador académico y psicólogo/bienestar estudiantil.
- **Respuesta_Simulada**: puntuación Likert y justificación textual generadas programáticamente para cada experto del Panel_Expertos, coherentes con el perfil profesional y el contexto institucional de la Pascual Bravo.
- **Ronda_Delphi**: iteración del proceso Delphi (exploración, priorización o validación).
- **Factor**: variable candidata evaluada por el Panel_Expertos durante el proceso Delphi.
- **Consenso**: estado alcanzado cuando un Factor cumple simultáneamente media ≥ 4, CV ≤ 0.30 y aprobación ≥ 70 %.
- **Variable_Aprobada**: Factor que alcanzó Consenso y es admitido en el sistema difuso.
- **Fuzzy_Module**: módulo que implementa el sistema de inferencia difuso tipo Mamdani con scikit-fuzzy.
- **Variable_Entrada**: Variable_Aprobada incorporada como antecedente del sistema difuso.
- **Variable_Salida**: variable de riesgo académico (rango 0–100) producida por el sistema difuso.
- **Funcion_Pertenencia**: función triangular, trapezoidal o gaussiana que define los conjuntos difusos de cada variable.
- **Regla_Difusa**: sentencia IF-THEN que relaciona etiquetas de Variables_Entrada con etiquetas de la Variable_Salida.
- **Montecarlo_Module**: módulo que ejecuta la simulación Montecarlo sobre el sistema difuso.
- **Simulacion**: ejecución individual del sistema difuso con valores muestreados aleatoriamente.
- **Base_Simulada**: conjunto de resultados de todas las Simulaciones, almacenado como archivo estructurado.
- **Regression_Module**: módulo que entrena y evalúa modelos de regresión/predicción sobre la Base_Simulada.
- **Modelo_Prediccion**: instancia entrenada de KNN Regressor, Random Forest o Árbol de Decisión.
- **Trazabilidad**: propiedad que garantiza que cada Variable_Entrada, Funcion_Pertenencia y Regla_Difusa puede vincularse a un resultado Delphi documentado.

---

## Requirements

### Requirement 1: Estructura del proyecto y configuración del entorno

**User Story:** Como desarrollador académico, quiero una estructura de directorios modular y reproducible, para que el proyecto sea mantenible y entregable como artefacto académico.

#### Acceptance Criteria

1. THE Sistema SHALL organizar el código fuente en los directorios `data/`, `delphi/`, `fuzzy_system/`, `montecarlo/`, `regression/`, `notebooks/` y `docs/`.
2. THE Sistema SHALL incluir un archivo `requirements.txt` con versiones fijas de todas las dependencias (pandas, numpy, matplotlib, plotly, scikit-fuzzy, scikit-learn).
3. THE Sistema SHALL incluir un notebook principal `notebooks/proyecto_completo.ipynb` que ejecute el flujo completo en orden secuencial.
4. IF un módulo Python importado no está disponible en el entorno, THEN THE Sistema SHALL lanzar un mensaje de error descriptivo que indique el paquete faltante y el comando de instalación.

---

### Requirement 2: Simulación del proceso Delphi — Ronda 1 (Exploración)

**User Story:** Como investigador de la Institución Universitaria Pascual Bravo, quiero estructurar la primera ronda Delphi con un panel de expertos simulado de la institución, para que los factores candidatos queden documentados con valoraciones iniciales contextualizadas.

#### Acceptance Criteria

1. THE Delphi_Module SHALL definir un Panel_Expertos con entre 3 y 5 perfiles, incluyendo al menos los roles: docente universitario, coordinador académico y psicólogo/bienestar estudiantil, cada uno con nombre ficticio, cargo específico y dependencia dentro de la Institución Universitaria Pascual Bravo (Medellín).
2. THE Delphi_Module SHALL presentar en la Ronda 1 al menos los factores candidatos: promedio académico, porcentaje de inasistencia, horas de estudio semanales y nivel de motivación/estrés.
3. WHEN el Delphi_Module ejecuta la Ronda 1, THE Delphi_Module SHALL generar programáticamente una Respuesta_Simulada para cada experto y cada Factor: una puntuación en escala Likert de 1 a 5 y una justificación textual coherente con el perfil del experto y el contexto de la Pascual Bravo (por ejemplo, el docente referencia patrones observados en sus cursos, el psicólogo menciona factores de bienestar estudiantil de la institución).
4. WHEN la Ronda 1 finaliza, THE Delphi_Module SHALL calcular y almacenar para cada Factor: media aritmética, desviación estándar y coeficiente de variación (CV).
5. WHEN la Ronda 1 finaliza, THE Delphi_Module SHALL guardar los resultados en `data/delphi_ronda1.json` con estructura que incluya factor, puntuaciones por experto (con nombre del experto, cargo y justificación textual), media, desviación estándar y CV.

---

### Requirement 3: Simulación del proceso Delphi — Ronda 2 (Priorización)

**User Story:** Como investigador, quiero ejecutar la segunda ronda Delphi con retroalimentación estadística, para que los expertos simulados ajusten sus valoraciones hacia el consenso de forma verosímil.

#### Acceptance Criteria

1. WHEN el Delphi_Module inicia la Ronda 2, THE Delphi_Module SHALL presentar a cada experto los estadísticos de la Ronda 1 (media y CV del grupo) junto con su puntuación individual previa.
2. WHEN el Delphi_Module ejecuta la Ronda 2, THE Delphi_Module SHALL generar programáticamente una nueva Respuesta_Simulada para cada experto y cada Factor, ajustando la puntuación hacia la media grupal de la Ronda 1 con una variación aleatoria controlada (±0 a ±1 punto), de modo que el proceso refleje convergencia realista hacia el consenso.
3. WHEN la Ronda 2 finaliza, THE Delphi_Module SHALL recalcular media, desviación estándar y CV para cada Factor con las puntuaciones actualizadas.
4. WHEN la Ronda 2 finaliza, THE Delphi_Module SHALL guardar los resultados en `data/delphi_ronda2.json` con la misma estructura que la Ronda 1, incluyendo la puntuación anterior y la nueva puntuación de cada experto para evidenciar el ajuste.

---

### Requirement 4: Simulación del proceso Delphi — Ronda 3 (Validación y consenso)

**User Story:** Como investigador, quiero ejecutar la tercera ronda Delphi y determinar qué factores alcanzan consenso, para que solo las variables validadas por el panel de la Pascual Bravo ingresen al sistema difuso.

#### Acceptance Criteria

1. WHEN el Delphi_Module inicia la Ronda 3, THE Delphi_Module SHALL presentar los estadísticos de la Ronda 2 y generar programáticamente la validación final de cada Factor por parte de cada experto, con una Respuesta_Simulada que incluya puntuación definitiva y comentario de validación contextualizado al perfil del experto.
2. WHEN la Ronda 3 finaliza, THE Delphi_Module SHALL evaluar cada Factor contra los tres criterios de Consenso: media ≥ 4, CV ≤ 0.30 y porcentaje de expertos con puntuación ≥ 4 mayor o igual a 70 %.
3. WHEN un Factor cumple los tres criterios de Consenso, THE Delphi_Module SHALL marcarlo como Variable_Aprobada.
4. IF un Factor no cumple alguno de los criterios de Consenso, THEN THE Delphi_Module SHALL registrar cuál criterio falló y excluir el Factor del modelo difuso.
5. WHEN la Ronda 3 finaliza, THE Delphi_Module SHALL guardar en `data/delphi_consenso.json` la lista de Variables_Aprobadas con sus estadísticos finales, criterios evaluados y resultado de aprobación.
6. WHEN la Ronda 3 finaliza, THE Delphi_Module SHALL generar el archivo `docs/delphi_informe.md` con la narrativa metodológica del proceso, los perfiles del Panel_Expertos (nombre, cargo y dependencia en la Institución Universitaria Pascual Bravo), las respuestas simuladas por ronda, los resultados estadísticos y la justificación de cada Variable_Aprobada.

---

### Requirement 5: Definición de variables y funciones de pertenencia del sistema difuso

**User Story:** Como ingeniero de conocimiento, quiero definir las variables difusas y sus funciones de pertenencia a partir de los resultados Delphi, para que el modelo tenga Trazabilidad completa hacia el consenso experto.

#### Acceptance Criteria

1. THE Fuzzy_Module SHALL incorporar como Variables_Entrada únicamente las Variables_Aprobadas registradas en `data/delphi_consenso.json`.
2. THE Fuzzy_Module SHALL definir la Variable_Salida `riesgo` con universo de discurso en el rango [0, 100] y etiquetas: bajo (0–40), medio (30–70) y alto (60–100).
3. WHEN el Fuzzy_Module define una Variable_Entrada, THE Fuzzy_Module SHALL asignar al menos tres etiquetas lingüísticas (bajo, medio, alto) con rangos derivados del dominio de cada variable.
4. WHEN el Fuzzy_Module define una Funcion_Pertenencia, THE Fuzzy_Module SHALL utilizar exclusivamente formas triangular, trapezoidal o gaussiana implementadas con scikit-fuzzy.
5. THE Fuzzy_Module SHALL almacenar en `data/fuzzy_variables.json` la definición completa de cada variable: nombre, universo, etiquetas, tipo de función y parámetros numéricos.
6. THE Fuzzy_Module SHALL generar gráficas de las funciones de pertenencia para cada variable y guardarlas en `docs/fuzzy_membership_plots/`.

---

### Requirement 6: Definición de reglas difusas

**User Story:** Como ingeniero de conocimiento, quiero definir las reglas difusas del sistema Mamdani a partir del consenso experto, para que la lógica de inferencia sea justificable y trazable.

#### Acceptance Criteria

1. THE Fuzzy_Module SHALL definir un conjunto de Reglas_Difusas en formato IF [antecedentes] THEN [consecuente] utilizando las etiquetas de las Variables_Entrada y la Variable_Salida.
2. THE Fuzzy_Module SHALL incluir al menos una Regla_Difusa para cada combinación de nivel de riesgo (bajo, medio, alto) en la Variable_Salida.
3. THE Fuzzy_Module SHALL almacenar las Reglas_Difusas en `data/fuzzy_rules.json` con descripción textual, antecedentes, consecuente y referencia al resultado Delphi que la justifica.
4. IF el conjunto de Reglas_Difusas no cubre alguna región del espacio de entrada definida por las Variables_Entrada, THEN THE Fuzzy_Module SHALL registrar la región no cubierta en un archivo de advertencias `data/fuzzy_warnings.json`.

---

### Requirement 7: Motor de inferencia difuso Mamdani

**User Story:** Como analista, quiero ejecutar el sistema de inferencia difuso sobre valores de entrada concretos, para que el sistema produzca un valor de riesgo entre 0 y 100.

#### Acceptance Criteria

1. WHEN el Fuzzy_Module recibe un conjunto de valores de entrada válidos para todas las Variables_Entrada, THE Fuzzy_Module SHALL ejecutar el proceso de inferencia Mamdani completo: fuzzificación → evaluación de reglas → agregación → defuzzificación.
2. THE Fuzzy_Module SHALL utilizar el método de defuzzificación centroide (centro de gravedad).
3. WHEN el Fuzzy_Module produce un resultado, THE Variable_Salida SHALL tener un valor numérico en el rango [0, 100].
4. IF algún valor de entrada está fuera del universo de discurso de su Variable_Entrada, THEN THE Fuzzy_Module SHALL recortar el valor al límite más cercano del universo y registrar la advertencia en `data/fuzzy_warnings.json`.
5. THE Fuzzy_Module SHALL exponer una función `evaluar_riesgo(valores_entrada: dict) -> float` que pueda ser invocada por otros módulos.

---

### Requirement 8: Simulación Montecarlo

**User Story:** Como analista de riesgo, quiero ejecutar al menos 1000 simulaciones del sistema difuso con valores muestreados aleatoriamente, para que pueda estimar la distribución de probabilidad del riesgo académico.

#### Acceptance Criteria

1. THE Montecarlo_Module SHALL ejecutar un mínimo de 1000 Simulaciones independientes del sistema difuso.
2. WHEN el Montecarlo_Module define la distribución de muestreo de cada Variable_Entrada, THE Montecarlo_Module SHALL documentar en `docs/montecarlo_distribuciones.md` la distribución elegida (uniforme, normal, beta u otra) y su justificación estadística.
3. WHEN el Montecarlo_Module ejecuta las Simulaciones, THE Montecarlo_Module SHALL muestrear los valores de cada Variable_Entrada de forma independiente según su distribución asignada.
4. WHEN todas las Simulaciones finalizan, THE Montecarlo_Module SHALL calcular: media, desviación estándar, mínimo, máximo y percentiles 25, 50, 75 y 95 del riesgo simulado.
5. WHEN todas las Simulaciones finalizan, THE Montecarlo_Module SHALL calcular la probabilidad P(riesgo ≥ 70) como proporción de Simulaciones con resultado mayor o igual a 70.
6. WHEN todas las Simulaciones finalizan, THE Montecarlo_Module SHALL identificar y almacenar los escenarios críticos, definidos como Simulaciones con riesgo ≥ 70, incluyendo los valores de entrada que los produjeron.
7. WHEN todas las Simulaciones finalizan, THE Montecarlo_Module SHALL guardar la Base_Simulada en `data/base_simulada.csv` con columnas para cada Variable_Entrada y la Variable_Salida.
8. THE Montecarlo_Module SHALL generar un histograma de la distribución del riesgo simulado y guardarlo en `docs/montecarlo_histograma.png`.

---

### Requirement 9: Entrenamiento y evaluación de modelos de predicción

**User Story:** Como científico de datos, quiero entrenar modelos de regresión sobre la Base_Simulada, para que pueda predecir el riesgo académico y comparar el enfoque estadístico con el difuso.

#### Acceptance Criteria

1. THE Regression_Module SHALL entrenar los siguientes Modelos_Prediccion sobre la Base_Simulada: KNN Regressor, Random Forest Regressor y Árbol de Decisión Regressor.
2. WHEN el Regression_Module divide la Base_Simulada, THE Regression_Module SHALL utilizar una partición 80 % entrenamiento / 20 % prueba con semilla aleatoria fija para reproducibilidad.
3. WHEN el Regression_Module evalúa cada Modelo_Prediccion, THE Regression_Module SHALL calcular sobre el conjunto de prueba: MAE (Mean Absolute Error), RMSE (Root Mean Squared Error) y R² (coeficiente de determinación).
4. THE Regression_Module SHALL generar una tabla comparativa de métricas para los tres Modelos_Prediccion y guardarla en `docs/regression_comparativa.md`.
5. THE Regression_Module SHALL calcular la importancia de Variables_Entrada para el modelo Random Forest y el Árbol de Decisión, y guardar los resultados en `docs/regression_importancia_variables.md`.
6. IF el R² de todos los Modelos_Prediccion es inferior a 0.80, THEN THE Regression_Module SHALL registrar una advertencia en `docs/regression_comparativa.md` indicando que el poder predictivo es insuficiente para reemplazar el sistema difuso.

---

### Requirement 10: Análisis comparativo entre sistema difuso y modelos de predicción

**User Story:** Como investigador, quiero comparar los resultados del sistema difuso con los de los modelos de regresión, para que pueda evaluar la consistencia metodológica del flujo completo.

#### Acceptance Criteria

1. THE Regression_Module SHALL calcular la correlación de Pearson entre las predicciones del mejor Modelo_Prediccion y los valores de la Variable_Salida generados por el sistema difuso en la Base_Simulada.
2. THE Regression_Module SHALL generar un gráfico de dispersión (predicciones vs. valores difusos) para el mejor Modelo_Prediccion y guardarlo en `docs/comparativo_difuso_vs_prediccion.png`.
3. THE Regression_Module SHALL producir el archivo `docs/analisis_comparativo.md` con: tabla de métricas, correlación, interpretación de la importancia de variables y conclusión sobre la consistencia entre el enfoque difuso y el estadístico.
4. WHEN el Regression_Module genera el análisis comparativo, THE Regression_Module SHALL incluir una sección de Trazabilidad que vincule cada Variable_Entrada del modelo con su Factor Delphi de origen.

---

### Requirement 11: Trazabilidad completa del flujo metodológico

**User Story:** Como evaluador académico, quiero que cada decisión de diseño del sistema pueda rastrearse hasta su origen en el proceso Delphi, para que el proyecto cumpla con los estándares de rigor metodológico.

#### Acceptance Criteria

1. THE Sistema SHALL mantener un archivo `docs/trazabilidad.md` que mapee cada Variable_Entrada del sistema difuso a su Factor Delphi correspondiente, incluyendo estadísticos de consenso.
2. THE Sistema SHALL mantener en `docs/trazabilidad.md` el mapeo de cada Regla_Difusa a la justificación experta que la originó.
3. IF el Delphi_Module modifica la lista de Variables_Aprobadas, THEN THE Fuzzy_Module SHALL detectar la inconsistencia al cargar `data/delphi_consenso.json` y lanzar un error descriptivo antes de continuar.
4. THE Sistema SHALL incluir en el notebook `notebooks/proyecto_completo.ipynb` una celda de verificación de Trazabilidad que confirme que todas las Variables_Entrada del sistema difuso están presentes en `data/delphi_consenso.json`.

---

### Requirement 12: Reproducibilidad y documentación de entregables

**User Story:** Como docente evaluador, quiero que el proyecto sea completamente reproducible y esté documentado, para que pueda verificar los resultados ejecutando el notebook desde cero.

#### Acceptance Criteria

1. THE Sistema SHALL fijar todas las semillas aleatorias (numpy, random, scikit-learn) con un valor constante documentado al inicio del notebook.
2. WHEN el notebook `notebooks/proyecto_completo.ipynb` se ejecuta en orden desde la primera celda, THE Sistema SHALL completar el flujo completo (Partes A, B, C y D) sin errores de ejecución.
3. THE Sistema SHALL incluir el archivo `docs/README.md` con: descripción del proyecto, instrucciones de instalación, instrucciones de ejecución y descripción de cada entregable generado.
4. THE Sistema SHALL generar todos los archivos de datos (`data/`) y documentos (`docs/`) como resultado de la ejecución del notebook, sin requerir archivos preexistentes distintos al código fuente.
```
