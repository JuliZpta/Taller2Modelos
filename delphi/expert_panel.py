"""
Módulo: delphi/expert_panel.py
Panel de expertos simulados de la Institución Universitaria Pascual Bravo.

Define la dataclass Expert y la clase ExpertPanel que gestiona los 4 expertos
simulados y genera respuestas Likert contextualizadas por perfil.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# ---------------------------------------------------------------------------
# Dataclass Expert
# ---------------------------------------------------------------------------

@dataclass
class Expert:
    """Representa un experto simulado del panel Delphi de la Pascual Bravo."""

    id: str           # identificador único, e.g. "E1"
    nombre: str       # nombre ficticio
    cargo: str        # cargo específico en la Pascual Bravo
    dependencia: str  # dependencia institucional
    perfil: str       # "docente" | "coordinador" | "psicologo" | "directivo"
    sesgo_base: float # puntuación base Likert (3.5–5.0) según perfil


# ---------------------------------------------------------------------------
# Justificaciones textuales por perfil y factor
# ---------------------------------------------------------------------------

# Estructura: _JUSTIFICACIONES[perfil][factor] -> str
# Cada perfil tiene al menos 2 justificaciones específicas y una genérica ("_default").

_JUSTIFICACIONES: dict[str, dict[str, str]] = {
    "docente": {
        "promedio_academico": (
            "En mis cursos de Ingeniería de Sistemas en la Pascual Bravo, "
            "el promedio académico es el indicador más directo del rendimiento "
            "estudiantil. Los estudiantes con promedios por debajo de 3.5 "
            "presentan dificultades acumuladas que raramente se revierten sin "
            "intervención temprana."
        ),
        "inasistencia": (
            "He observado que los estudiantes con alta inasistencia en la "
            "Facultad de Ingeniería presentan dificultades para recuperar "
            "contenidos técnicos acumulativos. Una inasistencia superior al "
            "20 % suele correlacionar con bajo rendimiento al final del semestre."
        ),
        "horas_estudio": (
            "En la Facultad de Ingeniería, las asignaturas de programación y "
            "matemáticas requieren práctica autónoma constante. Los estudiantes "
            "que dedican menos de 8 horas semanales fuera del aula muestran "
            "rezagos significativos en evaluaciones parciales."
        ),
        "motivacion_estres": (
            "He notado que el estrés académico en semestres con alta carga "
            "de proyectos afecta directamente la calidad del trabajo entregado. "
            "Un nivel de motivación bajo al inicio del semestre es señal de "
            "alerta que suelo reportar a Bienestar Universitario."
        ),
        "_default": (
            "Desde mi experiencia docente en la Facultad de Ingeniería de la "
            "Pascual Bravo, este factor tiene una influencia relevante en el "
            "desempeño académico de los estudiantes de pregrado."
        ),
    },
    "coordinador": {
        "promedio_academico": (
            "Desde la Vicerrectoría Académica, el promedio es el criterio "
            "principal para activar alertas tempranas en el sistema de "
            "seguimiento estudiantil de la Pascual Bravo. Un promedio inferior "
            "a 3.0 activa automáticamente el protocolo de acompañamiento."
        ),
        "inasistencia": (
            "Los reportes de inasistencia que recibimos en la Vicerrectoría "
            "Académica muestran que el ausentismo reiterado precede en la "
            "mayoría de los casos a la deserción o a la pérdida de materias "
            "en el semestre en curso."
        ),
        "horas_estudio": (
            "Las encuestas de caracterización estudiantil aplicadas en la "
            "Pascual Bravo revelan que las horas de estudio autónomo son un "
            "predictor consistente del rendimiento, especialmente en programas "
            "con alta carga teórica."
        ),
        "motivacion_estres": (
            "Desde la coordinación académica hemos identificado que los "
            "períodos de mayor estrés —parciales y entregas de proyectos— "
            "coinciden con los picos de solicitudes de cancelación de materias "
            "y de asesorías académicas."
        ),
        "_default": (
            "Desde la Vicerrectoría Académica de la Pascual Bravo, este factor "
            "es considerado relevante en los procesos de seguimiento y "
            "acompañamiento estudiantil que coordinamos institucionalmente."
        ),
    },
    "psicologo": {
        "promedio_academico": (
            "En Bienestar Universitario observamos que los estudiantes con "
            "promedios bajos frecuentemente presentan síntomas de ansiedad y "
            "baja autoeficacia académica. El promedio actúa como indicador "
            "proxy de bienestar psicológico en muchos casos."
        ),
        "inasistencia": (
            "Desde Bienestar Universitario, la inasistencia reiterada suele "
            "ser una señal de alerta de problemas emocionales, familiares o "
            "económicos subyacentes. Atendemos estudiantes que dejan de asistir "
            "antes de solicitar ayuda formal."
        ),
        "horas_estudio": (
            "En las sesiones de orientación psicológica identificamos que los "
            "estudiantes con pocas horas de estudio frecuentemente reportan "
            "dificultades de concentración, procrastinación o situaciones "
            "personales que interfieren con su rutina académica."
        ),
        "motivacion_estres": (
            "En Bienestar Universitario atendemos estudiantes con altos niveles "
            "de estrés que correlacionan directamente con bajo rendimiento. "
            "La motivación intrínseca es el factor protector más importante "
            "que identificamos en los estudiantes resilientes de la Pascual Bravo."
        ),
        "_default": (
            "Desde Bienestar Universitario de la Pascual Bravo, este factor "
            "tiene implicaciones directas en la salud mental y el bienestar "
            "de los estudiantes que acompañamos en procesos de orientación."
        ),
    },
    "directivo": {
        "promedio_academico": (
            "Los datos institucionales de la Pascual Bravo confirman que el "
            "promedio académico es el indicador con mayor poder predictivo "
            "de permanencia y graduación oportuna en todos los programas "
            "de pregrado."
        ),
        "inasistencia": (
            "Desde la Dirección de Currículo hemos analizado que la inasistencia "
            "acumulada impacta negativamente los indicadores de calidad "
            "institucional, especialmente en los procesos de acreditación "
            "que adelanta la Pascual Bravo."
        ),
        "horas_estudio": (
            "Los datos institucionales de la Pascual Bravo muestran que las "
            "horas de estudio autónomo son un predictor clave del rendimiento "
            "académico. Los programas con mayor carga de trabajo independiente "
            "presentan mejores indicadores de aprendizaje profundo."
        ),
        "motivacion_estres": (
            "Desde la Dirección de Currículo reconocemos que el diseño "
            "curricular debe considerar la carga cognitiva y emocional de los "
            "estudiantes. Un alto nivel de estrés sostenido compromete los "
            "resultados de aprendizaje esperados en el perfil de egreso."
        ),
        "_default": (
            "Desde la Dirección de Currículo de la Pascual Bravo, este factor "
            "es relevante para el diseño y la evaluación de los programas "
            "académicos en el marco de los procesos de mejora continua."
        ),
    },
}


def _get_justificacion(perfil: str, factor: str) -> str:
    """Retorna la justificación textual para un perfil y factor dados."""
    perfil_dict = _JUSTIFICACIONES.get(perfil, {})
    return perfil_dict.get(factor, perfil_dict.get("_default", (
        "Este factor es relevante para el rendimiento académico estudiantil "
        "en el contexto de la Institución Universitaria Pascual Bravo."
    )))


# ---------------------------------------------------------------------------
# Clase ExpertPanel
# ---------------------------------------------------------------------------

class ExpertPanel:
    """
    Define y gestiona el panel de 4 expertos simulados de la Pascual Bravo.

    Los perfiles cubren: docente universitario, coordinador académico,
    psicólogo de bienestar estudiantil y directivo académico.
    """

    def __init__(self, seed: int = 42) -> None:
        """
        Inicializa el panel con una semilla numpy para reproducibilidad.

        Parameters
        ----------
        seed : int
            Semilla para numpy.random (default 42).
        """
        self._rng = np.random.default_rng(seed)

        self._experts: list[Expert] = [
            Expert(
                id="E1",
                nombre="Dr. Carlos Restrepo",
                cargo="Docente de Ingeniería de Sistemas",
                dependencia="Facultad de Ingeniería",
                perfil="docente",
                sesgo_base=4.5,
            ),
            Expert(
                id="E2",
                nombre="Mg. Adriana Gómez",
                cargo="Coordinadora Académica",
                dependencia="Vicerrectoría Académica",
                perfil="coordinador",
                sesgo_base=4.2,
            ),
            Expert(
                id="E3",
                nombre="Ps. Juliana Martínez",
                cargo="Psicóloga de Bienestar Estudiantil",
                dependencia="Bienestar Universitario",
                perfil="psicologo",
                sesgo_base=4.0,
            ),
            Expert(
                id="E4",
                nombre="Dr. Hernán Ospina",
                cargo="Director de Currículo",
                dependencia="Vicerrectoría Académica",
                perfil="directivo",
                sesgo_base=4.3,
            ),
        ]

    # ------------------------------------------------------------------
    # Interfaz pública
    # ------------------------------------------------------------------

    def get_experts(self) -> list[Expert]:
        """Retorna la lista de expertos del panel."""
        return list(self._experts)

    def generate_likert_response(
        self,
        expert: Expert,
        factor: str,
        round_num: int,
        previous_score: float | None = None,
        group_mean: float | None = None,
    ) -> tuple[int, str]:
        """
        Genera una puntuación Likert (1–5) y justificación textual coherente
        con el perfil del experto y el contexto institucional.

        Ronda 1
        -------
        Puntuación basada en ``sesgo_base`` del experto con variación
        aleatoria ±0.5, redondeada a entero y recortada a [1, 5].

        Ronda 2
        -------
        Ajusta ``previous_score`` un paso hacia ``group_mean`` con variación
        aleatoria ±0–1, manteniendo resultado en [1, 5].

        Ronda 3
        -------
        Puntuación final similar a ronda 2 pero con menor variación (±0.3).

        Parameters
        ----------
        expert : Expert
            Experto que emite la respuesta.
        factor : str
            Factor candidato evaluado (e.g. "promedio_academico").
        round_num : int
            Número de ronda (1, 2 o 3).
        previous_score : float | None
            Puntuación de la ronda anterior (requerida en rondas 2 y 3).
        group_mean : float | None
            Media grupal de la ronda anterior (requerida en rondas 2 y 3).

        Returns
        -------
        tuple[int, str]
            (puntuacion, justificacion) donde puntuacion ∈ [1, 5].
        """
        if round_num == 1:
            raw = expert.sesgo_base + self._rng.uniform(-0.5, 0.5)
        elif round_num == 2:
            if previous_score is None or group_mean is None:
                raise ValueError(
                    "previous_score y group_mean son requeridos en ronda 2."
                )
            # Mover un paso hacia la media grupal
            direction = np.sign(group_mean - previous_score)
            step = direction * self._rng.uniform(0.0, 1.0)
            raw = previous_score + step + self._rng.uniform(-0.5, 0.5)
        else:
            # Ronda 3: similar a ronda 2 pero con menor variación (±0.3)
            if previous_score is None or group_mean is None:
                raise ValueError(
                    "previous_score y group_mean son requeridos en ronda 3."
                )
            direction = np.sign(group_mean - previous_score)
            step = direction * self._rng.uniform(0.0, 0.5)
            raw = previous_score + step + self._rng.uniform(-0.3, 0.3)

        puntuacion = int(np.clip(round(raw), 1, 5))
        justificacion = _get_justificacion(expert.perfil, factor)

        return puntuacion, justificacion
