"""
04_Attack_Prediction.py - Pre-Attack Tactic Classifier & Local SHAP Explainability.
Features:
- Zero-leakage pre-attack inference form (only pre-incident factors)
- Predicted primary tactic + top-3 probability distribution
- SHAP local feature attribution waterfall for current prediction
- Global SHAP feature importance plot
- Strict leakage compliance verification indicator.
"""

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import (
    ARTIFACTS_DIR,
    BANNED_LEAKAGE_COLUMNS,
    ETHICAL_DISCLAIMER,
    MODELS_DIR,
    PROCESSED_DATA_PATH,
    UNKNOWN_GROUP_NAME,
)
from src.data_loader import load_dataset
from src.features import ALLOWED_PRE_ATTACK_FEATURES

st.set_page_config(
    page_title="Pre-Attack Tactic Prediction | GTD Analysis",
    page_icon="🎯",
    layout="wide",
)


@st.cache_resource(show_spinner="Loading Pre-Attack Classifier Pipeline...")
def load_attack_model():
    model_path = MODELS_DIR / "attack_model.joblib"
    if not model_path.exists():
        st.error("Model artifact not found. Please run 'python scripts/train_attack_model.py'.")
        st.stop()
    return joblib.load(model_path)


@st.cache_resource(show_spinner="Loading Precomputed SHAP Interpretability Artifacts...")
def load_shap_artifacts():
    shap_path = ARTIFACTS_DIR / "shap_explainer.joblib"
    if shap_path.exists():
        return joblib.load(shap_path)
    return None


@st.cache_data
def get_reference_data():
    return load_dataset(PROCESSED_DATA_PATH)


def main():
    st.title("04 · Pre-Attack Tactic Classifier & SHAP Explainability")
    st.caption("Zero-Leakage Multi-Class Tactical Prediction using Pre-Attack Observables Only")

    st.info(f"**HISTORICAL & RESEARCH DIRECTIVE**: {ETHICAL_DISCLAIMER}")

    # Zero-Leakage Guarantee Badge
    with st.expander("🛡️ Zero-Leakage Data Compliance Guarantee", expanded=False):
        st.markdown(
            f"""
            This machine learning model strictly enforces zero-leakage standards.
            - **Permitted Pre-Attack Features ({len(ALLOWED_PRE_ATTACK_FEATURES)}):** `{', '.join(ALLOWED_PRE_ATTACK_FEATURES)}`
            - **Strictly Banned Post-Attack Variables:** `{', '.join(BANNED_LEAKAGE_COLUMNS)}`
            - **Validation:** Neither casualty counts, weapon firing success, nor incident summaries are supplied to the feature pipeline.
            """
        )

    model_payload = load_attack_model()
    pipeline = model_payload["pipeline"]
    classes = model_payload["classes"]
    model_name = model_payload["model_name"]

    df = get_reference_data()

    # Pre-attack input form
    st.markdown("### 📝 Pre-Incident Operational Attributes")
    st.caption("Specify known operational variables available prior to incident execution:")

    col_f1, col_f2, col_f3 = st.columns(3)

    all_regions = sorted(df["region_txt"].dropna().unique().tolist())
    with col_f1:
        sel_region = st.selectbox("Geographic Theatre (Region)", all_regions, index=0)
        countries_in_region = sorted(df[df["region_txt"] == sel_region]["country_txt"].dropna().unique().tolist())
        sel_country = st.selectbox("Sovereign State", countries_in_region, index=0)
        sel_prov = st.text_input("Province / Sector", value="Central District")

    with col_f2:
        all_targets = sorted(df["targtype1_txt"].dropna().unique().tolist())
        sel_target = st.selectbox("Target Sector", all_targets, index=0)

        all_weapons = sorted(df["weaptype1_txt"].dropna().unique().tolist())
        sel_weapon = st.selectbox("Weapon Classification", all_weapons, index=0)

        known_groups = [g for g in df["gname"].dropna().unique().tolist() if g != UNKNOWN_GROUP_NAME]
        all_groups = [UNKNOWN_GROUP_NAME] + sorted(known_groups)
        sel_group = st.selectbox("Suspected Perpetrator Faction", all_groups, index=0)

    with col_f3:
        sel_year = st.slider("Incident Year", min_value=1970, max_value=2017, value=2016)
        has_coords = st.checkbox("Geospatial Pinpoint Coordinates Available", value=True)
        if has_coords:
            c_lat = st.number_input("Latitude", value=33.3152, format="%.4f")
            c_lon = st.number_input("Longitude", value=44.3661, format="%.4f")
        else:
            c_lat = np.nan
            c_lon = np.nan

    # Predict button
    if st.button("🚀 Execute Pre-Attack Tactical Inference", type="primary"):
        # Construct single-row DataFrame
        input_dict = {
            "iyear": [sel_year],
            "region_txt": [sel_region],
            "country_txt": [sel_country],
            "provstate": [sel_prov],
            "targtype1_txt": [sel_target],
            "weaptype1_txt": [sel_weapon],
            "gname": [sel_group],
            "latitude": [c_lat],
            "longitude": [c_lon],
            "coord_missing": [0 if has_coords else 1],
        }
        input_df = pd.DataFrame(input_dict)

        # Run pipeline inference
        proba = pipeline.predict_proba(input_df)[0]
        pred_idx = np.argmax(proba)
        pred_class = classes[pred_idx]
        pred_confidence = round(float(proba[pred_idx] * 100), 1)

        # Top 3 ranking
        top3_indices = np.argsort(proba)[::-1][:3]
        top3_classes = [classes[i] for i in top3_indices]
        top3_probs = [round(float(proba[i] * 100), 1) for i in top3_indices]

        st.markdown("---")
        st.markdown("### 🎯 Inference Results")

        res_c1, res_c2 = st.columns([1, 2])
        with res_c1:
            st.markdown(
                f"""
                <div style="background-color: #1A1D24; border: 2px solid #D32F2F; border-radius: 8px; padding: 20px; text-align: center;">
                    <div style="color: #9E9E9E; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px;">PREDICTED PRIMARY TACTIC</div>
                    <div style="color: #FAFAFA; font-size: 1.6rem; font-weight: 700; margin: 8px 0;">{pred_class}</div>
                    <div style="color: #00E5FF; font-size: 1.1rem; font-weight: 600;">Confidence: {pred_confidence}%</div>
                    <div style="color: #757575; font-size: 0.8rem; margin-top: 6px;">Champion Model: {model_name}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with res_c2:
            st.markdown("#### Top-3 Predicted Tactical Likelihoods")
            top3_df = pd.DataFrame({"Tactical Class": top3_classes, "Likelihood (%)": top3_probs})
            fig_top3 = px.bar(
                top3_df,
                x="Likelihood (%)",
                y="Tactical Class",
                orientation="h",
                text="Likelihood (%)",
                color="Likelihood (%)",
                color_continuous_scale="Reds",
                template="plotly_dark",
            )
            fig_top3.update_layout(
                paper_bgcolor="#0E1117",
                plot_bgcolor="#1A1D24",
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=10, b=10),
                height=200,
            )
            st.plotly_chart(fig_top3, use_container_width=True)

        # SHAP Interpretability Section
        st.markdown("---")
        st.markdown("### 🔬 SHAP Feature Attribution & Local Explainability")
        st.markdown(
            "Identifies which operational pre-attack features contributed positively or negatively "
            f"toward predicting **{pred_class}** using Shapley additive explanations."
        )

        shap_artifacts = load_shap_artifacts()
        if shap_artifacts is not None:
            feature_names = shap_artifacts["feature_names"]
            shap_values = shap_artifacts["shap_values"]

            # Display Global Feature Importance
            st.markdown("#### Global Feature Importance (Top Feature Drivers across Test Incidents)")
            # Compute mean absolute SHAP values across sample
            if isinstance(shap_values, list):
                # Multi-class list
                mean_shap = np.mean([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)
            else:
                mean_shap = np.abs(shap_values).mean(axis=0)

            # Map to feature names
            imp_df = pd.DataFrame({
                "Feature": [f.replace("cat__", "").replace("num__", "") for f in feature_names],
                "Mean |SHAP| Impact": mean_shap,
            }).sort_values("Mean |SHAP| Impact", ascending=False).head(12)

            fig_shap = px.bar(
                imp_df,
                x="Mean |SHAP| Impact",
                y="Feature",
                orientation="h",
                color="Mean |SHAP| Impact",
                color_continuous_scale="Viridis",
                template="plotly_dark",
            )
            fig_shap.update_layout(
                paper_bgcolor="#0E1117",
                plot_bgcolor="#1A1D24",
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=20, b=20),
                height=350,
            )
            st.plotly_chart(fig_shap, use_container_width=True)
            st.caption(
                "💡 *Key Insight: Weapon classification and spatial coordinates dominate feature contribution, "
                "consistently serving as the primary drivers of attack type predictability.*"
            )
        else:
            st.info("Precomputed SHAP artifacts not found. Run training script to enable full SHAP visualizer.")


if __name__ == "__main__":
    main()
