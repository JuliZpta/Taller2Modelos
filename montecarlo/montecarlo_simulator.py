"""
montecarlo/montecarlo_simulator.py
Simulación Montecarlo sobre el sistema difuso Mamdani para evaluación
de riesgo de bajo rendimiento académico.
Institución Universitaria Pascual Bravo · Medellín, Colombia
"""

from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")  # backend no interactivo para entornos sin display
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import truncnorm


# ---------------------------------------------------------------------------
# Distribuciones estadísticas por variable de entrada
# ---------------------------------------------------------------------------

DISTRIBUTIONS: dict[str, dict] = {
    "promedio_academico": {
        "type": "truncated_normal",
        "params": {"mean": 3.5, "std": 0.7, "low": 0.0, "high": 5.0},
        "justification": (
            "El promedio académico en poblaciones universitarias sigue una "
            "distribución aproximadamente normal. Se trunca en [0,5] para "
            "respetar el universo de discurso. Media 3.5 y std 0.7 reflejan "
            "la distribución típica observada en instituciones colombianas."
        ),
    },
    "inasistencia": {
        "type": "beta",
        "params": {"alpha": 2.0, "beta": 5.0, "scale": 100.0},
        "justification": (
            "La inasistencia es una proporción en [0,100]. La distribución "
            "Beta(2,5) modela la asimetría positiva observada: la mayoría de "
            "estudiantes tiene inasistencia baja, con cola hacia valores altos."
        ),
    },
    "horas_estudio": {
        "type": "triangular",
        "params": {"low": 0.0, "mode": 12.0, "high": 30.0},
        "justification": (
            "Las horas de estudio tienen límites naturales claros (0–30 h/semana). "
            "La distribución triangular es apropiada cuando se conocen mínimo, "
            "máximo y valor más probable. Moda en 12 h refleja el promedio "
            "reportado en encuestas de hábitos de estudio universitario."
        ),
    },
    "motivacion_estres": {
        "type": "triangular",
        "params": {"low": 0.0, "mode": 5.0, "high": 10.0},
        "justification": (
            "Escala subjetiva [0–10] con distribución simétrica alrededor del "
            "punto medio. La triangular con moda=5 modela la tendencia central "
            "sin asumir normalidad en escalas ordinales."
        ),
    },
}


class MontecarloSimulator:
    """
    Ejecuta simulación Montecarlo sobre el sistema difuso.
    Muestrea cada Variable_Entrada según su distribución estadística justificada.
    Persiste base_simulada.csv, montecarlo_histograma.png y
    montecarlo_distribuciones.md.
    """

    DISTRIBUTIONS = DISTRIBUTIONS

    def __init__(
        self,
        fuzzy_system,
        data_dir: str = "data/",
        docs_dir: str = "docs/",
        seed: int = 42,
    ) -> None:
        """
        Inicializa el simulador Montecarlo.

        Parameters
        ----------
        fuzzy_system : FuzzySystemBuilder
            Instancia ya construida (build() ya llamado) del sistema difuso.
        data_dir : str
            Directorio de datos de salida.
        docs_dir : str
            Directorio de documentación de salida.
        seed : int
            Semilla para reproducibilidad.
        """
        self._fuzzy_system = fuzzy_system
        self._data_dir = data_dir
        self._docs_dir = docs_dir
        self._rng = np.random.default_rng(seed)

        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(docs_dir, exist_ok=True)

        # Se populan durante run()
        self._statistics: dict | None = None

    # ------------------------------------------------------------------
    # Interfaz pública
    # ------------------------------------------------------------------

    def run(self, n_simulaciones: int = 1000) -> pd.DataFrame:
        """
        Ejecuta n_simulaciones del sistema difuso.

        Parameters
        ----------
        n_simulaciones : int
            Número de simulaciones a ejecutar.

        Returns
        -------
        pd.DataFrame
            DataFrame con columnas [promedio_academico, inasistencia,
            horas_estudio, motivacion_estres, riesgo].
        """
        registros = []
        for _ in range(n_simulaciones):
            inputs = self._sample_inputs()
            riesgo = self._fuzzy_system.evaluar_riesgo(inputs)
            registros.append({**inputs, "riesgo": riesgo})

        df = pd.DataFrame(registros, columns=[
            "promedio_academico",
            "inasistencia",
            "horas_estudio",
            "motivacion_estres",
            "riesgo",
        ])

        # Persistir CSV
        csv_path = os.path.join(self._data_dir, "base_simulada.csv")
        df.to_csv(csv_path, index=False)

        # Calcular estadísticas
        self._statistics = self._calculate_statistics(df["riesgo"])

        # Identificar escenarios críticos (almacenado internamente, disponible si se necesita)
        self._critical_scenarios = self._identify_critical_scenarios(df)

        # Generar artefactos de documentación
        self._generate_histogram(df["riesgo"])
        self._generate_distributions_doc()

        return df

    # ------------------------------------------------------------------
    # Métodos privados
    # ------------------------------------------------------------------

    def _sample_inputs(self) -> dict:
        """
        Muestrea un conjunto de valores de entrada según las distribuciones definidas.

        Returns
        -------
        dict
            Diccionario con las 4 variables de entrada muestreadas.
        """
        samples: dict[str, float] = {}

        for var_name, dist_def in DISTRIBUTIONS.items():
            dist_type = dist_def["type"]
            params = dist_def["params"]

            if dist_type == "truncated_normal":
                mean = params["mean"]
                std = params["std"]
                low = params["low"]
                high = params["high"]
                a = (low - mean) / std
                b = (high - mean) / std
                valor = truncnorm.rvs(a, b, loc=mean, scale=std, random_state=self._rng)

            elif dist_type == "beta":
                alpha = params["alpha"]
                beta = params["beta"]
                scale = params["scale"]
                valor = self._rng.beta(alpha, beta) * scale

            elif dist_type == "triangular":
                low = params["low"]
                mode = params["mode"]
                high = params["high"]
                valor = self._rng.triangular(low, mode, high)

            else:
                raise ValueError(
                    f"Tipo de distribución no soportado: '{dist_type}' "
                    f"para variable '{var_name}'."
                )

            samples[var_name] = float(valor)

        return samples

    def _calculate_statistics(self, results: pd.Series) -> dict:
        """
        Calcula estadísticas descriptivas sobre los resultados de la simulación.

        Parameters
        ----------
        results : pd.Series
            Serie con los valores de riesgo simulados.

        Returns
        -------
        dict
            Diccionario con mean, std, min, max, p25, p50, p75, p95, p_riesgo_alto.
        """
        p_riesgo_alto = float((results >= 70).sum()) / len(results)

        return {
            "mean": float(results.mean()),
            "std": float(results.std()),
            "min": float(results.min()),
            "max": float(results.max()),
            "p25": float(results.quantile(0.25)),
            "p50": float(results.quantile(0.50)),
            "p75": float(results.quantile(0.75)),
            "p95": float(results.quantile(0.95)),
            "p_riesgo_alto": p_riesgo_alto,
        }

    def _identify_critical_scenarios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filtra filas donde riesgo >= 70.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame completo de simulaciones.

        Returns
        -------
        pd.DataFrame
            Sub-DataFrame con escenarios de riesgo alto.
        """
        return df[df["riesgo"] >= 70].copy()

    def _generate_histogram(self, results: pd.Series) -> None:
        """
        Genera y guarda el histograma de distribución del riesgo.

        Parameters
        ----------
        results : pd.Series
            Serie con los valores de riesgo simulados.
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.hist(results, bins=30, color="steelblue", edgecolor="white", alpha=0.85)
        ax.axvline(x=70, color="red", linestyle="--", linewidth=2, label="Umbral crítico (70)")

        ax.set_title(
            "Distribución del Riesgo Académico — Simulación Montecarlo",
            fontsize=14,
            fontweight="bold",
        )
        ax.set_xlabel("Riesgo Académico", fontsize=12)
        ax.set_ylabel("Frecuencia", fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)

        # Añadir estadísticas en el gráfico si están disponibles
        if self._statistics is not None:
            stats = self._statistics
            textstr = (
                f"n = {len(results)}\n"
                f"Media = {stats['mean']:.2f}\n"
                f"Mediana = {stats['p50']:.2f}\n"
                f"P(riesgo ≥ 70) = {stats['p_riesgo_alto']:.1%}"
            )
            props = dict(boxstyle="round", facecolor="lightyellow", alpha=0.8)
            ax.text(
                0.02, 0.97, textstr,
                transform=ax.transAxes,
                fontsize=10,
                verticalalignment="top",
                bbox=props,
            )

        plt.tight_layout()
        hist_path = os.path.join(self._docs_dir, "montecarlo_histograma.png")
        plt.savefig(hist_path, dpi=100)
        plt.close(fig)

    def _generate_distributions_doc(self) -> None:
        """
        Genera docs/montecarlo_distribuciones.md con la descripción de las
        distribuciones estadísticas utilizadas y las estadísticas de la simulación.
        """
        lines = [
            "# Distribuciones Estadísticas — Simulación Montecarlo",
            "",
            "**Institución Universitaria Pascual Bravo · Medellín, Colombia**",
            "",
            "## Descripción",
            "",
            "Este documento describe las distribuciones estadísticas utilizadas para "
            "muestrear cada variable de entrada en la simulación Montecarlo del sistema "
            "difuso de evaluación de riesgo académico. Cada distribución fue seleccionada "
            "con base en evidencia empírica y justificación metodológica.",
            "",
            "## Distribuciones por Variable",
            "",
            "| Variable | Distribución | Parámetros | Justificación |",
            "|---|---|---|---|",
        ]

        for var_name, dist_def in DISTRIBUTIONS.items():
            dist_type = dist_def["type"]
            params = dist_def["params"]
            justification = dist_def["justification"]

            # Formatear parámetros
            params_str = ", ".join(f"{k}={v}" for k, v in params.items())

            # Nombre legible de la distribución
            dist_names = {
                "truncated_normal": "Normal Truncada",
                "beta": "Beta",
                "triangular": "Triangular",
            }
            dist_display = dist_names.get(dist_type, dist_type)

            lines.append(f"| `{var_name}` | {dist_display} | {params_str} | {justification} |")

        lines.append("")

        # Estadísticas de la simulación (si están disponibles)
        if self._statistics is not None:
            stats = self._statistics
            lines += [
                "## Estadísticas de la Simulación",
                "",
                "| Estadístico | Valor |",
                "|---|---|",
                f"| Media del riesgo | {stats['mean']:.4f} |",
                f"| Desviación estándar | {stats['std']:.4f} |",
                f"| Mínimo | {stats['min']:.4f} |",
                f"| Percentil 25 (P25) | {stats['p25']:.4f} |",
                f"| Mediana (P50) | {stats['p50']:.4f} |",
                f"| Percentil 75 (P75) | {stats['p75']:.4f} |",
                f"| Percentil 95 (P95) | {stats['p95']:.4f} |",
                f"| Máximo | {stats['max']:.4f} |",
                f"| P(riesgo ≥ 70) | {stats['p_riesgo_alto']:.4f} ({stats['p_riesgo_alto']:.1%}) |",
                "",
            ]

        lines += [
            "## Notas Metodológicas",
            "",
            "- La semilla global `RANDOM_SEED = 42` garantiza reproducibilidad completa.",
            "- La distribución normal truncada usa `scipy.stats.truncnorm` para respetar "
            "los límites del universo de discurso.",
            "- Las distribuciones beta y triangular usan `numpy.random.default_rng` "
            "para consistencia con la semilla global.",
            "- El umbral de riesgo alto se define en **70** puntos sobre 100.",
            "",
        ]

        doc_path = os.path.join(self._docs_dir, "montecarlo_distribuciones.md")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
