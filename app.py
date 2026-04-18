"""
app.py — Taller 2: Modelos y Simulación
Aplicación Streamlit interactiva que integra todos los módulos del Taller 2.

Institución Universitaria Pascual Bravo · Medellín, Colombia
Integrantes: Julian Zapata · Juan José Orrego · 2026

Ejecutar con:
    streamlit run app.py
"""

from __future__ import annotations

import json
import os
import sys

import streamlit as st

# ---------------------------------------------------------------------------
# Configuración de página (debe ser la primera llamada a Streamlit)
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Taller 2 — Modelos y Simulación",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Importaciones opcionales de plotly / matplotlib
# ---------------------------------------------------------------------------

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# CSS personalizado
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #4fc3f7;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: #1a1a2e;
        border-left: 4px solid #4fc3f7;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }
    .conclusion-box {
        background: #0d3b1a;
        border-left: 4px solid #81c784;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }
    .warning-box {
        background: #3d0a0a;
        border-left: 4px solid #ef5350;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Inicializar session_state
# ---------------------------------------------------------------------------

_STATE_KEYS = {
    "delphi_done": False,
    "fuzzy_built": False,
    "montecarlo_done": False,
    "regression_done": False,
    "df_simulado": None,
    "delphi_r1": None,
    "delphi_r2": None,
    "delphi_r3": None,
    "mc_stats": None,
    "reg_metrics": None,
    "reg_importance": None,
    "reg_corr": None,
    # Streaming
    "st_delphi_done": False,
    "st_fuzzy_built": False,
    "st_montecarlo_done": False,
    "st_regression_done": False,
    "st_df_simulado": None,
    "st_delphi_r1": None,
    "st_delphi_r2": None,
    "st_delphi_r3": None,
    "st_mc_stats": None,
    "st_reg_metrics": None,
    "st_reg_importance": None,
    "st_reg_corr": None,
}

for key, default in _STATE_KEYS.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

st.sidebar.title(" Taller 2")
st.sidebar.markdown("**Modelos y Simulación**")
st.sidebar.markdown("I.U. Pascual Bravo · 2026")
st.sidebar.markdown("---")
st.sidebar.markdown("**Integrantes:**")
st.sidebar.markdown("Julian Zapata")
st.sidebar.markdown("Juan José Orrego")
st.sidebar.markdown("---")

if st.sidebar.button(" Limpiar caché"):
    st.cache_data.clear()
    st.cache_resource.clear()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.sidebar.success("Caché limpiado. Recarga la página.")
    st.rerun()

seccion = st.sidebar.radio("Navegación", [
    " Inicio",
    " Parte A — Delphi",
    " Parte B — Sistema Difuso",
    " Parte C — Montecarlo",
    " Parte D — Regresión",
    " Parte E — Streaming",
    " Conclusiones",
])

# ---------------------------------------------------------------------------
# Helpers de carga de módulos
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def run_delphi():
    """Ejecuta el proceso Delphi de 3 rondas (caso base académico)."""
    sys.path.insert(0, ".")
    from delphi import ExpertPanel, DelphiSimulator
    panel = ExpertPanel(seed=42)
    sim = DelphiSimulator(panel, data_dir="data/", docs_dir="docs/")
    r1 = sim.run_round1()
    r2 = sim.run_round2(r1)
    r3 = sim.run_round3(r2)
    return r1, r2, r3


@st.cache_resource(show_spinner=False)
def get_fuzzy_system():
    """Construye y retorna el sistema difuso académico."""
    from fuzzy_system import FuzzySystemBuilder
    fs = FuzzySystemBuilder(
        consenso_path="data/delphi_consenso.json",
        data_dir="data/",
        docs_dir="docs/",
    )
    fs.build()
    return fs


def run_montecarlo(n_sims: int, fuzzy_system):
    """Ejecuta la simulación Montecarlo sobre el sistema difuso académico."""
    from montecarlo import MontecarloSimulator
    mc = MontecarloSimulator(fuzzy_system, data_dir="data/", docs_dir="docs/", seed=42)
    df = mc.run(n_simulaciones=n_sims)
    return df, mc._statistics


def run_regression():
    """Entrena y evalúa los modelos de regresión para el caso académico."""
    from regression import RegressionAnalyzer
    ra = RegressionAnalyzer(
        data_path="data/base_simulada.csv",
        consenso_path="data/delphi_consenso.json",
        docs_dir="docs/",
    )
    metrics = ra.train_and_evaluate()
    importance = ra.get_feature_importance()
    corr = ra.calculate_pearson_correlation()
    return ra, metrics, importance, corr


# Streaming helpers

@st.cache_data(show_spinner=False)
def run_delphi_streaming():
    """Ejecuta el proceso Delphi de 3 rondas (caso streaming)."""
    from trabajo_final.delphi import ExpertPanel as ExpertPanelST, DelphiSimulator as DelphiSimulatorST
    panel = ExpertPanelST(seed=42)
    sim = DelphiSimulatorST(panel, data_dir="trabajo_final/data/", docs_dir="trabajo_final/docs/")
    r1 = sim.run_round1()
    r2 = sim.run_round2(r1)
    r3 = sim.run_round3(r2)
    return r1, r2, r3


@st.cache_resource(show_spinner=False)
def get_fuzzy_system_streaming():
    """Construye y retorna el sistema difuso de streaming."""
    from trabajo_final.fuzzy_system import FuzzySystemBuilder as FuzzySystemBuilderST
    fs = FuzzySystemBuilderST(
        consenso_path="trabajo_final/data/delphi_consenso.json",
        data_dir="trabajo_final/data/",
        docs_dir="trabajo_final/docs/",
    )
    fs.build()
    return fs


def run_montecarlo_streaming(n_sims: int, fuzzy_system):
    """Ejecuta la simulación Montecarlo sobre el sistema difuso de streaming."""
    from trabajo_final.montecarlo import MontecarloSimulator as MontecarloSimulatorST
    mc = MontecarloSimulatorST(fuzzy_system, data_dir="trabajo_final/data/", docs_dir="trabajo_final/docs/", seed=42)
    df = mc.run(n_simulaciones=n_sims)
    return df, mc._statistics


def run_regression_streaming():
    """Entrena y evalúa los modelos de regresión para el caso streaming."""
    from trabajo_final.regression import RegressionAnalyzer as RegressionAnalyzerST
    ra = RegressionAnalyzerST(
        data_path="trabajo_final/data/base_simulada_streaming.csv",
        consenso_path="trabajo_final/data/delphi_consenso.json",
        docs_dir="trabajo_final/docs/",
    )
    metrics = ra.train_and_evaluate()
    importance = ra.get_feature_importance()
    corr = ra.calculate_pearson_correlation()
    return ra, metrics, importance, corr


# ---------------------------------------------------------------------------
# Utilidades de visualización
# ---------------------------------------------------------------------------

def _color_riesgo(val: float) -> str:
    """Retorna color CSS según nivel de riesgo."""
    if val >= 70:
        return "color: #ef5350; font-weight: bold"
    elif val >= 40:
        return "color: #ffa726; font-weight: bold"
    return "color: #66bb6a; font-weight: bold"


def _gauge_riesgo(valor: float, titulo: str = "Riesgo") -> None:
    """Muestra un indicador visual de riesgo con barra de progreso y métrica."""
    if valor >= 70:
        nivel = "ALTO ALTO"
        color = "red"
    elif valor >= 40:
        nivel = "MEDIO MEDIO"
        color = "orange"
    else:
        nivel = "BAJO BAJO"
        color = "green"

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label=titulo, value=f"{valor:.1f} / 100", delta=nivel)
    with col2:
        st.progress(int(valor))
        st.caption(f"Nivel: **{nivel}**  |  Valor: `{valor:.2f}`")


def _tabla_delphi_ronda(ronda_data: dict) -> pd.DataFrame:
    """Convierte los datos de una ronda Delphi (r1 o r2) en un DataFrame tabular.
    Estructura esperada: {"factores": [{"factor": ..., "estadisticos": {...}, "respuestas": [...]}]}
    """
    rows = []
    for fd in ronda_data.get("factores", []):
        factor = fd["factor"]
        stats = fd["estadisticos"]
        for resp in fd["respuestas"]:
            rows.append({
                "Factor": factor,
                "Experto": resp["nombre"],
                "Cargo": resp["cargo"],
                "Puntuación R. anterior": resp.get("puntuacion_anterior", "—"),
                "Puntuación": resp["puntuacion"],
                "Media grupal": round(stats["media"], 3),
                "CV": round(stats["cv"], 3),
            })
    return pd.DataFrame(rows)


def _tabla_delphi_consenso(r3: dict) -> pd.DataFrame:
    """Convierte el documento de consenso (r3) en un DataFrame tabular para la Ronda 3.
    Estructura esperada: {"variables_aprobadas": [...], "variables_rechazadas": [...]}
    Cada variable tiene: {"factor": ..., "estadisticos_finales": {...}, "criterios": {...}, "aprobado": bool}
    """
    rows = []
    todas = r3.get("variables_aprobadas", []) + r3.get("variables_rechazadas", [])
    for v in todas:
        st_fin = v.get("estadisticos_finales", {})
        criterios = v.get("criterios", {})
        rows.append({
            "Factor": v["factor"],
            "Media final": round(st_fin.get("media", 0), 3),
            "Std": round(st_fin.get("std", 0), 3),
            "CV": round(st_fin.get("cv", 0), 3),
            "% Aprobación": f"{criterios.get('approval_pct', 0):.1f} %",
            "Media ≥ 4.0": "" if criterios.get("mean_ok") else "",
            "CV ≤ 0.30": "" if criterios.get("cv_ok") else "",
            "Aprobación ≥ 70%": "" if criterios.get("approval_ok") else "",
            "Estado": " Aprobado" if v.get("aprobado") else f" Rechazado ({v.get('criterio_fallido', '—')})",
        })
    return pd.DataFrame(rows)


def _convergencia_chart(r1: dict, r2: dict, r3: dict, consenso_path: str = "data/delphi_consenso.json"):
    """Genera gráfico de convergencia de medias por ronda.

    r1 y r2 tienen estructura {"factores": [{"factor": ..., "estadisticos": {...}}, ...]}.
    r3 es el documento de consenso {"variables_aprobadas": [...], "variables_rechazadas": [...]}.
    Para la Ronda 3 se leen los estadísticos desde variables_aprobadas + variables_rechazadas.
    """
    # Construir datos de Ronda 1 y Ronda 2 desde la estructura con "factores"
    data = []
    for ronda_num, ronda in enumerate([r1, r2], start=1):
        factores_list = ronda.get("factores", [])
        for fd in factores_list:
            data.append({
                "Ronda": f"Ronda {ronda_num}",
                "Factor": fd["factor"],
                "Media": fd["estadisticos"]["media"],
                "CV": fd["estadisticos"]["cv"],
            })

    # Construir datos de Ronda 3 desde el documento de consenso
    # r3 tiene "variables_aprobadas" y "variables_rechazadas"
    todas_r3 = r3.get("variables_aprobadas", []) + r3.get("variables_rechazadas", [])
    for v in todas_r3:
        st_fin = v.get("estadisticos_finales", {})
        data.append({
            "Ronda": "Ronda 3",
            "Factor": v["factor"],
            "Media": st_fin.get("media", 0),
            "CV": st_fin.get("cv", 0),
        })

    if not data:
        st.warning("No hay datos suficientes para el gráfico de convergencia.")
        return

    df = pd.DataFrame(data)
    factores = df["Factor"].unique().tolist()

    if PLOTLY_AVAILABLE:
        fig = px.line(
            df, x="Ronda", y="Media", color="Factor",
            markers=True,
            title="Convergencia de medias por ronda — Proceso Delphi",
            labels={"Media": "Puntuación media (Likert 1–5)"},
        )
        fig.add_hline(y=4.0, line_dash="dash", line_color="red",
                      annotation_text="Umbral mínimo (4.0)")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig, ax = plt.subplots(figsize=(8, 4))
        for factor in factores:
            subset = df[df["Factor"] == factor].sort_values("Ronda")
            ax.plot(subset["Ronda"].tolist(), subset["Media"].tolist(), marker="o", label=factor)
        ax.axhline(y=4.0, linestyle="--", color="red", label="Umbral (4.0)")
        ax.set_ylabel("Media Likert")
        ax.set_title("Convergencia Delphi")
        ax.legend()
        st.pyplot(fig)
        plt.close(fig)


def _metrics_table(metrics: dict) -> pd.DataFrame:
    """Convierte el dict de métricas de regresión en DataFrame."""
    rows = []
    model_names = {
        "knn": "K-Nearest Neighbors",
        "random_forest": "Random Forest",
        "decision_tree": "Decision Tree",
    }
    for key, vals in metrics.items():
        rows.append({
            "Modelo": model_names.get(key, key),
            "MAE": round(vals["mae"], 4),
            "RMSE": round(vals["rmse"], 4),
            "R²": round(vals["r2"], 4),
        })
    return pd.DataFrame(rows)


def _importance_chart(importance: dict, title: str = "Importancia de variables"):
    """Gráfico de barras horizontales de importancia de variables."""
    # Usar Random Forest si está disponible
    imp_data = importance.get("random_forest", importance.get(list(importance.keys())[0], {}))
    df_imp = pd.DataFrame(
        list(imp_data.items()), columns=["Variable", "Importancia"]
    ).sort_values("Importancia", ascending=True)

    if PLOTLY_AVAILABLE:
        fig = px.bar(
            df_imp, x="Importancia", y="Variable", orientation="h",
            title=title,
            color="Importancia",
            color_continuous_scale="Blues",
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.barh(df_imp["Variable"], df_imp["Importancia"], color="steelblue")
        ax.set_title(title)
        ax.set_xlabel("Importancia")
        st.pyplot(fig)
        plt.close(fig)


def _r2_comparison_chart(metrics: dict, title: str = "Comparación R² por modelo"):
    """Gráfico de barras comparando R² de los modelos."""
    model_names = {
        "knn": "KNN",
        "random_forest": "Random Forest",
        "decision_tree": "Decision Tree",
    }
    df_r2 = pd.DataFrame([
        {"Modelo": model_names.get(k, k), "R²": v["r2"]}
        for k, v in metrics.items()
    ])

    if PLOTLY_AVAILABLE:
        fig = px.bar(
            df_r2, x="Modelo", y="R²",
            title=title,
            color="R²",
            color_continuous_scale="Greens",
            text_auto=".3f",
        )
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(df_r2["Modelo"], df_r2["R²"], color="seagreen")
        ax.set_title(title)
        ax.set_ylabel("R²")
        st.pyplot(fig)
        plt.close(fig)


def _montecarlo_histogram(df_riesgo: pd.Series, col_name: str = "riesgo", title: str = "Distribución del Riesgo"):
    """Histograma interactivo de la distribución del riesgo."""
    if PLOTLY_AVAILABLE:
        fig = px.histogram(
            df_riesgo, x=col_name, nbins=40,
            title=title,
            labels={col_name: "Riesgo"},
            color_discrete_sequence=["#4fc3f7"],
        )
        fig.add_vline(x=70, line_dash="dash", line_color="red",
                      annotation_text="Umbral crítico (70)")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.hist(df_riesgo[col_name], bins=40, color="steelblue", edgecolor="white", alpha=0.85)
        ax.axvline(x=70, color="red", linestyle="--", label="Umbral crítico (70)")
        ax.set_title(title)
        ax.set_xlabel("Riesgo")
        ax.set_ylabel("Frecuencia")
        ax.legend()
        st.pyplot(fig)
        plt.close(fig)


def _scatter_vars_vs_riesgo(df: pd.DataFrame, input_cols: list[str], riesgo_col: str = "riesgo"):
    """Scatter plots de variables de entrada vs riesgo."""
    if PLOTLY_AVAILABLE:
        n = len(input_cols)
        cols_per_row = 2
        rows = (n + cols_per_row - 1) // cols_per_row
        cols_st = st.columns(cols_per_row)
        for i, col in enumerate(input_cols):
            with cols_st[i % cols_per_row]:
                fig = px.scatter(
                    df, x=col, y=riesgo_col,
                    opacity=0.4,
                    title=f"{col} vs {riesgo_col}",
                    color_discrete_sequence=["#4fc3f7"],
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    else:
        n = len(input_cols)
        fig, axes = plt.subplots(1, n, figsize=(5 * n, 4))
        if n == 1:
            axes = [axes]
        for ax, col in zip(axes, input_cols):
            ax.scatter(df[col], df[riesgo_col], alpha=0.3, s=5, color="steelblue")
            ax.set_xlabel(col)
            ax.set_ylabel(riesgo_col)
            ax.set_title(f"{col} vs {riesgo_col}")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)


# ===========================================================================
# SECCIÓN 1: INICIO
# ===========================================================================

if seccion == " Inicio":
    st.markdown('<div class="main-header"> Taller 2 — Modelos y Simulación</div>', unsafe_allow_html=True)
    st.markdown("### Institución Universitaria Pascual Bravo · Medellín, Colombia")
    st.markdown("**Integrantes:** Julian Zapata · Juan José Orrego · 2026")
    st.markdown("---")

    st.markdown("""
    Este taller implementa un flujo metodológico completo de modelado y simulación
    aplicado a dos casos de estudio:

    - **Caso Base:** Evaluación del riesgo de bajo rendimiento académico en la I.U. Pascual Bravo.
    - **Caso Streaming (Parte E):** Evaluación del riesgo de degradación de QoS en una plataforma de streaming.
    """)

    # Flujo metodológico
    st.info("""
    **Flujo metodológico:**
     Delphi (validación de variables)
    →  Sistema Difuso Mamdani (inferencia)
    →  Montecarlo (simulación estocástica)
    →  Regresión (predicción y validación)
    """)

    st.markdown("---")
    st.subheader(" Resumen de resultados")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Caso Base — Rendimiento Académico")
        resumen_base = {
            "Módulo": ["Delphi", "Sistema Difuso", "Montecarlo", "Regresión"],
            "Estado": [
                " Completado" if st.session_state.delphi_done else " Pendiente",
                " Completado" if st.session_state.fuzzy_built else " Pendiente",
                " Completado" if st.session_state.montecarlo_done else " Pendiente",
                " Completado" if st.session_state.regression_done else " Pendiente",
            ],
            "Descripción": [
                "4 variables validadas por 4 expertos",
                "12 reglas Mamdani, 4 variables entrada",
                "Simulación estocástica N iteraciones",
                "KNN, Random Forest, Decision Tree",
            ],
        }
        st.dataframe(pd.DataFrame(resumen_base), use_container_width=True, hide_index=True)

    with col2:
        st.markdown("#### Caso Streaming — QoS")
        resumen_st = {
            "Módulo": ["Delphi", "Sistema Difuso", "Montecarlo", "Regresión"],
            "Estado": [
                " Completado" if st.session_state.st_delphi_done else " Pendiente",
                " Completado" if st.session_state.st_fuzzy_built else " Pendiente",
                " Completado" if st.session_state.st_montecarlo_done else " Pendiente",
                " Completado" if st.session_state.st_regression_done else " Pendiente",
            ],
            "Descripción": [
                "4 variables de red validadas",
                "12 reglas Mamdani, riesgo QoS",
                "Simulación estocástica N iteraciones",
                "KNN, Random Forest, Decision Tree",
            ],
        }
        st.dataframe(pd.DataFrame(resumen_st), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader(" Ejecutar flujo completo")
    st.warning("Ejecutar el flujo completo puede tardar varios minutos. Se ejecutarán ambos casos (base y streaming).")

    if st.button(" Ejecutar flujo completo (Caso Base)", type="primary"):
        progress = st.progress(0, text="Iniciando flujo completo...")
        try:
            # Delphi
            progress.progress(10, text="Ejecutando Delphi...")
            r1, r2, r3 = run_delphi()
            st.session_state.delphi_r1 = r1
            st.session_state.delphi_r2 = r2
            st.session_state.delphi_r3 = r3
            st.session_state.delphi_done = True

            # Fuzzy
            progress.progress(35, text="Construyendo sistema difuso...")
            fs = get_fuzzy_system()
            st.session_state.fuzzy_built = True

            # Montecarlo
            progress.progress(55, text="Ejecutando simulación Montecarlo (1000 sims)...")
            df_mc, mc_stats = run_montecarlo(1000, fs)
            st.session_state.df_simulado = df_mc
            st.session_state.mc_stats = mc_stats
            st.session_state.montecarlo_done = True

            # Regresión
            progress.progress(80, text="Entrenando modelos de regresión...")
            _, metrics, importance, corr = run_regression()
            st.session_state.reg_metrics = metrics
            st.session_state.reg_importance = importance
            st.session_state.reg_corr = corr
            st.session_state.regression_done = True

            progress.progress(100, text="¡Flujo completo ejecutado!")
            st.success(" Flujo completo ejecutado exitosamente. Navega por las secciones para ver los resultados.")
        except Exception as e:
            st.error(f" Error durante la ejecución: {e}")


# ===========================================================================
# SECCIÓN 2: PARTE A — DELPHI
# ===========================================================================

elif seccion == " Parte A — Delphi":
    st.title(" Parte A — Método Delphi")
    st.markdown("""
    El **método Delphi** es una técnica de consulta estructurada a expertos que busca alcanzar
    consenso sobre un tema mediante rondas iterativas de retroalimentación. Se aplicaron
    **3 rondas** para validar los factores candidatos de riesgo académico.
    """)
    st.info("""
    **¿Qué se muestra aquí?**
    Esta sección ejecuta el proceso Delphi con un panel de 4 expertos simulados de la I.U. Pascual Bravo.
    Cada experto asigna una puntuación Likert (1–5) a cada factor candidato. En 3 rondas iterativas,
    las puntuaciones convergen hacia el consenso.

    **¿Qué significan los resultados?**
    - **Media ≥ 4.0**: el factor es considerado relevante por el panel.
    - **CV ≤ 0.30**: hay acuerdo entre los expertos (baja dispersión).
    - **Aprobación ≥ 70%**: la mayoría calificada respalda el factor.
    - Solo los factores que cumplen los **3 criterios simultáneamente** ingresan al sistema difuso.
    - El gráfico de convergencia muestra cómo las puntuaciones se acercan entre rondas — esto valida que el proceso Delphi funcionó correctamente.
    """)

    # Panel de expertos
    with st.expander(" Panel de expertos", expanded=True):
        expertos_df = pd.DataFrame([
            {"ID": "E1", "Nombre": "Dr. Carlos Restrepo", "Cargo": "Docente de Ingeniería de Sistemas", "Dependencia": "Facultad de Ingeniería", "Perfil": "Docente"},
            {"ID": "E2", "Nombre": "Mg. Adriana Gómez", "Cargo": "Coordinadora Académica", "Dependencia": "Vicerrectoría Académica", "Perfil": "Coordinador"},
            {"ID": "E3", "Nombre": "Ps. Juliana Martínez", "Cargo": "Psicóloga de Bienestar Estudiantil", "Dependencia": "Bienestar Universitario", "Perfil": "Psicólogo"},
            {"ID": "E4", "Nombre": "Dr. Hernán Ospina", "Cargo": "Director de Currículo", "Dependencia": "Vicerrectoría Académica", "Perfil": "Directivo"},
        ])
        st.dataframe(expertos_df, use_container_width=True, hide_index=True)

    st.markdown("**Criterios de consenso:**")
    col1, col2, col3 = st.columns(3)
    col1.metric("Media mínima", "≥ 4.0")
    col2.metric("CV máximo", "≤ 0.30")
    col3.metric("% Aprobación mínimo", "≥ 70 %")

    st.markdown("---")

    if st.button(" Ejecutar proceso Delphi", type="primary"):
        with st.spinner("Ejecutando proceso Delphi (3 rondas)..."):
            try:
                r1, r2, r3 = run_delphi()
                st.session_state.delphi_r1 = r1
                st.session_state.delphi_r2 = r2
                st.session_state.delphi_r3 = r3
                st.session_state.delphi_done = True
                st.success(" Proceso Delphi completado exitosamente.")
            except Exception as e:
                st.error(f" Error al ejecutar Delphi: {e}")

    if st.session_state.delphi_done:
        r1 = st.session_state.delphi_r1
        r2 = st.session_state.delphi_r2
        r3 = st.session_state.delphi_r3

        tab1, tab2, tab3, tab4 = st.tabs(["Ronda 1", "Ronda 2", "Ronda 3", "Consenso Final"])

        with tab1:
            st.subheader("Ronda 1 — Evaluación inicial")
            df_r1 = _tabla_delphi_ronda(r1)
            st.dataframe(df_r1, use_container_width=True, hide_index=True)

        with tab2:
            st.subheader("Ronda 2 — Retroalimentación y ajuste")
            df_r2 = _tabla_delphi_ronda(r2)
            st.dataframe(df_r2, use_container_width=True, hide_index=True)

        with tab3:
            st.subheader("Ronda 3 — Validación final")
            df_r3 = _tabla_delphi_consenso(r3)
            st.dataframe(df_r3, use_container_width=True, hide_index=True)

        with tab4:
            st.subheader("Consenso Final — Variables aprobadas")
            aprobadas = r3.get("variables_aprobadas", [])
            rechazadas = r3.get("variables_rechazadas", [])

            if aprobadas:
                rows_ap = []
                for v in aprobadas:
                    st_fin = v["estadisticos_finales"]
                    rows_ap.append({
                        "Factor": v["factor"],
                        "Media": round(st_fin["media"], 4),
                        "CV": round(st_fin["cv"], 4),
                        "% Aprobación": f"{v['criterios']['approval_pct']:.1f} %",
                        "Estado": " Aprobado",
                    })
                df_ap = pd.DataFrame(rows_ap)
                st.dataframe(df_ap, use_container_width=True, hide_index=True)
            else:
                st.warning("No se aprobaron variables en este proceso.")

            if rechazadas:
                st.markdown("**Variables rechazadas:**")
                rows_re = []
                for v in rechazadas:
                    st_fin = v["estadisticos_finales"]
                    rows_re.append({
                        "Factor": v["factor"],
                        "Media": round(st_fin["media"], 4),
                        "CV": round(st_fin["cv"], 4),
                        "Criterio fallido": v.get("criterio_fallido", "—"),
                        "Estado": " Rechazado",
                    })
                st.dataframe(pd.DataFrame(rows_re), use_container_width=True, hide_index=True)

        # Gráfico de convergencia
        st.markdown("---")
        st.subheader(" Convergencia de medias por ronda")
        _convergencia_chart(r1, r2, r3)

        # JSON generado
        with st.expander(" Ver delphi_consenso.json"):
            try:
                with open("data/delphi_consenso.json", encoding="utf-8") as f:
                    consenso_json = json.load(f)
                st.json(consenso_json)
            except FileNotFoundError:
                st.warning("El archivo delphi_consenso.json no se ha generado todavía.")


# ===========================================================================
# SECCIÓN 3: PARTE B — SISTEMA DIFUSO
# ===========================================================================

elif seccion == " Parte B — Sistema Difuso":
    st.title(" Parte B — Sistema de Inferencia Difuso (Mamdani)")
    st.markdown("""
    El **sistema Mamdani** utiliza las variables validadas por el proceso Delphi para
    inferir el nivel de riesgo académico mediante lógica difusa. Combina 4 variables
    de entrada con reglas lingüísticas para producir un valor de riesgo en [0, 100].
    """)
    st.info("""
    **¿Qué se muestra aquí?**
    Esta sección construye el sistema de inferencia difusa con las variables aprobadas en el Delphi.
    Incluye una **calculadora interactiva** donde puedes mover los sliders y ver el riesgo calculado en tiempo real.

    **¿Qué significan los resultados?**
    - El valor de **riesgo** (0–100) es el resultado de aplicar las 27 reglas IF-THEN sobre los valores de entrada.
    - **0–30**: riesgo muy bajo — el estudiante tiene condiciones favorables.
    - **30–55**: riesgo bajo a medio — condiciones aceptables con áreas de mejora.
    - **55–75**: riesgo medio a alto — señales de alerta que requieren atención.
    - **75–100**: riesgo muy alto — intervención urgente recomendada.
    - Las **funciones de pertenencia** muestran cómo cada valor numérico se traduce a etiquetas lingüísticas (bajo/medio/alto).
    - La **defuzzificación centroide** convierte el área difusa resultante en un número concreto.
    """)

    # Tabla de variables
    with st.expander(" Variables y funciones de pertenencia", expanded=False):
        vars_df = pd.DataFrame([
            {"Variable": "promedio_academico", "Rango": "[0.0, 5.0]", "Etiquetas": "bajo, medio, alto", "Tipo": "Antecedente"},
            {"Variable": "inasistencia", "Rango": "[0, 100]", "Etiquetas": "baja, media, alta", "Tipo": "Antecedente"},
            {"Variable": "horas_estudio", "Rango": "[0, 30]", "Etiquetas": "pocas, moderadas, muchas", "Tipo": "Antecedente"},
            {"Variable": "motivacion_estres", "Rango": "[0.0, 10.0]", "Etiquetas": "bajo, medio, alto", "Tipo": "Antecedente"},
            {"Variable": "riesgo", "Rango": "[0, 100]", "Etiquetas": "bajo, medio, alto", "Tipo": "Consecuente"},
        ])
        st.dataframe(vars_df, use_container_width=True, hide_index=True)

    # Tabla de reglas
    with st.expander(" Las 27 reglas Mamdani (5 niveles de riesgo)", expanded=False):
        reglas_df = pd.DataFrame([
            {"ID": "R01", "Descripción": "promedio=bajo ∧ inasistencia=alta ∧ horas=pocas → riesgo=muy_alto", "Consecuente": "muy_alto"},
            {"ID": "R02", "Descripción": "motivacion=bajo ∧ inasistencia=alta ∧ promedio=bajo → riesgo=muy_alto", "Consecuente": "muy_alto"},
            {"ID": "R03", "Descripción": "promedio=bajo ∧ inasistencia=alta → riesgo=alto", "Consecuente": "alto"},
            {"ID": "R04", "Descripción": "motivacion=bajo ∧ horas=pocas → riesgo=alto", "Consecuente": "alto"},
            {"ID": "R05", "Descripción": "promedio=bajo ∧ horas=pocas → riesgo=alto", "Consecuente": "alto"},
            {"ID": "R06", "Descripción": "inasistencia=alta ∧ horas=pocas → riesgo=alto", "Consecuente": "alto"},
            {"ID": "R07", "Descripción": "promedio=medio ∧ inasistencia=alta → riesgo=alto", "Consecuente": "alto"},
            {"ID": "R08", "Descripción": "promedio=bajo ∧ inasistencia=media → riesgo=medio", "Consecuente": "medio"},
            {"ID": "R09", "Descripción": "promedio=medio ∧ inasistencia=media → riesgo=medio", "Consecuente": "medio"},
            {"ID": "R10", "Descripción": "horas=moderadas ∧ motivacion=medio → riesgo=medio", "Consecuente": "medio"},
            {"ID": "R11", "Descripción": "promedio=medio ∧ horas=pocas → riesgo=medio", "Consecuente": "medio"},
            {"ID": "R12", "Descripción": "motivacion=bajo ∧ promedio=medio → riesgo=medio", "Consecuente": "medio"},
            {"ID": "R13", "Descripción": "promedio=alto ∧ inasistencia=media → riesgo=medio", "Consecuente": "medio"},
            {"ID": "R14", "Descripción": "promedio=alto ∧ motivacion=medio → riesgo=bajo", "Consecuente": "bajo"},
            {"ID": "R15", "Descripción": "promedio=medio ∧ motivacion=alto → riesgo=bajo", "Consecuente": "bajo"},
            {"ID": "R16", "Descripción": "promedio=medio ∧ horas=muchas → riesgo=bajo", "Consecuente": "bajo"},
            {"ID": "R17", "Descripción": "promedio=alto ∧ inasistencia=baja → riesgo=bajo", "Consecuente": "bajo"},
            {"ID": "R18", "Descripción": "promedio=alto ∧ horas=muchas ∧ motivacion=alto → riesgo=muy_bajo", "Consecuente": "muy_bajo"},
            {"ID": "R19", "Descripción": "promedio=alto ∧ inasistencia=baja ∧ motivacion=alto → riesgo=muy_bajo", "Consecuente": "muy_bajo"},
            {"ID": "R20", "Descripción": "promedio=alto ∧ horas=muchas → riesgo=muy_bajo", "Consecuente": "muy_bajo"},
        ])

        def _color_consecuente(val):
            if val == "muy_alto":
                return "background-color: #7b0000; color: white"
            elif val == "alto":
                return "background-color: #b71c1c; color: white"
            elif val == "medio":
                return "background-color: #e65100; color: white"
            elif val == "bajo":
                return "background-color: #1b5e20; color: white"
            return "background-color: #0d3b1a; color: white"

        st.dataframe(
            reglas_df.style.map(_color_consecuente, subset=["Consecuente"]),
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")
    st.subheader(" Construir sistema difuso")

    # Verificar que existe el consenso
    if not os.path.exists("data/delphi_consenso.json"):
        st.warning(" No se encontró `data/delphi_consenso.json`. Ejecuta primero la Parte A — Delphi.")
    else:
        if st.button(" Construir sistema difuso", type="primary"):
            with st.spinner("Construyendo sistema difuso Mamdani..."):
                try:
                    get_fuzzy_system()
                    st.session_state.fuzzy_built = True
                    st.success(" Sistema difuso construido exitosamente.")
                except Exception as e:
                    st.error(f" Error al construir el sistema difuso: {e}")

        if st.session_state.fuzzy_built:
            st.markdown("---")
            st.subheader(" Calculadora interactiva de riesgo")
            st.markdown("Mueve los sliders para calcular el riesgo en tiempo real:")

            col1, col2 = st.columns(2)
            with col1:
                promedio = st.slider(" Promedio académico", 0.0, 5.0, 3.5, 0.1)
                inasistencia = st.slider(" Inasistencia (%)", 0, 100, 30, 1)
            with col2:
                horas = st.slider(" Horas de estudio / semana", 0, 30, 12, 1)
                motivacion = st.slider(" Motivación / Estrés (0=bajo, 10=alto)", 0.0, 10.0, 5.0, 0.1)

            try:
                fs = get_fuzzy_system()
                riesgo_val = fs.evaluar_riesgo({
                    "promedio_academico": promedio,
                    "inasistencia": float(inasistencia),
                    "horas_estudio": float(horas),
                    "motivacion_estres": motivacion,
                })
                st.markdown("---")
                st.subheader(" Resultado")
                _gauge_riesgo(riesgo_val, "Riesgo Académico")

                # Reglas activadas (aproximación heurística)
                st.markdown("**Reglas potencialmente activadas:**")
                reglas_activadas = []
                if promedio < 2.5 and inasistencia > 60:
                    reglas_activadas.append("R01 — promedio bajo ∧ inasistencia alta → riesgo alto")
                if motivacion < 3.5 and horas < 8:
                    reglas_activadas.append("R02 — motivación baja ∧ horas pocas → riesgo alto")
                if promedio < 2.5 and horas < 8:
                    reglas_activadas.append("R03 — promedio bajo ∧ horas pocas → riesgo alto")
                if promedio > 4.2 and inasistencia < 15:
                    reglas_activadas.append("R04 — promedio alto ∧ inasistencia baja → riesgo bajo")
                if promedio > 4.2 and horas > 22:
                    reglas_activadas.append("R05 — promedio alto ∧ horas muchas → riesgo bajo")
                if motivacion > 7.5 and promedio > 4.2:
                    reglas_activadas.append("R06 — motivación alta ∧ promedio alto → riesgo bajo")
                if 2.5 <= promedio <= 4.0 and 25 <= inasistencia <= 55:
                    reglas_activadas.append("R07 — promedio medio ∧ inasistencia media → riesgo medio")
                if 10 <= horas <= 20 and 3.5 <= motivacion <= 6.5:
                    reglas_activadas.append("R08 — horas moderadas ∧ motivación media → riesgo medio")
                if inasistencia > 60 and horas < 8:
                    reglas_activadas.append("R10 — inasistencia alta ∧ horas pocas → riesgo alto")
                if motivacion < 3.5 and inasistencia > 60:
                    reglas_activadas.append("R12 — motivación baja ∧ inasistencia alta → riesgo alto")

                if reglas_activadas:
                    for r in reglas_activadas:
                        st.markdown(f"- `{r}`")
                else:
                    st.info("Ninguna regla con activación dominante para estos valores.")

            except Exception as e:
                st.error(f" Error al evaluar el sistema difuso: {e}")

            # Gráficas de funciones de pertenencia
            with st.expander(" Ver gráficas de funciones de pertenencia"):
                plots_dir = "docs/fuzzy_membership_plots"
                if os.path.exists(plots_dir):
                    vars_plot = ["promedio_academico", "inasistencia", "horas_estudio", "motivacion_estres", "riesgo"]
                    cols_plot = st.columns(2)
                    for i, var in enumerate(vars_plot):
                        img_path = os.path.join(plots_dir, f"{var}.png")
                        if os.path.exists(img_path):
                            with cols_plot[i % 2]:
                                st.image(img_path, caption=var, use_container_width=True)
                else:
                    st.info("Las gráficas se generan al construir el sistema difuso.")


# ===========================================================================
# SECCIÓN 4: PARTE C — MONTECARLO
# ===========================================================================

elif seccion == " Parte C — Montecarlo":
    st.title(" Parte C — Simulación Montecarlo")
    st.markdown("""
    La **simulación Montecarlo** muestrea aleatoriamente las variables de entrada
    según distribuciones estadísticas justificadas y evalúa el sistema difuso
    para cada muestra, generando una distribución empírica del riesgo académico.
    """)
    st.info("""
    **¿Qué se muestra aquí?**
    Se generan N escenarios aleatorios de estudiantes (combinaciones de promedio, inasistencia, horas de estudio y motivación),
    cada uno pasa por el sistema difuso y se obtiene su índice de riesgo. El resultado es una distribución estadística del riesgo.

    **¿Qué significan los resultados?**
    - **Histograma**: muestra cuántos estudiantes simulados caen en cada nivel de riesgo. Una distribución amplia indica que el sistema difuso diferencia bien entre escenarios.
    - **Media del riesgo**: el nivel de riesgo promedio en la población simulada.
    - **P(riesgo ≥ 70)**: proporción de estudiantes en situación crítica — requieren intervención inmediata.
    - **Percentiles**: P25/P50/P75/P95 permiten entender la distribución completa del riesgo.
    - **Escenarios críticos**: los casos con mayor riesgo, con sus valores de entrada — útiles para identificar perfiles de alto riesgo.
    - La línea roja en el histograma marca el **umbral crítico de 70** — por encima de este valor se recomienda intervención.
    """)

    # Distribuciones
    with st.expander(" Distribuciones estadísticas utilizadas", expanded=False):
        dist_df = pd.DataFrame([
            {"Variable": "promedio_academico", "Distribución": "Uniforme", "Parámetros": "[0.5, 5.0]", "Justificación": "Cobertura uniforme de todo el espacio de estados del sistema difuso"},
            {"Variable": "inasistencia", "Distribución": "Uniforme", "Parámetros": "[0, 100]", "Justificación": "Exploración completa del rango de inasistencia"},
            {"Variable": "horas_estudio", "Distribución": "Uniforme", "Parámetros": "[0, 30]", "Justificación": "Cobertura uniforme del universo de discurso"},
            {"Variable": "motivacion_estres", "Distribución": "Uniforme", "Parámetros": "[0, 10]", "Justificación": "Cobertura uniforme de todos los niveles de motivación/estrés"},
        ])
        st.dataframe(dist_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Verificar prerequisitos
    if not os.path.exists("data/delphi_consenso.json"):
        st.warning(" Ejecuta primero la Parte A — Delphi para generar `delphi_consenso.json`.")
    elif not st.session_state.fuzzy_built:
        st.warning(" Construye primero el sistema difuso en la Parte B.")
    else:
        n_sims = st.slider("Número de simulaciones", 100, 5000, 1000, 100)

        if st.button(" Ejecutar simulación Montecarlo", type="primary"):
            with st.spinner(f"Ejecutando {n_sims} simulaciones..."):
                try:
                    fs = get_fuzzy_system()
                    df_mc, mc_stats = run_montecarlo(n_sims, fs)
                    st.session_state.df_simulado = df_mc
                    st.session_state.mc_stats = mc_stats
                    st.session_state.montecarlo_done = True
                    st.success(f" Simulación completada: {n_sims} iteraciones.")
                except Exception as e:
                    st.error(f" Error en la simulación Montecarlo: {e}")

        if st.session_state.montecarlo_done and st.session_state.df_simulado is not None:
            df_mc = st.session_state.df_simulado
            mc_stats = st.session_state.mc_stats

            tab1, tab2, tab3, tab4 = st.tabs(["Histograma", "Estadísticos", "Scatter plots", "Escenarios críticos"])

            with tab1:
                st.subheader("Distribución del riesgo académico")
                _montecarlo_histogram(df_mc, col_name="riesgo", title="Distribución del Riesgo Académico — Montecarlo")
                st.info(
                    "**Nota metodológica:** El pico visible en ~50 es el centroide de la función de "
                    "pertenencia `riesgo=medio` del sistema Mamdani. Cuando las variables de entrada "
                    "caen en la zona media (promedio ~3.5, inasistencia ~40%, horas ~15h), el sistema "
                    "difuso activa las reglas de riesgo medio y el centroide converge a ~50. "
                    "Esto es **comportamiento correcto** del sistema difuso, no un error."
                )

            with tab2:
                st.subheader("Estadísticos descriptivos")
                if mc_stats:
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Media", f"{mc_stats['mean']:.2f}")
                    col2.metric("Desv. estándar", f"{mc_stats['std']:.2f}")
                    col3.metric("Mediana (P50)", f"{mc_stats['p50']:.2f}")
                    col4.metric("P(riesgo ≥ 70)", f"{mc_stats['p_riesgo_alto']:.1%}")

                    stats_df = pd.DataFrame([
                        {"Estadístico": "Media", "Valor": round(mc_stats["mean"], 4)},
                        {"Estadístico": "Desv. estándar", "Valor": round(mc_stats["std"], 4)},
                        {"Estadístico": "Mínimo", "Valor": round(mc_stats["min"], 4)},
                        {"Estadístico": "Percentil 25", "Valor": round(mc_stats["p25"], 4)},
                        {"Estadístico": "Mediana (P50)", "Valor": round(mc_stats["p50"], 4)},
                        {"Estadístico": "Percentil 75", "Valor": round(mc_stats["p75"], 4)},
                        {"Estadístico": "Percentil 95", "Valor": round(mc_stats["p95"], 4)},
                        {"Estadístico": "Máximo", "Valor": round(mc_stats["max"], 4)},
                        {"Estadístico": "P(riesgo ≥ 70)", "Valor": f"{mc_stats['p_riesgo_alto']:.4f}"},
                    ])
                    st.dataframe(stats_df, use_container_width=True, hide_index=True)

            with tab3:
                st.subheader("Variables de entrada vs Riesgo")
                input_cols = ["promedio_academico", "inasistencia", "horas_estudio", "motivacion_estres"]
                _scatter_vars_vs_riesgo(df_mc, input_cols, riesgo_col="riesgo")

            with tab4:
                st.subheader("Top 10 escenarios críticos (riesgo ≥ 70)")
                criticos = df_mc[df_mc["riesgo"] >= 70].nlargest(10, "riesgo")
                if len(criticos) > 0:
                    st.dataframe(criticos.round(3), use_container_width=True, hide_index=True)
                    st.info(f"Total de escenarios críticos: **{len(df_mc[df_mc['riesgo'] >= 70])}** de {len(df_mc)} simulaciones ({len(df_mc[df_mc['riesgo'] >= 70])/len(df_mc):.1%})")
                else:
                    st.success("No se encontraron escenarios con riesgo ≥ 70 en esta simulación.")


# ===========================================================================
# SECCIÓN 5: PARTE D — REGRESIÓN
# ===========================================================================

elif seccion == " Parte D — Regresión":
    st.title(" Parte D — Análisis de Regresión")
    st.markdown("""
    Se entrenan tres modelos de aprendizaje automático para predecir el riesgo
    académico a partir de las variables de entrada, validando la coherencia del
    sistema difuso mediante métricas de regresión y correlación de Pearson.
    """)
    st.info("""
    **¿Qué se muestra aquí?**
    Los modelos de regresión se entrenan sobre la base de datos generada por Montecarlo (variables de entrada + riesgo difuso).
    El objetivo es verificar si un modelo estadístico puede aproximar el comportamiento del sistema experto-difuso.

    **¿Qué significan los resultados?**
    - **R² (coeficiente de determinación)**: qué porcentaje de la variabilidad del riesgo explica el modelo. R²=0.90 significa que el modelo captura el 90% del comportamiento del sistema difuso.
    - **MAE (Error Absoluto Medio)**: error promedio en puntos de riesgo. MAE=3 significa que el modelo se equivoca en promedio 3 puntos sobre 100.
    - **RMSE**: similar al MAE pero penaliza más los errores grandes.
    - **Correlación de Pearson (r)**: mide la concordancia lineal entre predicciones y valores difusos. r > 0.90 indica alta consistencia.
    - **Importancia de variables**: qué factores usa más el modelo para predecir — debe coincidir con lo que los expertos priorizaron en el Delphi.
    - Un R² alto confirma que el sistema difuso es **coherente y reproducible** estadísticamente.
    """)
    st.markdown("**Modelos entrenados:** K-Nearest Neighbors · Random Forest · Decision Tree")
    st.markdown("**División de datos:** 80 % entrenamiento / 20 % prueba")
    st.markdown("---")

    # Verificar prerequisitos
    if not os.path.exists("data/base_simulada.csv"):
        st.warning(" Ejecuta primero la Parte C — Montecarlo para generar `base_simulada.csv`.")
    else:
        if st.button(" Entrenar modelos de regresión", type="primary"):
            with st.spinner("Entrenando KNN, Random Forest y Decision Tree..."):
                try:
                    _, metrics, importance, corr = run_regression()
                    st.session_state.reg_metrics = metrics
                    st.session_state.reg_importance = importance
                    st.session_state.reg_corr = corr
                    st.session_state.regression_done = True
                    st.success(" Modelos entrenados y evaluados exitosamente.")
                except Exception as e:
                    st.error(f" Error al entrenar los modelos: {e}")

        if st.session_state.regression_done and st.session_state.reg_metrics:
            metrics = st.session_state.reg_metrics
            importance = st.session_state.reg_importance
            corr = st.session_state.reg_corr

            tab1, tab2, tab3, tab4 = st.tabs(["Métricas", "Importancia de variables", "Comparación R²", "Correlación"])

            with tab1:
                st.subheader("Tabla comparativa de métricas")
                df_metrics = _metrics_table(metrics)
                st.dataframe(df_metrics, use_container_width=True, hide_index=True)

                st.markdown("**Interpretación:**")
                col1, col2, col3 = st.columns(3)
                col1.info("**MAE** (Error Absoluto Medio): Promedio de errores absolutos. Menor es mejor.")
                col2.info("**RMSE** (Raíz del Error Cuadrático Medio): Penaliza errores grandes. Menor es mejor.")
                col3.info("**R²** (Coeficiente de determinación): Proporción de varianza explicada. Más cercano a 1 es mejor.")

                # Mejor modelo
                best_model = max(metrics, key=lambda k: metrics[k]["r2"])
                model_names = {"knn": "K-Nearest Neighbors", "random_forest": "Random Forest", "decision_tree": "Decision Tree"}
                st.success(f" Mejor modelo: **{model_names.get(best_model, best_model)}** con R² = {metrics[best_model]['r2']:.4f}")

            with tab2:
                st.subheader("Importancia de variables (Random Forest)")
                if importance:
                    _importance_chart(importance, "Importancia de variables — Random Forest")

                    # Tabla de importancias
                    imp_rf = importance.get("random_forest", {})
                    imp_dt = importance.get("decision_tree", {})
                    if imp_rf and imp_dt:
                        imp_df = pd.DataFrame({
                            "Variable": list(imp_rf.keys()),
                            "Random Forest": [round(v, 4) for v in imp_rf.values()],
                            "Decision Tree": [round(imp_dt.get(k, 0), 4) for k in imp_rf.keys()],
                        }).sort_values("Random Forest", ascending=False)
                        st.dataframe(imp_df, use_container_width=True, hide_index=True)

            with tab3:
                st.subheader("Comparación de R² por modelo")
                _r2_comparison_chart(metrics, "R² por modelo — Caso Académico")

            with tab4:
                st.subheader("Correlación de Pearson")
                if corr is not None:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Correlación de Pearson (r)", f"{corr:.4f}")
                        st.metric("R² equivalente", f"{corr**2:.4f}")
                    with col2:
                        if abs(corr) >= 0.9:
                            st.success(f" Correlación muy alta ({corr:.4f}): el modelo predice con alta fidelidad los valores difusos.")
                        elif abs(corr) >= 0.7:
                            st.info(f" Correlación alta ({corr:.4f}): buena concordancia entre predicción y sistema difuso.")
                        elif abs(corr) >= 0.5:
                            st.warning(f" Correlación moderada ({corr:.4f}): concordancia aceptable.")
                        else:
                            st.error(f" Correlación baja ({corr:.4f}): el modelo no captura bien el comportamiento difuso.")

                    st.markdown("""
                    **Interpretación:** La correlación de Pearson mide la concordancia lineal entre
                    las predicciones del mejor modelo de regresión y los valores de riesgo generados
                    por el sistema difuso. Un valor cercano a 1 indica que el modelo de regresión
                    puede replicar fielmente el comportamiento del sistema difuso.
                    """)


# ===========================================================================
# SECCIÓN 6: PARTE E — STREAMING
# ===========================================================================

elif seccion == " Parte E — Streaming":
    st.title(" Parte E — Plataforma de Streaming (QoS)")
    st.markdown("""
    Aplicación del mismo flujo metodológico al caso de una **plataforma de streaming**,
    evaluando el riesgo de degradación de la calidad de servicio (QoS) en función de
    variables de red e infraestructura.
    """)
    st.markdown("---")

    # Sub-secciones con tabs
    tab_delphi, tab_fuzzy, tab_mc, tab_reg = st.tabs([
        " Delphi Streaming",
        " Sistema Difuso",
        " Montecarlo",
        " Regresión",
    ])

    # ---- Delphi Streaming ----
    with tab_delphi:
        st.subheader("Proceso Delphi — Plataforma de Streaming")
        st.markdown("Validación de variables de red mediante panel de expertos en infraestructura.")
        st.info("""
¿Qué se muestra aquí?
El proceso Delphi para el caso streaming valida los factores de red mediante un panel de 4 expertos del sector tecnológico (arquitecto cloud, analista QoS, investigador, especialista UX).

¿Qué significan los resultados?
- Media >= 4.0: el factor de red es considerado crítico para la QoS por el panel experto.
- CV <= 0.30: hay acuerdo entre los expertos sobre la importancia del factor.
- El grafico de convergencia muestra como las puntuaciones se acercan entre rondas.
- Solo los factores que cumplen los 3 criterios ingresan al sistema difuso de streaming.
""")

        if st.button(" Ejecutar Delphi Streaming", type="primary", key="btn_delphi_st"):
            with st.spinner("Ejecutando proceso Delphi de streaming..."):
                try:
                    r1, r2, r3 = run_delphi_streaming()
                    st.session_state.st_delphi_r1 = r1
                    st.session_state.st_delphi_r2 = r2
                    st.session_state.st_delphi_r3 = r3
                    st.session_state.st_delphi_done = True
                    st.success(" Delphi Streaming completado.")
                except Exception as e:
                    st.error(f" Error: {e}")

        if st.session_state.st_delphi_done:
            r1 = st.session_state.st_delphi_r1
            r2 = st.session_state.st_delphi_r2
            r3 = st.session_state.st_delphi_r3

            sub1, sub2, sub3 = st.tabs(["Ronda 1", "Ronda 2", "Consenso"])
            with sub1:
                st.dataframe(_tabla_delphi_ronda(r1), use_container_width=True, hide_index=True)
            with sub2:
                st.dataframe(_tabla_delphi_ronda(r2), use_container_width=True, hide_index=True)
            with sub3:
                aprobadas = r3.get("variables_aprobadas", [])
                if aprobadas:
                    rows_ap = []
                    for v in aprobadas:
                        st_fin = v["estadisticos_finales"]
                        rows_ap.append({
                            "Factor": v["factor"],
                            "Media": round(st_fin["media"], 4),
                            "CV": round(st_fin["cv"], 4),
                            "% Aprobación": f"{v['criterios']['approval_pct']:.1f} %",
                            "Estado": " Aprobado",
                        })
                    st.dataframe(pd.DataFrame(rows_ap), use_container_width=True, hide_index=True)

            st.markdown("**Convergencia de medias:**")
            _convergencia_chart(r1, r2, r3)

            with st.expander(" Ver delphi_consenso.json (streaming)"):
                try:
                    with open("trabajo_final/data/delphi_consenso.json", encoding="utf-8") as f:
                        st.json(json.load(f))
                except FileNotFoundError:
                    st.warning("Archivo no encontrado.")

    # ---- Sistema Difuso Streaming ----
    with tab_fuzzy:
        st.subheader("Sistema Difuso Mamdani — QoS Streaming")
        st.info("""
¿Qué se muestra aquí?
El sistema difuso Mamdani para streaming usa las 4 variables de red validadas por el Delphi.
La calculadora interactiva permite simular escenarios en tiempo real.

¿Qué significan los resultados?
- riesgo_qos (0-100): probabilidad de degradacion del servicio (buffering, cortes, baja calidad).
- 0-25: servicio estable, recursos suficientes para todos los usuarios.
- 25-50: riesgo moderado, posibles degradaciones en horas pico.
- 50-75: riesgo alto, se recomienda escalar infraestructura.
- 75-100: riesgo critico, degradacion severa inminente, activar auto-scaling.
- Las 27 reglas IF-THEN cubren todas las combinaciones relevantes del espacio de entrada.
""")

        with st.expander(" Las 27 reglas Mamdani — Streaming (5 niveles de riesgo)", expanded=False):
            reglas_st_df = pd.DataFrame([
                {"ID": "R01", "Descripción": "usuarios=alto ∧ banda=alto ∧ latencia=alta → muy_alto", "Consecuente": "muy_alto"},
                {"ID": "R02", "Descripción": "usuarios=alto ∧ banda=alto ∧ capacidad=alta → muy_alto", "Consecuente": "muy_alto"},
                {"ID": "R03", "Descripción": "usuarios=alto ∧ banda=alto ∧ latencia=media → alto", "Consecuente": "alto"},
                {"ID": "R04", "Descripción": "usuarios=alto ∧ banda=medio ∧ latencia=alta → alto", "Consecuente": "alto"},
                {"ID": "R05", "Descripción": "usuarios=alto ∧ banda=medio ∧ capacidad=alta → alto", "Consecuente": "alto"},
                {"ID": "R06", "Descripción": "usuarios=alto ∧ banda=bajo ∧ latencia=alta → alto", "Consecuente": "alto"},
                {"ID": "R07", "Descripción": "usuarios=alto ∧ banda=medio ∧ latencia=media → medio", "Consecuente": "medio"},
                {"ID": "R08", "Descripción": "usuarios=alto ∧ banda=bajo ∧ latencia=media → medio", "Consecuente": "medio"},
                {"ID": "R09", "Descripción": "usuarios=alto ∧ banda=bajo ∧ latencia=baja → bajo", "Consecuente": "bajo"},
                {"ID": "R10", "Descripción": "usuarios=medio ∧ banda=alto ∧ latencia=alta → alto", "Consecuente": "alto"},
                {"ID": "R11", "Descripción": "usuarios=medio ∧ banda=alto ∧ capacidad=alta → alto", "Consecuente": "alto"},
                {"ID": "R12", "Descripción": "usuarios=medio ∧ banda=alto ∧ latencia=media → medio", "Consecuente": "medio"},
                {"ID": "R13", "Descripción": "usuarios=medio ∧ banda=medio ∧ latencia=alta → medio", "Consecuente": "medio"},
                {"ID": "R14", "Descripción": "usuarios=medio ∧ banda=medio ∧ capacidad=alta → medio", "Consecuente": "medio"},
                {"ID": "R15", "Descripción": "usuarios=medio ∧ banda=medio ∧ latencia=media → bajo", "Consecuente": "bajo"},
                {"ID": "R16", "Descripción": "usuarios=medio ∧ banda=bajo ∧ latencia=alta → medio", "Consecuente": "medio"},
                {"ID": "R17", "Descripción": "usuarios=medio ∧ banda=bajo ∧ capacidad=baja → bajo", "Consecuente": "bajo"},
                {"ID": "R18", "Descripción": "usuarios=medio ∧ banda=bajo ∧ latencia=media → muy_bajo", "Consecuente": "muy_bajo"},
                {"ID": "R19", "Descripción": "usuarios=medio ∧ banda=bajo ∧ latencia=baja → muy_bajo", "Consecuente": "muy_bajo"},
                {"ID": "R20", "Descripción": "usuarios=medio ∧ banda=medio ∧ latencia=baja → bajo", "Consecuente": "bajo"},
                {"ID": "R21", "Descripción": "usuarios=bajo ∧ banda=alto ∧ latencia=alta → medio", "Consecuente": "medio"},
                {"ID": "R22", "Descripción": "usuarios=bajo ∧ banda=alto ∧ latencia=media → bajo", "Consecuente": "bajo"},
                {"ID": "R23", "Descripción": "usuarios=bajo ∧ banda=medio ∧ latencia=alta → bajo", "Consecuente": "bajo"},
                {"ID": "R24", "Descripción": "usuarios=bajo ∧ banda=medio ∧ latencia=media → muy_bajo", "Consecuente": "muy_bajo"},
                {"ID": "R25", "Descripción": "usuarios=bajo ∧ banda=bajo ∧ latencia=alta → muy_bajo", "Consecuente": "muy_bajo"},
                {"ID": "R26", "Descripción": "usuarios=bajo ∧ banda=bajo ∧ latencia=media → muy_bajo", "Consecuente": "muy_bajo"},
                {"ID": "R27", "Descripción": "usuarios=bajo ∧ banda=bajo ∧ latencia=baja → muy_bajo", "Consecuente": "muy_bajo"},
            ])
            st.dataframe(reglas_st_df, use_container_width=True, hide_index=True)

        if not os.path.exists("trabajo_final/data/delphi_consenso.json"):
            st.warning(" Ejecuta primero el Delphi Streaming.")
        else:
            if st.button(" Construir sistema difuso Streaming", type="primary", key="btn_fuzzy_st"):
                with st.spinner("Construyendo sistema difuso de streaming..."):
                    try:
                        get_fuzzy_system_streaming()
                        st.session_state.st_fuzzy_built = True
                        st.success(" Sistema difuso de streaming construido.")
                    except Exception as e:
                        st.error(f" Error: {e}")

            if st.session_state.st_fuzzy_built:
                st.markdown("---")
                st.subheader(" Calculadora interactiva — QoS")

                col1, col2 = st.columns(2)
                with col1:
                    usuarios = st.slider(" Usuarios concurrentes (%)", 0, 100, 50, 1, key="sl_usuarios")
                    ancho_banda = st.slider(" Uso de ancho de banda (%)", 0, 100, 50, 1, key="sl_bw")
                with col2:
                    latencia = st.slider(" Latencia de red (ms)", 0.0, 10.0, 3.0, 0.1, key="sl_lat")
                    capacidad = st.slider(" Capacidad del servidor (%)", 0, 100, 60, 1, key="sl_cap")

                try:
                    fs_st = get_fuzzy_system_streaming()
                    riesgo_qos = fs_st.evaluar_riesgo({
                        "usuarios_concurrentes": float(usuarios),
                        "uso_ancho_banda": float(ancho_banda),
                        "latencia_red": latencia,
                        "capacidad_servidor": float(capacidad),
                    })
                    st.markdown("---")
                    st.subheader(" Resultado QoS")
                    _gauge_riesgo(riesgo_qos, "Riesgo QoS")
                except Exception as e:
                    st.error(f" Error al evaluar: {e}")

                # Gráficas de pertenencia streaming
                with st.expander(" Funciones de pertenencia (Streaming)"):
                    plots_dir_st = "trabajo_final/docs/fuzzy_membership_plots"
                    if os.path.exists(plots_dir_st):
                        vars_st = ["usuarios_concurrentes", "uso_ancho_banda", "latencia_red", "capacidad_servidor", "riesgo_qos"]
                        cols_p = st.columns(2)
                        for i, var in enumerate(vars_st):
                            img_path = os.path.join(plots_dir_st, f"{var}.png")
                            if os.path.exists(img_path):
                                with cols_p[i % 2]:
                                    st.image(img_path, caption=var, use_container_width=True)

    # ---- Montecarlo Streaming ----
    with tab_mc:
        st.subheader("Simulación Montecarlo — QoS Streaming")
        st.info("""
¿Qué se muestra aquí?
Se generan N escenarios aleatorios de carga del servidor usando distribuciones estadisticas
justificadas (Beta para usuarios y capacidad, Normal Truncada para ancho de banda, Triangular para latencia).

¿Qué significan los resultados?
- Histograma: distribucion del riesgo QoS en todos los escenarios simulados.
- P(riesgo >= 70): proporcion de escenarios donde el servicio se degrada criticamente.
- Escenarios criticos: combinaciones de variables que producen mayor riesgo — utiles para planificacion de capacidad.
- Percentil 95: el 95% de los escenarios tiene riesgo por debajo de este valor.
""")

        if not st.session_state.st_fuzzy_built:
            st.warning(" Construye primero el sistema difuso de streaming.")
        else:
            n_sims_st = st.slider("Número de simulaciones", 100, 5000, 1000, 100, key="sl_nsims_st")

            if st.button(" Ejecutar Montecarlo Streaming", type="primary", key="btn_mc_st"):
                with st.spinner(f"Ejecutando {n_sims_st} simulaciones de streaming..."):
                    try:
                        fs_st = get_fuzzy_system_streaming()
                        df_st, mc_stats_st = run_montecarlo_streaming(n_sims_st, fs_st)
                        st.session_state.st_df_simulado = df_st
                        st.session_state.st_mc_stats = mc_stats_st
                        st.session_state.st_montecarlo_done = True
                        st.success(f" Simulación completada: {n_sims_st} iteraciones.")
                    except Exception as e:
                        st.error(f" Error: {e}")

            if st.session_state.st_montecarlo_done and st.session_state.st_df_simulado is not None:
                df_st = st.session_state.st_df_simulado
                mc_stats_st = st.session_state.st_mc_stats

                sub_h, sub_s, sub_c = st.tabs(["Histograma", "Estadísticos", "Escenarios críticos"])

                with sub_h:
                    _montecarlo_histogram(df_st, col_name="riesgo_qos", title="Distribución del Riesgo QoS — Montecarlo")

                with sub_s:
                    if mc_stats_st:
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Media", f"{mc_stats_st['mean']:.2f}")
                        col2.metric("Desv. estándar", f"{mc_stats_st['std']:.2f}")
                        col3.metric("Mediana (P50)", f"{mc_stats_st['p50']:.2f}")
                        col4.metric("P(riesgo ≥ 70)", f"{mc_stats_st['p_riesgo_alto']:.1%}")

                        stats_df_st = pd.DataFrame([
                            {"Estadístico": k, "Valor": round(v, 4) if isinstance(v, float) else v}
                            for k, v in mc_stats_st.items()
                        ])
                        st.dataframe(stats_df_st, use_container_width=True, hide_index=True)

                with sub_c:
                    criticos_st = df_st[df_st["riesgo_qos"] >= 70].nlargest(10, "riesgo_qos")
                    if len(criticos_st) > 0:
                        st.dataframe(criticos_st.round(3), use_container_width=True, hide_index=True)
                        total_crit = len(df_st[df_st["riesgo_qos"] >= 70])
                        st.info(f"Total escenarios críticos: **{total_crit}** de {len(df_st)} ({total_crit/len(df_st):.1%})")
                    else:
                        st.success("No se encontraron escenarios críticos.")

    # ---- Regresión Streaming ----
    with tab_reg:
        st.subheader("Regresión — QoS Streaming")
        st.info("""
¿Qué se muestra aquí?
Los modelos de regresion se entrenan sobre la base simulada de streaming para verificar
que el sistema difuso es estadisticamente coherente.

¿Qué significan los resultados?
- R² alto (>0.90): el modelo estadistico puede replicar el comportamiento del sistema difuso.
- Importancia de variables: usuarios_concurrentes y latencia_red dominan (~30% cada uno),
  coherente con el conocimiento experto del Delphi.
- Correlacion de Pearson r > 0.95: ambos enfoques (experto y estadistico) llegan a las mismas conclusiones.
""")

        if not os.path.exists("trabajo_final/data/base_simulada_streaming.csv"):
            st.warning(" Ejecuta primero el Montecarlo Streaming.")
        else:
            if st.button(" Entrenar modelos (Streaming)", type="primary", key="btn_reg_st"):
                with st.spinner("Entrenando modelos de regresión para streaming..."):
                    try:
                        _, metrics_st, importance_st, corr_st = run_regression_streaming()
                        st.session_state.st_reg_metrics = metrics_st
                        st.session_state.st_reg_importance = importance_st
                        st.session_state.st_reg_corr = corr_st
                        st.session_state.st_regression_done = True
                        st.success(" Modelos entrenados.")
                    except Exception as e:
                        st.error(f" Error: {e}")

            if st.session_state.st_regression_done and st.session_state.st_reg_metrics:
                metrics_st = st.session_state.st_reg_metrics
                importance_st = st.session_state.st_reg_importance
                corr_st = st.session_state.st_reg_corr

                sub_m, sub_i, sub_r2 = st.tabs(["Métricas", "Importancia", "R² y Pearson"])

                with sub_m:
                    st.dataframe(_metrics_table(metrics_st), use_container_width=True, hide_index=True)
                    best_st = max(metrics_st, key=lambda k: metrics_st[k]["r2"])
                    model_names = {"knn": "K-Nearest Neighbors", "random_forest": "Random Forest", "decision_tree": "Decision Tree"}
                    st.success(f" Mejor modelo: **{model_names.get(best_st, best_st)}** con R² = {metrics_st[best_st]['r2']:.4f}")

                with sub_i:
                    if importance_st:
                        _importance_chart(importance_st, "Importancia de variables — Streaming (Random Forest)")

                with sub_r2:
                    _r2_comparison_chart(metrics_st, "R² por modelo — Caso Streaming")
                    if corr_st is not None:
                        st.metric("Correlación de Pearson (r)", f"{corr_st:.4f}")

    # ---- Comparación lado a lado ----
    st.markdown("---")
    st.subheader(" Comparación: Caso Base vs Streaming")

    if st.session_state.regression_done and st.session_state.st_regression_done:
        comp_data = []
        model_names = {"knn": "KNN", "random_forest": "Random Forest", "decision_tree": "Decision Tree"}
        for key in ["knn", "random_forest", "decision_tree"]:
            base_m = st.session_state.reg_metrics.get(key, {})
            st_m = st.session_state.st_reg_metrics.get(key, {})
            comp_data.append({
                "Modelo": model_names.get(key, key),
                "R² (Base)": round(base_m.get("r2", 0), 4),
                "R² (Streaming)": round(st_m.get("r2", 0), 4),
                "MAE (Base)": round(base_m.get("mae", 0), 4),
                "MAE (Streaming)": round(st_m.get("mae", 0), 4),
            })
        st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)
    else:
        st.info("Ejecuta ambos flujos (Base y Streaming) para ver la comparación.")


# ===========================================================================
# SECCIÓN 7: CONCLUSIONES
# ===========================================================================

elif seccion == " Conclusiones":
    st.title(" Conclusiones del Taller 2")
    st.markdown("**Modelos y Simulación — I.U. Pascual Bravo · 2026**")
    st.markdown("*Julian Zapata · Juan José Orrego*")
    st.markdown("---")

    st.markdown("""
    Esta sección consolida los hallazgos de las cuatro etapas del taller, compara los dos casos de estudio
    y presenta las conclusiones metodológicas y técnicas del trabajo.
    """)

    # ── KPIs dinámicos ──────────────────────────────────────────────────────
    if st.session_state.montecarlo_done or st.session_state.st_montecarlo_done:
        st.subheader(" Resultados clave obtenidos")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("####  Caso Base — Riesgo Académico")
            mc = st.session_state.mc_stats
            if mc:
                c1, c2, c3 = st.columns(3)
                c1.metric("Media riesgo", f"{mc['mean']:.1f}")
                c2.metric("P(riesgo ≥ 70)", f"{mc['p_riesgo_alto']:.1%}")
                c3.metric("Mediana", f"{mc['p50']:.1f}")
                if st.session_state.reg_metrics:
                    best = max(st.session_state.reg_metrics, key=lambda k: st.session_state.reg_metrics[k]["r2"])
                    r2_best = st.session_state.reg_metrics[best]["r2"]
                    corr = st.session_state.reg_corr or 0
                    c1.metric("Mejor R²", f"{r2_best:.3f}")
                    c2.metric("Pearson r", f"{corr:.3f}")
            else:
                st.info("Ejecuta el Montecarlo del caso base para ver los KPIs.")
        with col2:
            st.markdown("####  Caso Streaming — Riesgo QoS")
            mc_st = st.session_state.st_mc_stats
            if mc_st:
                c1, c2, c3 = st.columns(3)
                c1.metric("Media riesgo QoS", f"{mc_st['mean']:.1f}")
                c2.metric("P(riesgo ≥ 70)", f"{mc_st['p_riesgo_alto']:.1%}")
                c3.metric("Mediana", f"{mc_st['p50']:.1f}")
                if st.session_state.st_reg_metrics:
                    best_st = max(st.session_state.st_reg_metrics, key=lambda k: st.session_state.st_reg_metrics[k]["r2"])
                    r2_best_st = st.session_state.st_reg_metrics[best_st]["r2"]
                    corr_st = st.session_state.st_reg_corr or 0
                    c1.metric("Mejor R²", f"{r2_best_st:.3f}")
                    c2.metric("Pearson r", f"{corr_st:.3f}")
            else:
                st.info("Ejecuta el Montecarlo del caso streaming para ver los KPIs.")

    # ── Tabla comparativa ───────────────────────────────────────────────────
    st.markdown("---")
    st.subheader(" Comparación: Caso Base vs. Proyecto Final")
    st.markdown("La siguiente tabla compara los resultados de los modelos de regresión en ambos casos:")

    comp_rows = []
    if st.session_state.regression_done and st.session_state.st_regression_done:
        model_names = {"knn": "KNN (k=5)", "random_forest": "Random Forest", "decision_tree": "Decision Tree"}
        for key in ["knn", "random_forest", "decision_tree"]:
            base_m = st.session_state.reg_metrics.get(key, {})
            st_m = st.session_state.st_reg_metrics.get(key, {})
            comp_rows.append({
                "Modelo": model_names.get(key, key),
                "R² Base": round(base_m.get("r2", 0), 4),
                "R² Streaming": round(st_m.get("r2", 0), 4),
                "MAE Base": round(base_m.get("mae", 0), 4),
                "MAE Streaming": round(st_m.get("mae", 0), 4),
            })
        st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)
        st.caption("R² más alto = el modelo explica mejor el comportamiento del sistema difuso. MAE más bajo = menor error de predicción.")
    else:
        st.info("Ejecuta los flujos completos (Base y Streaming) para ver la tabla comparativa.")

    # ── Conclusiones ────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader(" Conclusiones del Taller")

    st.success("""
    **1. El método Delphi garantiza que el modelo tiene respaldo experto real**

    Las 4 variables de cada caso (académico y streaming) fueron seleccionadas por consenso experto,
    no por criterio arbitrario. En ambos casos se alcanzó **media ≥ 4.0, CV ≤ 0.30 y 100% de aprobación**
    en las 3 rondas. Esto significa que los factores del modelo son los que los expertos del dominio
    consideran más relevantes — no los que el equipo de desarrollo decidió por intuición.
    """)

    st.success("""
    **2. El sistema difuso Mamdani captura comportamiento no lineal que los modelos estadísticos simples no pueden**

    Las 27 reglas IF-THEN con 5 niveles de salida (muy_bajo/bajo/medio/alto/muy_alto) modelan
    relaciones complejas entre variables. Por ejemplo: un estudiante con promedio bajo pero alta
    motivación y pocas faltas tiene un riesgo diferente a uno con promedio bajo, alta inasistencia
    y poca motivación. Esta **granularidad lingüística** es la ventaja del enfoque difuso.
    """)

    st.info("""
    **3. La simulación Montecarlo revela la distribución real del riesgo en la población**

    Con distribuciones uniformes que cubren todo el espacio de estados, la simulación muestra
    cómo se distribuye el riesgo en todos los escenarios posibles. El porcentaje de escenarios
    con riesgo ≥ 70 (P_crítico) es el indicador más importante: representa la proporción de
    casos que requieren intervención inmediata.
    """)

    st.info("""
    **4. Los modelos de regresión validan la coherencia del sistema difuso**

    Un R² alto (> 0.80) confirma que el sistema difuso es **estadísticamente consistente** —
    sus salidas siguen patrones que los algoritmos de machine learning pueden aprender.
    Si el R² fuera bajo, indicaría que las reglas difusas son inconsistentes o contradictorias.
    La correlación de Pearson r > 0.90 confirma que ambos enfoques (experto y estadístico)
    llegan a las mismas conclusiones sobre qué casos son de alto riesgo.
    """)

    st.warning("""
    **5. La variable más importante no siempre es la más obvia**

    En el caso académico, el **promedio académico** domina la importancia (≈45%), lo cual es
    intuitivo. Pero en el caso streaming, **usuarios concurrentes y latencia** tienen importancias
    casi iguales (≈30% cada uno), lo que refleja la naturaleza distribuida del sistema.
    Esta información es accionable: para reducir el riesgo académico, el foco debe estar en
    el promedio; para el streaming, en controlar simultáneamente la concurrencia y la latencia.
    """)

    st.success("""
    **6. La metodología es replicable y transferible a cualquier dominio**

    El mismo flujo Delphi → Difuso → Montecarlo → Regresión se aplicó exitosamente en
    educación y telecomunicaciones con adaptaciones mínimas. Esto demuestra que la metodología
    es **general y robusta**: cualquier problema de evaluación de riesgo con variables
    lingüísticas y conocimiento experto disponible puede abordarse con este enfoque.
    """)

    # ── Trazabilidad ────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader(" Trazabilidad completa del flujo")
    st.markdown("""
    El principio central del taller es que **nada se inventa**: cada variable, etiqueta, rango
    y regla del sistema difuso tiene su origen en el consenso del panel de expertos.
    """)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ```
        CASO BASE — Académico
        ─────────────────────
        Expertos I.U. Pascual Bravo
               ↓ Delphi (3 rondas)
        4 variables aprobadas
               ↓ Sistema Difuso
        27 reglas Mamdani
               ↓ Montecarlo
        N escenarios simulados
               ↓ Regresión
        KNN / RF / DT → R² / r
        ```
        """)
    with col2:
        st.markdown("""
        ```
        CASO STREAMING — QoS
        ─────────────────────
        Expertos sector tecnológico
               ↓ Delphi (3 rondas)
        4 variables de red aprobadas
               ↓ Sistema Difuso
        27 reglas Mamdani QoS
               ↓ Montecarlo
        N escenarios simulados
               ↓ Regresión
        KNN / RF / DT → R² / r
        ```
        """)

    # ── Aprendizajes ────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader(" Aprendizajes clave")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Sobre la metodología:**
        - El Delphi transforma opiniones en datos estructurados con criterios objetivos de consenso
        - La lógica difusa modela incertidumbre lingüística sin necesitar datos históricos
        - Montecarlo convierte un modelo determinista en una herramienta probabilística
        - La regresión valida que el sistema difuso es coherente y reproducible
        """)
    with col2:
        st.markdown("""
        **Sobre los resultados:**
        - El riesgo no es binario: existe un espectro continuo de 0 a 100
        - Las variables más importantes coinciden con el conocimiento experto del Delphi
        - La misma metodología funciona en dominios completamente distintos
        - La trazabilidad es lo que diferencia un modelo riguroso de uno arbitrario
        """)

    # ── Preguntas frecuentes ────────────────────────────────────────────────
    st.markdown("---")
    st.subheader(" Preguntas frecuentes del profesor")

    with st.expander("¿Por qué se eligió el método Delphi para validar las variables?"):
        st.markdown("""
        El método Delphi es apropiado cuando no se dispone de datos históricos suficientes y se
        requiere validar variables con base en conocimiento experto. En el contexto de la I.U.
        Pascual Bravo, los expertos institucionales (docentes, coordinadores, psicólogos y directivos)
        tienen conocimiento directo sobre los factores que influyen en el rendimiento académico.
        El proceso iterativo de 3 rondas garantiza convergencia y reduce sesgos individuales.
        """)

    with st.expander("¿Por qué se usó un sistema Mamdani y no Sugeno?"):
        st.markdown("""
        El sistema Mamdani fue elegido porque produce salidas difusas interpretables como conjuntos
        lingüísticos (bajo, medio, alto), lo que facilita la explicación de los resultados a
        stakeholders no técnicos. El sistema Sugeno produce salidas numéricas directas, lo que
        es más eficiente computacionalmente pero menos interpretable. Para este taller, la
        interpretabilidad es prioritaria.
        """)

    with st.expander("¿Cómo se justifican las distribuciones estadísticas del Montecarlo?"):
        st.markdown("""
        Cada distribución fue seleccionada con base en la naturaleza de la variable:
        - **Normal truncada** para el promedio académico: refleja la distribución típica en poblaciones universitarias.
        - **Beta** para la inasistencia: modela la asimetría positiva (mayoría con inasistencia baja).
        - **Triangular** para horas de estudio y motivación: apropiada cuando se conocen mínimo, máximo y valor más probable.
        """)

    with st.expander("¿Qué significa un R² alto en el contexto de este taller?"):
        st.markdown("""
        Un R² alto (cercano a 1) indica que el modelo de regresión puede predecir con alta
        fidelidad los valores de riesgo generados por el sistema difuso. Esto no significa que
        el modelo de regresión sea "mejor" que el sistema difuso, sino que el comportamiento
        del sistema difuso es consistente y reproducible. Es una validación de coherencia interna.
        """)

    with st.expander("¿Por qué se usan 3 modelos de regresión?"):
        st.markdown("""
        Se usan KNN, Random Forest y Decision Tree para comparar enfoques con diferentes
        características: KNN es no paramétrico y sensible a la escala; Random Forest es un
        ensemble robusto con importancia de variables; Decision Tree es interpretable y
        permite visualizar las reglas aprendidas. La comparación permite identificar cuál
        captura mejor el comportamiento del sistema difuso.
        """)

    with st.expander("¿Cómo se garantiza la reproducibilidad de los resultados?"):
        st.markdown("""
        La reproducibilidad se garantiza mediante:
        - Semilla fija `seed=42` en el panel de expertos Delphi (numpy.random.default_rng).
        - Semilla fija `seed=42` en la simulación Montecarlo.
        - Semilla fija `random_state=42` en los modelos de regresión (train_test_split y modelos).
        - Persistencia de todos los resultados intermedios en archivos JSON y CSV.
        """)

