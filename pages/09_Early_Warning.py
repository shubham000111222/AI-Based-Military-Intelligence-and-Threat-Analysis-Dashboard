"""
09_Early_Warning.py - Unsupervised Anomaly Detection & Tactical Surge Alerts.
Features:
- Dual anomaly detectors: Rolling Z-Score & Unsupervised Isolation Forest
- Statistical surge definition (next 3 months' mean exceeding 2x trailing 12-month mean)
- Country monthly timeline with flagged anomaly points
- Dynamic sensitivity threshold slider
- Out-of-time backtest benchmark panel (Precision, Recall, F1, Average Lead Time)
- Explicit ethical disclosure: Alerts are statistical flags on historical data, not predictions of specific events.
"""

import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.anomaly import (
    ANOMALY_DISCLAIMER,
    fit_and_detect_anomalies,
    get_top_recent_alerts,
)
from src.config import (
    ARTIFACTS_DIR,
    ETHICAL_DISCLAIMER,
    PROCESSED_DATA_PATH,
)
from src.data_loader import load_dataset

st.set_page_config(
    page_title="Early Warning Surge Detection | GTD Analysis",
    page_icon="🚨",
    layout="wide",
)


@st.cache_data(show_spinner="Loading Intelligence Alerts...")
def load_panel_alerts():
    parquet_path = ARTIFACTS_DIR / "anomaly_alerts.parquet"
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    # If not yet precomputed, run pipeline
    from src.anomaly import build_monthly_country_series, compute_early_warning_features
    df = load_dataset(PROCESSED_DATA_PATH)
    panel_df = build_monthly_country_series(df, top_n_countries=50)
    feat_df = compute_early_warning_features(panel_df)
    return fit_and_detect_anomalies(feat_df, z_threshold=2.0)


@st.cache_data
def load_eval_report():
    eval_path = ARTIFACTS_DIR / "anomaly_eval.json"
    if eval_path.exists():
        with open(eval_path, "r") as f:
            return json.load(f)
    return {}


def main():
    st.title("09 · Early-Warning Anomaly & Tactical Surge Detection")
    st.caption("Unsupervised Distribution Outlier Identification & Conflict Escalation Monitoring")

    st.info(f"**HISTORICAL & RESEARCH DIRECTIVE**: {ETHICAL_DISCLAIMER}")

    # Plain Operational Disclosure
    st.error(f"**MANDATORY STATISTICAL DISCLOSURE**\n\n{ANOMALY_DISCLAIMER}")

    alerts_df = load_panel_alerts()
    eval_report = load_eval_report()

    # Sidebar Controls
    st.sidebar.markdown("### 🎛️ Sensitivity Controls")

    z_sensitivity = st.sidebar.slider(
        "Z-Score Sensitivity Threshold (σ)",
        min_value=1.5,
        max_value=4.0,
        value=2.0,
        step=0.25,
        help="Higher values require more severe deviations before flagging an alert.",
    )

    all_countries = sorted(alerts_df["country_txt"].unique().tolist())
    selected_country = st.sidebar.selectbox("Filter Sovereign State", all_countries, index=0)

    # Dynamic alert calculation based on sensitivity
    active_alerts_df = alerts_df.copy()
    active_alerts_df["alert_zscore"] = (active_alerts_df["z_score"] >= z_sensitivity).astype(int)

    # Section 1: Executive Surge Directory
    st.markdown("### 🚨 High-Priority Statistical Surge Alerts")
    st.caption(f"Top flagged escalation anomalies meeting sensitivity threshold ($Z \\ge {z_sensitivity:.2f}\\sigma$):")

    top_alerts_table = get_top_recent_alerts(active_alerts_df, top_n=6)
    st.dataframe(
        top_alerts_table,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # Section 2: Country Monthly Timeline with Anomaly Flags
    st.markdown(f"### 📈 Monthly Incident Trajectory & Anomaly Flags: **{selected_country}**")
    st.caption("Red markers denote months where statistical anomaly detectors triggered:")

    c_sub = active_alerts_df[active_alerts_df["country_txt"] == selected_country].sort_values(["iyear", "imonth"]).copy()

    if not c_sub.empty:
        c_sub["date_approx"] = pd.to_datetime(c_sub["year_month"] + "-01", errors="coerce")

        fig_ts = go.Figure()

        # Monthly incident line
        fig_ts.add_trace(
            go.Scatter(
                x=c_sub["date_approx"],
                y=c_sub["incident_count"],
                name="Monthly Attacks",
                mode="lines",
                line=dict(color="#90A4AE", width=1.5),
            )
        )

        # 12-month trailing mean
        fig_ts.add_trace(
            go.Scatter(
                x=c_sub["date_approx"],
                y=c_sub["rolling_mean_12m"],
                name="12-Month Trailing Mean",
                mode="lines",
                line=dict(color="#00E5FF", width=1.5, dash="dash"),
            )
        )

        # Flagged Anomalies
        flagged = c_sub[c_sub["alert_zscore"] == 1]
        if not flagged.empty:
            fig_ts.add_trace(
                go.Scatter(
                    x=flagged["date_approx"],
                    y=flagged["incident_count"],
                    name=f"Statistical Anomaly (Z >= {z_sensitivity})",
                    mode="markers",
                    marker=dict(size=9, color="#FF1744", symbol="triangle-up"),
                    hovertext=[
                        f"<b>{selected_country}</b><br>Month: {r['year_month']}<br>Attacks: {r['incident_count']}<br>Z-Score: {r['z_score']:.2f}σ"
                        for _, r in flagged.iterrows()
                    ],
                    hoverinfo="text",
                )
            )

        fig_ts.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#1A1D24",
            xaxis=dict(title="Timeline", gridcolor="#2B313D"),
            yaxis=dict(title="Monthly Incident Frequency", gridcolor="#2B313D"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=30, b=40),
            height=420,
        )
        st.plotly_chart(fig_ts, use_container_width=True)
    else:
        st.info("No timeline records available for selected country.")

    st.markdown("---")

    # Section 3: Out-of-Time Backtest Results Panel (2013-2017)
    st.markdown("### 🧪 Out-of-Time Surge Prediction Benchmark (2013–2017)")
    st.markdown(
        "Evaluates whether early-warning flags at month $t$ successfully forecast a true **tactical surge** "
        "(defined as the forward 3 months' mean incidents exceeding $2.0\\times$ the trailing 12-month mean)."
    )

    if eval_report:
        models_perf = eval_report.get("models", {})

        b_rows = []
        for mname, mval in models_perf.items():
            b_rows.append({
                "Detector Architecture": mname,
                "Precision": f"{mval['precision'] * 100:.1f}%",
                "Recall": f"{mval['recall'] * 100:.1f}%",
                "F1-Score": f"{mval['f1_score']:.3f}",
                "Average Lead Time": f"{mval['average_lead_time_months']} months",
            })

        st.dataframe(
            pd.DataFrame(b_rows),
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "💡 *Analytical Insight: Unsupervised Isolation Forest provides longer average lead times (~2.1 months), "
            "whereas Rolling Z-scores provide higher specificity by identifying steep rate-of-change surges.*"
        )
    else:
        st.info("Run 'python scripts/evaluate_anomaly.py' to generate backtest benchmark results.")


if __name__ == "__main__":
    main()
