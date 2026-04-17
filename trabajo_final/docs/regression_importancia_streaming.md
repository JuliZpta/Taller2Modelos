# Importancia de Variables — Modelos de Regresión (Streaming)

**Parte E — Taller 2 de Modelos y Simulación**

La importancia de variables cuantifica la contribución relativa de cada variable de entrada al poder predictivo del modelo. Los valores suman 1.0.

## Random Forest (100 árboles)

| Variable | Importancia | Porcentaje |
|----------|-------------|------------|
| usuarios_concurrentes | 0.303191 | 30.32% |
| latencia_red | 0.293633 | 29.36% |
| uso_ancho_banda | 0.203162 | 20.32% |
| capacidad_servidor | 0.200014 | 20.00% |

**Variable más influyente:** `usuarios_concurrentes` (30.32% de importancia).

## Decision Tree

| Variable | Importancia | Porcentaje |
|----------|-------------|------------|
| usuarios_concurrentes | 0.300355 | 30.04% |
| latencia_red | 0.295578 | 29.56% |
| capacidad_servidor | 0.202923 | 20.29% |
| uso_ancho_banda | 0.201144 | 20.11% |

**Variable más influyente:** `usuarios_concurrentes` (30.04% de importancia).

## Interpretación General

Las variables con mayor importancia son las que el modelo utiliza con mayor frecuencia para realizar divisiones en los árboles de decisión. Una importancia alta indica alta capacidad discriminativa para predecir el nivel de riesgo QoS en la plataforma de streaming.

La consistencia entre Random Forest y Decision Tree en el ranking de importancias refuerza la validez de los factores priorizados en el proceso Delphi.
