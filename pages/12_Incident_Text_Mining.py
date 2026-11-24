"""
Page 12: Incident Text Mining & Narrative Intelligence
Explores unstructured attack summaries through:
  - Latent topic modeling via TF-IDF + Non-Negative Matrix Factorization (NMF).
  - Longitudinal and regional tactical theme prevalence.
  - Named Entity Recognition (NER) for GPE, ORG, and PERSON entities.
  - Semantic vector similarity search over historical incidents using dense embeddings.
"""

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import (
    ARTIFACTS_DIR,
    ETHICAL_DISCLAIMER,
    MISSING_YEAR,
    MISSING_YEAR_ANNOTATION,
    THEME_COLORS,
)
from src.data_loader import load_dataset
from src.text_mining import (
    extract_named_entities,
    fit_nmf_topics,
    get_topic_prevalence_by_region,
    get_topic_prevalence_over_time,
    prepare_text_corpus,
    search_similar_incidents,
)

st.set_page_config(
    page_title="Incident Text Mining | AI Threat Intelligence",
    page_icon="📝",
    layout="wide",
)

st.title("📝 Incident Narrative Text Mining & NLP Intelligence")
st.caption(
    "Unstructured intelligence mining across historical GTD event summaries using NMF topic decomposition, "
    "entity extraction, and vector similarity retrieval."
)

st.warning(f"⚖️ **Ethical & Analytical Notice**: {ETHICAL_DISCLAIMER}")


@st.cache_data
def load_text_data():
    meta_path = ARTIFACTS_DIR / "embeddings_meta.parquet"
    if meta_path.exists():
        df = pd.read_parquet(meta_path)
    else:
        df = load_dataset()
        df = prepare_text_corpus(df, text_col="summary")
    return df


@st.cache_data
def load_embeddings_and_models():
    emb_path = ARTIFACTS_DIR / "embeddings.npy"
    meta_path = ARTIFACTS_DIR / "embeddings_meta.parquet"
    topic_path = ARTIFACTS_DIR / "nmf_topic_model.joblib"
    fallback_path = ARTIFACTS_DIR / "fallback_vectorizer.joblib"

    embeddings = np.load(emb_path) if emb_path.exists() else None
    meta_df = pd.read_parquet(meta_path) if meta_path.exists() else None
    topic_data = joblib.load(topic_path) if topic_path.exists() else None
    fallback_data = joblib.load(fallback_path) if fallback_path.exists() else None

    return embeddings, meta_df, topic_data, fallback_data


df = load_text_data()
embeddings, meta_df, topic_data, fallback_data = load_embeddings_and_models()

# If precomputed topics don't exist yet, fit on the fly with caching
if topic_data is None:
    with st.spinner("Compiling NMF topic model from incident corpus..."):
        nmf_model, tfidf_vec, topic_info, enriched_df = fit_nmf_topics(df, text_col="clean_summary" if "clean_summary" in df.columns else "summary")
        topic_data = {"nmf_model": nmf_model, "vectorizer": tfidf_vec, "topic_info": topic_info}
else:
    topic_info = topic_data["topic_info"]
    # Ensure enriched columns are present
    if "dominant_topic" not in df.columns:
        nmf_weights = topic_data["nmf_model"].transform(topic_data["vectorizer"].transform(df["clean_summary" if "clean_summary" in df.columns else "summary"]))
        df["dominant_topic"] = nmf_weights.argmax(axis=1)
        label_map = {t["topic_id"]: t["label"] for t in topic_info}
        df["dominant_topic_label"] = df["dominant_topic"].map(label_map)
    enriched_df = df

# ---------------------------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------------------------
st.sidebar.header("🔍 Corpus Filters")

min_yr = int(df["iyear"].min()) if "iyear" in df.columns else 1970
max_yr = int(df["iyear"].max()) if "iyear" in df.columns else 2017

selected_years = st.sidebar.slider(
    "Temporal Range",
    min_value=min_yr,
    max_value=max_yr,
    value=(min_yr, max_yr),
)

regions = ["All Regions"] + sorted(df["region_txt"].dropna().unique().tolist()) if "region_txt" in df.columns else ["All Regions"]
selected_region = st.sidebar.selectbox("Geographic Theatre", options=regions)

# Apply filters
filtered_df = enriched_df[
    (enriched_df["iyear"] >= selected_years[0]) & (enriched_df["iyear"] <= selected_years[1])
]
if selected_region != "All Regions":
    filtered_df = filtered_df[filtered_df["region_txt"] == selected_region]

# Summary KPI Header
col_a, col_b, col_c, col_d = st.columns(4)
col_a.metric("Analyzed Narratives", f"{len(filtered_df):,}")
col_b.metric("Discovered Topics", f"{len(topic_info)}")
col_c.metric("Active Theatres", f"{filtered_df['region_txt'].nunique() if 'region_txt' in filtered_df.columns else 0}")
col_d.metric("Precomputed Embeddings", f"{len(embeddings):,}" if embeddings is not None else "Dynamic Fallback")

st.markdown("---")

# ---------------------------------------------------------------------------
# Multipage Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "🎯 Latent Topics (TF-IDF + NMF)",
    "🏷️ Named Entity Recognition (NER)",
    "🔎 Semantic Similarity Search",
])

# ---------------------------------------------------------------------------
# TAB 1: Topics
# ---------------------------------------------------------------------------
with tab1:
    st.subheader("Tactical & Operational Topic Clusters")
    st.markdown(
        "Unsupervised Non-Negative Matrix Factorization (NMF) decomposes the TF-IDF incident narrative matrix "
        "into distinct tactical vocabularies without requiring human labeling."
    )

    # Topic cards
    cols = st.columns(len(topic_info))
    for i, t in enumerate(topic_info):
        with cols[i]:
            st.markdown(f"**{t['label']}**")
            keywords_text = ", ".join([f"`{w}`" for w in t["top_words"][:5]])
            st.markdown(f"Keywords:\n{keywords_text}")

    st.markdown("---")
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Topic Prevalence Over Time")
        time_prev = get_topic_prevalence_over_time(filtered_df)
        if not time_prev.empty and len(time_prev) > 1:
            fig_time = px.line(
                time_prev,
                x="iyear",
                y=[c for c in time_prev.columns if c != "iyear"],
                title="Yearly Share of Dominant Topics (%)",
                labels={"iyear": "Year", "value": "Prevalence (%)", "variable": "Topic"},
                template="plotly_dark",
            )
            # Add 1993 missing gap annotation if in range
            if selected_years[0] <= MISSING_YEAR <= selected_years[1]:
                fig_time.add_vrect(
                    x0=MISSING_YEAR - 0.5,
                    x1=MISSING_YEAR + 0.5,
                    fillcolor=THEME_COLORS["missing_annotation"],
                    opacity=0.3,
                    layer="below",
                    line_width=0,
                )
                fig_time.add_annotation(
                    x=MISSING_YEAR,
                    y=90,
                    text="1993 Gap",
                    showarrow=False,
                    font={"color": THEME_COLORS["missing_annotation"], "size": 11},
                )
            fig_time.update_layout(height=420, legend={"orientation": "h", "y": -0.2})
            st.plotly_chart(fig_time, use_container_width=True)
            st.caption(f"Note: {MISSING_YEAR_ANNOTATION}")
        else:
            st.info("Insufficient longitudinal data for selected filter to render temporal distribution.")

    with col_right:
        st.subheader("Topic Prevalence by Geographic Region")
        reg_prev = get_topic_prevalence_by_region(filtered_df)
        if not reg_prev.empty:
            topic_cols = [c for c in reg_prev.columns if c != "region_txt"]
            fig_reg = px.bar(
                reg_prev,
                x="region_txt",
                y=topic_cols,
                title="Regional Composition of Tactical Topics (%)",
                labels={"region_txt": "Region", "value": "Prevalence (%)", "variable": "Topic"},
                template="plotly_dark",
                barmode="stack",
            )
            fig_reg.update_layout(height=420, xaxis_tickangle=-35, legend={"orientation": "h", "y": -0.4})
            st.plotly_chart(fig_reg, use_container_width=True)
        else:
            st.info("No regional distribution available.")

# ---------------------------------------------------------------------------
# TAB 2: Named Entity Recognition
# ---------------------------------------------------------------------------
with tab2:
    st.subheader("Named Entity Recognition (NER)")
    st.markdown(
        "Identifies high-frequency geopolitical locations (`GPE`), militant organizations and institutional actors (`ORG`), "
        "and military commanders or political targets (`PERSON`) across the filtered narrative corpus."
    )

    with st.spinner("Extracting named entities from narrative sample..."):
        narratives = filtered_df["clean_summary" if "clean_summary" in filtered_df.columns else "summary"].dropna().tolist()
        entities = extract_named_entities(narratives, max_docs=600, top_n=10)

    e_col1, e_col2, e_col3 = st.columns(3)

    with e_col1:
        st.markdown("### 🌍 Top Locations (GPE)")
        if entities["GPE"]:
            gpe_df = pd.DataFrame(entities["GPE"], columns=["Location", "Mentions"])
            fig_gpe = px.bar(
                gpe_df.sort_values("Mentions", ascending=True),
                x="Mentions",
                y="Location",
                orientation="h",
                title="Geopolitical Entities",
                template="plotly_dark",
                color_discrete_sequence=["#00E5FF"],
            )
            fig_gpe.update_layout(height=380, margin={"l": 10, "r": 10, "t": 40, "b": 10})
            st.plotly_chart(fig_gpe, use_container_width=True)
        else:
            st.info("No GPE entities detected in current sample.")

    with e_col2:
        st.markdown("### ⚔️ Top Organizations (ORG)")
        if entities["ORG"]:
            org_df = pd.DataFrame(entities["ORG"], columns=["Organization", "Mentions"])
            fig_org = px.bar(
                org_df.sort_values("Mentions", ascending=True),
                x="Mentions",
                y="Organization",
                orientation="h",
                title="Militant & State Organizations",
                template="plotly_dark",
                color_discrete_sequence=["#FF1744"],
            )
            fig_org.update_layout(height=380, margin={"l": 10, "r": 10, "t": 40, "b": 10})
            st.plotly_chart(fig_org, use_container_width=True)
        else:
            st.info("No ORG entities detected in current sample.")

    with e_col3:
        st.markdown("### 👤 Key Figures & Roles (PERSON)")
        if entities["PERSON"]:
            person_df = pd.DataFrame(entities["PERSON"], columns=["Person / Role", "Mentions"])
            fig_person = px.bar(
                person_df.sort_values("Mentions", ascending=True),
                x="Mentions",
                y="Person / Role",
                orientation="h",
                title="Identified Individuals & Targets",
                template="plotly_dark",
                color_discrete_sequence=["#FFD600"],
            )
            fig_person.update_layout(height=380, margin={"l": 10, "r": 10, "t": 40, "b": 10})
            st.plotly_chart(fig_person, use_container_width=True)
        else:
            st.info("No PERSON entities detected in current sample.")

    st.info(
        "💡 **Intelligence Reporting Context**: Entity frequencies reflect source reporting density. "
        "Western media and urban incidents historically receive significantly higher named detail than remote rural skirmishes."
    )

# ---------------------------------------------------------------------------
# TAB 3: Semantic Similar Incident Search
# ---------------------------------------------------------------------------
with tab3:
    st.subheader("Semantic Similar-Incident Retrieval Engine")
    st.markdown(
        "Search historical records using precomputed dense narrative embeddings. "
        "Unlike keyword matching, semantic vector search captures tactical analogies, weapons modality, and target contexts."
    )

    if embeddings is None or meta_df is None:
        st.warning(
            "Dense embeddings have not been precomputed. "
            "Run `python scripts/build_embeddings.py` to compile `artifacts/embeddings.npy`."
        )
    else:
        search_mode = st.radio(
            "Search Modality",
            options=["Select Historical Reference Incident", "Custom Freeform Threat Scenario"],
            horizontal=True,
        )

        top_k = st.slider("Number of Similar Incidents", min_value=3, max_value=20, value=10)

        if search_mode == "Select Historical Reference Incident":
            # Select an incident from meta_df
            incident_labels = [
                f"[{r.iyear}] {r.country_txt} - {r.attacktype1_txt} ({r.gname}) - {str(r.clean_summary)[:70]}..."
                for _, r in meta_df.head(500).iterrows()
            ]
            selected_idx = st.selectbox(
                "Choose reference incident:",
                options=range(len(incident_labels)),
                format_func=lambda x: incident_labels[x],
            )

            ref_row = meta_df.iloc[selected_idx]
            st.markdown(f"**Selected Reference Narrative:**\n> *\"{ref_row['clean_summary']}\"*")

            if st.button("🔎 Find Analogous Incidents", key="btn_ref"):
                results = search_similar_incidents(
                    query=selected_idx,
                    embeddings=embeddings,
                    meta_df=meta_df,
                    top_k=top_k,
                )
                st.session_state["search_results"] = results
        else:
            custom_query = st.text_area(
                "Enter custom incident narrative or operational scenario:",
                value="Suspected separatist insurgents detonated an improvised explosive device targeting a military convoy on a rural highway.",
                height=100,
            )
            if st.button("🔎 Search Semantic Space", key="btn_custom"):
                vec = fallback_data["vectorizer"] if fallback_data else None
                svd = fallback_data["svd"] if fallback_data else None
                results = search_similar_incidents(
                    query=custom_query,
                    embeddings=embeddings,
                    meta_df=meta_df,
                    top_k=top_k,
                    vectorizer=vec,
                    svd=svd,
                )
                st.session_state["search_results"] = results

        if "search_results" in st.session_state:
            res = st.session_state["search_results"]
            if not res.empty:
                st.markdown(f"### Top {len(res)} Most Analogous Incidents")
                for _, row in res.iterrows():
                    sim_pct = f"{row['similarity_score'] * 100:.1f}%"
                    with st.expander(f"🔹 [{sim_pct} Match] {row['iyear']} | {row['country_txt']} | {row['attacktype1_txt']} ({row['gname']})"):
                        c1, c2, c3 = st.columns(3)
                        c1.markdown(f"**Target:** {row.get('targtype1_txt', 'Unknown')}")
                        c2.markdown(f"**Weapon:** {row.get('weaptype1_txt', 'Unknown')}")
                        c3.markdown(f"**Casualties:** {int(row.get('nkill', 0))} killed, {int(row.get('nwound', 0))} wounded")
                        st.markdown(f"**Incident Summary:**\n> {row.get('clean_summary', row.get('summary', ''))}")
            else:
                st.info("No matching incidents found.")
