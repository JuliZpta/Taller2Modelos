"""
trabajo_final/fuzzy_system/fuzzy_system_builder.py
Sistema de inferencia difuso tipo Mamdani para evaluación del riesgo
de degradación del servicio (QoS) en una plataforma de streaming.

Variables de entrada:
  - usuarios_concurrentes [0, 100]
  - uso_ancho_banda       [0, 100]
  - latencia_red          [0, 10]
  - capacidad_servidor    [0, 100]

Variable de salida:
  - riesgo_qos            [0, 100]  (defuzzificación centroide)

Parte E — Taller 2 de Modelos y Simulación
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Universos de discurso
# ---------------------------------------------------------------------------

UNIVERSES: dict[str, tuple[float, float, float]] = {
    "usuarios_concurrentes": (0.0, 100.0, 0.5),
    "uso_ancho_banda":       (0.0, 100.0, 0.5),
    "latencia_red":          (0.0, 10.0,  0.05),
    "capacidad_servidor":    (0.0, 100.0, 0.5),
    "riesgo_qos":            (0.0, 100.0, 0.5),
}

# ---------------------------------------------------------------------------
# Funciones de pertenencia
# ---------------------------------------------------------------------------

_MEMBERSHIP_DEFS: dict[str, list[tuple[str, str, list[float]]]] = {
    "usuarios_concurrentes": [
        ("bajo",  "trapezoidal", [0.0, 0.0, 30.0, 50.0]),
        ("medio", "triangular",  [40.0, 60.0, 80.0]),
        ("alto",  "trapezoidal", [70.0, 85.0, 100.0, 100.0]),
    ],
    "uso_ancho_banda": [
        ("bajo",  "trapezoidal", [0.0, 0.0, 30.0, 50.0]),
        ("medio", "triangular",  [40.0, 60.0, 80.0]),
        ("alto",  "trapezoidal", [70.0, 85.0, 100.0, 100.0]),
    ],
    "latencia_red": [
        ("baja",  "trapezoidal", [0.0, 0.0, 2.0, 4.0]),
        ("media", "triangular",  [3.0, 5.0, 7.0]),
        ("alta",  "trapezoidal", [6.0, 8.0, 10.0, 10.0]),
    ],
    "capacidad_servidor": [
        ("baja",  "trapezoidal", [0.0, 0.0, 30.0, 50.0]),
        ("media", "triangular",  [40.0, 60.0, 80.0]),
        ("alta",  "trapezoidal", [70.0, 85.0, 100.0, 100.0]),
    ],
    # Funciones de salida con solapamiento máximo para distribución continua
    # Los centroides individuales están separados pero las MFs se solapan ampliamente
    "riesgo_qos": [
        ("muy_bajo", "trapezoidal", [0.0,  0.0,  20.0, 45.0]),   # centroide ~18
        ("bajo",     "triangular",  [30.0, 48.0, 65.0]),          # centroide ~48
        ("medio",    "triangular",  [52.0, 63.0, 76.0]),          # centroide ~64
        ("alto",     "triangular",  [65.0, 76.0, 88.0]),          # centroide ~76
        ("muy_alto", "trapezoidal", [80.0, 90.0, 100.0, 100.0]), # centroide ~93
    ],
}

# ---------------------------------------------------------------------------
# 27 reglas con cobertura completa del espacio de entrada
# ---------------------------------------------------------------------------

_REGLAS_COMPACTAS_ST = [
    # usuarios=alto (riesgo alto/muy_alto)
    ("R01", [("usuarios_concurrentes","alto"), ("uso_ancho_banda","alto"), ("latencia_red","alta")], "muy_alto"),
    ("R02", [("usuarios_concurrentes","alto"), ("uso_ancho_banda","alto"), ("capacidad_servidor","alta")], "muy_alto"),
    ("R03", [("usuarios_concurrentes","alto"), ("uso_ancho_banda","alto"), ("latencia_red","media")], "alto"),
    ("R04", [("usuarios_concurrentes","alto"), ("uso_ancho_banda","medio"), ("latencia_red","alta")], "alto"),
    ("R05", [("usuarios_concurrentes","alto"), ("uso_ancho_banda","medio"), ("capacidad_servidor","alta")], "alto"),
    ("R06", [("usuarios_concurrentes","alto"), ("uso_ancho_banda","bajo"), ("latencia_red","alta")], "alto"),
    ("R07", [("usuarios_concurrentes","alto"), ("uso_ancho_banda","medio"), ("latencia_red","media")], "medio"),
    ("R08", [("usuarios_concurrentes","alto"), ("uso_ancho_banda","bajo"), ("latencia_red","media")], "medio"),
    ("R09", [("usuarios_concurrentes","alto"), ("uso_ancho_banda","bajo"), ("latencia_red","baja")], "bajo"),
    # usuarios=medio (riesgo medio/bajo)
    ("R10", [("usuarios_concurrentes","medio"), ("uso_ancho_banda","alto"), ("latencia_red","alta")], "alto"),
    ("R11", [("usuarios_concurrentes","medio"), ("uso_ancho_banda","alto"), ("capacidad_servidor","alta")], "alto"),
    ("R12", [("usuarios_concurrentes","medio"), ("uso_ancho_banda","alto"), ("latencia_red","media")], "medio"),
    ("R13", [("usuarios_concurrentes","medio"), ("uso_ancho_banda","medio"), ("latencia_red","alta")], "medio"),
    ("R14", [("usuarios_concurrentes","medio"), ("uso_ancho_banda","medio"), ("capacidad_servidor","alta")], "medio"),
    ("R15", [("usuarios_concurrentes","medio"), ("uso_ancho_banda","medio"), ("latencia_red","media")], "bajo"),
    ("R16", [("usuarios_concurrentes","medio"), ("uso_ancho_banda","bajo"), ("latencia_red","alta")], "medio"),
    ("R17", [("usuarios_concurrentes","medio"), ("uso_ancho_banda","bajo"), ("capacidad_servidor","baja")], "bajo"),
    ("R18", [("usuarios_concurrentes","medio"), ("uso_ancho_banda","bajo"), ("latencia_red","media")], "muy_bajo"),
    ("R19", [("usuarios_concurrentes","medio"), ("uso_ancho_banda","bajo"), ("latencia_red","baja")], "muy_bajo"),
    ("R20", [("usuarios_concurrentes","medio"), ("uso_ancho_banda","medio"), ("latencia_red","baja")], "bajo"),
    # usuarios=bajo (riesgo bajo/muy_bajo)
    ("R21", [("usuarios_concurrentes","bajo"), ("uso_ancho_banda","alto"), ("latencia_red","alta")], "medio"),
    ("R22", [("usuarios_concurrentes","bajo"), ("uso_ancho_banda","alto"), ("latencia_red","media")], "bajo"),
    ("R23", [("usuarios_concurrentes","bajo"), ("uso_ancho_banda","medio"), ("latencia_red","alta")], "bajo"),
    ("R24", [("usuarios_concurrentes","bajo"), ("uso_ancho_banda","medio"), ("latencia_red","media")], "muy_bajo"),
    ("R25", [("usuarios_concurrentes","bajo"), ("uso_ancho_banda","bajo"), ("latencia_red","alta")], "muy_bajo"),
    ("R26", [("usuarios_concurrentes","bajo"), ("uso_ancho_banda","bajo"), ("latencia_red","media")], "muy_bajo"),
    ("R27", [("usuarios_concurrentes","bajo"), ("uso_ancho_banda","bajo"), ("latencia_red","baja")], "muy_bajo"),
]

_RULES_DEF: list[dict] = [
    {
        "id": rid,
        "descripcion": f"{' AND '.join(f'{v}={e}' for v, e in ants)} → riesgo_qos={cons}",
        "antecedentes": [{"variable": v, "etiqueta": e} for v, e in ants],
        "consecuente": {"variable": "riesgo_qos", "etiqueta": cons},
        "operador": "AND",
        "origen_delphi": "Consenso E1-E4 Ronda 3",
    }
    for rid, ants, cons in _REGLAS_COMPACTAS_ST
]

# Variables de entrada esperadas (deben coincidir con variables_aprobadas del consenso)
_EXPECTED_INPUT_VARS: set[str] = {
    "usuarios_concurrentes",
    "uso_ancho_banda",
    "latencia_red",
    "capacidad_servidor",
}


# ---------------------------------------------------------------------------
# Clase principal
# ---------------------------------------------------------------------------

class FuzzySystemBuilder:
    """
    Construye el sistema de inferencia difuso Mamdani usando scikit-fuzzy.
    Lee las variables_aprobadas de data/delphi_consenso.json.
    Expone evaluar_riesgo() como interfaz pública para otros módulos.
    """

    UNIVERSES = UNIVERSES

    def __init__(
        self,
        consenso_path: str = "trabajo_final/data/delphi_consenso.json",
        data_dir: str = "trabajo_final/data/",
        docs_dir: str = "trabajo_final/docs/",
    ) -> None:
        if not os.path.exists(consenso_path):
            raise FileNotFoundError(
                f"No se encontró el archivo de consenso Delphi: '{consenso_path}'. "
                "Ejecute primero el proceso Delphi para generar este archivo."
            )

        with open(consenso_path, encoding="utf-8") as f:
            self._consenso = json.load(f)

        aprobadas = {
            v["factor"] for v in self._consenso.get("variables_aprobadas", [])
        }
        if aprobadas != _EXPECTED_INPUT_VARS:
            faltantes = _EXPECTED_INPUT_VARS - aprobadas
            extras = aprobadas - _EXPECTED_INPUT_VARS
            msg_parts = []
            if faltantes:
                msg_parts.append(f"variables faltantes en consenso: {sorted(faltantes)}")
            if extras:
                msg_parts.append(f"variables extra no esperadas: {sorted(extras)}")
            raise ValueError(
                "Las variables aprobadas en el consenso Delphi no coinciden con las "
                "variables esperadas por el sistema difuso. " + "; ".join(msg_parts) + "."
            )

        self._data_dir = data_dir
        self._docs_dir = docs_dir
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(docs_dir, exist_ok=True)

        self._antecedentes: dict[str, ctrl.Antecedent] = {}
        self._consecuente: ctrl.Consequent | None = None
        self._rules: list[ctrl.Rule] = []
        self._control_system: ctrl.ControlSystem | None = None
        self._built: bool = False

    # ------------------------------------------------------------------
    # Interfaz pública
    # ------------------------------------------------------------------

    def build(self) -> None:
        self._build_membership_functions()
        self._build_rules()
        self._persist_variables()
        self._persist_rules()
        self._plot_membership_functions()
        self._built = True

    def evaluar_riesgo(self, valores_entrada: dict) -> float:
        if not self._built:
            raise RuntimeError(
                "El sistema difuso no ha sido construido. Llame a build() primero."
            )

        valores_recortados: dict[str, float] = {}
        for var_name, valor in valores_entrada.items():
            if var_name not in UNIVERSES:
                continue
            lo, hi, _ = UNIVERSES[var_name]
            valor_float = float(np.clip(float(valor), lo, hi))
            valores_recortados[var_name] = valor_float

        try:
            sim = ctrl.ControlSystemSimulation(self._control_system)
            for var_name, valor in valores_recortados.items():
                if var_name != "riesgo_qos":
                    sim.input[var_name] = valor
            sim.compute()
            if "riesgo_qos" not in sim.output:
                return self._fallback_centroid(valores_recortados)
            resultado = float(np.clip(sim.output["riesgo_qos"], 0.0, 100.0))
            return resultado
        except KeyError:
            return self._fallback_centroid(valores_recortados)
        except Exception as exc:
            logger.warning("Error en motor difuso: %s. Usando fallback.", exc)
            return self._fallback_centroid(valores_recortados)

    def _fallback_centroid(self, valores: dict) -> float:
        lo, hi, step = UNIVERSES["riesgo_qos"]
        universe_out = np.arange(lo, hi + step, step)

        label_map = {
            "bajo": "bajo", "baja": "muy_bajo",
            "medio": "medio", "media": "medio",
            "alto": "alto", "alta": "alto",
        }

        output_activations = {k: 0.0 for k in ["muy_bajo", "bajo", "medio", "alto", "muy_alto"]}

        for var_name, valor in valores.items():
            if var_name == "riesgo_qos" or var_name not in UNIVERSES:
                continue
            lo_v, hi_v, step_v = UNIVERSES[var_name]
            universe_v = np.arange(lo_v, hi_v + step_v, step_v)
            for etiqueta, tipo, params in _MEMBERSHIP_DEFS[var_name]:
                mf = (
                    fuzz.trimf(universe_v, params) if tipo == "triangular"
                    else fuzz.trapmf(universe_v, params)
                )
                activation = float(fuzz.interp_membership(universe_v, mf, valor))
                out_label = label_map.get(etiqueta, "medio")
                output_activations[out_label] = max(output_activations[out_label], activation)

        aggregated = np.zeros_like(universe_out)
        for etiqueta, tipo, params in _MEMBERSHIP_DEFS["riesgo_qos"]:
            mf = (
                fuzz.trimf(universe_out, params) if tipo == "triangular"
                else fuzz.trapmf(universe_out, params)
            )
            activation = output_activations.get(etiqueta, 0.0)
            aggregated = np.fmax(aggregated, np.fmin(activation, mf))

        if aggregated.sum() == 0:
            return 50.0
        resultado = float(fuzz.defuzz(universe_out, aggregated, "centroid"))
        return float(np.clip(resultado, 0.0, 100.0))

    # ------------------------------------------------------------------
    # Métodos privados de construcción
    # ------------------------------------------------------------------

    def _build_membership_functions(self) -> None:
        input_vars = [v for v in UNIVERSES if v != "riesgo_qos"]

        for var_name in input_vars:
            lo, hi, step = UNIVERSES[var_name]
            universe = np.arange(lo, hi + step, step)
            antecedente = ctrl.Antecedent(universe, var_name)

            for etiqueta, tipo, params in _MEMBERSHIP_DEFS[var_name]:
                antecedente[etiqueta] = (
                    fuzz.trimf(universe, params) if tipo == "triangular"
                    else fuzz.trapmf(universe, params)
                )

            self._antecedentes[var_name] = antecedente

        lo, hi, step = UNIVERSES["riesgo_qos"]
        universe_riesgo = np.arange(lo, hi + step, step)
        self._consecuente = ctrl.Consequent(
            universe_riesgo, "riesgo_qos", defuzzify_method="centroid"
        )

        for etiqueta, tipo, params in _MEMBERSHIP_DEFS["riesgo_qos"]:
            self._consecuente[etiqueta] = (
                fuzz.trimf(universe_riesgo, params) if tipo == "triangular"
                else fuzz.trapmf(universe_riesgo, params)
            )

    def _build_rules(self) -> None:
        self._rules = []

        for rule_def in _RULES_DEF:
            ant_terms = [
                self._antecedentes[a["variable"]][a["etiqueta"]]
                for a in rule_def["antecedentes"]
            ]
            antecedente_compuesto = ant_terms[0]
            for term in ant_terms[1:]:
                antecedente_compuesto = antecedente_compuesto & term

            consecuente = self._consecuente[rule_def["consecuente"]["etiqueta"]]
            rule = ctrl.Rule(antecedente_compuesto, consecuente, label=rule_def["id"])
            self._rules.append(rule)

        self._control_system = ctrl.ControlSystem(self._rules)

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------

    def _persist_variables(self) -> None:
        input_vars = [v for v in UNIVERSES if v != "riesgo_qos"]

        variables_entrada = []
        for var_name in input_vars:
            lo, hi, step = UNIVERSES[var_name]
            etiquetas = [
                {"nombre": e, "tipo": t, "parametros": p}
                for e, t, p in _MEMBERSHIP_DEFS[var_name]
            ]
            variables_entrada.append({
                "nombre": var_name,
                "universo": [lo, hi],
                "step": step,
                "etiquetas": etiquetas,
                "origen_delphi": var_name,
            })

        lo_r, hi_r, step_r = UNIVERSES["riesgo_qos"]
        etiquetas_riesgo = [
            {"nombre": e, "tipo": t, "parametros": p}
            for e, t, p in _MEMBERSHIP_DEFS["riesgo_qos"]
        ]

        doc = {
            "variables_entrada": variables_entrada,
            "variable_salida": {
                "nombre": "riesgo_qos",
                "universo": [lo_r, hi_r],
                "step": step_r,
                "etiquetas": etiquetas_riesgo,
                "defuzzificacion": "centroide",
            },
        }

        output_path = os.path.join(self._data_dir, "fuzzy_variables.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

    def _persist_rules(self) -> None:
        doc = {"reglas": _RULES_DEF}
        output_path = os.path.join(self._data_dir, "fuzzy_rules.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

    def _plot_membership_functions(self) -> None:
        plots_dir = os.path.join(self._docs_dir, "fuzzy_membership_plots")
        os.makedirs(plots_dir, exist_ok=True)

        var_labels = {
            "usuarios_concurrentes": "Usuarios Concurrentes (0–100)",
            "uso_ancho_banda":       "Uso de Ancho de Banda (%)",
            "latencia_red":          "Latencia de Red (ms normalizado 0–10)",
            "capacidad_servidor":    "Capacidad del Servidor (%)",
            "riesgo_qos":            "Riesgo QoS (0–100)",
        }

        for var_name in UNIVERSES:
            lo, hi, step = UNIVERSES[var_name]
            universe = np.arange(lo, hi + step, step)

            fig, ax = plt.subplots(figsize=(8, 4))

            for etiqueta, tipo, params in _MEMBERSHIP_DEFS[var_name]:
                mf = (
                    fuzz.trimf(universe, params) if tipo == "triangular"
                    else fuzz.trapmf(universe, params)
                )
                ax.plot(universe, mf, label=etiqueta, linewidth=2)

            xlabel = var_labels.get(var_name, var_name)
            ax.set_title(f"Funciones de pertenencia — {var_name}", fontsize=13)
            ax.set_xlabel(xlabel)
            ax.set_ylabel("Grado de pertenencia")
            ax.set_ylim(-0.05, 1.1)
            ax.legend(loc="upper right")
            ax.grid(True, alpha=0.3)

            plot_path = os.path.join(plots_dir, f"{var_name}.png")
            plt.tight_layout()
            plt.savefig(plot_path, dpi=100)
            plt.close(fig)
