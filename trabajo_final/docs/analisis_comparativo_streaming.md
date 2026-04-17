# Análisis Comparativo: Sistema Difuso vs. Modelos Estadísticos (Streaming)

**Parte E — Taller 2 de Modelos y Simulación**

Este documento compara el enfoque de inferencia difusa Mamdani con modelos estadísticos de regresión supervisada para la plataforma de streaming.

---

## 1. Métricas de Evaluación de Modelos

| Modelo | MAE | RMSE | R² |
|--------|-----|------|-----|
| KNN (k=5) | 7.2619 | 10.5524 | 0.6385 |
| Random Forest (100 árboles) ✓ | 1.4039 | 3.2238 | 0.9663 |
| Decision Tree | 1.6924 | 4.4312 | 0.9362 |

> **Mejor modelo:** Random Forest (100 árboles) (R² = 0.9663)

---

## 2. Correlación de Pearson

La correlación de Pearson entre las predicciones del mejor modelo (**Random Forest (100 árboles)**) y los valores difusos reales del conjunto de prueba es:

**r = 0.9832**

Esto indica una **correlación muy alta** entre el modelo estadístico y el sistema de inferencia difusa, lo que sugiere que ambos enfoques capturan patrones similares en los datos de la plataforma de streaming.

---

## 3. Importancia de Variables

### Random Forest (100 árboles)

| Variable | Importancia |
|----------|-------------|
| usuarios_concurrentes | 0.303191 (30.32%) |
| latencia_red | 0.293633 (29.36%) |
| uso_ancho_banda | 0.203162 (20.32%) |
| capacidad_servidor | 0.200014 (20.00%) |

### Decision Tree

| Variable | Importancia |
|----------|-------------|
| usuarios_concurrentes | 0.300355 (30.04%) |
| latencia_red | 0.295578 (29.56%) |
| capacidad_servidor | 0.202923 (20.29%) |
| uso_ancho_banda | 0.201144 (20.11%) |

**Interpretación:** En Random Forest, la variable más influyente es `usuarios_concurrentes`. En Decision Tree, la variable más influyente es `usuarios_concurrentes`. La consistencia entre ambos modelos refuerza la validez de los factores priorizados en el proceso Delphi.

---

## 4. Trazabilidad: Variable → Factor Delphi → Estadísticos

| Variable | Factor Delphi | Media Delphi | CV Delphi | % Aprobación | Aprobado |
|----------|---------------|--------------|-----------|--------------|----------|
| usuarios_concurrentes | usuarios_concurrentes | 4.7500 | 0.0912 | 100.0% | ✓ |
| uso_ancho_banda | uso_ancho_banda | 4.2500 | 0.1019 | 100.0% | ✓ |
| latencia_red | latencia_red | 4.2500 | 0.1019 | 100.0% | ✓ |
| capacidad_servidor | capacidad_servidor | 4.2500 | 0.1019 | 100.0% | ✓ |

---

## 5. Conclusión: Consistencia Difuso vs. Estadístico

El análisis comparativo muestra que los modelos estadísticos de regresión logran un R² de hasta **0.9663** al predecir el índice de riesgo QoS generado por el sistema difuso Mamdani. La correlación de Pearson de **0.9832** confirma una correlación muy alta entre ambos enfoques.

Las variables priorizadas por el proceso Delphi (`usuarios_concurrentes`, `uso_ancho_banda`, `latencia_red`, `capacidad_servidor`) son consistentes con las importancias identificadas por los modelos estadísticos, validando la coherencia metodológica del sistema.
