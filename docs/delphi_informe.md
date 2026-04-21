# Informe del Proceso Delphi — Riesgo de Bajo Rendimiento Académico

## Institución Universitaria Pascual Bravo, Medellín

**Fecha de generación:** 2026-04-21 00:37 UTC

---

## 1. Descripción Metodológica del Proceso Delphi

El método Delphi es una técnica de consulta estructurada a expertos que busca alcanzar consenso sobre un tema mediante rondas iterativas de retroalimentación. En este estudio se aplicaron **tres rondas** para validar los factores candidatos de riesgo de bajo rendimiento académico en la Institución Universitaria Pascual Bravo.

**Ronda 1 — Evaluación inicial:** Cada experto asignó una puntuación Likert (1–5) a cada factor candidato de forma independiente, sin conocer las respuestas de los demás. Se calcularon la media, la desviación estándar y el coeficiente de variación (CV) por factor.

**Ronda 2 — Retroalimentación y ajuste:** Los expertos recibieron la media grupal de la ronda anterior y tuvieron la oportunidad de revisar y ajustar sus puntuaciones. Este proceso favorece la convergencia hacia el consenso.

**Ronda 3 — Validación final:** Se realizó una última ronda de ajuste con menor variación permitida (±0.3). Al finalizar, se evaluaron los criterios de consenso para determinar qué factores son aprobados como variables del modelo.

**Criterios de consenso aplicados:**

| Criterio | Umbral |
|---|---|
| Media grupal | ≥ 4.0 |
| Coeficiente de variación (CV) | ≤ 0.3 |
| Porcentaje de aprobación (puntuación ≥ 4) | ≥ 70.0 % |

---

## 2. Perfiles del Panel de Expertos

El panel está conformado por cuatro expertos de la Institución Universitaria Pascual Bravo, con perfiles complementarios que cubren las dimensiones docente, administrativa, psicosocial y directiva.

| ID | Nombre | Cargo | Dependencia |
|---|---|---|---|
| E1 | Dr. Carlos Restrepo | Docente de Ingeniería de Sistemas | Facultad de Ingeniería |
| E2 | Mg. Adriana Gómez | Coordinadora Académica | Vicerrectoría Académica |
| E3 | Ps. Juliana Martínez | Psicóloga de Bienestar Estudiantil | Bienestar Universitario |
| E4 | Dr. Hernán Ospina | Director de Currículo | Vicerrectoría Académica |

---

## 3. Resultados por Ronda

### 3.1. Ronda 1 — Evaluación Inicial

| Factor | Media | Std | CV |
|---|---|---|---|
| promedio_academico | 4.2500 | 0.4330 | 0.1019 |
| inasistencia | 4.5000 | 0.5000 | 0.1111 |
| horas_estudio | 4.2500 | 0.4330 | 0.1019 |
| motivacion_estres | 4.5000 | 0.5000 | 0.1111 |

### 3.2. Ronda 2 — Retroalimentación y Ajuste

| Factor | Media | Std | CV |
|---|---|---|---|
| promedio_academico | 4.7500 | 0.4330 | 0.0912 |
| inasistencia | 4.2500 | 0.4330 | 0.1019 |
| horas_estudio | 4.2500 | 0.4330 | 0.1019 |
| motivacion_estres | 4.5000 | 0.5000 | 0.1111 |

### 3.3. Ronda 3 — Validación Final

| Factor | Media | Std | CV | Aprobado |
|---|---|---|---|---|
| promedio_academico | 4.7500 | 0.4330 | 0.0912 | ✅ Sí |
| inasistencia | 4.2500 | 0.4330 | 0.1019 | ✅ Sí |
| horas_estudio | 4.2500 | 0.4330 | 0.1019 | ✅ Sí |
| motivacion_estres | 4.2500 | 0.4330 | 0.1019 | ✅ Sí |

---

## 4. Variables Aprobadas

Las siguientes variables alcanzaron consenso en las tres rondas y serán utilizadas como variables de entrada del sistema de inferencia difuso:

| Factor | Media | CV | % Aprobación | Resultado |
|---|---|---|---|---|
| promedio_academico | 4.7500 | 0.0912 | 100.0 % | ✅ Aprobado |
| inasistencia | 4.2500 | 0.1019 | 100.0 % | ✅ Aprobado |
| horas_estudio | 4.2500 | 0.1019 | 100.0 % | ✅ Aprobado |
| motivacion_estres | 4.2500 | 0.1019 | 100.0 % | ✅ Aprobado |

---

## 5. Variables Rechazadas

Todas las variables candidatas alcanzaron consenso. No hay variables rechazadas.

---

## 6. Conclusión Metodológica

El proceso Delphi de tres rondas permitió validar **4 de 4 factores candidatos** para el modelo de riesgo de bajo rendimiento académico en la Institución Universitaria Pascual Bravo.

Los factores aprobados — `promedio_academico`, `inasistencia`, `horas_estudio`, `motivacion_estres` — presentaron alta convergencia entre los expertos del panel, con medias superiores a 4.0, coeficientes de variación bajos (≤ 0.30) y porcentajes de aprobación superiores al 70 %. Estos factores constituyen la base del sistema de inferencia difuso Mamdani que se desarrolla en la siguiente etapa.

La metodología Delphi garantiza que las variables seleccionadas cuentan con respaldo experto institucional, lo que otorga validez de contenido al modelo y asegura la trazabilidad entre el juicio experto y las decisiones de diseño del sistema de evaluación de riesgo.
