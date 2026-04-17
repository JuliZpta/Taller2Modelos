"""
trabajo_final/delphi/expert_panel.py
Panel de expertos simulados del sector tecnológico/streaming.

Define la dataclass Expert y la clase ExpertPanel que gestiona los 4 expertos
simulados y genera respuestas Likert contextualizadas por perfil.

Parte E — Simulación de Plataforma de Streaming
Taller 2 de Modelos y Simulación
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


# ---------------------------------------------------------------------------
# Dataclass Expert
# ---------------------------------------------------------------------------

@dataclass
class Expert:
    """Representa un experto simulado del panel Delphi del sector streaming."""

    id: str           # identificador único, e.g. "E1"
    nombre: str       # nombre del experto
    cargo: str        # cargo específico
    dependencia: str  # área o departamento
    perfil: str       # "arquitecto" | "analista_qos" | "investigador" | "especialista_ux"
    sesgo_base: float # puntuación base Likert (3.5–5.0) según perfil


# ---------------------------------------------------------------------------
# Justificaciones textuales por perfil y factor
# ---------------------------------------------------------------------------

_JUSTIFICACIONES: dict[str, dict[str, str]] = {
    "arquitecto": {
        "usuarios_concurrentes": (
            "En nuestra infraestructura cloud, el número de usuarios concurrentes "
            "es el principal driver de escalado. Superado el 70% de capacidad, "
            "activamos auto-scaling para evitar degradación del servicio y garantizar "
            "la disponibilidad de la plataforma de streaming."
        ),
        "uso_ancho_banda": (
            "El ancho de banda es el cuello de botella más frecuente en plataformas "
            "de streaming. Monitoreamos en tiempo real y aplicamos CDN cuando supera "
            "el 80% para distribuir la carga y mantener la calidad del servicio."
        ),
        "_default": (
            "Desde mi experiencia como arquitecto de infraestructura cloud, este "
            "factor tiene una influencia relevante en la estabilidad y escalabilidad "
            "de la plataforma de streaming bajo condiciones de alta demanda."
        ),
    },
    "analista_qos": {
        "latencia_red": (
            "La latencia es el indicador más sensible para el usuario final. "
            "Una latencia superior a 150ms genera buffering visible que impacta "
            "directamente la retención de usuarios y la percepción de calidad "
            "del servicio de streaming."
        ),
        "capacidad_servidor": (
            "El uso de CPU por encima del 85% correlaciona con timeouts y errores "
            "de transcodificación que degradan la calidad del stream. Monitoreamos "
            "este indicador como señal de alerta temprana en nuestros dashboards de QoS."
        ),
        "_default": (
            "Como analista de QoS y redes, este factor es un indicador clave en "
            "el monitoreo continuo de la calidad del servicio de streaming y "
            "la experiencia de usuario en condiciones de carga variable."
        ),
    },
    "investigador": {
        "usuarios_concurrentes": (
            "Los modelos de carga en sistemas distribuidos muestran comportamiento "
            "no lineal cuando la concurrencia supera el 75% de la capacidad nominal. "
            "Nuestras investigaciones en sistemas de streaming confirman este umbral "
            "crítico para la degradación del servicio."
        ),
        "uso_ancho_banda": (
            "La distribución del ancho de banda en plataformas de streaming sigue "
            "patrones de Pareto: el 20% de los usuarios consume el 80% del ancho "
            "de banda disponible. Este fenómeno debe modelarse con distribuciones "
            "asimétricas para capturar los picos de demanda."
        ),
        "_default": (
            "Desde la perspectiva de la investigación en sistemas distribuidos, "
            "este factor presenta comportamientos emergentes que son relevantes "
            "para modelar la degradación del servicio en plataformas de streaming "
            "bajo condiciones de alta concurrencia."
        ),
    },
    "especialista_ux": {
        "latencia_red": (
            "Los estudios de UX muestran que el usuario percibe degradación de "
            "calidad a partir de 100ms de latencia. Por encima de 200ms, la tasa "
            "de abandono aumenta un 40%, lo que tiene un impacto directo en la "
            "retención y satisfacción del usuario de la plataforma."
        ),
        "capacidad_servidor": (
            "Cuando el servidor supera el 90% de capacidad, los tiempos de respuesta "
            "se vuelven impredecibles y la experiencia del usuario se deteriora "
            "significativamente. Los usuarios perciben esto como 'lentitud' o "
            "'congelamiento' del contenido en streaming."
        ),
        "_default": (
            "Desde la perspectiva de la experiencia de usuario, este factor "
            "influye directamente en la percepción de calidad del servicio de "
            "streaming y en las métricas de satisfacción y retención de usuarios "
            "de la plataforma."
        ),
    },
}


def _get_justificacion(perfil: str, factor: str) -> str:
    """Retorna la justificación textual para un perfil y factor dados."""
    perfil_dict = _JUSTIFICACIONES.get(perfil, {})
    return perfil_dict.get(factor, perfil_dict.get("_default", (
        "Este factor es relevante para la calidad del servicio y el rendimiento "
        "de la plataforma de streaming bajo condiciones de alta demanda."
    )))


# ---------------------------------------------------------------------------
# Clase ExpertPanel
# ---------------------------------------------------------------------------

class ExpertPanel:
    """
    Define y gestiona el panel de 4 expertos simulados del sector streaming.

    Los perfiles cubren: arquitecto de infraestructura cloud, analista de QoS,
    investigador en sistemas distribuidos y especialista en UX.
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
                nombre="Ing. Santiago Vargas",
                cargo="Arquitecto de Infraestructura Cloud",
                dependencia="Área de Plataformas Digitales",
                perfil="arquitecto",
                sesgo_base=4.4,
            ),
            Expert(
                id="E2",
                nombre="Mg. Valentina Torres",
                cargo="Analista de QoS y Redes",
                dependencia="Área de Operaciones de Red",
                perfil="analista_qos",
                sesgo_base=4.2,
            ),
            Expert(
                id="E3",
                nombre="Dr. Felipe Morales",
                cargo="Investigador en Sistemas Distribuidos",
                dependencia="Departamento de I+D",
                perfil="investigador",
                sesgo_base=4.0,
            ),
            Expert(
                id="E4",
                nombre="Ing. Camila Ríos",
                cargo="Especialista en Experiencia de Usuario (UX)",
                dependencia="Área de Producto",
                perfil="especialista_ux",
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
        con el perfil del experto y el contexto de streaming.

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
            Factor candidato evaluado (e.g. "usuarios_concurrentes").
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
            direction = np.sign(group_mean - previous_score)
            step = direction * self._rng.uniform(0.0, 1.0)
            raw = previous_score + step + self._rng.uniform(-0.5, 0.5)
        else:
            # Ronda 3: menor variación (±0.3)
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
