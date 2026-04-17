# Análisis Comparativo: Sistema Difuso vs. Modelos Estadísticos

**Institución Universitaria Pascual Bravo · Medellín, Colombia**

Este documento compara el enfoque de inferencia difusa Mamdani con modelos estadísticos de regresión supervisada, evaluando la consistencia metodológica y la capacidad predictiva de cada enfoque.

---

## 1. Métricas de Evaluación de Modelos

| Modelo | MAE | RMSE | R² |
|--------|-----|------|-----|
| KNN (k=5) | 7.5071 | 10.9894 | 0.3102 |
| Random Forest ✓ | 2.4183 | 5.2906 | 0.8401 |
| Decision Tree | 2.9258 | 6.3978 | 0.7662 |

> **Mejor modelo:** Random Forest (R² = 0.8401)

---

## 2. Correlación de Pearson

La correlación de Pearson entre las predicciones del mejor modelo (**Random Forest**) y los valores difusos reales del conjunto de prueba es:

**r = 0.9186**

Esto indica una **correlación muy alta** entre el modelo estadístico y el sistema de inferencia difusa, lo que sugiere que ambos enfoques capturan patrones similares en los datos.

---

## 3. Importancia de Variables

### Random Forest

| Variable | Importancia |
|----------|-------------|
| promedio_academico | 0.458938 (45.89%) |
| horas_estudio | 0.245721 (24.57%) |
| motivacion_estres | 0.158494 (15.85%) |
| inasistencia | 0.136846 (13.68%) |

### Decision Tree

| Variable | Importancia |
|----------|-------------|
| promedio_academico | 0.449230 (44.92%) |
| horas_estudio | 0.254630 (25.46%) |
| motivacion_estres | 0.149516 (14.95%) |
| inasistencia | 0.146625 (14.66%) |

**Interpretación:** En Random Forest, la variable más influyente es `promedio_academico`. En Decision Tree, la variable más influyente es `promedio_academico`. La consistencia entre ambos modelos en el ranking de importancias refuerza la validez de los factores priorizados en el proceso Delphi.

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

El análisis comparativo muestra que los modelos estadísticos de regresión logran un R² de hasta **0.8401** al predecir el índice de riesgo generado por el sistema difuso Mamdani. La correlación de Pearson de **0.9186** confirma una correlación muy alta entre ambos enfoques.

Las variables priorizadas por el proceso Delphi (`promedio_academico`, `inasistencia`, `horas_estudio`, `motivacion_estres`) son consistentes con las importancias identificadas por los modelos estadísticos, lo que valida la coherencia metodológica del sistema.

Esta consistencia entre el enfoque experto-difuso y el enfoque estadístico-supervisado proporciona evidencia de la solidez del modelo de evaluación de riesgo académico desarrollado para la Institución Universitaria Pascual Bravo.
