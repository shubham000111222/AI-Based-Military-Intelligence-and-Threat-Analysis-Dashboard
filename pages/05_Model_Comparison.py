"""
05_Model_Comparison.py - Multi-Model Benchmark, Reliability Curves & Error Breakdown.
Features:
- Side-by-side metric comparison table (Accuracy, Macro-F1, Weighted-F1, Top-3 Accuracy)
- Interactive Confusion Matrix viewer (Counts and Normalized %)
- Reliability diagrams (Calibration curves) per class and model
- Geographic Theatre Macro-F1 performance breakdown
- Analytical interpretation of champion model advantages and failure modes.
"""

import json

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.config import (
    ETHICAL_DISCLAIMER,
    METRICS_JSON_PATH,
)

st.set_page_config(
    page_title="Model Benchmark & Comparison | GTD Analysis",
    page_icon="⚖️",
    layout="wide",
)


@st.cache_data
def load_metrics():
    if not METRICS_JSON_PATH.exists():
        st.error(f"Metrics report not found at '{METRICS_JSON_PATH}'. Run 'python scripts/train_attack_model.py'.")
        st.stop()
    with open(METRICS_JSON_PATH, "r") as f:
        return json.load(f)


def main():
    st.title("05 · Model Benchmark & Evaluation Comparison")
    st.caption("Temporal Backtest Evaluation (Train <= 2012, Test 2013–2017) Across Candidate Architectures")

    st.info(f"**HISTORICAL & RESEARCH DIRECTIVE**: {ETHICAL_DISCLAIMER}")

    report = load_metrics()
    meta = report["metadata"]
    models_data = report["models"]
    best_model = meta.get("best_model", "LightGBM")

    # Metadata Telemetry Cards
    st.markdown("### 📊 Backtest Protocol & Scope")
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("TRAIN SAMPLES", f"{meta['train_samples']:,} (<= 2012)")
    with m2:
        st.metric("TEST SAMPLES", f"{meta['test_samples']:,} (2013–2017)")
    with m3:
        st.metric("TARGET CLASSES", f"{len(meta['classes'])}")
    with m4:
        st.metric("MODEL FEATURES", f"{meta['feature_count']}")
    with m5:
        st.metric("CHAMPION MODEL", best_model)

    st.markdown("---")

    # Section 1: Side-by-side Metric Table
    st.markdown("### 🏆 Comprehensive Model Leaderboard")
    st.caption("All models evaluated strictly out-of-time on 2013–2017 test incidents:")

    table_rows = []
    for mname, mval in models_data.items():
        table_rows.append({
            "Candidate Architecture": mname,
            "Accuracy": f"{mval['accuracy']:.4f}",
            "Macro-F1": f"{mval['macro_f1']:.4f}",
            "Weighted-F1": f"{mval['weighted_f1']:.4f}",
            "Top-3 Accuracy": f"{mval['top3_accuracy']:.4f}",
            "Training Time (s)": f"{mval.get('train_time_sec', 0.0):.2f}",
        })

    leaderboard_df = pd.DataFrame(table_rows)
    st.dataframe(
        leaderboard_df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # Section 2: Interactive Confusion Matrix
    st.markdown("### 🧩 Confusion Matrix Visualizer")
    col_sel_model, col_norm = st.columns([2, 1])

    with col_sel_model:
        selected_cm_model = st.selectbox("Select Model Architecture", list(models_data.keys()), index=list(models_data.keys()).index(best_model))
    with col_norm:
        normalize_cm = st.checkbox("Normalize by True Class Row (%)", value=True)

    cm_data = models_data[selected_cm_model]["confusion_matrix"]
    classes = models_data[selected_cm_model]["classes"]
    cm_matrix = np.array(cm_data)

    if normalize_cm:
        row_sums = cm_matrix.sum(axis=1)[:, np.newaxis]
        # Avoid division by zero
        cm_display = np.divide(cm_matrix, row_sums, out=np.zeros_like(cm_matrix, dtype=float), where=row_sums != 0) * 100
        cm_display = np.round(cm_display, 1)
        z_title = "Recall (%)"
        fmt = ".1f"
    else:
        cm_display = cm_matrix
        z_title = "Incident Count"
        fmt = "d"

    fig_cm = px.imshow(
        cm_display,
        x=classes,
        y=classes,
        text_auto=fmt,
        color_continuous_scale="Reds",
        labels=dict(x="Predicted Tactic", y="Actual Tactic", color=z_title),
        template="plotly_dark",
    )
    fig_cm.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#1A1D24",
        margin=dict(l=40, r=40, t=30, b=40),
        height=450,
    )
    st.plotly_chart(fig_cm, use_container_width=True)

    st.markdown("---")

    # Section 3: Calibration Curves (Reliability Diagrams)
    st.markdown("### 📐 Reliability Diagrams (Calibration Curves)")
    st.caption(
        "Evaluates probability calibration: a well-calibrated model produces predicted probabilities "
        "matching empirical observed frequencies along the 45° diagonal."
    )

    selected_class_calib = st.selectbox("Tactical Class for Reliability Curve", classes, index=2 if len(classes) > 2 else 0)

    fig_calib = go.Figure()

    # Perfectly calibrated benchmark
    fig_calib.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            name="Perfect Calibration (Ideal)",
            line=dict(color="#757575", dash="dash", width=1.5),
        )
    )

    colors = ["#9E9E9E", "#00E5FF", "#FFD600", "#FF1744"]
    for idx, (mname, mval) in enumerate(models_data.items()):
        calib_dict = mval.get("calibration_curves", {}).get(selected_class_calib, {})
        p_pred = calib_dict.get("prob_pred", [])
        p_true = calib_dict.get("prob_true", [])
        if len(p_pred) > 0 and len(p_true) > 0:
            fig_calib.add_trace(
                go.Scatter(
                    x=p_pred,
                    y=p_true,
                    mode="lines+markers",
                    name=mname,
                    line=dict(color=colors[idx % len(colors)], width=2),
                    marker=dict(size=6),
                )
            )

    fig_calib.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        plot_bgcolor="#1A1D24",
        xaxis=dict(title="Mean Predicted Probability", range=[0, 1], gridcolor="#2B313D"),
        yaxis=dict(title="Fraction of Positives (Empirical)", range=[0, 1], gridcolor="#2B313D"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=30, b=40),
        height=420,
    )
    st.plotly_chart(fig_calib, use_container_width=True)

    st.markdown("---")

    # Section 4: Geographic Theatre Error Breakdown
    st.markdown("### 🌍 Geographic Performance Disparity (Macro-F1 by Theatre)")
    st.caption("Exposes geographic error variance across sovereign theatres:")

    # Build regional comparison table
    reg_rows = []
    sample_reg_dict = models_data[best_model].get("per_region_macro_f1", {})
    all_regions = sorted(sample_reg_dict.keys())

    for r in all_regions:
        row = {"Theatre": r, "Test Incidents": sample_reg_dict[r]["sample_count"]}
        for mname, mval in models_data.items():
            r_dict = mval.get("per_region_macro_f1", {}).get(r, {})
            row[mname] = r_dict.get("macro_f1", 0.0)
        reg_rows.append(row)

    reg_df = pd.DataFrame(reg_rows)

    fig_reg_f1 = px.bar(
        reg_df,
        x="Theatre",
        y=[m for m in models_data.keys() if m != "Baseline (Majority Class)"],
        barmode="group",
        template="plotly_dark",
        title="Macro-F1 Performance across Geographic Theatres",
    )
    fig_reg_f1.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#1A1D24",
        margin=dict(l=20, r=20, t=40, b=30),
        xaxis=dict(tickangle=-25),
        height=380,
    )
    st.plotly_chart(fig_reg_f1, use_container_width=True)

    st.markdown("---")

    # Section 5: Analytical Interpretation
    st.markdown("### 📝 Analytical Synthesis: Why the Champion Wins & Where It Fails")
    st.markdown(
        """
        #### 1. Why Gradient Boosted Trees (LightGBM) & Random Forest Outperform Baselines
        - **Non-Linear Geographic & Tactical Coupling:** Linear models fail to capture compound regional rules (e.g. Firearms in South America correlating heavily with Assassinations, while Explosives in Middle East correlate with Bombing/Explosion). Tree ensembles partition this high-cardinality interaction space without combinatorial feature explosion.
        - **Class-Weight Rebalancing:** Unweighted baselines predict the majority class (Bombing/Explosion) nearly 100% of the time. Balanced class weights enable trees to correctly identify minority tactics like Assassinations and Facility Attacks.

        #### 2. Primary Failure Modes & Boundary Limitations
        - **Unclaimed Incidents (Unknown Perpetrator):** In active insurgencies with unclaimed attacks, the absence of group doctrine removes a primary predictive anchor, forcing the model to rely solely on weapon and location.
        - **Tactical Ambiguity of Weapons:** Firearms are used across Armed Assaults, Assassinations, and Kidnappings; without post-event outcome data (which is strictly withheld to prevent data leakage), distinguishing these tactics ex-ante remains fundamentally challenging.
        - **Temporal Drift Post-2012:** Syrian and Iraqi battlefield evolutions post-2012 introduced tactical patterns not present in pre-2012 training data, demonstrating the inevitable performance degradation of historical static models.
        """
    )


if __name__ == "__main__":
    main()
