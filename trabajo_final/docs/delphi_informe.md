# Informe del Proceso Delphi — Simulación de Plataforma de Streaming

## Parte E — Taller 2 de Modelos y Simulación

**Fecha de generación:** 2026-04-18 01:34 UTC

---

## 1. Descripción Metodológica del Proceso Delphi

El método Delphi es una técnica de consulta estructurada a expertos que busca alcanzar consenso sobre un tema mediante rondas iterativas de retroalimentación. En este estudio se aplicaron **tres rondas** para validar los factores candidatos que determinan el riesgo de degradación del servicio (QoS) en una plataforma de streaming.

**Ronda 1 — Evaluación inicial:** Cada experto asignó una puntuación Likert (1–5) a cada factor candidato de forma independiente. Se calcularon media, desviación estándar y coeficiente de variación (CV) por factor.

**Ronda 2 — Retroalimentación y ajuste:** Los expertos recibieron la media grupal de la ronda anterior y ajustaron sus puntuaciones. Este proceso favorece la convergencia hacia el consenso.

**Ronda 3 — Validación final:** Última ronda de ajuste con menor variación permitida (±0.3). Se evaluaron los criterios de consenso para determinar qué factores son aprobados como variables del modelo difuso.

**Criterios de consenso aplicados:**

| Criterio | Umbral |
|---|---|
| Media grupal | ≥ 4.0 |
| Coeficiente de variación (CV) | ≤ 0.3 |
| Porcentaje de aprobación (puntuación ≥ 4) | ≥ 70.0 % |

---

## 2. Perfiles del Panel de Expertos

El panel está conformado por cuatro expertos del sector tecnológico/streaming, con perfiles complementarios que cubren las dimensiones de infraestructura, calidad de servicio, investigación y experiencia de usuario.

| ID | Nombre | Cargo | Área |
|---|---|---|---|
| E1 | Ing. Santiago Vargas | Arquitecto de Infraestructura Cloud | Área de Plataformas Digitales |
| E2 | Mg. Valentina Torres | Analista de QoS y Redes | Área de Operaciones de Red |
| E3 | Dr. Felipe Morales | Investigador en Sistemas Distribuidos | Departamento de I+D |
| E4 | Ing. Camila Ríos | Especialista en Experiencia de Usuario (UX) | Área de Producto |

---

## 3. Resultados por Ronda

### 3.1. Ronda 1 — Evaluación Inicial

| Factor | Media | Std | CV |
|---|---|---|---|
| usuarios_concurrentes | 4.2500 | 0.4330 | 0.1019 |
| uso_ancho_banda | 4.5000 | 0.5000 | 0.1111 |
| latencia_red | 4.2500 | 0.4330 | 0.1019 |
| capacidad_servidor | 4.5000 | 0.5000 | 0.1111 |

### 3.2. Ronda 2 — Retroalimentación y Ajuste

| Factor | Media | Std | CV |
|---|---|---|---|
| usuarios_concurrentes | 4.7500 | 0.4330 | 0.0912 |
| uso_ancho_banda | 4.2500 | 0.4330 | 0.1019 |
| latencia_red | 4.2500 | 0.4330 | 0.1019 |
| capacidad_servidor | 4.5000 | 0.5000 | 0.1111 |

### 3.3. Ronda 3 — Validación Final

| Factor | Media | Std | CV | Aprobado |
|---|---|---|---|---|
| usuarios_concurrentes | 4.7500 | 0.4330 | 0.0912 | ✅ Sí |
| uso_ancho_banda | 4.2500 | 0.4330 | 0.1019 | ✅ Sí |
| latencia_red | 4.2500 | 0.4330 | 0.1019 | ✅ Sí |
| capacidad_servidor | 4.2500 | 0.4330 | 0.1019 | ✅ Sí |

---

## 4. Variables Aprobadas

Las siguientes variables alcanzaron consenso y serán utilizadas como variables de entrada del sistema de inferencia difuso Mamdani:

| Factor | Media | CV | % Aprobación | Resultado |
|---|---|---|---|---|
| usuarios_concurrentes | 4.7500 | 0.0912 | 100.0 % | ✅ Aprobado |
| uso_ancho_banda | 4.2500 | 0.1019 | 100.0 % | ✅ Aprobado |
| latencia_red | 4.2500 | 0.1019 | 100.0 % | ✅ Aprobado |
| capacidad_servidor | 4.2500 | 0.1019 | 100.0 % | ✅ Aprobado |

---

## 5. Variables Rechazadas

Todas las variables candidatas alcanzaron consenso. No hay variables rechazadas.

---

## 6. Conclusión Metodológica

El proceso Delphi de tres rondas permitió validar **4 de 4 factores candidatos** para el modelo de riesgo de degradación del servicio (QoS) en la plataforma de streaming.

Los factores aprobados — `usuarios_concurrentes`, `uso_ancho_banda`, `latencia_red`, `capacidad_servidor` — presentaron alta convergencia entre los expertos del panel, con medias superiores a 4.0, coeficientes de variación bajos (≤ 0.30) y porcentajes de aprobación superiores al 70 %. Estos factores constituyen la base del sistema de inferencia difuso Mamdani para la evaluación del riesgo QoS.
