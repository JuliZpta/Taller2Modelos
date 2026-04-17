# Reporte Comparativo de Modelos de Regresión

**Institución Universitaria Pascual Bravo · Medellín, Colombia**

## Métricas de Evaluación

| Modelo | MAE | RMSE | R² |
|--------|-----|------|-----|
| KNN (k=5) | 7.5071 | 10.9894 | 0.3102 |
| Random Forest ✓ | 2.4183 | 5.2906 | 0.8401 |
| Decision Tree | 2.9258 | 6.3978 | 0.7662 |

> **Mejor modelo:** Random Forest (R² = 0.8401)

## Descripción de Modelos

- **KNN (k=5):** Algoritmo basado en los 5 vecinos más cercanos. No paramétrico, sensible a la escala de las variables.
- **Random Forest:** Ensemble de 100 árboles de decisión con `random_state=42`. Robusto ante sobreajuste.
- **Decision Tree:** Árbol de decisión individual con `random_state=42`. Alta interpretabilidad.

## Partición de Datos

- Entrenamiento: 80% de los datos
- Prueba: 20% de los datos
- `random_state = 42`
