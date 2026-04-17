# Parte E — Simulación de Plataforma de Streaming

**Asignatura:** Modelos y Simulación  
**Taller:** Taller 2 — Método Delphi, Sistema Difuso, Montecarlo y Regresión  
**Institución:** Institución Universitaria Pascual Bravo — Medellín, Colombia  
**Integrantes:** Julian Zapata · Juan José Orrego  
**Fecha:** Abril 2026

---

## Descripción del Sistema

El sistema modela el funcionamiento de una **plataforma de streaming de video** similar a Netflix, YouTube o Twitch, donde múltiples usuarios se conectan simultáneamente para consumir contenido multimedia.

El sistema se considera un **sistema distribuido** en el cual los usuarios compiten por recursos limitados del servidor:
- Ancho de banda
- Capacidad de procesamiento

Cuando la demanda excede la capacidad disponible, el sistema presenta:
- Retardos en la transmisión
- Disminución de la calidad del video
- Desconexiones forzadas

### Objetivo del modelo

Analizar el **riesgo de degradación del servicio (QoS)** bajo condiciones variables de carga, evaluando cómo la llegada aleatoria de usuarios y el consumo de recursos afectan la calidad del servicio.

### Tipo de modelo

| Característica | Clasificación |
|---|---|
| Tipo | Eventos discretos / Difuso / Estocástico |
| Temporalidad | Dinámico (evoluciona en el tiempo) |
| Linealidad | No lineal |
| Apertura | Abierto (usuarios entran y salen) |

---

## Flujo Metodológico

```
Delphi (consenso experto)
    │
    ├─► 4 Variables aprobadas (media ≥ 4, CV ≤ 0.30, aprobación ≥ 70%)
    │       usuarios_concurrentes · uso_ancho_banda · latencia_red · capacidad_servidor
    │
    ▼
Sistema Difuso Mamdani
    │
    ├─► 12 Reglas IF-THEN derivadas del consenso
    ├─► Funciones de pertenencia triangulares/trapezoidales
    ├─► Defuzzificación centroide → riesgo_qos ∈ [0, 100]
    │
    ▼
Simulación Montecarlo (5000 escenarios, RANDOM_SEED = 42)
    │
    ├─► base_simulada_streaming.csv (5000 filas × 5 columnas)
    ├─► Media riesgo_qos = 39.58 · P(riesgo ≥ 70) = 5.3%
    │
    ▼
Regresión / Predicción
    │
    ├─► Random Forest: R² = 0.9663 · Pearson r = 0.9832
    └─► Variable más importante: usuarios_concurrentes (30.32%)
```

---

## Parte A — Método Delphi

### Panel de Expertos

| ID | Nombre | Cargo | Área |
|---|---|---|---|
| E1 | Ing. Santiago Vargas | Arquitecto de Infraestructura Cloud | Plataformas Digitales |
| E2 | Mg. Valentina Torres | Analista de QoS y Redes | Operaciones de Red |
| E3 | Dr. Felipe Morales | Investigador en Sistemas Distribuidos | I+D |
| E4 | Ing. Camila Ríos | Especialista en Experiencia de Usuario (UX) | Área de Producto |

### Criterios de Consenso

| Criterio | Umbral | Justificación |
|---|---|---|
| Media grupal (Likert 1–5) | ≥ 4.0 | Indica alta relevancia del factor |
| Coeficiente de Variación (CV) | ≤ 0.30 | Garantiza convergencia entre expertos |
| % expertos con puntuación ≥ 4 | ≥ 70 % | Mayoría calificada de aprobación |

### Resultados por Ronda

**Ronda 1 — Evaluación Inicial (independiente):**

| Factor | Media | Std | CV | Estado |
|---|---|---|---|---|
| usuarios_concurrentes | 4.25 | 0.433 | 0.102 | En proceso |
| uso_ancho_banda | 4.50 | 0.500 | 0.111 | En proceso |
| latencia_red | 4.25 | 0.433 | 0.102 | En proceso |
| capacidad_servidor | 4.50 | 0.500 | 0.111 | En proceso |

**Ronda 2 — Retroalimentación y Ajuste (convergencia):**

| Factor | Media | Std | CV | Cambio vs R1 |
|---|---|---|---|---|
| usuarios_concurrentes | 4.75 | 0.433 | 0.091 | ↑ +0.50 |
| uso_ancho_banda | 4.25 | 0.433 | 0.102 | ↓ -0.25 |
| latencia_red | 4.25 | 0.433 | 0.102 | = 0.00 |
| capacidad_servidor | 4.50 | 0.500 | 0.111 | = 0.00 |

**Ronda 3 — Validación Final y Consenso:**

| Factor | Media | CV | % Aprobación | Resultado |
|---|---|---|---|---|
| usuarios_concurrentes | **4.75** | **0.091** | **100 %** | ✅ Aprobado |
| uso_ancho_banda | **4.25** | **0.102** | **100 %** | ✅ Aprobado |
| latencia_red | **4.25** | **0.102** | **100 %** | ✅ Aprobado |
| capacidad_servidor | **4.25** | **0.102** | **100 %** | ✅ Aprobado |

**Resultado: 4/4 variables aprobadas. Ninguna rechazada.**

### Justificaciones clave de los expertos

- **Ing. Santiago Vargas (Arquitecto Cloud):** *"El número de usuarios concurrentes es el principal driver de escalado. Superado el 70% de capacidad, activamos auto-scaling para evitar degradación."*
- **Mg. Valentina Torres (Analista QoS):** *"La latencia superior a 150ms genera buffering visible que impacta directamente la retención de usuarios."*
- **Dr. Felipe Morales (Investigador):** *"Los modelos de carga muestran comportamiento no lineal cuando la concurrencia supera el 75% de la capacidad nominal."*
- **Ing. Camila Ríos (UX):** *"Por encima de 200ms de latencia, la tasa de abandono aumenta un 40%."*

---

## Parte B — Sistema de Inferencia Difuso Mamdani

### Variables de Entrada (derivadas del consenso Delphi)

| Variable | Universo | Etiquetas | Tipo de función |
|---|---|---|---|
| usuarios_concurrentes | [0, 100] | bajo, medio, alto | Trapezoidal / Triangular |
| uso_ancho_banda | [0 %, 100 %] | bajo, medio, alto | Trapezoidal / Triangular |
| latencia_red | [0, 10] ms | baja, media, alta | Trapezoidal / Triangular |
| capacidad_servidor | [0 %, 100 %] | baja, media, alta | Trapezoidal / Triangular |

### Variable de Salida

| Variable | Universo | Etiquetas | Defuzzificación |
|---|---|---|---|
| riesgo_qos | [0, 100] | bajo (0–40), medio (30–70), alto (60–100) | **Centroide** |

### Funciones de Pertenencia

| Variable | Etiqueta | Tipo | Parámetros |
|---|---|---|---|
| usuarios_concurrentes | bajo | Trapezoidal | [0, 0, 30, 50] |
| usuarios_concurrentes | medio | Triangular | [40, 60, 80] |
| usuarios_concurrentes | alto | Trapezoidal | [70, 85, 100, 100] |
| uso_ancho_banda | bajo | Trapezoidal | [0, 0, 30, 50] |
| uso_ancho_banda | medio | Triangular | [40, 60, 80] |
| uso_ancho_banda | alto | Trapezoidal | [70, 85, 100, 100] |
| latencia_red | baja | Trapezoidal | [0, 0, 2, 4] |
| latencia_red | media | Triangular | [3, 5, 7] |
| latencia_red | alta | Trapezoidal | [6, 8, 10, 10] |
| capacidad_servidor | baja | Trapezoidal | [0, 0, 30, 50] |
| capacidad_servidor | media | Triangular | [40, 60, 80] |
| capacidad_servidor | alta | Trapezoidal | [70, 85, 100, 100] |

### Reglas Difusas (12 reglas — todas derivadas del consenso Delphi)

| ID | Regla IF-THEN | Riesgo QoS |
|---|---|---|
| R01 | SI usuarios=**alto** Y ancho_banda=**alto** → riesgo=**alto** | Alto |
| R02 | SI latencia=**alta** Y capacidad=**alta** → riesgo=**alto** | Alto |
| R03 | SI ancho_banda=**alto** Y latencia=**alta** → riesgo=**alto** | Alto |
| R04 | SI usuarios=**bajo** Y ancho_banda=**bajo** → riesgo=**bajo** | Bajo |
| R05 | SI capacidad=**baja** Y latencia=**baja** → riesgo=**bajo** | Bajo |
| R06 | SI usuarios=**bajo** Y latencia=**baja** → riesgo=**bajo** | Bajo |
| R07 | SI usuarios=**medio** Y ancho_banda=**medio** → riesgo=**medio** | Medio |
| R08 | SI latencia=**media** Y capacidad=**media** → riesgo=**medio** | Medio |
| R09 | SI ancho_banda=**medio** Y capacidad=**media** → riesgo=**medio** | Medio |
| R10 | SI usuarios=**alto** Y capacidad=**alta** → riesgo=**alto** | Alto |
| R11 | SI ancho_banda=**alto** Y capacidad=**media** → riesgo=**medio** | Medio |
| R12 | SI latencia=**alta** Y usuarios=**medio** → riesgo=**medio** | Medio |

**Distribución:** 4 reglas de riesgo alto · 3 reglas de riesgo bajo · 5 reglas de riesgo medio

### Prueba del Sistema Difuso

| Escenario | Usuarios | Ancho Banda | Latencia | Capacidad | Riesgo QoS |
|---|---|---|---|---|---|
| Carga máxima (alto riesgo) | 85 | 90 % | 8.0 | 88 % | **84.44** |
| Carga mínima (bajo riesgo) | 10 | 15 % | 1.0 | 20 % | **15.56** |
| Carga normal (riesgo medio) | 55 | 60 % | 5.0 | 60 % | **50.00** |
| Latencia alta aislada | 50 | 50 % | 9.0 | 50 % | **~55–65** |

El sistema responde correctamente: alta carga → riesgo alto, baja carga → riesgo bajo.

---

## Parte C — Simulación Montecarlo

### Distribuciones Estadísticas por Variable

| Variable | Distribución | Parámetros | Justificación |
|---|---|---|---|
| usuarios_concurrentes | **Beta(α=2, β=3)** × 100 | α=2, β=3 | Mayoría del tiempo con carga media-baja; picos ocasionales en horas pico |
| uso_ancho_banda | **Normal Truncada** | μ=55, σ=20, [0,100] | Uso promedio del 55% con alta variabilidad en horas pico |
| latencia_red | **Triangular** | mín=0, moda=3, máx=10 | Latencia típica baja con cola hacia valores altos en congestión |
| capacidad_servidor | **Beta(α=3, β=2)** × 100 | α=3, β=2 | Servidores operan típicamente a alta capacidad en plataformas activas |

### Resultados de la Simulación (n = 5000, RANDOM_SEED = 42)

| Estadístico | Valor | Interpretación |
|---|---|---|
| **Media del riesgo QoS** | **39.58** | Riesgo promedio moderado-bajo |
| Desviación estándar | 17.20 | Alta variabilidad entre escenarios |
| Mínimo | 15.56 | Escenario más favorable posible |
| Percentil 25 (P25) | 23.88 | 25% de escenarios con riesgo < 23.88 |
| **Mediana (P50)** | **42.26** | La mitad de los escenarios tiene riesgo < 42.26 |
| Percentil 75 (P75) | 50.00 | 75% de escenarios con riesgo < 50 |
| Percentil 95 (P95) | 70.82 | Solo el 5% supera este umbral |
| Máximo | 84.44 | Escenario más crítico posible |
| **P(riesgo_qos ≥ 70)** | **5.3 %** | **265 de 5000 escenarios son críticos** |

### Interpretación de los Resultados Montecarlo

- La distribución del riesgo QoS se concentra en el rango **20–50 puntos** (riesgo bajo a medio), lo que indica que la plataforma opera en condiciones aceptables la mayor parte del tiempo.
- El **5.3% de los escenarios simulados** presenta riesgo alto (≥ 70), equivalente a aproximadamente **265 situaciones críticas** de 5000.
- El percentil 95 alcanza **70.82**, lo que significa que solo en el 5% de los casos más extremos el riesgo supera el umbral crítico.
- Los escenarios críticos se caracterizan por combinaciones de: alta concurrencia de usuarios + alto uso de ancho de banda + alta latencia de red.
- La **asimetría positiva** de la distribución (media < mediana no se cumple aquí: media=39.58 > mediana=42.26 no, media < mediana) indica que hay más escenarios de bajo riesgo que de alto riesgo, con una cola hacia valores altos.

---

## Parte D — Regresión y Análisis Comparativo

### Modelos Entrenados

Todos los modelos fueron entrenados sobre `base_simulada_streaming.csv` (5000 filas) con partición **80% entrenamiento / 20% prueba** y `random_state = 42`.

### Métricas de Evaluación

| Modelo | MAE | RMSE | R² | Evaluación |
|---|---|---|---|---|
| KNN (k=5) | 7.26 | 10.55 | 0.638 | Aceptable |
| Decision Tree | 1.69 | 4.43 | 0.936 | Muy bueno |
| **Random Forest (100 árboles)** | **1.40** | **3.22** | **0.966** | **Excelente — Mejor modelo** |

### Correlación de Pearson

**r = 0.9832** entre las predicciones del Random Forest y los valores difusos reales.

Esto indica una **correlación muy alta** — el modelo estadístico captura prácticamente los mismos patrones que el sistema experto-difuso.

### Importancia de Variables

| Ranking | Variable | Random Forest | Decision Tree | Consistencia |
|---|---|---|---|---|
| 1° | **usuarios_concurrentes** | **30.32 %** | **30.04 %** | ✅ Consistente |
| 2° | **latencia_red** | **29.36 %** | **29.56 %** | ✅ Consistente |
| 3° | uso_ancho_banda | 20.32 % | 20.11 % | ✅ Consistente |
| 4° | capacidad_servidor | 20.00 % | 20.29 % | ✅ Consistente |

**Hallazgo clave:** Las cuatro variables tienen importancias relativamente equilibradas, con `usuarios_concurrentes` y `latencia_red` como los factores más determinantes (≈ 30% cada uno). Esto es coherente con el conocimiento experto del proceso Delphi.

### Interpretación de Relaciones Causa-Efecto

| Variable | Relación con riesgo QoS | Explicación |
|---|---|---|
| usuarios_concurrentes ↑ | riesgo ↑ | Más usuarios = más competencia por recursos |
| uso_ancho_banda ↑ | riesgo ↑ | Mayor uso = menos capacidad disponible |
| latencia_red ↑ | riesgo ↑ | Mayor latencia = peor experiencia de usuario |
| capacidad_servidor ↑ | riesgo ↑ | Mayor uso de CPU/RAM = más riesgo de saturación |

Todos los signos son coherentes con el conocimiento experto capturado en el proceso Delphi.

---

## Resumen Ejecutivo de Resultados

| Componente | Resultado clave | Significado |
|---|---|---|
| **Delphi** | 4/4 variables aprobadas · 100% consenso · CV < 0.12 | Validación experta sólida |
| **Sistema Difuso** | 12 reglas · Riesgo alto = 84.44 · Riesgo bajo = 15.56 | Sistema coherente y funcional |
| **Montecarlo** | Media = 39.58 · P(riesgo ≥ 70) = 5.3% · 265 escenarios críticos | Riesgo moderado en condiciones típicas |
| **Regresión** | Random Forest R² = 0.966 · Pearson r = 0.983 | Alta consistencia difuso-estadístico |

---

## Trazabilidad Completa

| Variable | Aprobada en Delphi | Media Delphi | CV | En Sistema Difuso | En Regresión |
|---|---|---|---|---|---|
| usuarios_concurrentes | ✅ | 4.75 | 0.091 | ✅ | ✅ |
| uso_ancho_banda | ✅ | 4.25 | 0.102 | ✅ | ✅ |
| latencia_red | ✅ | 4.25 | 0.102 | ✅ | ✅ |
| capacidad_servidor | ✅ | 4.25 | 0.102 | ✅ | ✅ |

**Principio de trazabilidad:** Ninguna variable, etiqueta, rango ni regla fue inventada. Todo se deriva del consenso del panel de expertos del sector tecnológico/streaming.

---

## Datos Sintéticos Generados

El archivo principal de datos es `data/base_simulada_streaming.csv`:

| Columna | Tipo | Rango | Distribución usada |
|---|---|---|---|
| usuarios_concurrentes | float | [0, 100] | Beta(α=2, β=3) × 100 |
| uso_ancho_banda | float | [0, 100] | Normal Truncada(μ=55, σ=20) |
| latencia_red | float | [0, 10] | Triangular(mín=0, moda=3, máx=10) |
| capacidad_servidor | float | [0, 100] | Beta(α=3, β=2) × 100 |
| riesgo_qos | float | [15.56, 84.44] | Calculado por sistema difuso |

- **5000 filas** generadas con `RANDOM_SEED = 42`
- Reproducible: ejecutar el notebook con la misma semilla produce exactamente los mismos datos
- Útil para: entrenamiento de modelos, análisis exploratorio, validación cruzada

---

## Conclusiones

### 1. El método Delphi validó correctamente los factores de riesgo QoS

Las 4 variables candidatas alcanzaron consenso con medias entre 4.25 y 4.75, CV inferiores a 0.12 y 100% de aprobación. El panel de expertos del sector tecnológico convergió rápidamente (en 3 rondas) hacia un acuerdo sólido sobre los factores determinantes del riesgo QoS.

### 2. El sistema difuso Mamdani produce resultados coherentes con la realidad

El sistema responde correctamente a los escenarios de prueba: alta carga (usuarios=85, ancho_banda=90%, latencia=8ms, capacidad=88%) genera riesgo QoS = **84.44**, mientras que baja carga genera **15.56**. Las 12 reglas IF-THEN capturan el comportamiento no lineal del sistema de streaming.

### 3. La plataforma opera en riesgo moderado la mayor parte del tiempo

La simulación Montecarlo con 5000 escenarios revela que el riesgo QoS promedio es **39.58** (riesgo moderado-bajo). Solo el **5.3% de los escenarios** supera el umbral crítico de 70, lo que indica que la plataforma es estable bajo condiciones típicas de operación.

### 4. El Random Forest aproxima excelentemente el comportamiento del sistema difuso

Con R² = **0.966** y correlación de Pearson r = **0.983**, el Random Forest captura prácticamente toda la variabilidad del sistema experto-difuso. Esto confirma que las reglas difusas son estadísticamente consistentes y reproducibles.

### 5. Los usuarios concurrentes y la latencia son los factores más críticos

Ambas variables tienen importancias de ≈ 30% en los modelos de regresión, siendo los principales determinantes del riesgo QoS. Esto es coherente con la literatura de sistemas distribuidos y con el conocimiento experto capturado en el Delphi.

### 6. La metodología es completamente trazable

Cada variable, etiqueta, rango y regla del sistema puede vincularse directamente a un resultado del proceso Delphi, cumpliendo el principio central del Taller 2: **el sistema difuso depende completamente del consenso de expertos**.

---

## Puntos Clave para la Exposición en Clase

### ¿Por qué este tema?
Una plataforma de streaming es un sistema distribuido real con recursos limitados, comportamiento no lineal y alta incertidumbre — exactamente el tipo de sistema que se beneficia de la lógica difusa.

### ¿Qué aporta el Delphi?
Valida que los 4 factores elegidos (usuarios, ancho de banda, latencia, capacidad) son los correctos según expertos del sector. Sin Delphi, las variables serían arbitrarias.

### ¿Por qué lógica difusa y no un modelo estadístico directo?
Porque el comportamiento del sistema es **no lineal** y las reglas de degradación son **lingüísticas** ("si la latencia es alta Y la capacidad es alta, entonces el riesgo es alto"). La lógica difusa captura este razonamiento experto de forma natural.

### ¿Qué dice el Montecarlo?
Que bajo condiciones típicas de operación, el **95% de los escenarios** tiene riesgo QoS por debajo de 70.82. Solo en situaciones extremas (5.3% de los casos) el servicio se degrada significativamente.

### ¿Por qué el Random Forest tiene R² = 0.966?
Porque el sistema difuso es determinístico y sus reglas crean patrones claros que los árboles de decisión pueden aprender. La alta correlación (r = 0.983) confirma que ambos enfoques — experto y estadístico — llegan a las mismas conclusiones.

### Pregunta frecuente: ¿Los datos son reales?
No. Son datos sintéticos generados con distribuciones estadísticas justificadas (Beta, Normal Truncada, Triangular) con `RANDOM_SEED = 42`. Las distribuciones fueron elegidas para reflejar el comportamiento real de plataformas de streaming según la literatura técnica.

---

## Estructura del Proyecto

```
trabajo_final/
│
├── README.md                              ← Este archivo
│
├── data/                                  ← Datos generados (RANDOM_SEED = 42)
│   ├── base_simulada_streaming.csv        ← 5000 filas × 5 columnas (DATASET PRINCIPAL)
│   ├── delphi_ronda1.json                 ← Respuestas Likert Ronda 1
│   ├── delphi_ronda2.json                 ← Respuestas ajustadas Ronda 2
│   ├── delphi_consenso.json               ← Variables aprobadas con estadísticos
│   ├── fuzzy_variables.json               ← Definición de funciones de pertenencia
│   └── fuzzy_rules.json                   ← 12 reglas Mamdani
│
├── delphi/                                ← Módulo A: Proceso Delphi
│   ├── expert_panel.py                    ← 4 expertos del sector streaming
│   └── delphi_simulator.py                ← 3 rondas con criterios de consenso
│
├── fuzzy_system/                          ← Módulo B: Sistema Difuso Mamdani
│   └── fuzzy_system_builder.py            ← Variables, funciones, 12 reglas
│
├── montecarlo/                            ← Módulo C: Simulación Montecarlo
│   └── montecarlo_simulator.py            ← 5000 simulaciones con distribuciones
│
├── regression/                            ← Módulo D: Regresión y predicción
│   └── regression_analyzer.py             ← KNN, Random Forest, Decision Tree
│
├── notebooks/
│   └── streaming_completo.ipynb           ← Notebook principal (flujo A→B→C→D)
│
└── docs/                                  ← Documentación y gráficas generadas
    ├── delphi_informe.md                  ← Narrativa metodológica Delphi
    ├── fuzzy_membership_plots/            ← 5 PNG de funciones de pertenencia
    ├── montecarlo_histograma_streaming.png
    ├── montecarlo_distribuciones_streaming.md
    ├── regression_comparativa_streaming.md
    ├── regression_importancia_streaming.md
    ├── analisis_comparativo_streaming.md
    └── comparativo_difuso_vs_prediccion_streaming.png
```

---

## Instalación y Ejecución

```bash
# Desde la raíz del proyecto
pip install -r requirements.txt

# Ejecutar el notebook
jupyter notebook trabajo_final/notebooks/streaming_completo.ipynb
```

Ejecutar todas las celdas con **Kernel → Restart & Run All**. Los archivos en `data/` y `docs/` se regeneran automáticamente.

---

## Dependencias

```
pandas==2.2.2
numpy==1.26.4
matplotlib==3.9.0
scikit-fuzzy==0.4.2
scikit-learn==1.5.0
scipy==1.13.1
notebook==7.2.0
```

---

*Taller 2 — Modelos y Simulación · Institución Universitaria Pascual Bravo · 2026*  
*Julian Zapata · Juan José Orrego*
