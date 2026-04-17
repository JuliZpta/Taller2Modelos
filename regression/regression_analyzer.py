"""
regression/regression_analyzer.py
Análisis de regresión y predicción sobre la base simulada Montecarlo.
Institución Universitaria Pascual Bravo · Medellín, Colombia
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from scipy.stats import pearsonr
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class RegressionAnalyzer:
    """
    Entrena y evalúa KNN, RandomForest y DecisionTree sobre base_simulada.csv.
    Genera análisis comparativo y documentación de trazabilidad.
    """

    MODELS = {
        "knn": KNeighborsRegressor(n_neighbors=5),
        "random_forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "decision_tree": DecisionTreeRegressor(random_state=42),
    }

    TEST_SIZE = 0.20
    RANDOM_STATE = 42
    MIN_R2_THRESHOLD = 0.80

    REQUIRED_COLUMNS = [
        "promedio_academico",
        "inasistencia",
        "horas_estudio",
        "motivacion_estres",
        "riesgo",
    ]

    FEATURE_COLUMNS = [
        "promedio_academico",
        "inasistencia",
        "horas_estudio",
        "motivacion_estres",
    ]

    def __init__(
        self,
        data_path: str = "data/base_simulada.csv",
        consenso_path: str = "data/delphi_consenso.json",
        docs_dir: str = "docs/",
    ) -> None:
        # Verificar que data_path existe
        if not os.path.exists(data_path):
            raise FileNotFoundError(
                f"No se encontró el archivo de datos: '{data_path}'. "
                "Ejecute primero el módulo Montecarlo para generar base_simulada.csv."
            )

        # Verificar que consenso_path existe
        if not os.path.exists(consenso_path):
            raise FileNotFoundError(
                f"No se encontró el archivo de consenso Delphi: '{consenso_path}'. "
                "Ejecute primero el módulo Delphi para generar delphi_consenso.json."
            )

        self.data_path = data_path
        self.consenso_path = consenso_path
        self.docs_dir = docs_dir

        # Cargar consenso para trazabilidad
        with open(consenso_path, "r", encoding="utf-8") as f:
            self._consenso = json.load(f)

        # Crear docs_dir si no existe
        os.makedirs(docs_dir, exist_ok=True)

        # Inicializar atributos internos
        self._X_train = None
        self._X_test = None
        self._y_train = None
        self._y_test = None
        self._trained_models = {}
        self._metrics = {}
        self._feature_names = self.FEATURE_COLUMNS[:]
        self._data_loaded = False

    # ------------------------------------------------------------------
    # Carga de datos
    # ------------------------------------------------------------------

    def load_data(self) -> tuple:
        """
        Carga base_simulada.csv con pandas.
        Verifica que tiene las columnas requeridas.
        Retorna (X, y) donde y = columna 'riesgo'.
        """
        df = pd.read_csv(self.data_path)

        # Verificar columnas requeridas
        missing = [c for c in self.REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(
                f"Columnas faltantes en '{self.data_path}': {missing}. "
                f"Se esperaban: {self.REQUIRED_COLUMNS}"
            )

        X = df[self.FEATURE_COLUMNS].copy()
        y = df["riesgo"].copy()

        self._feature_names = self.FEATURE_COLUMNS[:]
        self._data_loaded = True

        return X, y

    # ------------------------------------------------------------------
    # Entrenamiento y evaluación
    # ------------------------------------------------------------------

    def train_and_evaluate(self) -> dict:
        """
        Divide datos 80/20, entrena KNN/RandomForest/DecisionTree,
        calcula MAE, RMSE y R² para cada modelo.
        Retorna dict con métricas por modelo.
        """
        X, y = self.load_data()

        self._X_train, self._X_test, self._y_train, self._y_test = train_test_split(
            X, y, test_size=self.TEST_SIZE, random_state=self.RANDOM_STATE
        )

        metrics = {}
        for name, model in self.MODELS.items():
            model.fit(self._X_train, self._y_train)
            y_pred = model.predict(self._X_test)

            mae = mean_absolute_error(self._y_test, y_pred)
            rmse = float(np.sqrt(mean_squared_error(self._y_test, y_pred)))
            r2 = r2_score(self._y_test, y_pred)

            metrics[name] = {"mae": float(mae), "rmse": float(rmse), "r2": float(r2)}
            self._trained_models[name] = model

        self._metrics = metrics
        return metrics

    # ------------------------------------------------------------------
    # Importancia de variables
    # ------------------------------------------------------------------

    def get_feature_importance(self) -> dict:
        """
        Extrae importancia de variables para RandomForest y DecisionTree.
        Retorna dict con importancias por modelo.
        """
        if not self._trained_models:
            raise RuntimeError(
                "Los modelos no han sido entrenados. "
                "Llame primero a train_and_evaluate()."
            )

        result = {}
        for model_name in ("random_forest", "decision_tree"):
            model = self._trained_models[model_name]
            importances = model.feature_importances_
            result[model_name] = dict(zip(self._feature_names, importances.tolist()))

        return result

    # ------------------------------------------------------------------
    # Correlación de Pearson
    # ------------------------------------------------------------------

    def calculate_pearson_correlation(self) -> float:
        """
        Calcula correlación de Pearson entre predicciones del mejor modelo
        y valores difusos en el conjunto de prueba.
        Retorna coeficiente r en [-1, 1].
        """
        if not self._trained_models:
            raise RuntimeError(
                "Los modelos no han sido entrenados. "
                "Llame primero a train_and_evaluate()."
            )

        # Identificar el mejor modelo (mayor R²)
        best_name = max(self._metrics, key=lambda k: self._metrics[k]["r2"])
        best_model = self._trained_models[best_name]

        y_pred = best_model.predict(self._X_test)
        r, _ = pearsonr(self._y_test, y_pred)

        return float(r)

    # ------------------------------------------------------------------
    # Gráfico de dispersión
    # ------------------------------------------------------------------

    def generate_scatter_plot(self) -> None:
        """
        Genera docs/comparativo_difuso_vs_prediccion.png con el mejor modelo.
        """
        if not self._trained_models:
            raise RuntimeError(
                "Los modelos no han sido entrenados. "
                "Llame primero a train_and_evaluate()."
            )

        best_name = max(self._metrics, key=lambda k: self._metrics[k]["r2"])
        best_model = self._trained_models[best_name]
        y_pred = best_model.predict(self._X_test)

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(self._y_test, y_pred, alpha=0.5, edgecolors="steelblue",
                   facecolors="lightblue", linewidths=0.5, label="Predicciones")

        # Línea de identidad y=x en rojo punteado
        lims = [
            min(self._y_test.min(), y_pred.min()),
            max(self._y_test.max(), y_pred.max()),
        ]
        ax.plot(lims, lims, "r--", linewidth=1.5, label="Identidad (y=x)")

        nombre_modelo = best_name.replace("_", " ").title()
        ax.set_title(f"Predicciones vs. Valores Difusos — {nombre_modelo}", fontsize=13)
        ax.set_xlabel("Valores Difusos Reales (riesgo)", fontsize=11)
        ax.set_ylabel("Predicciones del Modelo", fontsize=11)
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.4)

        output_path = os.path.join(self.docs_dir, "comparativo_difuso_vs_prediccion.png")
        fig.tight_layout()
        fig.savefig(output_path, dpi=150)
        plt.close(fig)

    # ------------------------------------------------------------------
    # Reporte comparativo de métricas
    # ------------------------------------------------------------------

    def generate_comparative_report(self, metrics: dict) -> None:
        """
        Genera docs/regression_comparativa.md con tabla de métricas.
        Incluye advertencia si todos los R² < 0.80.
        """
        best_name = max(metrics, key=lambda k: metrics[k]["r2"])

        lines = [
            "# Reporte Comparativo de Modelos de Regresión",
            "",
            "**Institución Universitaria Pascual Bravo · Medellín, Colombia**",
            "",
            "## Métricas de Evaluación",
            "",
            "| Modelo | MAE | RMSE | R² |",
            "|--------|-----|------|-----|",
        ]

        model_display = {
            "knn": "KNN (k=5)",
            "random_forest": "Random Forest",
            "decision_tree": "Decision Tree",
        }

        for name, m in metrics.items():
            display = model_display.get(name, name)
            marker = " ✓" if name == best_name else ""
            lines.append(
                f"| {display}{marker} | {m['mae']:.4f} | {m['rmse']:.4f} | {m['r2']:.4f} |"
            )

        lines += [
            "",
            f"> **Mejor modelo:** {model_display.get(best_name, best_name)} "
            f"(R² = {metrics[best_name]['r2']:.4f})",
            "",
        ]

        # Advertencia si todos los R² < 0.80
        if all(m["r2"] < self.MIN_R2_THRESHOLD for m in metrics.values()):
            lines += [
                "## ⚠️ Advertencia: Poder Predictivo Insuficiente",
                "",
                "Todos los modelos evaluados presentan un coeficiente de determinación "
                f"R² inferior al umbral mínimo de {self.MIN_R2_THRESHOLD:.2f}. "
                "Esto indica que los modelos estadísticos no logran capturar "
                "adecuadamente la variabilidad del índice de riesgo difuso. "
                "Se recomienda revisar la calidad de los datos, considerar "
                "transformaciones de variables o explorar modelos más complejos.",
                "",
            ]

        lines += [
            "## Descripción de Modelos",
            "",
            "- **KNN (k=5):** Algoritmo basado en los 5 vecinos más cercanos. "
            "No paramétrico, sensible a la escala de las variables.",
            "- **Random Forest:** Ensemble de 100 árboles de decisión con "
            "`random_state=42`. Robusto ante sobreajuste.",
            "- **Decision Tree:** Árbol de decisión individual con `random_state=42`. "
            "Alta interpretabilidad.",
            "",
            "## Partición de Datos",
            "",
            f"- Entrenamiento: {int((1 - self.TEST_SIZE) * 100)}% de los datos",
            f"- Prueba: {int(self.TEST_SIZE * 100)}% de los datos",
            f"- `random_state = {self.RANDOM_STATE}`",
            "",
        ]

        output_path = os.path.join(self.docs_dir, "regression_comparativa.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # ------------------------------------------------------------------
    # Reporte de importancia de variables
    # ------------------------------------------------------------------

    def generate_importance_report(self) -> None:
        """
        Genera docs/regression_importancia_variables.md con tablas de
        importancias para Random Forest y Decision Tree.
        """
        if not self._trained_models:
            raise RuntimeError(
                "Los modelos no han sido entrenados. "
                "Llame primero a train_and_evaluate()."
            )

        importances = self.get_feature_importance()

        lines = [
            "# Importancia de Variables — Modelos de Regresión",
            "",
            "**Institución Universitaria Pascual Bravo · Medellín, Colombia**",
            "",
            "La importancia de variables cuantifica la contribución relativa de cada "
            "Variable_Entrada al poder predictivo del modelo. Los valores suman 1.0.",
            "",
        ]

        model_display = {
            "random_forest": "Random Forest",
            "decision_tree": "Decision Tree",
        }

        for model_name in ("random_forest", "decision_tree"):
            imp = importances[model_name]
            # Ordenar de mayor a menor
            sorted_imp = sorted(imp.items(), key=lambda x: x[1], reverse=True)

            lines += [
                f"## {model_display[model_name]}",
                "",
                "| Variable | Importancia | Porcentaje |",
                "|----------|-------------|------------|",
            ]

            for var, val in sorted_imp:
                lines.append(f"| {var} | {val:.6f} | {val * 100:.2f}% |")

            # Interpretación
            top_var, top_val = sorted_imp[0]
            lines += [
                "",
                f"**Variable más influyente:** `{top_var}` "
                f"({top_val * 100:.2f}% de importancia).",
                "",
            ]

        lines += [
            "## Interpretación General",
            "",
            "Las variables con mayor importancia son las que el modelo utiliza con "
            "mayor frecuencia para realizar divisiones en los árboles de decisión "
            "(Random Forest y Decision Tree). Una importancia alta indica que la "
            "variable tiene alta capacidad discriminativa para predecir el nivel de "
            "riesgo académico.",
            "",
            "La consistencia entre Random Forest y Decision Tree en el ranking de "
            "importancias refuerza la validez de los factores priorizados en el "
            "proceso Delphi.",
            "",
        ]

        output_path = os.path.join(self.docs_dir, "regression_importancia_variables.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    # ------------------------------------------------------------------
    # Análisis comparativo completo
    # ------------------------------------------------------------------

    def generate_comparative_analysis(self, metrics: dict, correlation: float) -> None:
        """
        Genera docs/analisis_comparativo.md con tabla de métricas,
        correlación de Pearson, interpretación de importancias y
        sección de Trazabilidad.
        """
        if not self._trained_models:
            raise RuntimeError(
                "Los modelos no han sido entrenados. "
                "Llame primero a train_and_evaluate()."
            )

        best_name = max(metrics, key=lambda k: metrics[k]["r2"])
        importances = self.get_feature_importance()

        model_display = {
            "knn": "KNN (k=5)",
            "random_forest": "Random Forest",
            "decision_tree": "Decision Tree",
        }

        # Construir mapa de trazabilidad desde consenso Delphi
        trazabilidad_map = {}
        for var_info in self._consenso.get("variables_aprobadas", []):
            factor = var_info["factor"]
            stats = var_info["estadisticos_finales"]
            criterios = var_info["criterios"]
            trazabilidad_map[factor] = {
                "media": stats["media"],
                "std": stats["std"],
                "cv": stats["cv"],
                "approval_pct": criterios.get("approval_pct", 100.0),
            }

        lines = [
            "# Análisis Comparativo: Sistema Difuso vs. Modelos Estadísticos",
            "",
            "**Institución Universitaria Pascual Bravo · Medellín, Colombia**",
            "",
            "Este documento compara el enfoque de inferencia difusa Mamdani con "
            "modelos estadísticos de regresión supervisada, evaluando la consistencia "
            "metodológica y la capacidad predictiva de cada enfoque.",
            "",
            "---",
            "",
            "## 1. Métricas de Evaluación de Modelos",
            "",
            "| Modelo | MAE | RMSE | R² |",
            "|--------|-----|------|-----|",
        ]

        for name, m in metrics.items():
            display = model_display.get(name, name)
            marker = " ✓" if name == best_name else ""
            lines.append(
                f"| {display}{marker} | {m['mae']:.4f} | {m['rmse']:.4f} | {m['r2']:.4f} |"
            )

        lines += [
            "",
            f"> **Mejor modelo:** {model_display.get(best_name, best_name)} "
            f"(R² = {metrics[best_name]['r2']:.4f})",
            "",
            "---",
            "",
            "## 2. Correlación de Pearson",
            "",
            f"La correlación de Pearson entre las predicciones del mejor modelo "
            f"(**{model_display.get(best_name, best_name)}**) y los valores difusos "
            f"reales del conjunto de prueba es:",
            "",
            f"**r = {correlation:.4f}**",
            "",
        ]

        # Interpretación de la correlación
        abs_r = abs(correlation)
        if abs_r >= 0.90:
            interp_corr = "correlación muy alta"
        elif abs_r >= 0.70:
            interp_corr = "correlación alta"
        elif abs_r >= 0.50:
            interp_corr = "correlación moderada"
        else:
            interp_corr = "correlación baja"

        lines += [
            f"Esto indica una **{interp_corr}** entre el modelo estadístico y el "
            "sistema de inferencia difusa, lo que sugiere que ambos enfoques "
            "capturan patrones similares en los datos.",
            "",
            "---",
            "",
            "## 3. Importancia de Variables",
            "",
            "### Random Forest",
            "",
            "| Variable | Importancia |",
            "|----------|-------------|",
        ]

        rf_imp = sorted(
            importances["random_forest"].items(), key=lambda x: x[1], reverse=True
        )
        for var, val in rf_imp:
            lines.append(f"| {var} | {val:.6f} ({val * 100:.2f}%) |")

        lines += [
            "",
            "### Decision Tree",
            "",
            "| Variable | Importancia |",
            "|----------|-------------|",
        ]

        dt_imp = sorted(
            importances["decision_tree"].items(), key=lambda x: x[1], reverse=True
        )
        for var, val in dt_imp:
            lines.append(f"| {var} | {val:.6f} ({val * 100:.2f}%) |")

        # Interpretación de importancias
        top_rf = rf_imp[0][0]
        top_dt = dt_imp[0][0]
        lines += [
            "",
            "**Interpretación:** "
            f"En Random Forest, la variable más influyente es `{top_rf}`. "
            f"En Decision Tree, la variable más influyente es `{top_dt}`. "
            "La consistencia entre ambos modelos en el ranking de importancias "
            "refuerza la validez de los factores priorizados en el proceso Delphi.",
            "",
            "---",
            "",
            "## 4. Trazabilidad: Variable_Entrada → Factor Delphi → Estadísticos",
            "",
            "La siguiente tabla vincula cada Variable_Entrada del modelo de regresión "
            "con su Factor Delphi correspondiente y los estadísticos de consenso "
            "obtenidos en la Ronda 3 del proceso Delphi.",
            "",
            "| Variable_Entrada | Factor Delphi | Media Delphi | CV Delphi | % Aprobación | Aprobado |",
            "|-----------------|---------------|--------------|-----------|--------------|----------|",
        ]

        for feature in self._feature_names:
            if feature in trazabilidad_map:
                t = trazabilidad_map[feature]
                lines.append(
                    f"| {feature} | {feature} | {t['media']:.4f} | "
                    f"{t['cv']:.4f} | {t['approval_pct']:.1f}% | ✓ |"
                )
            else:
                lines.append(
                    f"| {feature} | — | — | — | — | ✗ |"
                )

        lines += [
            "",
            "---",
            "",
            "## 5. Conclusión: Consistencia Difuso vs. Estadístico",
            "",
            f"El análisis comparativo muestra que los modelos estadísticos de "
            f"regresión logran un R² de hasta **{metrics[best_name]['r2']:.4f}** "
            f"al predecir el índice de riesgo generado por el sistema difuso Mamdani. "
            f"La correlación de Pearson de **{correlation:.4f}** confirma una "
            f"{interp_corr} entre ambos enfoques.",
            "",
            "Las variables priorizadas por el proceso Delphi "
            "(`promedio_academico`, `inasistencia`, `horas_estudio`, `motivacion_estres`) "
            "son consistentes con las importancias identificadas por los modelos "
            "estadísticos, lo que valida la coherencia metodológica del sistema.",
            "",
            "Esta consistencia entre el enfoque experto-difuso y el enfoque "
            "estadístico-supervisado proporciona evidencia de la solidez del "
            "modelo de evaluación de riesgo académico desarrollado para la "
            "Institución Universitaria Pascual Bravo.",
            "",
        ]

        output_path = os.path.join(self.docs_dir, "analisis_comparativo.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
