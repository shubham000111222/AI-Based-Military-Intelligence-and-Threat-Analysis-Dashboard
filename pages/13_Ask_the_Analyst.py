"""
Page 13: Conversational Intelligence Analyst (Ask the Analyst)
Natural language analytical querying over the historical Global Terrorism Database (GTD).
Converts questions to verified JSON query specs, executes pure pandas routines (zero eval/exec),
and generates multi-sentence intelligence answers with Plotly visualizations.
"""

import plotly.express as px
import streamlit as st

from src.config import (
    ETHICAL_DISCLAIMER,
    MISSING_YEAR,
    THEME_COLORS,
)
from src.data_loader import load_dataset
from src.query_engine import ask_analyst

st.set_page_config(
    page_title="Ask the Analyst | AI Threat Intelligence",
    page_icon="💬",
    layout="wide",
)

st.title("💬 Conversational Threat Intelligence Analyst")
st.caption(
    "Query the historical GTD corpus in natural language. Powered by Gemini structured query translation, "
    "strict security whitelist validation, and secure pandas execution."
)

st.warning(f"⚖️ **Ethical & Retrospective Notice**: {ETHICAL_DISCLAIMER}")


@st.cache_data
def get_data():
    return load_dataset()


df = get_data()

# Initialize message history in session state
if "analyst_chat_history" not in st.session_state:
    st.session_state["analyst_chat_history"] = []

# ---------------------------------------------------------------------------
# Recommended Query Chips
# ---------------------------------------------------------------------------
st.subheader("💡 Recommended Analytical Inquiries")
st.markdown("Click any chip below to immediately execute a benchmark intelligence query:")

chips = [
    "Deadliest perpetrator groups globally",
    "Most frequent weapon types in the Middle East",
    "Annual trend of incidents in South Asia",
    "Top 10 countries by casualty count",
    "Primary targeted infrastructure sectors",
    "Distribution of suicide attacks by region",
    "Tactical attack modalities in Colombia",
    "Longitudinal incident frequency in Afghanistan",
]

# Render 2 rows of 4 buttons
chip_rows = [chips[:4], chips[4:]]
selected_chip = None

for row in chip_rows:
    cols = st.columns(len(row))
    for i, chip_text in enumerate(row):
        with cols[i]:
            if st.button(chip_text, key=f"chip_{chip_text}", use_container_width=True):
                selected_chip = chip_text

st.markdown("---")

# ---------------------------------------------------------------------------
# Chat Display
# ---------------------------------------------------------------------------
chat_container = st.container()

with chat_container:
    for msg in st.session_state["analyst_chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("has_data") and not msg.get("dataframe").empty:
                res_df = msg["dataframe"]
                chart_type = msg.get("chart_type", "bar")
                spec = msg.get("spec", {})
                group_col = spec.get("group_by")
                if isinstance(group_col, list):
                    group_col = group_col[0]

                # Render Visualisation
                val_cols = [c for c in res_df.columns if c != group_col]
                if group_col and val_cols:
                    val_col = val_cols[0]
                    title = spec.get("title", f"{val_col.title()} by {group_col.title()}")

                    if chart_type == "line" or group_col == "iyear":
                        fig = px.line(
                            res_df,
                            x=group_col,
                            y=val_col,
                            title=title,
                            template="plotly_dark",
                            markers=True,
                            color_discrete_sequence=[THEME_COLORS["accent_cyan"]],
                        )
                        # Annotate 1993 gap if iyear is in chart
                        if group_col == "iyear" and res_df[group_col].min() <= MISSING_YEAR <= res_df[group_col].max():
                            fig.add_vrect(
                                x0=MISSING_YEAR - 0.5,
                                x1=MISSING_YEAR + 0.5,
                                fillcolor=THEME_COLORS["missing_annotation"],
                                opacity=0.3,
                                layer="below",
                                line_width=0,
                            )
                            fig.add_annotation(
                                x=MISSING_YEAR,
                                y=res_df[val_col].max() * 0.9,
                                text="1993 Gap",
                                showarrow=False,
                                font={"color": THEME_COLORS["missing_annotation"], "size": 11},
                            )
                        fig.update_layout(height=360)
                        st.plotly_chart(fig, use_container_width=True)
                    elif chart_type == "pie":
                        fig = px.pie(
                            res_df,
                            names=group_col,
                            values=val_col,
                            title=title,
                            template="plotly_dark",
                            hole=0.4,
                        )
                        fig.update_layout(height=360)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        fig = px.bar(
                            res_df,
                            x=val_col,
                            y=group_col,
                            orientation="h",
                            title=title,
                            template="plotly_dark",
                            color_discrete_sequence=[THEME_COLORS["primary"]],
                        )
                        fig.update_layout(
                            height=360,
                            yaxis={"autorange": "reversed"},
                            margin={"l": 10, "r": 10, "t": 35, "b": 10},
                        )
                        st.plotly_chart(fig, use_container_width=True)

                # Render data table
                with st.expander(f"📋 View Data Table ({len(res_df)} rows)"):
                    st.dataframe(res_df, use_container_width=True)

                # Render executed query spec
                with st.expander("🛡️ Inspect Validated Query Spec (Pure Pandas Execution)"):
                    st.json(spec)

# ---------------------------------------------------------------------------
# Chat Input Handling
# ---------------------------------------------------------------------------
user_prompt = st.chat_input("Enter an analytical threat inquiry (e.g., 'Deadliest attacks in Iraq during 2014')...")

active_query = selected_chip or user_prompt

if active_query:
    # 1. Add user message
    st.session_state["analyst_chat_history"].append({"role": "user", "content": active_query})
    with st.chat_message("user"):
        st.markdown(active_query)

    # 2. Process query
    with st.chat_message("assistant"):
        with st.spinner("Analyzing historical GTD intelligence..."):
            response = ask_analyst(active_query, df)

            st.markdown(response["answer"])

            res_df = response["dataframe"]
            chart_type = response.get("chart_type", "bar")
            spec = response.get("query_spec", {})
            group_col = spec.get("group_by")
            if isinstance(group_col, list):
                group_col = group_col[0]

            if not res_df.empty and group_col:
                val_cols = [c for c in res_df.columns if c != group_col]
                if val_cols:
                    val_col = val_cols[0]
                    title = spec.get("title", f"{val_col.title()} by {group_col.title()}")
                    if chart_type == "line" or group_col == "iyear":
                        fig = px.line(
                            res_df,
                            x=group_col,
                            y=val_col,
                            title=title,
                            template="plotly_dark",
                            markers=True,
                            color_discrete_sequence=[THEME_COLORS["accent_cyan"]],
                        )
                        if group_col == "iyear" and res_df[group_col].min() <= MISSING_YEAR <= res_df[group_col].max():
                            fig.add_vrect(
                                x0=MISSING_YEAR - 0.5,
                                x1=MISSING_YEAR + 0.5,
                                fillcolor=THEME_COLORS["missing_annotation"],
                                opacity=0.3,
                                layer="below",
                                line_width=0,
                            )
                        fig.update_layout(height=360)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        fig = px.bar(
                            res_df,
                            x=val_col,
                            y=group_col,
                            orientation="h",
                            title=title,
                            template="plotly_dark",
                            color_discrete_sequence=[THEME_COLORS["primary"]],
                        )
                        fig.update_layout(
                            height=360,
                            yaxis={"autorange": "reversed"},
                            margin={"l": 10, "r": 10, "t": 35, "b": 10},
                        )
                        st.plotly_chart(fig, use_container_width=True)

                with st.expander(f"📋 View Data Table ({len(res_df)} rows)"):
                    st.dataframe(res_df, use_container_width=True)

                with st.expander("🛡️ Inspect Validated Query Spec (Pure Pandas Execution)"):
                    st.json(spec)

    # 3. Add assistant response to history
    st.session_state["analyst_chat_history"].append({
        "role": "assistant",
        "content": response["answer"],
        "has_data": not response["dataframe"].empty,
        "dataframe": response["dataframe"],
        "chart_type": response["chart_type"],
        "spec": response["query_spec"],
    })
