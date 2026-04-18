# Distribuciones Estadísticas — Simulación Montecarlo (Streaming)

**Parte E — Taller 2 de Modelos y Simulación**

## Descripción

Este documento describe las distribuciones estadísticas utilizadas para muestrear cada variable de entrada en la simulación Montecarlo del sistema difuso de evaluación del riesgo QoS en la plataforma de streaming.

## Distribuciones por Variable

| Variable | Distribución | Parámetros | Justificación |
|---|---|---|---|
| `usuarios_concurrentes` | Beta | alpha=2.0, beta=3.0, scale=100.0 | Mayoría de tiempo con carga media-baja, picos en horas pico. Beta(2,3) modela la asimetría positiva: la plataforma opera frecuentemente por debajo del 50% de capacidad con picos ocasionales. |
| `uso_ancho_banda` | Normal Truncada | mean=55.0, std=20.0, low=0.0, high=100.0 | Uso promedio del 55% con variabilidad alta en horas pico. La distribución normal truncada en [0,100] refleja el comportamiento típico del ancho de banda en plataformas de streaming activas. |
| `latencia_red` | Triangular | low=0.0, mode=3.0, high=10.0 | Latencia típica baja con cola hacia valores altos en congestión. La distribución triangular con moda=3ms refleja condiciones normales de red con eventos ocasionales de alta latencia por congestión. |
| `capacidad_servidor` | Beta | alpha=3.0, beta=2.0, scale=100.0 | Servidores operan típicamente a alta capacidad en plataformas activas. Beta(3,2) modela la tendencia a operar en rangos altos de utilización con cola hacia valores bajos durante períodos de baja demanda. |

## Estadísticas de la Simulación

| Estadístico | Valor |
|---|---|
| Media del riesgo QoS | 36.5823 |
| Desviación estándar | 16.1409 |
| Mínimo | 17.0513 |
| Percentil 25 (P25) | 20.4621 |
| Mediana (P50) | 34.7029 |
| Percentil 75 (P75) | 47.6349 |
| Percentil 95 (P95) | 63.8628 |
| Máximo | 91.5635 |
| P(riesgo_qos ≥ 70) | 0.0290 (2.9%) |

## Notas Metodológicas

- La semilla global `RANDOM_SEED = 42` garantiza reproducibilidad completa.
- La distribución normal truncada usa `scipy.stats.truncnorm` para respetar los límites del universo de discurso.
- Las distribuciones beta y triangular usan `numpy.random.default_rng` para consistencia con la semilla global.
- El umbral de riesgo alto se define en **70** puntos sobre 100.
- Se ejecutaron **5000 simulaciones** con `RANDOM_SEED = 42`.
