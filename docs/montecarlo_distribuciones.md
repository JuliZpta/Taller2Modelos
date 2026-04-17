# Distribuciones Estadísticas — Simulación Montecarlo

**Institución Universitaria Pascual Bravo · Medellín, Colombia**

## Descripción

Este documento describe las distribuciones estadísticas utilizadas para muestrear cada variable de entrada en la simulación Montecarlo del sistema difuso de evaluación de riesgo académico. Cada distribución fue seleccionada con base en evidencia empírica y justificación metodológica.

## Distribuciones por Variable

| Variable | Distribución | Parámetros | Justificación |
|---|---|---|---|
| `promedio_academico` | Normal Truncada | mean=3.5, std=0.7, low=0.0, high=5.0 | El promedio académico en poblaciones universitarias sigue una distribución aproximadamente normal. Se trunca en [0,5] para respetar el universo de discurso. Media 3.5 y std 0.7 reflejan la distribución típica observada en instituciones colombianas. |
| `inasistencia` | Beta | alpha=2.0, beta=5.0, scale=100.0 | La inasistencia es una proporción en [0,100]. La distribución Beta(2,5) modela la asimetría positiva observada: la mayoría de estudiantes tiene inasistencia baja, con cola hacia valores altos. |
| `horas_estudio` | Triangular | low=0.0, mode=12.0, high=30.0 | Las horas de estudio tienen límites naturales claros (0–30 h/semana). La distribución triangular es apropiada cuando se conocen mínimo, máximo y valor más probable. Moda en 12 h refleja el promedio reportado en encuestas de hábitos de estudio universitario. |
| `motivacion_estres` | Triangular | low=0.0, mode=5.0, high=10.0 | Escala subjetiva [0–10] con distribución simétrica alrededor del punto medio. La triangular con moda=5 modela la tendencia central sin asumir normalidad en escalas ordinales. |

## Estadísticas de la Simulación

| Estadístico | Valor |
|---|---|
| Media del riesgo | 51.3808 |
| Desviación estándar | 13.1247 |
| Mínimo | 15.5556 |
| Percentil 25 (P25) | 50.0000 |
| Mediana (P50) | 50.0000 |
| Percentil 75 (P75) | 56.0795 |
| Percentil 95 (P95) | 72.2141 |
| Máximo | 84.3612 |
| P(riesgo ≥ 70) | 0.0710 (7.1%) |

## Notas Metodológicas

- La semilla global `RANDOM_SEED = 42` garantiza reproducibilidad completa.
- La distribución normal truncada usa `scipy.stats.truncnorm` para respetar los límites del universo de discurso.
- Las distribuciones beta y triangular usan `numpy.random.default_rng` para consistencia con la semilla global.
- El umbral de riesgo alto se define en **70** puntos sobre 100.
