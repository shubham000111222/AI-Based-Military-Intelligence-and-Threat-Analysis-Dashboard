"""
Conversational intelligence query engine for natural language interaction.
Translates analyst questions into structured, validated JSON query specifications.
Executes queries via pure, secure pandas routines (strictly zero eval/exec)
and synthesizes multi-sentence intelligence answers with Plotly visualizations.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.config import GEMINI_MODEL

logger = logging.getLogger(__name__)

# Strict Security Whitelist
SAFE_COLUMNS: List[str] = [
    "iyear",
    "imonth",
    "iday",
    "country_txt",
    "region_txt",
    "provstate",
    "city",
    "attacktype1_txt",
    "targtype1_txt",
    "weaptype1_txt",
    "gname",
    "nkill",
    "nwound",
    "ncasualty",
    "success",
    "suicide",
    "casualties_known",
]

NUMERIC_COLUMNS: List[str] = [
    "iyear",
    "imonth",
    "iday",
    "nkill",
    "nwound",
    "ncasualty",
    "success",
    "suicide",
]

SAFE_OPERATORS: List[str] = [
    "==",
    "!=",
    ">",
    ">=",
    "<",
    "<=",
    "in",
    "between",
]

SAFE_METRICS: List[str] = [
    "count",
    "sum",
    "mean",
    "min",
    "max",
]

SAFE_CHART_TYPES: List[str] = [
    "bar",
    "line",
    "pie",
    "table",
]


def validate_query_spec(spec: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validates a JSON query specification against strict security whitelists.
    Prevents arbitrary code execution, unauthorized column access, or injection attacks.
    """
    if not isinstance(spec, dict):
        return False, "Query specification must be a JSON object dictionary."

    # Validate filters
    filters = spec.get("filters", [])
    if not isinstance(filters, list):
        return False, "Query 'filters' attribute must be a list."

    for f in filters:
        if not isinstance(f, dict):
            return False, "Each filter condition must be an object."
        col = f.get("column")
        op = f.get("op")
        val = f.get("value")

        if col not in SAFE_COLUMNS:
            return False, f"Unauthorized filter column '{col}'. Must be one of {SAFE_COLUMNS}."
        if op not in SAFE_OPERATORS:
            return False, f"Unauthorized filter operator '{op}'. Must be one of {SAFE_OPERATORS}."

        # Check for command injection in string values
        if isinstance(val, str) and any(bad in val for bad in ["__", "import", "exec", "eval", ";", "--", "DROP"]):
            return False, f"Potentially malicious pattern detected in filter value '{val}'."

    # Validate group_by
    group_by = spec.get("group_by")
    if group_by is not None:
        if isinstance(group_by, list):
            for g in group_by:
                if g not in SAFE_COLUMNS:
                    return False, f"Unauthorized group_by column '{g}'."
        elif isinstance(group_by, str):
            if group_by not in SAFE_COLUMNS:
                return False, f"Unauthorized group_by column '{group_by}'."
        else:
            return False, "'group_by' must be a column string, list of columns, or null."

    # Validate metric
    metric = spec.get("metric", "count")
    if metric not in SAFE_METRICS:
        return False, f"Unauthorized metric '{metric}'. Must be one of {SAFE_METRICS}."

    # Validate metric_column
    metric_col = spec.get("metric_column")
    if metric_col is not None:
        if metric_col not in NUMERIC_COLUMNS:
            return False, f"Metric column '{metric_col}' is not a valid numeric column."

    # Validate chart_type
    chart_type = spec.get("chart_type", "bar")
    if chart_type not in SAFE_CHART_TYPES:
        spec["chart_type"] = "bar"

    # Validate top_n
    top_n = spec.get("top_n", 10)
    if not isinstance(top_n, int) or top_n < 1 or top_n > 1000:
        spec["top_n"] = 10

    return True, "Valid query specification."


def execute_query_spec(spec: Dict[str, Any], df: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    """
    Executes a validated query specification on a pandas DataFrame using pure pandas routines.
    Strictly zero string evaluation or dynamic execution.
    """
    is_valid, err_msg = validate_query_spec(spec)
    if not is_valid:
        raise ValueError(f"Security validation failure: {err_msg}")

    filtered = df.copy()

    # 1. Apply filters
    for f in spec.get("filters", []):
        col = f["column"]
        op = f["op"]
        val = f["value"]

        if col not in filtered.columns:
            continue

        if op == "==":
            filtered = filtered[filtered[col] == val]
        elif op == "!=":
            filtered = filtered[filtered[col] != val]
        elif op == ">":
            filtered = filtered[filtered[col] > float(val)]
        elif op == ">=":
            filtered = filtered[filtered[col] >= float(val)]
        elif op == "<":
            filtered = filtered[filtered[col] < float(val)]
        elif op == "<=":
            filtered = filtered[filtered[col] <= float(val)]
        elif op == "in":
            if isinstance(val, (list, tuple, set)):
                filtered = filtered[filtered[col].isin(val)]
            else:
                filtered = filtered[filtered[col] == val]
        elif op == "between":
            if isinstance(val, (list, tuple)) and len(val) >= 2:
                filtered = filtered[filtered[col].between(val[0], val[1])]

    if len(filtered) == 0:
        return pd.DataFrame(), spec.get("chart_type", "bar")

    # 2. Apply Grouping & Aggregation
    group_by = spec.get("group_by")
    metric = spec.get("metric", "count")
    metric_col = spec.get("metric_column", "nkill" if metric != "count" else None)
    top_n = spec.get("top_n", 10)
    sort_dir = spec.get("sort", "desc").lower() == "desc"

    if group_by:
        if metric == "count":
            res = filtered.groupby(group_by, observed=False).size().reset_index(name="incident_count")
            res = res.sort_values("incident_count", ascending=not sort_dir).head(top_n)
        else:
            agg_col = metric_col if (metric_col and metric_col in filtered.columns) else "nkill"
            res = filtered.groupby(group_by, observed=False)[agg_col].agg(metric).reset_index(name=f"{metric}_{agg_col}")
            res = res.sort_values(f"{metric}_{agg_col}", ascending=not sort_dir).head(top_n)
    else:
        # Return tabular view of relevant columns
        cols = [c for c in ["iyear", "country_txt", "attacktype1_txt", "targtype1_txt", "gname", "nkill", "nwound"] if c in filtered.columns]
        res = filtered[cols].head(top_n)

    return res, spec.get("chart_type", "bar")


def parse_query_deterministically(question: str) -> Dict[str, Any]:
    """
    Robust rule-based heuristic query parser for offline / zero-API-key execution.
    Recognizes common intelligence questions and patterns.
    """
    q = question.lower().strip()

    # 1. Deadliest groups
    if "deadliest group" in q or "top group" in q or "most lethal group" in q:
        return {
            "filters": [{"column": "gname", "op": "!=", "value": "Unknown"}],
            "group_by": "gname",
            "metric": "sum",
            "metric_column": "nkill",
            "sort": "desc",
            "top_n": 10,
            "chart_type": "bar",
            "title": "Top Perpetrator Groups by Verified Fatalities",
        }

    # 2. Weapon types
    if "weapon" in q:
        filters = []
        if "middle east" in q:
            filters.append({"column": "region_txt", "op": "==", "value": "Middle East & North Africa"})
        elif "south asia" in q:
            filters.append({"column": "region_txt", "op": "==", "value": "South Asia"})
        return {
            "filters": filters,
            "group_by": "weaptype1_txt",
            "metric": "count",
            "sort": "desc",
            "top_n": 8,
            "chart_type": "bar",
            "title": "Distribution of Attacks by Weapon Modality",
        }

    # 3. Annual trend / timeline
    if "trend" in q or "yearly" in q or "annual" in q or "over time" in q:
        filters = []
        if "afghanistan" in q:
            filters.append({"column": "country_txt", "op": "==", "value": "Afghanistan"})
        elif "iraq" in q:
            filters.append({"column": "country_txt", "op": "==", "value": "Iraq"})
        elif "south asia" in q:
            filters.append({"column": "region_txt", "op": "==", "value": "South Asia"})
        return {
            "filters": filters,
            "group_by": "iyear",
            "metric": "count",
            "sort": "asc",
            "top_n": 50,
            "chart_type": "line",
            "title": "Longitudinal Incident Frequency Over Time",
        }

    # 4. Top countries by casualties / incidents
    if "top country" in q or "countries" in q or "highest casualty" in q:
        metric = "sum" if "casualt" in q or "death" in q or "fatal" in q else "count"
        metric_col = "nkill" if metric == "sum" else None
        return {
            "filters": [],
            "group_by": "country_txt",
            "metric": metric,
            "metric_column": metric_col,
            "sort": "desc",
            "top_n": 10,
            "chart_type": "bar",
            "title": "Top Countries by Historical Threat Impact",
        }

    # 5. Infrastructure targets
    if "target" in q or "infrastructure" in q or "sector" in q:
        return {
            "filters": [],
            "group_by": "targtype1_txt",
            "metric": "count",
            "sort": "desc",
            "top_n": 10,
            "chart_type": "bar",
            "title": "Primary Targeted Civil and Defense Sectors",
        }

    # 6. Suicide attacks
    if "suicide" in q:
        return {
            "filters": [{"column": "suicide", "op": "==", "value": 1}],
            "group_by": "region_txt",
            "metric": "count",
            "sort": "desc",
            "top_n": 8,
            "chart_type": "bar",
            "title": "Distribution of Suicide Attacks Across Geographic Theatres",
        }

    # 7. Attacks in Colombia or specific country
    if "colombia" in q:
        return {
            "filters": [{"column": "country_txt", "op": "==", "value": "Colombia"}],
            "group_by": "attacktype1_txt",
            "metric": "count",
            "sort": "desc",
            "top_n": 8,
            "chart_type": "bar",
            "title": "Tactical Attack Modalities in Colombia",
        }

    # Default fallback: top attack types globally
    return {
        "filters": [],
        "group_by": "attacktype1_txt",
        "metric": "count",
        "sort": "desc",
        "top_n": 8,
        "chart_type": "bar",
        "title": "Global Distribution of Attack Tactics",
    }


def synthesize_answer(spec: Dict[str, Any], result_df: pd.DataFrame, question: str) -> str:
    """
    Synthesizes a 2-3 sentence intelligence answer derived strictly from the query results.
    """
    if result_df.empty:
        return (
            f"No historical incidents match the query criteria for '{question}'. "
            "Please verify the filter constraints or try broadening the search parameters."
        )

    group_col = spec.get("group_by")
    if isinstance(group_col, list):
        group_col = group_col[0]

    val_cols = [c for c in result_df.columns if c != group_col]
    val_col = val_cols[0] if val_cols else None

    if group_col and val_col and len(result_df) > 0:
        top_row = result_df.iloc[0]
        top_name = str(top_row[group_col])
        top_val = top_row[val_col]
        val_str = f"{top_val:,}" if isinstance(top_val, (int, np.integer)) else f"{top_val:.1f}"

        second_str = ""
        if len(result_df) > 1:
            second_row = result_df.iloc[1]
            s_val = second_row[val_col]
            s_val_str = f"{s_val:,}" if isinstance(s_val, (int, np.integer)) else f"{s_val:.1f}"
            second_str = f", followed by **{second_row[group_col]}** with {s_val_str}"

        return (
            f"Based on historical GTD records, **{top_name}** represents the highest observed concentration "
            f"with **{val_str} {val_col.replace('_', ' ')}**{second_str}. "
            f"Across the top {len(result_df)} categories evaluated, tactical distribution highlights clear geographic "
            f"and operational focus areas across the archival collection period."
        )

    return (
        f"Retrieved {len(result_df):,} historical records corresponding to your analytical query. "
        "Review the compiled data table and breakdown below for detailed tactical specifics."
    )


def ask_analyst(
    question: str,
    df: pd.DataFrame,
    api_key: Optional[str] = None,
    model: str = GEMINI_MODEL,
) -> Dict[str, Any]:
    """
    Main entry point for the conversational analyst.
    Translates natural language questions to validated query specs,
    executes them safely on the dataset, and synthesizes answers.
    """
    resolved_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not resolved_key:
        try:
            import streamlit as st
            resolved_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            resolved_key = None

    query_spec = None

    # Attempt Gemini natural language translation if key available
    if resolved_key:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=resolved_key)

            prompt = f"""
You are an expert database query generator for the Global Terrorism Database (GTD).
Translate the analyst's question into a strict JSON query specification.

APPROVED COLUMNS: {SAFE_COLUMNS}
APPROVED OPERATORS: {SAFE_OPERATORS}
APPROVED METRICS: {SAFE_METRICS}
APPROVED CHART TYPES: {SAFE_CHART_TYPES}

SCHEMA SPECIFICATION FORMAT:
{{
  "filters": [{{"column": "<col>", "op": "<op>", "value": <val>}}],
  "group_by": "<col_name or null>",
  "metric": "<count | sum | mean | min | max>",
  "metric_column": "<nkill | nwound | ncasualty | null>",
  "sort": "<desc | asc>",
  "top_n": <int between 1 and 50>,
  "chart_type": "<bar | line | pie | table>",
  "title": "<short descriptive title>"
}}

CRITICAL: Return ONLY valid JSON. No explanations, no markdown codeblocks.

ANALYST QUESTION: "{question}"
"""
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                ),
            )
            if response and response.text:
                cleaned_text = response.text.strip()
                # Remove code blocks if present
                cleaned_text = re.sub(r"^```json\s*", "", cleaned_text)
                cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
                parsed = json.loads(cleaned_text)
                is_valid, _ = validate_query_spec(parsed)
                if is_valid:
                    query_spec = parsed
        except Exception as e:
            logger.warning("Gemini query translation failed (%s). Falling back to heuristic parser.", e)

    # Use deterministic parser if Gemini was unavailable or returned invalid spec
    if query_spec is None:
        query_spec = parse_query_deterministically(question)

    # Validate spec
    is_valid, validation_msg = validate_query_spec(query_spec)
    if not is_valid:
        return {
            "success": False,
            "error": f"Security validation error: {validation_msg}",
            "answer": "Unable to execute query due to security policy violations.",
            "dataframe": pd.DataFrame(),
            "chart_type": "bar",
            "query_spec": query_spec,
        }

    try:
        result_df, chart_type = execute_query_spec(query_spec, df)
        answer_text = synthesize_answer(query_spec, result_df, question)
        return {
            "success": True,
            "error": None,
            "answer": answer_text,
            "dataframe": result_df,
            "chart_type": chart_type,
            "query_spec": query_spec,
        }
    except Exception as e:
        logger.error("Query execution error: %s", e)
        return {
            "success": False,
            "error": str(e),
            "answer": f"An error occurred while executing the query: {e}",
            "dataframe": pd.DataFrame(),
            "chart_type": "bar",
            "query_spec": query_spec,
        }
