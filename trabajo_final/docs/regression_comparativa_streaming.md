# Reporte Comparativo de Modelos de Regresión — Streaming

**Parte E — Taller 2 de Modelos y Simulación**

## Métricas de Evaluación

| Modelo | MAE | RMSE | R² |
|--------|-----|------|-----|
| KNN (k=5) | 7.2619 | 10.5524 | 0.6385 |
| Random Forest (100 árboles) ✓ | 1.4039 | 3.2238 | 0.9663 |
| Decision Tree | 1.6924 | 4.4312 | 0.9362 |

> **Mejor modelo:** Random Forest (100 árboles) (R² = 0.9663)

## Descripción de Modelos

- **KNN (k=5):** Algoritmo basado en los 5 vecinos más cercanos. No paramétrico, sensible a la escala de las variables.
- **Random Forest (100 árboles):** Ensemble de 100 árboles de decisión con `random_state=42`. Robusto ante sobreajuste.
- **Decision Tree:** Árbol de decisión individual con `random_state=42`. Alta interpretabilidad.

## Partición de Datos

- Entrenamiento: 80% de los datos
- Prueba: 20% de los datos
- `random_state = 42`
