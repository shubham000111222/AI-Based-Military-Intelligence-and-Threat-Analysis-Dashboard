"""
07_Scenario_Simulator.py - Dynamic Risk Scenario & Weight Sensitivity Simulator.
Features:
- Live parameter adjustment sliders for the 4 component weights
- Outlier casualty capping slider to test sensitivity to mega-events
- Dynamic country re-ranking with Kendall-tau ranking stability benchmark
- Rank change bar chart displaying top shift gainers and decliners
- Side-by-side comparison table of Default vs Simulated rankings.
"""

import plotly.graph_objects as go
import streamlit as st

from src.config import (
    DEFAULT_RISK_WEIGHTS,
    ETHICAL_DISCLAIMER,
    MISSING_YEAR,
    PROCESSED_DATA_PATH,
)
from src.data_loader import load_dataset
from src.risk_index import (
    calculate_risk_index,
    evaluate_ranking_stability,
    normalize_weights,
)

st.set_page_config(
    page_title="Risk Scenario Simulator | GTD Analysis",
    page_icon="🎛️",
    layout="wide",
)


@st.cache_data(show_spinner="Loading Intelligence Dataset...")
def get_sim_data():
    return load_dataset(PROCESSED_DATA_PATH)


def main():
    st.title("07 · Strategic Risk Scenario & Sensitivity Simulator")
    st.caption("Stress-Testing Country Threat Rankings under Custom Policy Assumptions")

    st.info(f"**HISTORICAL & RESEARCH DIRECTIVE**: {ETHICAL_DISCLAIMER}")

    df = get_sim_data()

    available_years = sorted([y for y in df["iyear"].unique() if y != MISSING_YEAR])
    default_year = max(available_years)

    st.sidebar.markdown("### 🎛️ Simulation Parameters")

    sim_year = st.sidebar.select_slider(
        "Evaluation Year",
        options=available_years,
        value=default_year,
    )

    st.sidebar.markdown("#### Component Weight Sliders")
    w_inc = st.sidebar.slider("Incident Volume Weight", 0.0, 1.0, DEFAULT_RISK_WEIGHTS["log_incidents"], step=0.05)
    w_cas = st.sidebar.slider("Casualty Severity Weight", 0.0, 1.0, DEFAULT_RISK_WEIGHTS["log_casualties"], step=0.05)
    w_trend = st.sidebar.slider("3-Yr Momentum Slope Weight", 0.0, 1.0, DEFAULT_RISK_WEIGHTS["trend_slope"], step=0.05)
    w_mass = st.sidebar.slider("Mass-Casualty Vulnerability Weight", 0.0, 1.0, DEFAULT_RISK_WEIGHTS["mass_casualty_ratio"], step=0.05)

    st.sidebar.markdown("#### Outlier Robustness Controls")
    apply_cap = st.sidebar.checkbox("Cap Casualties per Incident", value=False)
    cas_cap = st.sidebar.slider("Max Casualties per Incident Cap", 10, 500, 50, step=10) if apply_cap else None

    # Compute baseline ranking (default weights)
    df_base = calculate_risk_index(df, year=sim_year, weights=DEFAULT_RISK_WEIGHTS, casualty_cap=None)

    # Compute scenario ranking (custom weights)
    custom_weights = {
        "log_incidents": w_inc,
        "log_casualties": w_cas,
        "trend_slope": w_trend,
        "mass_casualty_ratio": w_mass,
    }
    norm_w = normalize_weights(custom_weights)

    df_sim = calculate_risk_index(df, year=sim_year, weights=norm_w, casualty_cap=cas_cap)

    if df_base.empty or df_sim.empty:
        st.warning(f"Insufficient data for simulation in year {sim_year}.")
        st.stop()

    # Calculate Kendall's tau and rank change
    tau, comp_df = evaluate_ranking_stability(df_base, df_sim)

    # Section 1: Sensitivity Benchmark KPI Cards
    st.markdown("### 🧪 Sensitivity & Rank Stability Telemetry")

    k1, k2, k3, k4 = st.columns(4)

    # Gauge status based on tau
    if tau >= 0.85:
        stability_desc = "ROBUST (Low Sensitivity)"
        tau_color = "#00E676"
    elif tau >= 0.70:
        stability_desc = "MODERATE SENSITIVITY"
        tau_color = "#FFD600"
    else:
        stability_desc = "HIGH SENSITIVITY (Volatile)"
        tau_color = "#FF1744"

    with k1:
        st.metric(
            "KENDALL-TAU STABILITY (τ)",
            f"{tau:.4f}",
            help="Measures rank correlation (-1.0 to 1.0) against baseline default weights.",
        )
    with k2:
        st.markdown(
            f"""
            <div style="background-color: #1A1D24; border: 1px solid #2B313D; border-radius: 8px; padding: 14px;">
                <div style="font-size: 0.75rem; color: #9E9E9E; text-transform: uppercase;">RANKING ROBUSTNESS</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: {tau_color}; margin-top: 4px;">{stability_desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k3:
        max_gain = comp_df["rank_change"].max()
        st.metric("MAX RANK SURGE", f"+{int(max_gain)} positions", delta_color="normal")
    with k4:
        max_drop = comp_df["rank_change"].min()
        st.metric("MAX RANK DROP", f"{int(max_drop)} positions", delta_color="inverse")

    st.markdown("---")

    # Section 2: Rank Shift Bar Chart (Top Gainers and Decliners)
    st.markdown("### 📊 Sovereign Rank Shifts vs. Default Weights")
    st.caption("Positive values indicate countries that rose in threat rank under custom scenario weights:")

    # Top 15 absolute rank changers
    comp_df["abs_change"] = comp_df["rank_change"].abs()
    top_movers = comp_df.sort_values("abs_change", ascending=False).head(15).sort_values("rank_change")

    if not top_movers.empty and (top_movers["abs_change"] > 0).any():
        colors = ["#00E676" if c < 0 else "#FF1744" for c in top_movers["rank_change"]]
        fig_shift = go.Figure()
        fig_shift.add_trace(
            go.Bar(
                x=top_movers["rank_change"],
                y=top_movers["country_txt"],
                orientation="h",
                marker_color=colors,
                text=top_movers["rank_change"].apply(lambda v: f"{v:+d}"),
                textposition="outside",
            )
        )
        fig_shift.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#1A1D24",
            xaxis=dict(title="Net Rank Shift (Positive = Higher Threat Rank)", gridcolor="#2B313D"),
            margin=dict(l=30, r=30, t=20, b=20),
            height=400,
        )
        st.plotly_chart(fig_shift, use_container_width=True)
    else:
        st.info("Scenario weights produce identical rankings to the default configuration (zero rank shift).")

    st.markdown("---")

    # Section 3: Side-by-Side Comparison Leaderboard
    st.markdown("### 📋 Side-by-Side Ranking Comparison")
    st.caption("Compare Default Baseline Rank vs Simulated Scenario Rank:")

    view_table = comp_df[[
        "sim_rank",
        "country_txt",
        "base_rank",
        "rank_change",
        "sim_score",
        "base_score",
    ]].rename(columns={
        "sim_rank": "Scenario Rank",
        "country_txt": "Sovereign State",
        "base_rank": "Default Rank",
        "rank_change": "Rank Shift",
        "sim_score": "Scenario Score",
        "base_score": "Default Score",
    })

    st.dataframe(
        view_table,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # Section 4: Mathematical Normalization Explainer
    with st.expander("ℹ️ Active Parameter Normalization Details", expanded=False):
        st.markdown(
            rf"""
            - **Raw User Inputs:** Incidents={w_inc}, Casualties={w_cas}, Momentum={w_trend}, Mass Casualties={w_mass}
            - **Normalized Weights ($\sum w_i = 1.0$):**
              - Incident Volume: `{norm_w['log_incidents'] * 100:.1f}%`
              - Casualty Severity: `{norm_w['log_casualties'] * 100:.1f}%`
              - 3-Year Momentum: `{norm_w['trend_slope'] * 100:.1f}%`
              - Mass-Casualty Ratio: `{norm_w['mass_casualty_ratio'] * 100:.1f}%`
            - **Casualty Cap:** `{'None (Uncapped)' if cas_cap is None else f'{cas_cap} casualties/attack'}`
            """
        )


if __name__ == "__main__":
    main()
