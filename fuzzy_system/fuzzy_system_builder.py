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
matplotlib.use("Agg")  # backend no interactivo para entornos sin display
import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Universos de discurso
# ---------------------------------------------------------------------------

UNIVERSES: dict[str, tuple[float, float, float]] = {
    "promedio_academico": (0.0, 5.0, 0.01),
    "inasistencia":       (0.0, 100.0, 0.5),
    "horas_estudio":      (0.0, 30.0, 0.1),
    "motivacion_estres":  (0.0, 10.0, 0.1),
    "riesgo":             (0.0, 100.0, 0.5),
}

# ---------------------------------------------------------------------------
# Definición de funciones de pertenencia por variable
# ---------------------------------------------------------------------------

# Estructura: {variable: [(etiqueta, tipo, parámetros), ...]}
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
    "riesgo": [
        ("bajo",  "trapezoidal", [0.0, 0.0, 20.0, 40.0]),
        ("medio", "triangular",  [30.0, 50.0, 70.0]),
        ("alto",  "trapezoidal", [60.0, 80.0, 100.0, 100.0]),
    ],
}

# ---------------------------------------------------------------------------
# Definición de reglas Mamdani
# ---------------------------------------------------------------------------

# Cada regla: (id, descripción, [(var, etiqueta), ...], (var_salida, etiqueta), operador, origen)
_RULES_DEF: list[dict] = [
    {
        "id": "R01",
        "descripcion": "Si promedio_academico es bajo Y inasistencia es alta ENTONCES riesgo es alto",
        "antecedentes": [
            {"variable": "promedio_academico", "etiqueta": "bajo"},
            {"variable": "inasistencia",       "etiqueta": "alta"},
        ],
        "consecuente": {"variable": "riesgo", "etiqueta": "alto"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R02",
        "descripcion": "Si motivacion_estres es bajo Y horas_estudio es pocas ENTONCES riesgo es alto",
        "antecedentes": [
            {"variable": "motivacion_estres", "etiqueta": "bajo"},
            {"variable": "horas_estudio",     "etiqueta": "pocas"},
        ],
        "consecuente": {"variable": "riesgo", "etiqueta": "alto"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R03",
        "descripcion": "Si promedio_academico es bajo Y horas_estudio es pocas ENTONCES riesgo es alto",
        "antecedentes": [
            {"variable": "promedio_academico", "etiqueta": "bajo"},
            {"variable": "horas_estudio",      "etiqueta": "pocas"},
        ],
        "consecuente": {"variable": "riesgo", "etiqueta": "alto"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R04",
        "descripcion": "Si promedio_academico es alto Y inasistencia es baja ENTONCES riesgo es bajo",
        "antecedentes": [
            {"variable": "promedio_academico", "etiqueta": "alto"},
            {"variable": "inasistencia",       "etiqueta": "baja"},
        ],
        "consecuente": {"variable": "riesgo", "etiqueta": "bajo"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R05",
        "descripcion": "Si promedio_academico es alto Y horas_estudio es muchas ENTONCES riesgo es bajo",
        "antecedentes": [
            {"variable": "promedio_academico", "etiqueta": "alto"},
            {"variable": "horas_estudio",      "etiqueta": "muchas"},
        ],
        "consecuente": {"variable": "riesgo", "etiqueta": "bajo"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R06",
        "descripcion": "Si motivacion_estres es alto Y promedio_academico es alto ENTONCES riesgo es bajo",
        "antecedentes": [
            {"variable": "motivacion_estres",  "etiqueta": "alto"},
            {"variable": "promedio_academico", "etiqueta": "alto"},
        ],
        "consecuente": {"variable": "riesgo", "etiqueta": "bajo"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R07",
        "descripcion": "Si promedio_academico es medio Y inasistencia es media ENTONCES riesgo es medio",
        "antecedentes": [
            {"variable": "promedio_academico", "etiqueta": "medio"},
            {"variable": "inasistencia",       "etiqueta": "media"},
        ],
        "consecuente": {"variable": "riesgo", "etiqueta": "medio"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R08",
        "descripcion": "Si horas_estudio es moderadas Y motivacion_estres es medio ENTONCES riesgo es medio",
        "antecedentes": [
            {"variable": "horas_estudio",     "etiqueta": "moderadas"},
            {"variable": "motivacion_estres", "etiqueta": "medio"},
        ],
        "consecuente": {"variable": "riesgo", "etiqueta": "medio"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R09",
        "descripcion": "Si promedio_academico es bajo Y inasistencia es media ENTONCES riesgo es medio",
        "antecedentes": [
            {"variable": "promedio_academico", "etiqueta": "bajo"},
            {"variable": "inasistencia",       "etiqueta": "media"},
        ],
        "consecuente": {"variable": "riesgo", "etiqueta": "medio"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R10",
        "descripcion": "Si inasistencia es alta Y horas_estudio es pocas ENTONCES riesgo es alto",
        "antecedentes": [
            {"variable": "inasistencia",  "etiqueta": "alta"},
            {"variable": "horas_estudio", "etiqueta": "pocas"},
        ],
        "consecuente": {"variable": "riesgo", "etiqueta": "alto"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R11",
        "descripcion": "Si promedio_academico es medio Y horas_estudio es pocas ENTONCES riesgo es medio",
        "antecedentes": [
            {"variable": "promedio_academico", "etiqueta": "medio"},
            {"variable": "horas_estudio",      "etiqueta": "pocas"},
        ],
        "consecuente": {"variable": "riesgo", "etiqueta": "medio"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
    {
        "id": "R12",
        "descripcion": "Si motivacion_estres es bajo Y inasistencia es alta ENTONCES riesgo es alto",
        "antecedentes": [
            {"variable": "motivacion_estres", "etiqueta": "bajo"},
            {"variable": "inasistencia",      "etiqueta": "alta"},
        ],
        "consecuente": {"variable": "riesgo", "etiqueta": "alto"},
        "operador": "AND",
        "origen_delphi": "Consenso expertos E1, E2, E3, E4 — Ronda 3",
    },
]

# Variables de entrada esperadas (deben coincidir con Variables_Aprobadas del consenso)
_EXPECTED_INPUT_VARS: set[str] = {
    "promedio_academico",
    "inasistencia",
    "horas_estudio",
    "motivacion_estres",
}


# ---------------------------------------------------------------------------
# Clase principal
# ---------------------------------------------------------------------------

class FuzzySystemBuilder:
    """
    Construye el sistema de inferencia difuso Mamdani usando scikit-fuzzy.
    Lee las Variables_Aprobadas de data/delphi_consenso.json.
    Expone evaluar_riesgo() como interfaz pública para otros módulos.
    """

    UNIVERSES = UNIVERSES

    def __init__(
        self,
        consenso_path: str = "data/delphi_consenso.json",
        data_dir: str = "data/",
        docs_dir: str = "docs/",
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
        self._simulation: ctrl.ControlSystemSimulation | None = None
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
        Evalúa el riesgo dado un conjunto de valores de entrada.

        Parameters
        ----------
        valores_entrada : dict
            Diccionario con claves = nombres de variables de entrada y
            valores = valores numéricos.

        Returns
        -------
        float
            Valor de riesgo en [0.0, 100.0].
        """
        if not self._built:
            raise RuntimeError(
                "El sistema difuso no ha sido construido. Llame a build() primero."
            )

        # Recortar valores fuera del universo y registrar advertencias
        valores_recortados: dict[str, float] = {}
        for var_name, valor in valores_entrada.items():
            if var_name not in UNIVERSES:
                continue
            lo, hi, _ = UNIVERSES[var_name]
            valor_float = float(valor)
            if valor_float < lo:
                self._log_warning(
                    f"Valor {valor_float} de '{var_name}' recortado al límite inferior {lo}",
                    tipo="valor_fuera_universo",
                    variable=var_name,
                    valor_original=valor_float,
                    valor_recortado=lo,
                )
                valor_float = lo
            elif valor_float > hi:
                self._log_warning(
                    f"Valor {valor_float} de '{var_name}' recortado al límite superior {hi}",
                    tipo="valor_fuera_universo",
                    variable=var_name,
                    valor_original=valor_float,
                    valor_recortado=hi,
                )
                valor_float = hi
            valores_recortados[var_name] = valor_float

        # Ejecutar simulación
        try:
            sim = ctrl.ControlSystemSimulation(self._control_system)
            for var_name, valor in valores_recortados.items():
                sim.input[var_name] = valor
            sim.compute()
            resultado = float(sim.output["riesgo"])
            # Garantizar que el resultado esté en [0, 100]
            resultado = float(np.clip(resultado, 0.0, 100.0))
            return resultado
        except Exception as exc:
            self._log_warning(
                f"Error en el motor difuso: {exc}. Retornando valor de fallback 50.0",
                tipo="error_motor_difuso",
                variable="riesgo",
                valor_original=None,
                valor_recortado=50.0,
            )
            logger.warning("Error en motor difuso: %s. Fallback=50.0", exc)
            return 50.0

    # ------------------------------------------------------------------
    # Métodos privados de construcción
    # ------------------------------------------------------------------

    def _build_membership_functions(self) -> None:
        """Construye antecedentes y consecuente con funciones de pertenencia."""
        input_vars = [v for v in UNIVERSES if v != "riesgo"]

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

        # Consecuente: riesgo
        lo, hi, step = UNIVERSES["riesgo"]
        universe_riesgo = np.arange(lo, hi + step, step)
        self._consecuente = ctrl.Consequent(universe_riesgo, "riesgo", defuzzify_method="centroid")

        for etiqueta, tipo, params in _MEMBERSHIP_DEFS["riesgo"]:
            if tipo == "triangular":
                self._consecuente[etiqueta] = fuzz.trimf(universe_riesgo, params)
            elif tipo == "trapezoidal":
                self._consecuente[etiqueta] = fuzz.trapmf(universe_riesgo, params)
            else:
                raise ValueError(
                    f"Tipo de función de pertenencia no soportado: '{tipo}' "
                    f"para variable 'riesgo', etiqueta '{etiqueta}'."
                )

    def _build_rules(self) -> None:
        """Construye las reglas Mamdani con skfuzzy.control."""
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

            # Combinar con AND
            antecedente_compuesto = ant_terms[0]
            for term in ant_terms[1:]:
                antecedente_compuesto = antecedente_compuesto & term

            # Consecuente
            consecuente = self._consecuente[consecuente_def["etiqueta"]]

            rule = ctrl.Rule(antecedente_compuesto, consecuente, label=rule_def["id"])
            self._rules.append(rule)

        # Crear sistema de control y simulación
        self._control_system = ctrl.ControlSystem(self._rules)
        # La simulación se crea en evaluar_riesgo() para evitar estado compartido

    # ------------------------------------------------------------------
    # Métodos privados de persistencia
    # ------------------------------------------------------------------

    def _persist_variables(self) -> None:
        """Guarda data/fuzzy_variables.json con el esquema del diseño."""
        input_vars = [v for v in UNIVERSES if v != "riesgo"]

        variables_entrada = []
        for var_name in input_vars:
            lo, hi, step = UNIVERSES[var_name]
            etiquetas = []
            for etiqueta, tipo, params in _MEMBERSHIP_DEFS[var_name]:
                etiquetas.append({
                    "nombre": etiqueta,
                    "tipo": tipo,
                    "parametros": params,
                })
            variables_entrada.append({
                "nombre": var_name,
                "universo": [lo, hi],
                "step": step,
                "etiquetas": etiquetas,
                "origen_delphi": var_name,
            })

        # Variable de salida
        lo_r, hi_r, step_r = UNIVERSES["riesgo"]
        etiquetas_riesgo = []
        for etiqueta, tipo, params in _MEMBERSHIP_DEFS["riesgo"]:
            etiquetas_riesgo.append({
                "nombre": etiqueta,
                "tipo": tipo,
                "parametros": params,
            })

        doc = {
            "variables_entrada": variables_entrada,
            "variable_salida": {
                "nombre": "riesgo",
                "universo": [lo_r, hi_r],
                "step": step_r,
                "etiquetas": etiquetas_riesgo,
            },
        }

        output_path = os.path.join(self._data_dir, "fuzzy_variables.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

    def _persist_rules(self) -> None:
        """Guarda data/fuzzy_rules.json con el esquema del diseño."""
        doc = {"reglas": _RULES_DEF}
        output_path = os.path.join(self._data_dir, "fuzzy_rules.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

    def _plot_membership_functions(self) -> None:
        """Genera una imagen PNG por variable en docs/fuzzy_membership_plots/."""
        plots_dir = os.path.join(self._docs_dir, "fuzzy_membership_plots")
        os.makedirs(plots_dir, exist_ok=True)

        all_vars = list(UNIVERSES.keys())

        for var_name in all_vars:
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

            ax.set_title(f"Funciones de pertenencia — {var_name}", fontsize=13)
            ax.set_xlabel(var_name)
            ax.set_ylabel("Grado de pertenencia")
            ax.set_ylim(-0.05, 1.1)
            ax.legend(loc="upper right")
            ax.grid(True, alpha=0.3)

            plot_path = os.path.join(plots_dir, f"{var_name}.png")
            plt.tight_layout()
            plt.savefig(plot_path, dpi=100)
            plt.close(fig)

    # ------------------------------------------------------------------
    # Advertencias
    # ------------------------------------------------------------------

    def _log_warning(
        self,
        message: str,
        tipo: str = "general",
        variable: str | None = None,
        valor_original: float | None = None,
        valor_recortado: float | None = None,
    ) -> None:
        """Acumula advertencias en data/fuzzy_warnings.json con timestamp."""
        warnings_path = os.path.join(self._data_dir, "fuzzy_warnings.json")

        # Cargar advertencias existentes
        if os.path.exists(warnings_path):
            try:
                with open(warnings_path, encoding="utf-8") as f:
                    doc = json.load(f)
            except (json.JSONDecodeError, OSError):
                doc = {"warnings": []}
        else:
            doc = {"warnings": []}

        entry: dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tipo": tipo,
            "mensaje": message,
        }
        if variable is not None:
            entry["variable"] = variable
        if valor_original is not None:
            entry["valor_original"] = valor_original
        if valor_recortado is not None:
            entry["valor_recortado"] = valor_recortado

        doc["warnings"].append(entry)

        with open(warnings_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
