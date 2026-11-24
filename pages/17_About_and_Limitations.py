"""
17_About_and_Limitations.py - Project Methodology, Ethical Charter & Analytical Boundaries.
"""

import streamlit as st

from src.config import ETHICAL_DISCLAIMER, MISSING_YEAR_ANNOTATION

st.set_page_config(
    page_title="About & Analytical Limitations | GTD Analysis",
    page_icon="📜",
    layout="wide",
)

st.title("17 · About the Project, Ethical Charter & Limitations")
st.caption("AI-Based Military Intelligence & Threat Analysis Dashboard (Historical Analytics)")

# Operational Directive Callout
st.error(f"**MANDATORY ETHICAL RESTRICTION**\n\n{ETHICAL_DISCLAIMER}")

st.markdown("---")

st.markdown("### 🎯 Project Framing & Purpose")
st.markdown(
    r"""
    The **AI-Based Military Intelligence and Threat Analysis Dashboard** is an academic, portfolio-grade
    data science system designed to demonstrate:

    1. **Historical Retrospective Analytics:** Longitudinal pattern discovery, casualty aggregation, and spatial analysis on historical violence data (1970–2017).
    2. **Rigorous Machine Learning Hygiene:** Strict leakage prevention, temporal-split evaluation (train $\le$ 2012, test 2013–2017), and interpretability via SHAP.
    3. **Composite Strategic Risk Modeling:** Multi-criteria risk index calculation with Kendall-tau parameter sensitivity simulation.
    4. **Data Integrity & Archival Auditing:** Transparent tracking of missingness, reporting bias, and collection discrepancies.

    **This platform is explicitly NOT an operational tactical tool, real-time kinetic targeting feed, or surveillance system.**
    """
)

st.markdown("---")

st.markdown("### ⚠️ Methodological Limitations & Known Biases")
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### 1. Archival Discontinuities")
    st.markdown(
        f"""
        - **1993 Archive Gap:** {MISSING_YEAR_ANNOTATION}
        - **Media Digitization Drift:** Incidents from 2000–2017 reflect vast increases in internet news coverage rather than purely physical increases in violence.
        - **Unclaimed Incidents:** Over 40% of incidents globally lack confirmed organizational attribution, remaining classified as 'Unknown'.
        """
    )

with c2:
    st.markdown("#### 2. Statistical & Machine Learning Limits")
    st.markdown(
        """
        - **Retrospective Nature:** Machine learning models predict patterns based on historical distributions. Geopolitical dynamics, military tactics, and emergent factions change unpredictably.
        - **Geocoding Precision:** Approximately 10–15% of records have missing or city-centroid coordinates. Hotspot density clusters (DBSCAN) reflect reported clusters, not continuous surveillance.
        - **Non-Causal Models:** Correlations identified by classifiers or anomaly detectors are statistical associations, not causal proofs.
        """
    )

st.markdown("---")

st.markdown("### 📚 Data Source & Attribution")
st.markdown(
    """
    - **Dataset:** Global Terrorism Database (GTD)
    - **Collector:** National Consortium for the Study of Terrorism and Responses to Terrorism (START), University of Maryland.
    - **Distribution Reference:** Kaggle Mirror (`globalterrorismdb_0718dist.csv`, 1970–2017).
    """
)
