# Importancia de Variables — Modelos de Regresión

**Institución Universitaria Pascual Bravo · Medellín, Colombia**

La importancia de variables cuantifica la contribución relativa de cada Variable_Entrada al poder predictivo del modelo. Los valores suman 1.0.

## Random Forest

| Variable | Importancia | Porcentaje |
|----------|-------------|------------|
| promedio_academico | 0.458938 | 45.89% |
| horas_estudio | 0.245721 | 24.57% |
| motivacion_estres | 0.158494 | 15.85% |
| inasistencia | 0.136846 | 13.68% |

**Variable más influyente:** `promedio_academico` (45.89% de importancia).

## Decision Tree

| Variable | Importancia | Porcentaje |
|----------|-------------|------------|
| promedio_academico | 0.449230 | 44.92% |
| horas_estudio | 0.254630 | 25.46% |
| motivacion_estres | 0.149516 | 14.95% |
| inasistencia | 0.146625 | 14.66% |

**Variable más influyente:** `promedio_academico` (44.92% de importancia).

## Interpretación General

Las variables con mayor importancia son las que el modelo utiliza con mayor frecuencia para realizar divisiones en los árboles de decisión (Random Forest y Decision Tree). Una importancia alta indica que la variable tiene alta capacidad discriminativa para predecir el nivel de riesgo académico.

La consistencia entre Random Forest y Decision Tree en el ranking de importancias refuerza la validez de los factores priorizados en el proceso Delphi.
