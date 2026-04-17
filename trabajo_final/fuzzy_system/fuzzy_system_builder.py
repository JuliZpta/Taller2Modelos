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
matplotlib.use("Agg")  # backend no interactivo
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
    "riesgo_qos": [
        ("bajo",  "trapezoidal", [0.0, 0.0, 20.0, 40.0]),
        ("medio", "triangular",  [30.0, 50.0, 70.0]),
        ("alto",  "trapezoidal", [60.0, 80.0, 100.0, 100.0]),
    ],
}

# ---------------------------------------------------------------------------
# Reglas Mamdani (12 reglas)
# ---------------------------------------------------------------------------

_RULES_DEF: list[dict] = [
    {
        "id": "R01",
        "descripcion": "SI usuarios_concurrentes=alto Y uso_ancho_banda=alto → riesgo_qos=alto",
        "antecedentes": [
            {"variable": "usuarios_concurrentes", "etiqueta": "alto"},
            {"variable": "uso_ancho_banda",        "etiqueta": "alto"},
        ],
        "consecuente": {"variable": "riesgo_qos", "etiqueta": "alto"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R02",
        "descripcion": "SI latencia_red=alta Y capacidad_servidor=alta → riesgo_qos=alto",
        "antecedentes": [
            {"variable": "latencia_red",       "etiqueta": "alta"},
            {"variable": "capacidad_servidor", "etiqueta": "alta"},
        ],
        "consecuente": {"variable": "riesgo_qos", "etiqueta": "alto"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R03",
        "descripcion": "SI uso_ancho_banda=alto Y latencia_red=alta → riesgo_qos=alto",
        "antecedentes": [
            {"variable": "uso_ancho_banda", "etiqueta": "alto"},
            {"variable": "latencia_red",    "etiqueta": "alta"},
        ],
        "consecuente": {"variable": "riesgo_qos", "etiqueta": "alto"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R04",
        "descripcion": "SI usuarios_concurrentes=bajo Y uso_ancho_banda=bajo → riesgo_qos=bajo",
        "antecedentes": [
            {"variable": "usuarios_concurrentes", "etiqueta": "bajo"},
            {"variable": "uso_ancho_banda",        "etiqueta": "bajo"},
        ],
        "consecuente": {"variable": "riesgo_qos", "etiqueta": "bajo"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R05",
        "descripcion": "SI capacidad_servidor=baja Y latencia_red=baja → riesgo_qos=bajo",
        "antecedentes": [
            {"variable": "capacidad_servidor", "etiqueta": "baja"},
            {"variable": "latencia_red",       "etiqueta": "baja"},
        ],
        "consecuente": {"variable": "riesgo_qos", "etiqueta": "bajo"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R06",
        "descripcion": "SI usuarios_concurrentes=bajo Y latencia_red=baja → riesgo_qos=bajo",
        "antecedentes": [
            {"variable": "usuarios_concurrentes", "etiqueta": "bajo"},
            {"variable": "latencia_red",          "etiqueta": "baja"},
        ],
        "consecuente": {"variable": "riesgo_qos", "etiqueta": "bajo"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R07",
        "descripcion": "SI usuarios_concurrentes=medio Y uso_ancho_banda=medio → riesgo_qos=medio",
        "antecedentes": [
            {"variable": "usuarios_concurrentes", "etiqueta": "medio"},
            {"variable": "uso_ancho_banda",        "etiqueta": "medio"},
        ],
        "consecuente": {"variable": "riesgo_qos", "etiqueta": "medio"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R08",
        "descripcion": "SI latencia_red=media Y capacidad_servidor=media → riesgo_qos=medio",
        "antecedentes": [
            {"variable": "latencia_red",       "etiqueta": "media"},
            {"variable": "capacidad_servidor", "etiqueta": "media"},
        ],
        "consecuente": {"variable": "riesgo_qos", "etiqueta": "medio"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R09",
        "descripcion": "SI uso_ancho_banda=medio Y capacidad_servidor=media → riesgo_qos=medio",
        "antecedentes": [
            {"variable": "uso_ancho_banda",    "etiqueta": "medio"},
            {"variable": "capacidad_servidor", "etiqueta": "media"},
        ],
        "consecuente": {"variable": "riesgo_qos", "etiqueta": "medio"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R10",
        "descripcion": "SI usuarios_concurrentes=alto Y capacidad_servidor=alta → riesgo_qos=alto",
        "antecedentes": [
            {"variable": "usuarios_concurrentes", "etiqueta": "alto"},
            {"variable": "capacidad_servidor",    "etiqueta": "alta"},
        ],
        "consecuente": {"variable": "riesgo_qos", "etiqueta": "alto"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R11",
        "descripcion": "SI uso_ancho_banda=alto Y capacidad_servidor=media → riesgo_qos=medio",
        "antecedentes": [
            {"variable": "uso_ancho_banda",    "etiqueta": "alto"},
            {"variable": "capacidad_servidor", "etiqueta": "media"},
        ],
        "consecuente": {"variable": "riesgo_qos", "etiqueta": "medio"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R12",
        "descripcion": "SI latencia_red=alta Y usuarios_concurrentes=medio → riesgo_qos=medio",
        "antecedentes": [
            {"variable": "latencia_red",          "etiqueta": "alta"},
            {"variable": "usuarios_concurrentes", "etiqueta": "medio"},
        ],
        "consecuente": {"variable": "riesgo_qos", "etiqueta": "medio"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
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
        """
        Inicializa el builder cargando el consenso Delphi.

        Parameters
        ----------
        consenso_path : str
            Ruta al archivo delphi_consenso.json.
        data_dir : str
            Directorio de datos de salida.
        docs_dir : str
            Directorio de documentación de salida.

        Raises
        ------
        FileNotFoundError
            Si consenso_path no existe.
        ValueError
            Si las variables aprobadas no coinciden con las variables esperadas.
        """
        if not os.path.exists(consenso_path):
            raise FileNotFoundError(
                f"No se encontró el archivo de consenso Delphi: '{consenso_path}'. "
                "Ejecute primero el proceso Delphi para generar este archivo."
            )

        with open(consenso_path, encoding="utf-8") as f:
            self._consenso = json.load(f)

        # Verificar que las variables aprobadas coinciden con las esperadas
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

        # Atributos que se populan en build()
        self._antecedentes: dict[str, ctrl.Antecedent] = {}
        self._consecuente: ctrl.Consequent | None = None
        self._rules: list[ctrl.Rule] = []
        self._control_system: ctrl.ControlSystem | None = None
        self._built: bool = False

    # ------------------------------------------------------------------
    # Interfaz pública
    # ------------------------------------------------------------------

    def build(self) -> None:
        """
        Orquesta la construcción completa del sistema difuso:
        funciones de pertenencia → reglas → persistencia → gráficas.
        """
        self._build_membership_functions()
        self._build_rules()
        self._persist_variables()
        self._persist_rules()
        self._plot_membership_functions()
        self._built = True

    def evaluar_riesgo(self, valores_entrada: dict) -> float:
        """
        Evalúa el riesgo QoS dado un conjunto de valores de entrada.

        Parameters
        ----------
        valores_entrada : dict
            Diccionario con claves = nombres de variables de entrada y
            valores = valores numéricos.

        Returns
        -------
        float
            Valor de riesgo_qos en [0.0, 100.0].
        """
        if not self._built:
            raise RuntimeError(
                "El sistema difuso no ha sido construido. Llame a build() primero."
            )

        # Recortar valores fuera del universo
        valores_recortados: dict[str, float] = {}
        for var_name, valor in valores_entrada.items():
            if var_name not in UNIVERSES:
                continue
            lo, hi, _ = UNIVERSES[var_name]
            valor_float = float(np.clip(float(valor), lo, hi))
            valores_recortados[var_name] = valor_float

        # Ejecutar simulación
        try:
            sim = ctrl.ControlSystemSimulation(self._control_system)
            for var_name, valor in valores_recortados.items():
                if var_name != "riesgo_qos":
                    sim.input[var_name] = valor
            sim.compute()
            if "riesgo_qos" not in sim.output:
                # No rules fired — compute centroid manually from partial activations
                return self._fallback_centroid(valores_recortados)
            resultado = float(np.clip(sim.output["riesgo_qos"], 0.0, 100.0))
            return resultado
        except KeyError:
            # Output variable not activated — use manual centroid fallback
            return self._fallback_centroid(valores_recortados)
        except Exception as exc:
            logger.warning("Error en motor difuso: %s. Fallback=50.0", exc)
            return 50.0

    def _fallback_centroid(self, valores: dict) -> float:
        """
        Calcula el centroide manualmente cuando ninguna regla activa la salida.
        Evalúa el grado de pertenencia de cada variable a sus etiquetas y
        pondera las etiquetas de salida correspondientes.
        """
        lo, hi, step = UNIVERSES["riesgo_qos"]
        universe_out = np.arange(lo, hi + step, step)

        # Mapeo de etiquetas de entrada a etiquetas de salida
        # Basado en las reglas: bajo→bajo, medio→medio, alto→alto
        label_map = {
            "bajo": "bajo", "baja": "bajo",
            "medio": "medio", "media": "medio",
            "alto": "alto", "alta": "alto",
        }

        # Acumular activaciones por etiqueta de salida
        output_activations = {"bajo": 0.0, "medio": 0.0, "alto": 0.0}

        for var_name, valor in valores.items():
            if var_name == "riesgo_qos" or var_name not in UNIVERSES:
                continue
            lo_v, hi_v, step_v = UNIVERSES[var_name]
            universe_v = np.arange(lo_v, hi_v + step_v, step_v)
            for etiqueta, tipo, params in _MEMBERSHIP_DEFS[var_name]:
                if tipo == "triangular":
                    mf = fuzz.trimf(universe_v, params)
                elif tipo == "trapezoidal":
                    mf = fuzz.trapmf(universe_v, params)
                else:
                    continue
                activation = float(fuzz.interp_membership(universe_v, mf, valor))
                out_label = label_map.get(etiqueta, "medio")
                output_activations[out_label] = max(output_activations[out_label], activation)

        # Construir función de salida agregada
        aggregated = np.zeros_like(universe_out)
        for etiqueta, tipo, params in _MEMBERSHIP_DEFS["riesgo_qos"]:
            if tipo == "triangular":
                mf = fuzz.trimf(universe_out, params)
            elif tipo == "trapezoidal":
                mf = fuzz.trapmf(universe_out, params)
            else:
                continue
            activation = output_activations.get(etiqueta, 0.0)
            aggregated = np.fmax(aggregated, np.fmin(activation, mf))

        # Defuzzificar con centroide
        if aggregated.sum() == 0:
            return 50.0
        resultado = float(fuzz.defuzz(universe_out, aggregated, "centroid"))
        return float(np.clip(resultado, 0.0, 100.0))

    # ------------------------------------------------------------------
    # Métodos privados de construcción
    # ------------------------------------------------------------------

    def _build_membership_functions(self) -> None:
        """Construye antecedentes y consecuente con funciones de pertenencia."""
        input_vars = [v for v in UNIVERSES if v != "riesgo_qos"]

        for var_name in input_vars:
            lo, hi, step = UNIVERSES[var_name]
            universe = np.arange(lo, hi + step, step)
            antecedente = ctrl.Antecedent(universe, var_name)

            for etiqueta, tipo, params in _MEMBERSHIP_DEFS[var_name]:
                if tipo == "triangular":
                    antecedente[etiqueta] = fuzz.trimf(universe, params)
                elif tipo == "trapezoidal":
                    antecedente[etiqueta] = fuzz.trapmf(universe, params)
                else:
                    raise ValueError(
                        f"Tipo de función de pertenencia no soportado: '{tipo}' "
                        f"para variable '{var_name}', etiqueta '{etiqueta}'."
                    )

            self._antecedentes[var_name] = antecedente

        # Consecuente: riesgo_qos
        lo, hi, step = UNIVERSES["riesgo_qos"]
        universe_riesgo = np.arange(lo, hi + step, step)
        self._consecuente = ctrl.Consequent(
            universe_riesgo, "riesgo_qos", defuzzify_method="centroid"
        )

        for etiqueta, tipo, params in _MEMBERSHIP_DEFS["riesgo_qos"]:
            if tipo == "triangular":
                self._consecuente[etiqueta] = fuzz.trimf(universe_riesgo, params)
            elif tipo == "trapezoidal":
                self._consecuente[etiqueta] = fuzz.trapmf(universe_riesgo, params)
            else:
                raise ValueError(
                    f"Tipo de función de pertenencia no soportado: '{tipo}' "
                    f"para variable 'riesgo_qos', etiqueta '{etiqueta}'."
                )

    def _build_rules(self) -> None:
        """Construye las 12 reglas Mamdani con skfuzzy.control."""
        self._rules = []

        for rule_def in _RULES_DEF:
            antecedentes = rule_def["antecedentes"]
            consecuente_def = rule_def["consecuente"]

            # Construir antecedente compuesto (AND)
            ant_terms = []
            for ant in antecedentes:
                var_name = ant["variable"]
                etiqueta = ant["etiqueta"]
                ant_terms.append(self._antecedentes[var_name][etiqueta])

            antecedente_compuesto = ant_terms[0]
            for term in ant_terms[1:]:
                antecedente_compuesto = antecedente_compuesto & term

            consecuente = self._consecuente[consecuente_def["etiqueta"]]
            rule = ctrl.Rule(antecedente_compuesto, consecuente, label=rule_def["id"])
            self._rules.append(rule)

        self._control_system = ctrl.ControlSystem(self._rules)

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------

    def _persist_variables(self) -> None:
        """Guarda data/fuzzy_variables.json."""
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
        """Guarda data/fuzzy_rules.json."""
        doc = {"reglas": _RULES_DEF}
        output_path = os.path.join(self._data_dir, "fuzzy_rules.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

    def _plot_membership_functions(self) -> None:
        """Genera una imagen PNG por variable en docs/fuzzy_membership_plots/."""
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
                if tipo == "triangular":
                    mf = fuzz.trimf(universe, params)
                elif tipo == "trapezoidal":
                    mf = fuzz.trapmf(universe, params)
                else:
                    continue
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
