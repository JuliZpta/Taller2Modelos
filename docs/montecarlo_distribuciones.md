# Distribuciones Estadísticas — Simulación Montecarlo

**Institución Universitaria Pascual Bravo · Medellín, Colombia**

## Descripción

Este documento describe las distribuciones estadísticas utilizadas para muestrear cada variable de entrada en la simulación Montecarlo del sistema difuso de evaluación de riesgo académico. Cada distribución fue seleccionada con base en evidencia empírica y justificación metodológica.

## Distribuciones por Variable

| Variable | Distribución | Parámetros | Justificación |
|---|---|---|---|
| `promedio_academico` | uniform | low=0.5, high=5.0 | Se usa distribución uniforme para cubrir todo el espacio de estados del sistema difuso y obtener una distribución de riesgo representativa de todos los escenarios posibles, desde el más favorable al más crítico. |
| `inasistencia` | uniform | low=0.0, high=100.0 | Distribución uniforme para explorar todo el rango de inasistencia y garantizar cobertura completa del espacio de entrada del sistema difuso. |
| `horas_estudio` | uniform | low=0.0, high=30.0 | Distribución uniforme sobre el universo de discurso [0,30] para explorar todos los escenarios posibles de dedicación al estudio. |
| `motivacion_estres` | uniform | low=0.0, high=10.0 | Distribución uniforme sobre la escala [0,10] para cubrir todos los niveles de motivación/estrés en la simulación. |

## Estadísticas de la Simulación

| Estadístico | Valor |
|---|---|
| Media del riesgo | 54.2630 |
| Desviación estándar | 22.4219 |
| Mínimo | 7.4286 |
| Percentil 25 (P25) | 40.4463 |
| Mediana (P50) | 47.4805 |
| Percentil 75 (P75) | 69.3093 |
| Percentil 95 (P95) | 90.1842 |
| Máximo | 90.1842 |
| P(riesgo ≥ 70) | 0.2240 (22.4%) |

## Notas Metodológicas

- La semilla global `RANDOM_SEED = 42` garantiza reproducibilidad completa.
- La distribución normal truncada usa `scipy.stats.truncnorm` para respetar los límites del universo de discurso.
- Las distribuciones beta y triangular usan `numpy.random.default_rng` para consistencia con la semilla global.
- El umbral de riesgo alto se define en **70** puntos sobre 100.
