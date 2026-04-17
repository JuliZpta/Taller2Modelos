"""
Módulo: delphi/delphi_simulator.py
Simulador del proceso Delphi de tres rondas para la validación de factores
de riesgo de bajo rendimiento académico.

Institución Universitaria Pascual Bravo · Medellín, Colombia
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from delphi.expert_panel import Expert, ExpertPanel


class DelphiSimulator:
    """
    Ejecuta el proceso Delphi de tres rondas sobre los factores candidatos.
    Persiste resultados en data/ y genera el informe en docs/.
    """

    FACTORS: list[str] = [
        "promedio_academico",
        "inasistencia",
        "horas_estudio",
        "motivacion_estres",
    ]

    CONSENSUS_CRITERIA: dict = {
        "min_mean": 4.0,
        "max_cv": 0.30,
        "min_approval_pct": 70.0,  # % de expertos con puntuación >= 4
    }

    def __init__(
        self,
        panel: ExpertPanel,
        data_dir: str = "data/",
        docs_dir: str = "docs/",
    ) -> None:
        """
        Inicializa el simulador con el panel de expertos y los directorios de salida.

        Parameters
        ----------
        panel : ExpertPanel
            Panel de expertos simulados.
        data_dir : str
            Directorio donde se persisten los JSON de resultados.
        docs_dir : str
            Directorio donde se genera el informe Markdown.
        """
        self._panel = panel
        self._data_dir = data_dir
        self._docs_dir = docs_dir
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(docs_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Métodos auxiliares privados
    # ------------------------------------------------------------------

    def _calculate_stats(self, scores: list[float]) -> dict:
        """
        Calcula media, desviación estándar y coeficiente de variación.

        Parameters
        ----------
        scores : list[float]
            Lista de puntuaciones Likert.

        Returns
        -------
        dict
            {"mean": float, "std": float, "cv": float}
        """
        n = len(scores)
        mean = sum(scores) / n
        variance = sum((s - mean) ** 2 for s in scores) / n
        std = variance ** 0.5
        cv = std / mean if mean != 0 else 0.0
        return {"mean": mean, "std": std, "cv": cv}

    def _evaluate_consensus(self, stats: dict, scores: list[float]) -> dict:
        """
        Evalúa los tres criterios de consenso Delphi.

        Parameters
        ----------
        stats : dict
            Estadísticos calculados por _calculate_stats().
        scores : list[float]
            Lista de puntuaciones Likert de la ronda.

        Returns
        -------
        dict
            {
              "approved": bool,
              "criteria": {
                "mean_ok": bool,
                "cv_ok": bool,
                "approval_ok": bool,
                "approval_pct": float
              },
              "criterio_fallido": str | None
            }
        """
        mean_ok = stats["mean"] >= self.CONSENSUS_CRITERIA["min_mean"]
        cv_ok = stats["cv"] <= self.CONSENSUS_CRITERIA["max_cv"]
        approval_count = sum(1 for s in scores if s >= 4)
        approval_pct = (approval_count / len(scores)) * 100.0
        approval_ok = approval_pct >= self.CONSENSUS_CRITERIA["min_approval_pct"]

        approved = mean_ok and cv_ok and approval_ok

        criterio_fallido: str | None = None
        if not approved:
            if not mean_ok:
                criterio_fallido = "mean_ok"
            elif not cv_ok:
                criterio_fallido = "cv_ok"
            else:
                criterio_fallido = "approval_ok"

        return {
            "approved": approved,
            "criteria": {
                "mean_ok": mean_ok,
                "cv_ok": cv_ok,
                "approval_ok": approval_ok,
                "approval_pct": round(approval_pct, 2),
            },
            "criterio_fallido": criterio_fallido,
        }

    # ------------------------------------------------------------------
    # Rondas Delphi
    # ------------------------------------------------------------------

    def run_round1(self) -> dict:
        """
        Genera respuestas Likert iniciales para cada experto × factor.
        Calcula media, std y CV por factor.
        Persiste en data/delphi_ronda1.json.

        Returns
        -------
        dict
            Diccionario de resultados de la ronda 1.
        """
        experts = self._panel.get_experts()
        factores_data = []

        for factor in self.FACTORS:
            respuestas = []
            scores: list[float] = []

            for expert in experts:
                puntuacion, justificacion = self._panel.generate_likert_response(
                    expert, factor, round_num=1
                )
                scores.append(float(puntuacion))
                respuestas.append(
                    {
                        "experto_id": expert.id,
                        "nombre": expert.nombre,
                        "cargo": expert.cargo,
                        "dependencia": expert.dependencia,
                        "puntuacion": puntuacion,
                        "puntuacion_anterior": None,
                        "justificacion": justificacion,
                    }
                )

            stats = self._calculate_stats(scores)
            factores_data.append(
                {
                    "factor": factor,
                    "respuestas": respuestas,
                    "estadisticos": {
                        "media": round(stats["mean"], 4),
                        "std": round(stats["std"], 4),
                        "cv": round(stats["cv"], 4),
                    },
                }
            )

        results = {
            "ronda": 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "factores": factores_data,
        }

        output_path = os.path.join(self._data_dir, "delphi_ronda1.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        return results

    def run_round2(self, round1_results: dict) -> dict:
        """
        Genera respuestas ajustadas hacia la media grupal de ronda 1.
        Incluye puntuacion_anterior en cada respuesta.
        Persiste en data/delphi_ronda2.json.

        Parameters
        ----------
        round1_results : dict
            Resultados de la ronda 1 (retornados por run_round1()).

        Returns
        -------
        dict
            Diccionario de resultados de la ronda 2.
        """
        experts = self._panel.get_experts()
        # Indexar expertos por id para acceso rápido
        experts_by_id = {e.id: e for e in experts}

        factores_data = []

        for factor_data in round1_results["factores"]:
            factor = factor_data["factor"]
            group_mean = factor_data["estadisticos"]["media"]

            # Construir mapa de puntuaciones anteriores por experto
            prev_scores_by_id = {
                r["experto_id"]: r["puntuacion"] for r in factor_data["respuestas"]
            }

            respuestas = []
            scores: list[float] = []

            for expert in experts:
                previous_score = float(prev_scores_by_id[expert.id])
                puntuacion, justificacion = self._panel.generate_likert_response(
                    expert,
                    factor,
                    round_num=2,
                    previous_score=previous_score,
                    group_mean=group_mean,
                )
                scores.append(float(puntuacion))
                respuestas.append(
                    {
                        "experto_id": expert.id,
                        "nombre": expert.nombre,
                        "cargo": expert.cargo,
                        "dependencia": expert.dependencia,
                        "puntuacion": puntuacion,
                        "puntuacion_anterior": int(previous_score),
                        "justificacion": justificacion,
                    }
                )

            stats = self._calculate_stats(scores)
            factores_data.append(
                {
                    "factor": factor,
                    "respuestas": respuestas,
                    "estadisticos": {
                        "media": round(stats["mean"], 4),
                        "std": round(stats["std"], 4),
                        "cv": round(stats["cv"], 4),
                    },
                }
            )

        results = {
            "ronda": 2,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "factores": factores_data,
        }

        output_path = os.path.join(self._data_dir, "delphi_ronda2.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        return results

    def run_round3(self, round2_results: dict) -> dict:
        """
        Genera validación final. Evalúa criterios de consenso por factor.
        Persiste en data/delphi_consenso.json y genera docs/delphi_informe.md.

        Parameters
        ----------
        round2_results : dict
            Resultados de la ronda 2 (retornados por run_round2()).

        Returns
        -------
        dict
            Diccionario de consenso con variables_aprobadas y variables_rechazadas.
        """
        experts = self._panel.get_experts()
        factores_data = []

        for factor_data in round2_results["factores"]:
            factor = factor_data["factor"]
            group_mean = factor_data["estadisticos"]["media"]

            prev_scores_by_id = {
                r["experto_id"]: r["puntuacion"] for r in factor_data["respuestas"]
            }

            respuestas = []
            scores: list[float] = []

            for expert in experts:
                previous_score = float(prev_scores_by_id[expert.id])
                puntuacion, justificacion = self._panel.generate_likert_response(
                    expert,
                    factor,
                    round_num=3,
                    previous_score=previous_score,
                    group_mean=group_mean,
                )
                scores.append(float(puntuacion))
                respuestas.append(
                    {
                        "experto_id": expert.id,
                        "nombre": expert.nombre,
                        "cargo": expert.cargo,
                        "dependencia": expert.dependencia,
                        "puntuacion": puntuacion,
                        "puntuacion_anterior": int(previous_score),
                        "justificacion": justificacion,
                    }
                )

            stats = self._calculate_stats(scores)
            consensus_eval = self._evaluate_consensus(stats, scores)

            factores_data.append(
                {
                    "factor": factor,
                    "respuestas": respuestas,
                    "estadisticos": {
                        "media": round(stats["mean"], 4),
                        "std": round(stats["std"], 4),
                        "cv": round(stats["cv"], 4),
                    },
                    "consenso": consensus_eval,
                }
            )

        # Separar variables aprobadas y rechazadas
        variables_aprobadas = []
        variables_rechazadas = []

        for fd in factores_data:
            stats = fd["estadisticos"]
            consensus = fd["consenso"]
            entry = {
                "factor": fd["factor"],
                "estadisticos_finales": {
                    "media": stats["media"],
                    "std": stats["std"],
                    "cv": stats["cv"],
                },
                "criterios": consensus["criteria"],
                "aprobado": consensus["approved"],
                "criterio_fallido": consensus["criterio_fallido"],
            }
            if consensus["approved"]:
                variables_aprobadas.append(entry)
            else:
                variables_rechazadas.append(entry)

        consensus_doc = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "variables_aprobadas": variables_aprobadas,
            "variables_rechazadas": variables_rechazadas,
        }

        output_path = os.path.join(self._data_dir, "delphi_consenso.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(consensus_doc, f, ensure_ascii=False, indent=2)

        # Construir all_rounds para el informe
        # Necesitamos los datos de ronda 1 y 2 también; los recuperamos del archivo si existen
        all_rounds = {
            "ronda3_factores": factores_data,
        }
        # Intentar cargar rondas anteriores para el informe completo
        try:
            with open(os.path.join(self._data_dir, "delphi_ronda1.json"), encoding="utf-8") as f:
                all_rounds["ronda1"] = json.load(f)
        except FileNotFoundError:
            all_rounds["ronda1"] = None

        try:
            with open(os.path.join(self._data_dir, "delphi_ronda2.json"), encoding="utf-8") as f:
                all_rounds["ronda2"] = json.load(f)
        except FileNotFoundError:
            all_rounds["ronda2"] = None

        self._generate_report(all_rounds, consensus_doc)

        return consensus_doc

    # ------------------------------------------------------------------
    # Generación del informe
    # ------------------------------------------------------------------

    def _generate_report(self, all_rounds: dict, consensus: dict) -> None:
        """
        Genera docs/delphi_informe.md con narrativa metodológica completa.

        Parameters
        ----------
        all_rounds : dict
            Datos de las tres rondas.
        consensus : dict
            Documento de consenso final.
        """
        experts = self._panel.get_experts()
        lines: list[str] = []

        # ---- Encabezado ----
        lines.append("# Informe del Proceso Delphi — Riesgo de Bajo Rendimiento Académico")
        lines.append("")
        lines.append("## Institución Universitaria Pascual Bravo, Medellín")
        lines.append("")
        lines.append(f"**Fecha de generación:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
        lines.append("")

        # ---- Descripción metodológica ----
        lines.append("---")
        lines.append("")
        lines.append("## 1. Descripción Metodológica del Proceso Delphi")
        lines.append("")
        lines.append(
            "El método Delphi es una técnica de consulta estructurada a expertos que busca "
            "alcanzar consenso sobre un tema mediante rondas iterativas de retroalimentación. "
            "En este estudio se aplicaron **tres rondas** para validar los factores candidatos "
            "de riesgo de bajo rendimiento académico en la Institución Universitaria Pascual Bravo."
        )
        lines.append("")
        lines.append(
            "**Ronda 1 — Evaluación inicial:** Cada experto asignó una puntuación Likert (1–5) "
            "a cada factor candidato de forma independiente, sin conocer las respuestas de los demás. "
            "Se calcularon la media, la desviación estándar y el coeficiente de variación (CV) por factor."
        )
        lines.append("")
        lines.append(
            "**Ronda 2 — Retroalimentación y ajuste:** Los expertos recibieron la media grupal de "
            "la ronda anterior y tuvieron la oportunidad de revisar y ajustar sus puntuaciones. "
            "Este proceso favorece la convergencia hacia el consenso."
        )
        lines.append("")
        lines.append(
            "**Ronda 3 — Validación final:** Se realizó una última ronda de ajuste con menor "
            "variación permitida (±0.3). Al finalizar, se evaluaron los criterios de consenso "
            "para determinar qué factores son aprobados como variables del modelo."
        )
        lines.append("")
        lines.append("**Criterios de consenso aplicados:**")
        lines.append("")
        lines.append("| Criterio | Umbral |")
        lines.append("|---|---|")
        lines.append(f"| Media grupal | ≥ {self.CONSENSUS_CRITERIA['min_mean']} |")
        lines.append(f"| Coeficiente de variación (CV) | ≤ {self.CONSENSUS_CRITERIA['max_cv']} |")
        lines.append(f"| Porcentaje de aprobación (puntuación ≥ 4) | ≥ {self.CONSENSUS_CRITERIA['min_approval_pct']} % |")
        lines.append("")

        # ---- Perfiles del panel ----
        lines.append("---")
        lines.append("")
        lines.append("## 2. Perfiles del Panel de Expertos")
        lines.append("")
        lines.append(
            "El panel está conformado por cuatro expertos de la Institución Universitaria "
            "Pascual Bravo, con perfiles complementarios que cubren las dimensiones docente, "
            "administrativa, psicosocial y directiva."
        )
        lines.append("")
        lines.append("| ID | Nombre | Cargo | Dependencia |")
        lines.append("|---|---|---|---|")
        for expert in experts:
            lines.append(
                f"| {expert.id} | {expert.nombre} | {expert.cargo} | {expert.dependencia} |"
            )
        lines.append("")

        # ---- Resultados por ronda ----
        lines.append("---")
        lines.append("")
        lines.append("## 3. Resultados por Ronda")
        lines.append("")

        ronda_labels = {
            "ronda1": ("Ronda 1 — Evaluación Inicial", "delphi_ronda1.json"),
            "ronda2": ("Ronda 2 — Retroalimentación y Ajuste", "delphi_ronda2.json"),
        }

        for key, (label, _) in ronda_labels.items():
            ronda_data = all_rounds.get(key)
            if ronda_data is None:
                continue
            lines.append(f"### 3.{list(ronda_labels.keys()).index(key) + 1}. {label}")
            lines.append("")
            lines.append("| Factor | Media | Std | CV |")
            lines.append("|---|---|---|---|")
            for fd in ronda_data.get("factores", []):
                st = fd["estadisticos"]
                lines.append(
                    f"| {fd['factor']} | {st['media']:.4f} | {st['std']:.4f} | {st['cv']:.4f} |"
                )
            lines.append("")

        # Ronda 3
        lines.append("### 3.3. Ronda 3 — Validación Final")
        lines.append("")
        lines.append("| Factor | Media | Std | CV | Aprobado |")
        lines.append("|---|---|---|---|---|")
        for fd in all_rounds.get("ronda3_factores", []):
            st = fd["estadisticos"]
            aprobado = "✅ Sí" if fd["consenso"]["approved"] else "❌ No"
            lines.append(
                f"| {fd['factor']} | {st['media']:.4f} | {st['std']:.4f} | {st['cv']:.4f} | {aprobado} |"
            )
        lines.append("")

        # ---- Variables aprobadas ----
        lines.append("---")
        lines.append("")
        lines.append("## 4. Variables Aprobadas")
        lines.append("")

        aprobadas = consensus.get("variables_aprobadas", [])
        if aprobadas:
            lines.append(
                "Las siguientes variables alcanzaron consenso en las tres rondas y serán "
                "utilizadas como variables de entrada del sistema de inferencia difuso:"
            )
            lines.append("")
            lines.append("| Factor | Media | CV | % Aprobación | Resultado |")
            lines.append("|---|---|---|---|---|")
            for v in aprobadas:
                st = v["estadisticos_finales"]
                pct = v["criterios"]["approval_pct"]
                lines.append(
                    f"| {v['factor']} | {st['media']:.4f} | {st['cv']:.4f} | {pct:.1f} % | ✅ Aprobado |"
                )
            lines.append("")
        else:
            lines.append("*No se aprobaron variables en este proceso.*")
            lines.append("")

        # ---- Variables rechazadas ----
        lines.append("---")
        lines.append("")
        lines.append("## 5. Variables Rechazadas")
        lines.append("")

        rechazadas = consensus.get("variables_rechazadas", [])
        if rechazadas:
            lines.append(
                "Las siguientes variables no alcanzaron el umbral de consenso requerido:"
            )
            lines.append("")
            lines.append("| Factor | Media | CV | % Aprobación | Criterio Fallido |")
            lines.append("|---|---|---|---|---|")
            for v in rechazadas:
                st = v["estadisticos_finales"]
                pct = v["criterios"]["approval_pct"]
                criterio = v["criterio_fallido"] or "—"
                lines.append(
                    f"| {v['factor']} | {st['media']:.4f} | {st['cv']:.4f} | {pct:.1f} % | {criterio} |"
                )
            lines.append("")
        else:
            lines.append(
                "Todas las variables candidatas alcanzaron consenso. No hay variables rechazadas."
            )
            lines.append("")

        # ---- Conclusión metodológica ----
        lines.append("---")
        lines.append("")
        lines.append("## 6. Conclusión Metodológica")
        lines.append("")
        n_aprobadas = len(aprobadas)
        n_rechazadas = len(rechazadas)
        lines.append(
            f"El proceso Delphi de tres rondas permitió validar **{n_aprobadas} de "
            f"{n_aprobadas + n_rechazadas} factores candidatos** para el modelo de riesgo "
            "de bajo rendimiento académico en la Institución Universitaria Pascual Bravo."
        )
        lines.append("")
        if n_aprobadas > 0:
            factores_aprobados = ", ".join(f"`{v['factor']}`" for v in aprobadas)
            lines.append(
                f"Los factores aprobados — {factores_aprobados} — presentaron alta "
                "convergencia entre los expertos del panel, con medias superiores a 4.0, "
                "coeficientes de variación bajos (≤ 0.30) y porcentajes de aprobación "
                "superiores al 70 %. Estos factores constituyen la base del sistema de "
                "inferencia difuso Mamdani que se desarrolla en la siguiente etapa."
            )
        lines.append("")
        lines.append(
            "La metodología Delphi garantiza que las variables seleccionadas cuentan con "
            "respaldo experto institucional, lo que otorga validez de contenido al modelo "
            "y asegura la trazabilidad entre el juicio experto y las decisiones de diseño "
            "del sistema de evaluación de riesgo."
        )
        lines.append("")

        # Escribir el archivo
        report_path = os.path.join(self._docs_dir, "delphi_informe.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
