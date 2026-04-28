# Reporte Comparativo de Modelos de Regresión

**Institución Universitaria Pascual Bravo · Medellín, Colombia**

## Métricas de Evaluación

| Modelo | MAE | RMSE | R² |
|--------|-----|------|-----|
| KNN (k=5) | 10.7976 | 13.7779 | 0.5814 |
| Random Forest ✓ | 1.8447 | 3.3867 | 0.9747 |
| Decision Tree | 2.3299 | 5.3156 | 0.9377 |
| SVR (RBF) | 4.8029 | 6.5474 | 0.9055 |

> **Mejor modelo:** Random Forest (R² = 0.9747)

## Descripción de Modelos

- **KNN (k=5):** Algoritmo basado en los 5 vecinos más cercanos. No paramétrico, sensible a la escala de las variables.
- **Random Forest:** Ensemble de 100 árboles de decisión con `random_state=42`. Robusto ante sobreajuste.
- **Decision Tree:** Árbol de decisión individual con `random_state=42`. Alta interpretabilidad.
- **SVR (RBF):** Support Vector Regression con kernel RBF (Radial Basis Function). Usa escalado estándar de variables y parámetros C=100, gamma='scale', epsilon=0.1. Efectivo para relaciones no lineales complejas.

## Partición de Datos

- Entrenamiento: 80% de los datos
- Prueba: 20% de los datos
- `random_state = 42`
