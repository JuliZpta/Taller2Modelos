"""
trabajo_final/montecarlo/montecarlo_simulator.py
Simulación Montecarlo sobre el sistema difuso Mamdani para evaluación
del riesgo de degradación del servicio (QoS) en una plataforma de streaming.

Variables de entrada y distribuciones:
  - usuarios_concurrentes : Beta(α=2, β=3, escala=100)
  - uso_ancho_banda        : Normal Truncada(μ=55, σ=20, [0,100])
  - latencia_red           : Triangular(mín=0, moda=3, máx=10)
  - capacidad_servidor     : Beta(α=3, β=2, escala=100)

Parte E — Taller 2 de Modelos y Simulación
"""

from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")  # backend no interactivo
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import truncnorm


# ---------------------------------------------------------------------------
# Distribuciones estadísticas por variable de entrada
# ---------------------------------------------------------------------------

DISTRIBUTIONS: dict[str, dict] = {
    "usuarios_concurrentes": {
        "type": "beta",
        "params": {"alpha": 2.0, "beta": 3.0, "scale": 100.0},
        "justification": (
            "Mayoría de tiempo con carga media-baja, picos en horas pico. "
            "Beta(2,3) modela la asimetría positiva: la plataforma opera "
            "frecuentemente por debajo del 50% de capacidad con picos ocasionales."
        ),
    },
    "uso_ancho_banda": {
        "type": "truncated_normal",
        "params": {"mean": 55.0, "std": 20.0, "low": 0.0, "high": 100.0},
        "justification": (
            "Uso promedio del 55% con variabilidad alta en horas pico. "
            "La distribución normal truncada en [0,100] refleja el comportamiento "
            "típico del ancho de banda en plataformas de streaming activas."
        ),
    },
    "latencia_red": {
        "type": "triangular",
        "params": {"low": 0.0, "mode": 3.0, "high": 10.0},
        "justification": (
            "Latencia típica baja con cola hacia valores altos en congestión. "
            "La distribución triangular con moda=3ms refleja condiciones normales "
            "de red con eventos ocasionales de alta latencia por congestión."
        ),
    },
    "capacidad_servidor": {
        "type": "beta",
        "params": {"alpha": 3.0, "beta": 2.0, "scale": 100.0},
        "justification": (
            "Servidores operan típicamente a alta capacidad en plataformas activas. "
            "Beta(3,2) modela la tendencia a operar en rangos altos de utilización "
            "con cola hacia valores bajos durante períodos de baja demanda."
        ),
    },
}


class MontecarloSimulator:
    """
    Ejecuta simulación Montecarlo sobre el sistema difuso de streaming.
    Muestrea cada variable de entrada según su distribución estadística justificada.
    Persiste base_simulada_streaming.csv, montecarlo_histograma_streaming.png y
    montecarlo_distribuciones_streaming.md.
    """

    DISTRIBUTIONS = DISTRIBUTIONS

    def __init__(
        self,
        fuzzy_system,
        data_dir: str = "trabajo_final/data/",
        docs_dir: str = "trabajo_final/docs/",
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
            Semilla para reproducibilidad (default 42).
        """
        self._fuzzy_system = fuzzy_system
        self._data_dir = data_dir
        self._docs_dir = docs_dir
        self._rng = np.random.default_rng(seed)

        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(docs_dir, exist_ok=True)

        self._statistics: dict | None = None

    # ------------------------------------------------------------------
    # Interfaz pública
    # ------------------------------------------------------------------

    def run(self, n_simulaciones: int = 5000) -> pd.DataFrame:
        """
        Ejecuta n_simulaciones del sistema difuso de streaming.

        Parameters
        ----------
        n_simulaciones : int
            Número de simulaciones a ejecutar (default 5000).

        Returns
        -------
        pd.DataFrame
            DataFrame con columnas [usuarios_concurrentes, uso_ancho_banda,
            latencia_red, capacidad_servidor, riesgo_qos].
        """
        registros = []
        for _ in range(n_simulaciones):
            inputs = self._sample_inputs()
            riesgo = self._fuzzy_system.evaluar_riesgo(inputs)
            registros.append({**inputs, "riesgo_qos": riesgo})

        df = pd.DataFrame(registros, columns=[
            "usuarios_concurrentes",
            "uso_ancho_banda",
            "latencia_red",
            "capacidad_servidor",
            "riesgo_qos",
        ])

        # Persistir CSV
        csv_path = os.path.join(self._data_dir, "base_simulada_streaming.csv")
        df.to_csv(csv_path, index=False)

        # Calcular estadísticas
        self._statistics = self._calculate_statistics(df["riesgo_qos"])

        # Generar artefactos de documentación
        self._generate_histogram(df["riesgo_qos"])
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
                beta_param = params["beta"]
                scale = params["scale"]
                valor = self._rng.beta(alpha, beta_param) * scale

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
            Serie con los valores de riesgo_qos simulados.

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

    def _generate_histogram(self, results: pd.Series) -> None:
        """Genera y guarda el histograma de distribución del riesgo QoS."""
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.hist(results, bins=30, color="steelblue", edgecolor="white", alpha=0.85)
        ax.axvline(x=70, color="red", linestyle="--", linewidth=2, label="Umbral crítico (70)")

        ax.set_title(
            "Distribución del Riesgo QoS — Simulación Montecarlo (Streaming)",
            fontsize=14,
            fontweight="bold",
        )
        ax.set_xlabel("Riesgo QoS (0–100)", fontsize=12)
        ax.set_ylabel("Frecuencia", fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)

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
        hist_path = os.path.join(self._docs_dir, "montecarlo_histograma_streaming.png")
        plt.savefig(hist_path, dpi=100)
        plt.close(fig)

    def _generate_distributions_doc(self) -> None:
        """
        Genera docs/montecarlo_distribuciones_streaming.md con la descripción
        de las distribuciones y las estadísticas de la simulación.
        """
        lines = [
            "# Distribuciones Estadísticas — Simulación Montecarlo (Streaming)",
            "",
            "**Parte E — Taller 2 de Modelos y Simulación**",
            "",
            "## Descripción",
            "",
            "Este documento describe las distribuciones estadísticas utilizadas para "
            "muestrear cada variable de entrada en la simulación Montecarlo del sistema "
            "difuso de evaluación del riesgo QoS en la plataforma de streaming.",
            "",
            "## Distribuciones por Variable",
            "",
            "| Variable | Distribución | Parámetros | Justificación |",
            "|---|---|---|---|",
        ]

        dist_names = {
            "truncated_normal": "Normal Truncada",
            "beta": "Beta",
            "triangular": "Triangular",
        }

        for var_name, dist_def in DISTRIBUTIONS.items():
            dist_type = dist_def["type"]
            params = dist_def["params"]
            justification = dist_def["justification"]
            params_str = ", ".join(f"{k}={v}" for k, v in params.items())
            dist_display = dist_names.get(dist_type, dist_type)
            lines.append(f"| `{var_name}` | {dist_display} | {params_str} | {justification} |")

        lines.append("")

        if self._statistics is not None:
            stats = self._statistics
            lines += [
                "## Estadísticas de la Simulación",
                "",
                "| Estadístico | Valor |",
                "|---|---|",
                f"| Media del riesgo QoS | {stats['mean']:.4f} |",
                f"| Desviación estándar | {stats['std']:.4f} |",
                f"| Mínimo | {stats['min']:.4f} |",
                f"| Percentil 25 (P25) | {stats['p25']:.4f} |",
                f"| Mediana (P50) | {stats['p50']:.4f} |",
                f"| Percentil 75 (P75) | {stats['p75']:.4f} |",
                f"| Percentil 95 (P95) | {stats['p95']:.4f} |",
                f"| Máximo | {stats['max']:.4f} |",
                f"| P(riesgo_qos ≥ 70) | {stats['p_riesgo_alto']:.4f} ({stats['p_riesgo_alto']:.1%}) |",
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
            "- Se ejecutaron **5000 simulaciones** con `RANDOM_SEED = 42`.",
            "",
        ]

        doc_path = os.path.join(self._docs_dir, "montecarlo_distribuciones_streaming.md")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
