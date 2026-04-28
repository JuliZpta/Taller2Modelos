# Importancia de Variables — Modelos de Regresión

**Institución Universitaria Pascual Bravo · Medellín, Colombia**

La importancia de variables cuantifica la contribución relativa de cada Variable_Entrada al poder predictivo del modelo. Los valores suman 1.0.

## Random Forest

| Variable | Importancia | Porcentaje |
|----------|-------------|------------|
| inasistencia | 0.500071 | 50.01% |
| promedio_academico | 0.410443 | 41.04% |
| horas_estudio | 0.049167 | 4.92% |
| motivacion_estres | 0.040319 | 4.03% |

**Variable más influyente:** `inasistencia` (50.01% de importancia).

## Decision Tree

| Variable | Importancia | Porcentaje |
|----------|-------------|------------|
| inasistencia | 0.489572 | 48.96% |
| promedio_academico | 0.422477 | 42.25% |
| horas_estudio | 0.048340 | 4.83% |
| motivacion_estres | 0.039611 | 3.96% |

**Variable más influyente:** `inasistencia` (48.96% de importancia).

## Interpretación General

Las variables con mayor importancia son las que el modelo utiliza con mayor frecuencia para realizar divisiones en los árboles de decisión (Random Forest y Decision Tree). Una importancia alta indica que la variable tiene alta capacidad discriminativa para predecir el nivel de riesgo académico.

La consistencia entre Random Forest y Decision Tree en el ranking de importancias refuerza la validez de los factores priorizados en el proceso Delphi.
