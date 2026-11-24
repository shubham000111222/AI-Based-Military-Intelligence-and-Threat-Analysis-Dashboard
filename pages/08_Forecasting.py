"""
08_Forecasting.py - Longitudinal Threat Forecasting & Backtest Validation.
Features:
- Time-series incident projections with 80% and 95% confidence intervals
- Rigorous out-of-time backtest overlay (Train <= 2012, Test 2013-2017)
- Metric comparison table against Naive and Moving Average baselines (MAE & MAPE)
- 1993 archival gap explicitly annotated on historical series
- Prominent operational guidance on forecasting horizon limits (maximum 5 years).
"""

import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.config import (
    ARTIFACTS_DIR,
    ETHICAL_DISCLAIMER,
    MISSING_YEAR,
    PROCESSED_DATA_PATH,
)
from src.data_loader import load_dataset
from src.forecasting import (
    HORIZON_LIMIT_EXPLANATION,
    MAX_FORECAST_HORIZON,
    generate_future_forecast,
)

st.set_page_config(
    page_title="Threat Forecasting | GTD Analysis",
    page_icon="📈",
    layout="wide",
)


@st.cache_data(show_spinner="Loading Intelligence Dataset...")
def get_data():
    return load_dataset(PROCESSED_DATA_PATH)


@st.cache_data
def get_backtest_report():
    report_path = ARTIFACTS_DIR / "forecast_eval.json"
    if report_path.exists():
        with open(report_path, "r") as f:
            return json.load(f)
    return {}


def main():
    st.title("08 · Longitudinal Threat Forecasting & Backtest Validation")
    st.caption("Statistical Time-Series Projections (Holt-Winters ETS) with Empirical Backtest Validation")

    st.info(f"**HISTORICAL & RESEARCH DIRECTIVE**: {ETHICAL_DISCLAIMER}")

    df = get_data()
    backtest_data = get_backtest_report()

    # Sidebar Controls
    st.sidebar.markdown("### 🎛️ Forecast Configuration")

    theatre_options = ["Global Total"] + sorted(df["region_txt"].dropna().unique().tolist())
    selected_theatre = st.sidebar.selectbox("Geographic Theatre", theatre_options, index=0)

    forecast_horizon = st.sidebar.slider(
        "Forecast Horizon (Years)",
        min_value=1,
        max_value=MAX_FORECAST_HORIZON,
        value=5,
        step=1,
        help="Maximum scientifically valid horizon for violent conflict forecasting is 5 years.",
    )

    # Operational Limit Callout
    st.warning(f"⚠️ **{HORIZON_LIMIT_EXPLANATION}**")

    # Generate future forecast
    forecast_results = generate_future_forecast(
        df,
        region=None if selected_theatre == "Global Total" else selected_theatre,
        horizon_years=forecast_horizon,
    )

    hist_years = forecast_results["historical_years"]
    hist_incidents = forecast_results["historical_incidents"]
    future_years = forecast_results["forecast_years"]
    pts = forecast_results["point_forecast"]
    l80 = forecast_results["lower_80"]
    u80 = forecast_results["upper_80"]
    l95 = forecast_results["lower_95"]
    u95 = forecast_results["upper_95"]

    # Section 1: Future Forecast with Confidence Intervals
    st.markdown(f"### 🔮 Threat Trajectory Forecast: **{selected_theatre}** (through {future_years[-1]})")
    st.caption(
        f"Historical trajectory (1970–2017) and Holt-Winters damped-trend projection (2018–{future_years[-1]}) "
        "with 80% and 95% confidence intervals."
    )

    fig_fc = go.Figure()

    # Historical observations line
    fig_fc.add_trace(
        go.Scatter(
            x=hist_years,
            y=hist_incidents,
            name="Historical Recorded Incidents",
            mode="lines+markers",
            line=dict(color="#90A4AE", width=2),
            marker=dict(size=4),
        )
    )

    # 1993 gap marker
    if MISSING_YEAR in hist_years:
        fig_fc.add_vrect(
            x0=1992.5,
            x1=1993.5,
            fillcolor="#FF9100",
            opacity=0.3,
            line_width=1.5,
            line_dash="dash",
            annotation_text="1993 Interpolated Gap",
            annotation_position="top left",
            annotation=dict(font_size=11, font_color="#FF9100"),
        )

    # 95% Confidence Interval Band
    fig_fc.add_trace(
        go.Scatter(
            x=future_years + future_years[::-1],
            y=u95 + l95[::-1],
            fill="toself",
            fillcolor="rgba(255, 23, 68, 0.12)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            showlegend=True,
            name="95% Confidence Interval",
        )
    )

    # 80% Confidence Interval Band
    fig_fc.add_trace(
        go.Scatter(
            x=future_years + future_years[::-1],
            y=u80 + l80[::-1],
            fill="toself",
            fillcolor="rgba(255, 23, 68, 0.25)",
            line=dict(color="rgba(255,255,255,0)"),
            hoverinfo="skip",
            showlegend=True,
            name="80% Confidence Interval",
        )
    )

    # Point Forecast Line (connect to last historical point)
    connect_years = [hist_years[-1]] + future_years
    connect_pts = [hist_incidents[-1]] + pts

    fig_fc.add_trace(
        go.Scatter(
            x=connect_years,
            y=connect_pts,
            name="Holt-Winters Point Forecast",
            mode="lines+markers",
            line=dict(color="#FF1744", width=3, dash="dash"),
            marker=dict(size=6, color="#FF1744"),
        )
    )

    fig_fc.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        plot_bgcolor="#1A1D24",
        xaxis=dict(title="Observation & Projection Year", dtick=5, gridcolor="#2B313D"),
        yaxis=dict(title="Annual Incident Volume", gridcolor="#2B313D"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=30, b=40),
        height=450,
    )
    st.plotly_chart(fig_fc, use_container_width=True)

    st.markdown("---")

    # Section 2: Out-of-Time Backtest Overlay (2013-2017)
    st.markdown(f"### 🧪 Out-of-Time Backtest Overlay (2013–2017 Evaluation): **{selected_theatre}**")
    st.caption(
        r"Trained exclusively on data through 2012 ($iyear \le 2012$) and projected across the 2013–2017 test window. "
        "Allows direct visual inspection of actual conflict trajectory versus model projections."
    )

    theatre_key = selected_theatre if selected_theatre in backtest_data else "Global Total"
    theatre_backtest = backtest_data.get(theatre_key, None)

    if theatre_backtest:
        test_yrs = theatre_backtest["test_years"]
        act_vals = theatre_backtest["actual_values"]
        m_dict = theatre_backtest["models"]

        fig_bt = go.Figure()

        # Actual observed incidents
        fig_bt.add_trace(
            go.Scatter(
                x=test_yrs,
                y=act_vals,
                name="Actual Observed Incidents",
                mode="lines+markers",
                line=dict(color="#FAFAFA", width=3),
                marker=dict(size=8, symbol="circle"),
            )
        )

        # Holt-Winters ETS
        fig_bt.add_trace(
            go.Scatter(
                x=test_yrs,
                y=m_dict["Holt-Winters ETS"]["predictions"],
                name="Holt-Winters ETS",
                mode="lines+markers",
                line=dict(color="#00E5FF", width=2.5, dash="dash"),
                marker=dict(size=6),
            )
        )

        # 3-Year Moving Average
        fig_bt.add_trace(
            go.Scatter(
                x=test_yrs,
                y=m_dict["Moving Average (3-Yr)"]["predictions"],
                name="Moving Average (3-Yr)",
                mode="lines",
                line=dict(color="#FFD600", width=2, dash="dot"),
            )
        )

        # Naive Last Value
        fig_bt.add_trace(
            go.Scatter(
                x=test_yrs,
                y=m_dict["Naive (Last Value)"]["predictions"],
                name="Naive (Last Value)",
                mode="lines",
                line=dict(color="#9E9E9E", width=1.5, dash="dot"),
            )
        )

        fig_bt.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#1A1D24",
            xaxis=dict(title="Backtest Evaluation Year", dtick=1, gridcolor="#2B313D"),
            yaxis=dict(title="Annual Incident Count", gridcolor="#2B313D"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=30, b=40),
            height=380,
        )
        st.plotly_chart(fig_bt, use_container_width=True)

        # Section 3: Metric Comparison Table
        st.markdown("### 📊 Backtest Metric Scorecard (MAE & MAPE)")
        col_t1, col_t2 = st.columns([2, 1])

        with col_t1:
            scorecard_rows = []
            for mname, mres in m_dict.items():
                scorecard_rows.append({
                    "Forecasting Model": mname,
                    "MAE (Mean Absolute Error)": f"{mres['mae']:.1f} incidents",
                    "MAPE (Mean Absolute % Error)": f"{mres['mape']:.1f}%",
                })

            st.dataframe(
                pd.DataFrame(scorecard_rows),
                use_container_width=True,
                hide_index=True,
            )

        with col_t2:
            ets_mae = m_dict["Holt-Winters ETS"]["mae"]
            naive_mae = m_dict["Naive (Last Value)"]["mae"]
            mae_improvement = round(((naive_mae - ets_mae) / naive_mae * 100), 1) if naive_mae > 0 else 0.0

            st.markdown(
                f"""
                <div style="background-color: #1A1D24; border: 1px solid #2B313D; border-radius: 8px; padding: 16px;">
                    <div style="font-size: 0.8rem; color: #9E9E9E; text-transform: uppercase;">ETS vs. Naive Benchmark</div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: {'#00E676' if mae_improvement >= 0 else '#FF1744'}; margin-top: 4px;">
                        {mae_improvement:+0.1f}% MAE
                    </div>
                    <div style="font-size: 0.85rem; color: #E0E0E0; margin-top: 6px;">
                        {'Lower error than naive baseline' if mae_improvement >= 0 else 'Higher error than naive baseline'}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("Run 'python scripts/evaluate_forecasts.py' to generate backtest telemetry.")


if __name__ == "__main__":
    main()
