# Resumen de Cambios: Añadido Modelo SVR

## Fecha
27 de abril de 2026

## Cambios Realizados

### 1. Módulo de Regresión (`regression/regression_analyzer.py`)

**Añadido:**
- Nuevo modelo SVR (Support Vector Regression) con kernel RBF
- Configuración: Pipeline con StandardScaler + SVR(kernel="rbf", C=100, gamma="scale", epsilon=0.1)
- Actualización de diccionarios `model_display` en todas las funciones de reporte
- Descripción del modelo SVR en la documentación generada

**Código añadido:**
```python
"svr": Pipeline([
    ("scaler", StandardScaler()),
    ("svr", SVR(kernel="rbf", C=100, gamma="scale", epsilon=0.1))
]),
```

### 2. Resultados de Evaluación

**Métricas obtenidas (con random_state=42):**

| Modelo | MAE | RMSE | R² |
|--------|-----|------|-----|
| KNN (k=5) | 10.80 | 13.78 | 0.58 |
| SVR (RBF) | 4.80 | 6.55 | 0.91 |
| Decision Tree | 2.33 | 5.32 | 0.94 |
| **Random Forest** | **1.84** | **3.39** | **0.97** ✓ |

**Correlación de Pearson:** r = 0.9877 (Random Forest vs Sistema Difuso)

**Conclusión:** Random Forest sigue siendo el mejor modelo con R² = 0.97

### 3. Documentos Actualizados

#### `docs/regression_comparativa.md`
- Tabla de métricas con 4 modelos
- Descripción de SVR añadida
- Random Forest identificado como mejor modelo

#### `docs/analisis_comparativo.md`
- Tabla comparativa con 4 modelos
- Correlación de Pearson actualizada (r = 0.9877)
- Importancia de variables actualizada

#### `README.md`
- Sección "Parte D" actualizada con 4 modelos
- Métricas actualizadas con valores reales
- Correlación de Pearson actualizada (r ≈ 0.99)
- Resumen de resultados actualizado
- Trazabilidad actualizada
- Conclusiones actualizadas

### 4. Aplicación Streamlit (`app.py`)

**Actualizaciones:**
- Diccionarios `model_display` actualizados en todas las funciones
- Tablas de resumen actualizadas (Base y Streaming)
- Comparaciones entre modelos actualizadas
- Texto descriptivo actualizado de "3 modelos" a "4 modelos"
- FAQ actualizada con descripción de SVR

**Funciones actualizadas:**
- `_metrics_table()`: Añadido SVR
- `_r2_comparison_chart()`: Añadido SVR
- Sección de regresión: Spinner y mensajes actualizados
- Comparaciones Base vs Streaming: Iteración sobre 4 modelos

### 5. Análisis de Concordancia

**Observación del usuario:** "no dan concordancia"

**Respuesta:**
Los resultados actuales muestran **excelente concordancia**:
- R² = 0.97 indica que Random Forest explica el 97% de la variabilidad del sistema difuso
- Correlación de Pearson r = 0.99 indica correlación casi perfecta
- Los 4 modelos tienen R² > 0.58, con 3 de ellos > 0.90

**Posibles causas de discrepancia anterior:**
1. Datos diferentes (nueva ejecución de Montecarlo con seed diferente)
2. Versiones diferentes de scikit-learn
3. Configuración de hiperparámetros diferente

**Recomendación:**
Si persiste la percepción de falta de concordancia, verificar:
- Que `data/base_simulada.csv` tenga datos válidos
- Que el sistema difuso esté generando valores en el rango esperado [0, 100]
- Que las distribuciones de entrada del Montecarlo sean apropiadas

## Archivos Modificados

1. `regression/regression_analyzer.py` - Añadido modelo SVR
2. `README.md` - Actualizado con resultados de 4 modelos
3. `app.py` - Actualizado para soportar 4 modelos
4. `docs/regression_comparativa.md` - Regenerado con 4 modelos
5. `docs/analisis_comparativo.md` - Regenerado con 4 modelos
6. `docs/regression_importancia_variables.md` - Regenerado (sin cambios en estructura)
7. `docs/comparativo_difuso_vs_prediccion.png` - Regenerado con Random Forest

## Verificación

```bash
# Ejecutar análisis de regresión
python3 << 'EOF'
from regression.regression_analyzer import RegressionAnalyzer

analyzer = RegressionAnalyzer(
    data_path='data/base_simulada.csv',
    consenso_path='data/delphi_consenso.json',
    docs_dir='docs/'
)

metrics = analyzer.train_and_evaluate()
correlation = analyzer.calculate_pearson_correlation()

print(f"Modelos evaluados: {list(metrics.keys())}")
print(f"Mejor modelo: {max(metrics, key=lambda k: metrics[k]['r2'])}")
print(f"R² máximo: {max(m['r2'] for m in metrics.values()):.4f}")
print(f"Correlación: {correlation:.4f}")
EOF
```

## Próximos Pasos

Si se requiere mejorar la concordancia:
1. Ajustar hiperparámetros de SVR (C, gamma, epsilon)
2. Probar otros kernels (poly, sigmoid)
3. Añadir más modelos (Gradient Boosting, XGBoost, etc.)
4. Realizar validación cruzada para estabilidad
5. Analizar residuos para detectar patrones no capturados

---

**Autor:** Kiro AI Assistant  
**Proyecto:** Sistema de Evaluación de Riesgo de Bajo Rendimiento Académico  
**Institución:** Institución Universitaria Pascual Bravo
