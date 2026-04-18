"""
fuzzy_system/fuzzy_system_builder.py
Sistema de inferencia difuso tipo Mamdani para evaluación de riesgo
de bajo rendimiento académico.
Institución Universitaria Pascual Bravo · Medellín, Colombia
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

UNIVERSES: dict[str, tuple[float, float, float]] = {
    "promedio_academico": (0.0, 5.0, 0.01),
    "inasistencia":       (0.0, 100.0, 0.5),
    "horas_estudio":      (0.0, 30.0, 0.1),
    "motivacion_estres":  (0.0, 10.0, 0.1),
    "riesgo":             (0.0, 100.0, 0.5),
}

_MEMBERSHIP_DEFS: dict[str, list[tuple[str, str, list[float]]]] = {
    "promedio_academico": [
        ("bajo",  "trapezoidal", [0.0, 0.0, 2.0, 3.0]),
        ("medio", "triangular",  [2.5, 3.5, 4.5]),
        ("alto",  "trapezoidal", [4.0, 4.5, 5.0, 5.0]),
    ],
    "inasistencia": [
        ("baja",  "trapezoidal", [0.0, 0.0, 15.0, 30.0]),
        ("media", "triangular",  [20.0, 40.0, 60.0]),
        ("alta",  "trapezoidal", [50.0, 70.0, 100.0, 100.0]),
    ],
    "horas_estudio": [
        ("pocas",     "trapezoidal", [0.0, 0.0, 5.0, 12.0]),
        ("moderadas", "triangular",  [8.0, 15.0, 22.0]),
        ("muchas",    "trapezoidal", [18.0, 24.0, 30.0, 30.0]),
    ],
    "motivacion_estres": [
        ("bajo",  "trapezoidal", [0.0, 0.0, 3.0, 5.0]),
        ("medio", "triangular",  [3.0, 5.0, 7.0]),
        ("alto",  "trapezoidal", [6.0, 8.0, 10.0, 10.0]),
    ],
    # Funciones ASIMÉTRICAS para evitar centroides en valores redondos
    "riesgo": [
        ("muy_bajo", "trapezoidal", [0.0,  0.0,  8.0,  20.0]),   # centroide ~9
        ("bajo",     "triangular",  [10.0, 22.0, 38.0]),          # centroide ~23
        ("medio",    "triangular",  [28.0, 47.0, 63.0]),          # centroide ~46
        ("alto",     "triangular",  [55.0, 70.0, 83.0]),          # centroide ~69
        ("muy_alto", "trapezoidal", [75.0, 87.0, 100.0, 100.0]), # centroide ~91
    ],
}

# ---------------------------------------------------------------------------
# 27 reglas con cobertura completa del espacio de entrada
# ---------------------------------------------------------------------------

_REGLAS_COMPACTAS = [
    # promedio=bajo (riesgo alto/muy_alto)
    ("R01", [("promedio_academico","bajo"), ("inasistencia","alta")], "muy_alto"),
    ("R02", [("promedio_academico","bajo"), ("inasistencia","media"), ("horas_estudio","pocas")], "alto"),
    ("R03", [("promedio_academico","bajo"), ("inasistencia","media"), ("motivacion_estres","bajo")], "alto"),
    ("R04", [("promedio_academico","bajo"), ("inasistencia","baja"), ("horas_estudio","pocas")], "alto"),
    ("R05", [("promedio_academico","bajo"), ("inasistencia","baja"), ("motivacion_estres","bajo")], "medio"),
    ("R06", [("promedio_academico","bajo"), ("inasistencia","baja"), ("horas_estudio","moderadas")], "medio"),
    ("R07", [("promedio_academico","bajo"), ("inasistencia","media"), ("horas_estudio","moderadas")], "medio"),
    ("R08", [("promedio_academico","bajo"), ("inasistencia","media"), ("motivacion_estres","alto")], "medio"),
    ("R09", [("promedio_academico","bajo"), ("inasistencia","baja"), ("motivacion_estres","alto")], "bajo"),
    # promedio=medio (riesgo medio)
    ("R10", [("promedio_academico","medio"), ("inasistencia","alta"), ("horas_estudio","pocas")], "alto"),
    ("R11", [("promedio_academico","medio"), ("inasistencia","alta"), ("motivacion_estres","bajo")], "alto"),
    ("R12", [("promedio_academico","medio"), ("inasistencia","alta"), ("horas_estudio","moderadas")], "medio"),
    ("R13", [("promedio_academico","medio"), ("inasistencia","media"), ("horas_estudio","pocas")], "medio"),
    ("R14", [("promedio_academico","medio"), ("inasistencia","media"), ("motivacion_estres","bajo")], "medio"),
    ("R15", [("promedio_academico","medio"), ("inasistencia","media"), ("horas_estudio","moderadas")], "medio"),
    ("R16", [("promedio_academico","medio"), ("inasistencia","baja"), ("horas_estudio","pocas")], "medio"),
    ("R17", [("promedio_academico","medio"), ("inasistencia","baja"), ("motivacion_estres","bajo")], "bajo"),
    ("R18", [("promedio_academico","medio"), ("inasistencia","baja"), ("horas_estudio","moderadas")], "bajo"),
    ("R19", [("promedio_academico","medio"), ("inasistencia","baja"), ("motivacion_estres","alto")], "bajo"),
    ("R20", [("promedio_academico","medio"), ("inasistencia","media"), ("motivacion_estres","alto")], "bajo"),
    # promedio=alto (riesgo bajo/muy_bajo)
    ("R21", [("promedio_academico","alto"), ("inasistencia","alta"), ("horas_estudio","pocas")], "medio"),
    ("R22", [("promedio_academico","alto"), ("inasistencia","alta"), ("horas_estudio","moderadas")], "medio"),
    ("R23", [("promedio_academico","alto"), ("inasistencia","media"), ("horas_estudio","pocas")], "bajo"),
    ("R24", [("promedio_academico","alto"), ("inasistencia","media"), ("horas_estudio","moderadas")], "bajo"),
    ("R25", [("promedio_academico","alto"), ("inasistencia","baja"), ("horas_estudio","pocas")], "bajo"),
    ("R26", [("promedio_academico","alto"), ("inasistencia","baja"), ("horas_estudio","moderadas")], "muy_bajo"),
    ("R27", [("promedio_academico","alto"), ("inasistencia","baja"), ("horas_estudio","muchas")], "muy_bajo"),
]

_RULES_DEF: list[dict] = [
    {
        "id": rid,
        "descripcion": f"{' AND '.join(f'{v}={e}' for v, e in ants)} → riesgo={cons}",
        "antecedentes": [{"variable": v, "etiqueta": e} for v, e in ants],
        "consecuente": {"variable": "riesgo", "etiqueta": cons},
        "operador": "AND",
        "origen_delphi": "Consenso E1-E4 Ronda 3",
    }
    for rid, ants, cons in _REGLAS_COMPACTAS
]

_EXPECTED_INPUT_VARS: set[str] = {
    "promedio_academico",
    "inasistencia",
    "horas_estudio",
    "motivacion_estres",
}


class FuzzySystemBuilder:
    UNIVERSES = UNIVERSES

    def __init__(self, consenso_path="data/delphi_consenso.json", data_dir="data/", docs_dir="docs/"):
        if not os.path.exists(consenso_path):
            raise FileNotFoundError(f"No se encontró: '{consenso_path}'")
        with open(consenso_path, encoding="utf-8") as f:
            self._consenso = json.load(f)
        aprobadas = {v["factor"] for v in self._consenso.get("variables_aprobadas", [])}
        if aprobadas != _EXPECTED_INPUT_VARS:
            faltantes = _EXPECTED_INPUT_VARS - aprobadas
            extras = aprobadas - _EXPECTED_INPUT_VARS
            msg_parts = []
            if faltantes:
                msg_parts.append(f"faltantes: {sorted(faltantes)}")
            if extras:
                msg_parts.append(f"extras: {sorted(extras)}")
            raise ValueError("Variables no coinciden. " + "; ".join(msg_parts))
        self._data_dir = data_dir
        self._docs_dir = docs_dir
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(docs_dir, exist_ok=True)
        self._antecedentes: dict = {}
        self._consecuente = None
        self._rules: list = []
        self._control_system = None
        self._built: bool = False

    def build(self):
        self._build_membership_functions()
        self._build_rules()
        self._persist_variables()
        self._persist_rules()
        self._plot_membership_functions()
        self._built = True

    def evaluar_riesgo(self, valores_entrada: dict) -> float:
        if not self._built:
            raise RuntimeError("Llame a build() primero.")
        valores_recortados: dict = {}
        for var_name, valor in valores_entrada.items():
            if var_name not in UNIVERSES:
                continue
            lo, hi, _ = UNIVERSES[var_name]
            valor_float = float(np.clip(float(valor), lo, hi))
            valores_recortados[var_name] = valor_float
        try:
            sim = ctrl.ControlSystemSimulation(self._control_system)
            for var_name, valor in valores_recortados.items():
                if var_name != "riesgo":
                    sim.input[var_name] = valor
            sim.compute()
            if "riesgo" not in sim.output:
                return self._fallback_centroid(valores_recortados)
            resultado = float(np.clip(sim.output["riesgo"], 0.0, 100.0))
            return resultado
        except KeyError:
            return self._fallback_centroid(valores_recortados)
        except Exception as exc:
            logger.warning("Error en motor difuso: %s. Usando fallback.", exc)
            return self._fallback_centroid(valores_recortados)

    def _fallback_centroid(self, valores: dict) -> float:
        lo, hi, step = UNIVERSES["riesgo"]
        universe_out = np.arange(lo, hi + step, step)
        label_map = {
            "bajo": "bajo", "baja": "muy_bajo",
            "medio": "medio", "media": "medio",
            "alto": "alto", "alta": "alto",
            "pocas": "alto", "moderadas": "medio", "muchas": "muy_bajo",
        }
        output_activations: dict = {k: 0.0 for k in ["muy_bajo", "bajo", "medio", "alto", "muy_alto"]}
        for var_name, valor in valores.items():
            if var_name not in UNIVERSES or var_name == "riesgo":
                continue
            lo_v, hi_v, step_v = UNIVERSES[var_name]
            universe_v = np.arange(lo_v, hi_v + step_v, step_v)
            for etiqueta, tipo, params in _MEMBERSHIP_DEFS[var_name]:
                mf = fuzz.trimf(universe_v, params) if tipo == "triangular" else fuzz.trapmf(universe_v, params)
                activation = float(fuzz.interp_membership(universe_v, mf, valor))
                out_label = label_map.get(etiqueta, "medio")
                output_activations[out_label] = max(output_activations[out_label], activation)
        aggregated = np.zeros_like(universe_out)
        for etiqueta, tipo, params in _MEMBERSHIP_DEFS["riesgo"]:
            mf = fuzz.trimf(universe_out, params) if tipo == "triangular" else fuzz.trapmf(universe_out, params)
            activation = output_activations.get(etiqueta, 0.0)
            aggregated = np.fmax(aggregated, np.fmin(activation, mf))
        if aggregated.sum() == 0:
            return 50.0
        return float(np.clip(fuzz.defuzz(universe_out, aggregated, "centroid"), 0.0, 100.0))

    def _build_membership_functions(self):
        input_vars = [v for v in UNIVERSES if v != "riesgo"]
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
        lo, hi, step = UNIVERSES["riesgo"]
        universe_riesgo = np.arange(lo, hi + step, step)
        self._consecuente = ctrl.Consequent(universe_riesgo, "riesgo", defuzzify_method="centroid")
        for etiqueta, tipo, params in _MEMBERSHIP_DEFS["riesgo"]:
            self._consecuente[etiqueta] = (
                fuzz.trimf(universe_riesgo, params) if tipo == "triangular"
                else fuzz.trapmf(universe_riesgo, params)
            )

    def _build_rules(self):
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
            self._rules.append(ctrl.Rule(antecedente_compuesto, consecuente, label=rule_def["id"]))
        self._control_system = ctrl.ControlSystem(self._rules)

    def _persist_variables(self):
        input_vars = [v for v in UNIVERSES if v != "riesgo"]
        variables_entrada = []
        for var_name in input_vars:
            lo, hi, step = UNIVERSES[var_name]
            etiquetas = [{"nombre": e, "tipo": t, "parametros": p} for e, t, p in _MEMBERSHIP_DEFS[var_name]]
            variables_entrada.append({
                "nombre": var_name,
                "universo": [lo, hi],
                "step": step,
                "etiquetas": etiquetas,
                "origen_delphi": var_name,
            })
        lo_r, hi_r, step_r = UNIVERSES["riesgo"]
        etiquetas_riesgo = [{"nombre": e, "tipo": t, "parametros": p} for e, t, p in _MEMBERSHIP_DEFS["riesgo"]]
        doc = {
            "variables_entrada": variables_entrada,
            "variable_salida": {
                "nombre": "riesgo",
                "universo": [lo_r, hi_r],
                "step": step_r,
                "etiquetas": etiquetas_riesgo,
            },
        }
        with open(os.path.join(self._data_dir, "fuzzy_variables.json"), "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

    def _persist_rules(self):
        with open(os.path.join(self._data_dir, "fuzzy_rules.json"), "w", encoding="utf-8") as f:
            json.dump({"reglas": _RULES_DEF}, f, ensure_ascii=False, indent=2)

    def _plot_membership_functions(self):
        plots_dir = os.path.join(self._docs_dir, "fuzzy_membership_plots")
        os.makedirs(plots_dir, exist_ok=True)
        for var_name in UNIVERSES:
            lo, hi, step = UNIVERSES[var_name]
            universe = np.arange(lo, hi + step, step)
            fig, ax = plt.subplots(figsize=(8, 4))
            for etiqueta, tipo, params in _MEMBERSHIP_DEFS[var_name]:
                mf = fuzz.trimf(universe, params) if tipo == "triangular" else fuzz.trapmf(universe, params)
                ax.plot(universe, mf, label=etiqueta, linewidth=2)
            ax.set_title(f"Funciones de pertenencia — {var_name}", fontsize=13)
            ax.set_xlabel(var_name)
            ax.set_ylabel("Grado de pertenencia")
            ax.set_ylim(-0.05, 1.1)
            ax.legend(loc="upper right")
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(os.path.join(plots_dir, f"{var_name}.png"), dpi=100)
            plt.close(fig)

    def _log_warning(self, message, tipo="general", variable=None, valor_original=None, valor_recortado=None):
        warnings_path = os.path.join(self._data_dir, "fuzzy_warnings.json")
        try:
            with open(warnings_path, encoding="utf-8") as f:
                doc = json.load(f)
        except Exception:
            doc = {"warnings": []}
        entry = {"timestamp": datetime.now(timezone.utc).isoformat(), "tipo": tipo, "mensaje": message}
        if variable is not None:
            entry["variable"] = variable
        doc["warnings"].append(entry)
        with open(warnings_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
