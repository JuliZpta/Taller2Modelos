# Análisis Comparativo: Sistema Difuso vs. Modelos Estadísticos

**Institución Universitaria Pascual Bravo · Medellín, Colombia**

Este documento compara el enfoque de inferencia difusa Mamdani con modelos estadísticos de regresión supervisada, evaluando la consistencia metodológica y la capacidad predictiva de cada enfoque.

---

## 1. Métricas de Evaluación de Modelos

| Modelo | MAE | RMSE | R² |
|--------|-----|------|-----|
| KNN (k=5) | 10.7976 | 13.7779 | 0.5814 |
| Random Forest ✓ | 1.8447 | 3.3867 | 0.9747 |
| Decision Tree | 2.3299 | 5.3156 | 0.9377 |
| SVR (RBF) | 4.8029 | 6.5474 | 0.9055 |

> **Mejor modelo:** Random Forest (R² = 0.9747)

---

## 2. Correlación de Pearson

La correlación de Pearson entre las predicciones del mejor modelo (**Random Forest**) y los valores difusos reales del conjunto de prueba es:

**r = 0.9877**

Esto indica una **correlación muy alta** entre el modelo estadístico y el sistema de inferencia difusa, lo que sugiere que ambos enfoques capturan patrones similares en los datos.

---

## 3. Importancia de Variables

### Random Forest

| Variable | Importancia |
|----------|-------------|
| inasistencia | 0.500071 (50.01%) |
| promedio_academico | 0.410443 (41.04%) |
| horas_estudio | 0.049167 (4.92%) |
| motivacion_estres | 0.040319 (4.03%) |

### Decision Tree

| Variable | Importancia |
|----------|-------------|
| inasistencia | 0.489572 (48.96%) |
| promedio_academico | 0.422477 (42.25%) |
| horas_estudio | 0.048340 (4.83%) |
| motivacion_estres | 0.039611 (3.96%) |

**Interpretación:** En Random Forest, la variable más influyente es `inasistencia`. En Decision Tree, la variable más influyente es `inasistencia`. La consistencia entre ambos modelos en el ranking de importancias refuerza la validez de los factores priorizados en el proceso Delphi.

---

## 4. Trazabilidad: Variable_Entrada → Factor Delphi → Estadísticos

La siguiente tabla vincula cada Variable_Entrada del modelo de regresión con su Factor Delphi correspondiente y los estadísticos de consenso obtenidos en la Ronda 3 del proceso Delphi.

| Variable_Entrada | Factor Delphi | Media Delphi | CV Delphi | % Aprobación | Aprobado |
|-----------------|---------------|--------------|-----------|--------------|----------|
| promedio_academico | promedio_academico | 4.7500 | 0.0912 | 100.0% | ✓ |
| inasistencia | inasistencia | 4.2500 | 0.1019 | 100.0% | ✓ |
| horas_estudio | horas_estudio | 4.2500 | 0.1019 | 100.0% | ✓ |
| motivacion_estres | motivacion_estres | 4.2500 | 0.1019 | 100.0% | ✓ |

---

## 5. Conclusión: Consistencia Difuso vs. Estadístico

El análisis comparativo muestra que los modelos estadísticos de regresión logran un R² de hasta **0.9747** al predecir el índice de riesgo generado por el sistema difuso Mamdani. La correlación de Pearson de **0.9877** confirma una correlación muy alta entre ambos enfoques.

Las variables priorizadas por el proceso Delphi (`promedio_academico`, `inasistencia`, `horas_estudio`, `motivacion_estres`) son consistentes con las importancias identificadas por los modelos estadísticos, lo que valida la coherencia metodológica del sistema.

Esta consistencia entre el enfoque experto-difuso y el enfoque estadístico-supervisado proporciona evidencia de la solidez del modelo de evaluación de riesgo académico desarrollado para la Institución Universitaria Pascual Bravo.
