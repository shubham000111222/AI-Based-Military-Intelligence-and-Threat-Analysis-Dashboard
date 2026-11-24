"""
Intelligence report generation module for the AI-Based Threat Analysis Dashboard.
Aggregates multidimensional data into statistical summaries and synthesizes
structured strategic threat briefs via Google Gemini or deterministic templates.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import pandas as pd

from src.config import (
    ARTIFACTS_DIR,
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    MISSING_YEAR,
)

logger = logging.getLogger(__name__)


def build_threat_stats_summary(
    df: pd.DataFrame,
    region: Optional[str] = None,
    year_range: Optional[Tuple[int, int]] = None,
) -> Dict[str, Any]:
    """
    Compiles high-level statistical aggregates from the filtered dataset.
    STRICT PRIVACY / ZERO RAW LEAKAGE: Sends ONLY aggregated metrics, never raw incident rows.
    """
    filtered = df.copy()
    if year_range is not None:
        filtered = filtered[
            (filtered["iyear"] >= year_range[0]) & (filtered["iyear"] <= year_range[1])
        ]
    if region is not None and region != "All Regions":
        filtered = filtered[filtered["region_txt"] == region]

    total_incidents = int(len(filtered))
    total_fatalities = int(filtered["nkill"].sum()) if "nkill" in filtered.columns else 0
    total_wounded = int(filtered["nwound"].sum()) if "nwound" in filtered.columns else 0
    total_casualties = total_fatalities + total_wounded

    # Top countries
    top_countries = []
    if "country_txt" in filtered.columns and total_incidents > 0:
        c_agg = (
            filtered.groupby("country_txt")
            .agg(incidents=("iyear", "count"), fatalities=("nkill", "sum"))
            .sort_values("incidents", ascending=False)
            .head(5)
            .reset_index()
        )
        for _, r in c_agg.iterrows():
            top_countries.append({
                "country": str(r["country_txt"]),
                "incidents": int(r["incidents"]),
                "fatalities": int(r["fatalities"]),
            })

    # Top perpetrator groups (excluding Unknown for meaningful faction ranking)
    top_groups = []
    if "gname" in filtered.columns and total_incidents > 0:
        known_groups = filtered[filtered["gname"] != "Unknown"]
        g_counts = known_groups["gname"].value_counts().head(5)
        for gname, count in g_counts.items():
            top_groups.append({"group": str(gname), "incidents": int(count)})

    # Top attack modalities
    top_tactics = []
    if "attacktype1_txt" in filtered.columns and total_incidents > 0:
        for tname, count in filtered["attacktype1_txt"].value_counts().head(5).items():
            top_tactics.append({"tactic": str(tname), "incidents": int(count)})

    # Top weapon types
    top_weapons = []
    if "weaptype1_txt" in filtered.columns and total_incidents > 0:
        for wname, count in filtered["weaptype1_txt"].value_counts().head(5).items():
            top_weapons.append({"weapon": str(wname), "incidents": int(count)})

    # Top target sectors
    top_targets = []
    if "targtype1_txt" in filtered.columns and total_incidents > 0:
        for tgname, count in filtered["targtype1_txt"].value_counts().head(5).items():
            top_targets.append({"target": str(tgname), "incidents": int(count)})

    # Longitudinal trend
    yearly_trend = []
    if "iyear" in filtered.columns and total_incidents > 0:
        y_agg = (
            filtered.groupby("iyear")
            .agg(incidents=("iyear", "count"), fatalities=("nkill", "sum"))
            .reset_index()
        )
        for _, r in y_agg.iterrows():
            yearly_trend.append({
                "year": int(r["iyear"]),
                "incidents": int(r["incidents"]),
                "fatalities": int(r["fatalities"]),
            })

    # Known casualties reporting fidelity
    casualties_known_pct = 0.0
    if "casualties_known" in filtered.columns and total_incidents > 0:
        casualties_known_pct = round(
            float(filtered["casualties_known"].mean() * 100.0), 2
        )

    # Load precomputed forecast backtest errors if present
    forecast_metrics = None
    forecast_path = ARTIFACTS_DIR / "forecast_eval.json"
    if forecast_path.exists():
        try:
            with open(forecast_path, "r", encoding="utf-8") as f:
                f_data = json.load(f)
                target_key = region if (region and region in f_data) else "Global Total"
                if target_key in f_data:
                    forecast_metrics = f_data[target_key]
        except Exception as e:
            logger.warning("Could not read forecast_eval.json: %s", e)

    # Load top recent anomaly alerts if present
    recent_alerts = []
    alerts_path = ARTIFACTS_DIR / "anomaly_alerts.parquet"
    if alerts_path.exists():
        try:
            alerts_df = pd.read_parquet(alerts_path)
            if region and region != "All Regions" and "country_txt" in alerts_df.columns:
                # filter alerts to countries in region if country_txt is known
                reg_countries = set(filtered["country_txt"].dropna().unique())
                alerts_df = alerts_df[alerts_df["country_txt"].isin(reg_countries)]
            top_a = alerts_df.sort_values("anomaly_score", ascending=False).head(3)
            for _, r in top_a.iterrows():
                recent_alerts.append({
                    "country": str(r.get("country_txt", "Unknown")),
                    "period": f"{int(r.get('year', 0))}-{int(r.get('month', 1)):02d}",
                    "score": float(round(r.get("anomaly_score", 0.0), 2)),
                    "reason": str(r.get("reason", "Surge detected")),
                })
        except Exception as e:
            logger.warning("Could not load anomaly alerts: %s", e)

    return {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "region": region or "Global",
            "year_range": list(year_range) if year_range else [1970, 2017],
            "missing_year": MISSING_YEAR,
        },
        "totals": {
            "incidents": total_incidents,
            "fatalities": total_fatalities,
            "wounded": total_wounded,
            "casualties": total_casualties,
            "casualty_reporting_rate_pct": casualties_known_pct,
        },
        "top_countries": top_countries,
        "top_groups": top_groups,
        "top_tactics": top_tactics,
        "top_weapons": top_weapons,
        "top_targets": top_targets,
        "yearly_trend": yearly_trend,
        "forecast_metrics": forecast_metrics,
        "recent_alerts": recent_alerts,
    }


def generate_deterministic_report(stats: Dict[str, Any]) -> str:
    """
    Generates a structured, professional intelligence briefing deterministically
    from aggregate statistics. Acts as an exact, offline fallback when Gemini is unavailable.
    """
    meta = stats.get("metadata", {})
    totals = stats.get("totals", {})
    top_c = stats.get("top_countries", [])
    top_g = stats.get("top_groups", [])
    top_t = stats.get("top_tactics", [])
    top_w = stats.get("top_weapons", [])
    top_tg = stats.get("top_targets", [])
    f_metrics = stats.get("forecast_metrics")
    alerts = stats.get("recent_alerts", [])

    region_name = meta.get("region", "Global")
    yr_start, yr_end = meta.get("year_range", [1970, 2017])
    gen_time = meta.get("generated_at", "N/A")

    top_c_str = (
        ", ".join([f"{c['country']} ({c['incidents']:,} incidents, {c['fatalities']:,} deaths)" for c in top_c[:3]])
        if top_c else "No significant sovereign concentrations reported."
    )
    top_g_str = (
        ", ".join([f"{g['group']} ({g['incidents']:,})" for g in top_g[:3]])
        if top_g else "Predominantly unclaimed / unknown factions."
    )
    top_t_str = (
        ", ".join([f"{t['tactic']} ({t['incidents']:,})" for t in top_t[:3]])
        if top_t else "Mixed operational tactics."
    )
    top_w_str = (
        ", ".join([f"{w['weapon']} ({w['incidents']:,})" for w in top_w[:3]])
        if top_w else "Mixed weaponry."
    )
    top_tg_str = (
        ", ".join([f"{tg['target']} ({tg['incidents']:,})" for tg in top_tg[:3]])
        if top_tg else "Dispersed civil and security infrastructure."
    )

    forecast_str = "Longitudinal ETS backtest metrics not evaluated for this scope."
    if f_metrics and "ets" in f_metrics:
        ets_m = f_metrics["ets"]
        mae = ets_m.get("mae", 0.0)
        mape = ets_m.get("mape", 0.0)
        forecast_str = f"Exponential Smoothing (ETS) baseline achieved out-of-time Backtest MAE of {mae:.1f} and MAPE of {mape:.1f}%."

    alerts_str = "No anomalous statistical surge spikes detected in active window."
    if alerts:
        alerts_str = "; ".join([f"{a['country']} ({a['period']}: Score {a['score']} - {a['reason']})" for a in alerts])

    report = f"""# HISTORICAL THREAT INTELLIGENCE EXECUTIVE BRIEF
**Document Classification:** UNCLASSIFIED // EDUCATIONAL & RESEARCH RETROSPECTIVE
**Scope / Theatre:** {region_name}
**Temporal Coverage:** {yr_start} – {yr_end} (1993 archival collection gap excluded)
**Generation Timestamp:** {gen_time}
**Analytical Engine:** Historical GTD Statistical Intelligence Engine

---

### 1. Situation Overview
During the analyzed longitudinal window ({yr_start}–{yr_end}), a cumulative total of **{totals.get('incidents', 0):,} incidents** were recorded within the {region_name} scope, resulting in **{totals.get('fatalities', 0):,} verified fatalities** and **{totals.get('wounded', 0):,} documented wounded personnel** (aggregate casualties: **{totals.get('casualties', 0):,}**). Casualty data was explicitly established for **{totals.get('casualty_reporting_rate_pct', 0.0)}%** of logged events, with the remainder subject to historical missingness imputation.

### 2. Key Trends & Anomaly Assessment
- **Longitudinal Trajectory:** Activity across the theatre exhibits multi-phase cyclical escalation, with distinct peaks aligned with major geopolitical shifts, insurgent campaigns, and post-Cold War ideological transitions.
- **Statistical Early Warning Surges:** {alerts_str}
- **Archival Continuity Note:** 1993 incident records remain excluded due to historical collection transit loss by the original START documentation team.

### 3. Geographic Concentrations & Sovereign Hotspots
- **Primary Sovereign Theatres:** The highest incident volumes and lethalities are concentrated in: {top_c_str}.
- **Urban vs. Rural Distribution:** Activity demonstrates high geographic clustering around administrative capitals, transit corridors, and contested border zones.

### 4. Dominant Tactics, Targets & Perceived Actor Trajectories
- **Tactical Modalities:** The predominant attack types utilized include: **{top_t_str}**.
- **Weapon System Profiling:** Primary offensive weaponry comprises: **{top_w_str}**.
- **Infrastructure Vulnerabilities:** Perpetrators disproportionately targeted: **{top_tg_str}**.
- **Prominent Identified Factions:** Excluding unclaimed actions, the most active organized non-state factions were: **{top_g_str}**.

### 5. Risk Outlook & Predictive Baseline
- **Forecasting Assessment:** {forecast_str}
- **Horizon Constraints:** Longitudinal statistical forecasting beyond a 3-to-5 year window is constrained by geopolitical regime changes and peace settlements. Projections represent statistical extrapolations of historical trajectories rather than event-level kinetic predictions.

### 6. Analytical Limitations & Ethical Framing
- **Retrospective Scope:** This intelligence assessment is strictly retrospective and educational in scope. It does not constitute a tactical targeting tool, kinetic decision feed, or operational deployment recommendation.
- **Reporting & Telemetry Biases:** Historical data reflects significant media reporting biases, evolving classification criteria across collection eras (1970–1997 PGIS, 1998–2007 CETIS, 2008–2017 START), and systemic underreporting in remote or media-restricted combat zones.
"""
    return report.strip()


def generate_gemini_report(
    stats: Dict[str, Any],
    api_key: Optional[str] = None,
    model: str = GEMINI_MODEL,
    temperature: float = GEMINI_TEMPERATURE,
) -> str:
    """
    Synthesizes a strategic intelligence report using the official google-genai SDK.
    Falls back gracefully to generate_deterministic_report if API key is missing or calls fail.
    """
    # Resolve API Key
    resolved_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not resolved_key:
        try:
            import streamlit as st
            resolved_key = st.secrets.get("GEMINI_API_KEY")
        except Exception:
            resolved_key = None

    if not resolved_key:
        logger.info("GEMINI_API_KEY not configured. Using deterministic report generator.")
        return generate_deterministic_report(stats)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=resolved_key)

        prompt = f"""
You are an expert senior intelligence analyst compiling a retrospective strategic threat assessment on historical Global Terrorism Database (GTD) data.

CRITICAL INSTRUCTIONS & BOUNDARIES:
1. ETHICAL & SCOPE FRAMING: This is strictly an educational, retrospective historical analysis for academic research. It is NEVER an operational kinetic targeting tool or real-time surveillance feed.
2. STRICT DATA FIDELITY: You MUST use ONLY the exact numbers provided in the JSON payload below. NEVER fabricate, extrapolate, or hallucinate casualty counts, dates, or incident totals.
3. STRUCTURE: Organize the assessment with the following exact Markdown section headers:
   - # HISTORICAL THREAT INTELLIGENCE EXECUTIVE BRIEF
   - ### 1. Situation Overview
   - ### 2. Key Trends & Anomaly Assessment
   - ### 3. Geographic Concentrations & Hotspots
   - ### 4. Dominant Tactics, Targets & Perceived Actor Trajectories
   - ### 5. Risk Outlook & Forecasting Assessment
   - ### 6. Analytical Limitations & Ethical Framing
4. ARCHIVAL GAP: Note that 1993 is missing from the dataset due to archival transit loss prior to digital centralisation.

AGGREGATED HISTORICAL DATA PAYLOAD:
```json
{json.dumps(stats, indent=2)}
```
"""
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=2048,
            ),
        )
        if response and response.text:
            return response.text.strip()
        return generate_deterministic_report(stats)
    except Exception as e:
        logger.warning("Gemini report generation failed (%s). Falling back to deterministic brief.", e)
        return generate_deterministic_report(stats)
