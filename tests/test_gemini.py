"""
Unit tests for Phase 9: Gemini AI features, privacy-preserving threat report generation,
deterministic fallback briefing, executive PDF export, and secure query engine validation.
"""

import pandas as pd
import pytest

from src.pdf_export import generate_pdf_report, sanitize_text_for_pdf
from src.query_engine import (
    ask_analyst,
    execute_query_spec,
    parse_query_deterministically,
    validate_query_spec,
)
from src.report import (
    build_threat_stats_summary,
    generate_deterministic_report,
    generate_gemini_report,
)


@pytest.fixture
def sample_intelligence_df() -> pd.DataFrame:
    """Creates a sample DataFrame of historical GTD records for testing."""
    return pd.DataFrame([
        {
            "iyear": 2012,
            "imonth": 5,
            "iday": 12,
            "country_txt": "Colombia",
            "region_txt": "South America",
            "attacktype1_txt": "Bombing/Explosion",
            "targtype1_txt": "Police",
            "weaptype1_txt": "Explosives",
            "gname": "Revolutionary Armed Forces of Colombia (FARC)",
            "nkill": 4,
            "nwound": 10,
            "ncasualty": 14,
            "casualties_known": True,
            "suicide": 0,
        },
        {
            "iyear": 2012,
            "imonth": 8,
            "iday": 20,
            "country_txt": "Colombia",
            "region_txt": "South America",
            "attacktype1_txt": "Armed Assault",
            "targtype1_txt": "Military",
            "weaptype1_txt": "Firearms",
            "gname": "Revolutionary Armed Forces of Colombia (FARC)",
            "nkill": 2,
            "nwound": 3,
            "ncasualty": 5,
            "casualties_known": True,
            "suicide": 0,
        },
        {
            "iyear": 2014,
            "imonth": 3,
            "iday": 15,
            "country_txt": "Iraq",
            "region_txt": "Middle East & North Africa",
            "attacktype1_txt": "Bombing/Explosion",
            "targtype1_txt": "Private Citizens & Property",
            "weaptype1_txt": "Explosives",
            "gname": "Islamic State of Iraq and the Levant (ISIL)",
            "nkill": 25,
            "nwound": 50,
            "ncasualty": 75,
            "casualties_known": True,
            "suicide": 1,
        },
        {
            "iyear": 2015,
            "imonth": 6,
            "iday": 10,
            "country_txt": "Afghanistan",
            "region_txt": "South Asia",
            "attacktype1_txt": "Armed Assault",
            "targtype1_txt": "Government (General)",
            "weaptype1_txt": "Firearms",
            "gname": "Taliban",
            "nkill": 6,
            "nwound": 8,
            "ncasualty": 14,
            "casualties_known": True,
            "suicide": 0,
        },
    ])


def test_build_threat_stats_summary_aggregates_only(sample_intelligence_df):
    stats = build_threat_stats_summary(sample_intelligence_df)
    assert "totals" in stats
    assert stats["totals"]["incidents"] == 4
    assert stats["totals"]["fatalities"] == 37
    assert stats["totals"]["wounded"] == 71
    assert stats["totals"]["casualties"] == 108
    assert "top_countries" in stats
    assert "top_groups" in stats
    assert "top_tactics" in stats
    assert "top_weapons" in stats

    # Strict check: ensure no raw row dumps
    for key, val in stats.items():
        if isinstance(val, list):
            for item in val:
                assert not isinstance(item, pd.Series)


def test_deterministic_report_generation(sample_intelligence_df):
    stats = build_threat_stats_summary(sample_intelligence_df, region="South America")
    report = generate_deterministic_report(stats)
    assert "# HISTORICAL THREAT INTELLIGENCE EXECUTIVE BRIEF" in report
    assert "South America" in report
    assert "Situation Overview" in report
    assert "Key Trends" in report
    assert "Analytical Limitations" in report
    assert "1993" in report


def test_gemini_report_fallback_when_no_key(sample_intelligence_df, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    stats = build_threat_stats_summary(sample_intelligence_df)
    report = generate_gemini_report(stats, api_key=None)
    assert "# HISTORICAL THREAT INTELLIGENCE EXECUTIVE BRIEF" in report
    assert "Situation Overview" in report


def test_validate_query_spec_whitelist():
    # Valid spec
    valid_spec = {
        "filters": [{"column": "country_txt", "op": "==", "value": "Colombia"}],
        "group_by": "attacktype1_txt",
        "metric": "count",
        "sort": "desc",
        "top_n": 5,
        "chart_type": "bar",
    }
    is_valid, msg = validate_query_spec(valid_spec)
    assert is_valid, msg

    # Unauthorized column
    bad_col_spec = {
        "filters": [{"column": "unauthorized_secret_col", "op": "==", "value": "val"}],
        "group_by": "attacktype1_txt",
    }
    is_valid, msg = validate_query_spec(bad_col_spec)
    assert not is_valid
    assert "Unauthorized filter column" in msg

    # Unauthorized operator
    bad_op_spec = {
        "filters": [{"column": "country_txt", "op": "LIKE", "value": "%test%"}],
    }
    is_valid, msg = validate_query_spec(bad_op_spec)
    assert not is_valid
    assert "Unauthorized filter operator" in msg


def test_validate_query_spec_malicious_rejection():
    # Attempt code injection in value
    injection_spec = {
        "filters": [{"column": "country_txt", "op": "==", "value": "Colombia; __import__('os').system('dir')"}],
    }
    is_valid, msg = validate_query_spec(injection_spec)
    assert not is_valid
    assert "malicious pattern" in msg.lower()


def test_execute_query_spec_pure_pandas(sample_intelligence_df):
    spec = {
        "filters": [{"column": "country_txt", "op": "==", "value": "Colombia"}],
        "group_by": "gname",
        "metric": "sum",
        "metric_column": "nkill",
        "sort": "desc",
        "top_n": 5,
        "chart_type": "bar",
    }
    result_df, chart_type = execute_query_spec(spec, sample_intelligence_df)
    assert chart_type == "bar"
    assert len(result_df) == 1
    assert result_df.iloc[0]["gname"] == "Revolutionary Armed Forces of Colombia (FARC)"
    assert result_df.iloc[0]["sum_nkill"] == 6


def test_parse_query_deterministically():
    spec1 = parse_query_deterministically("What are the deadliest groups globally?")
    assert spec1["group_by"] == "gname"
    assert spec1["metric"] == "sum"

    spec2 = parse_query_deterministically("Show me the annual trend of incidents")
    assert spec2["group_by"] == "iyear"
    assert spec2["chart_type"] == "line"

    spec3 = parse_query_deterministically("What are the most common weapon types in the Middle East?")
    assert spec3["group_by"] == "weaptype1_txt"


def test_ask_analyst_offline(sample_intelligence_df, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    resp = ask_analyst("Top countries by casualties", sample_intelligence_df, api_key=None)
    assert resp["success"] is True
    assert len(resp["dataframe"]) > 0
    assert "answer" in resp
    assert len(resp["answer"]) > 10


def test_pdf_export_generation(sample_intelligence_df):
    stats = build_threat_stats_summary(sample_intelligence_df)
    report_md = generate_deterministic_report(stats)
    pdf_bytes = generate_pdf_report(report_md, stats)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    # PDF magic byte header check: %PDF
    assert pdf_bytes.startswith(b"%PDF")


def test_sanitize_text_for_pdf():
    raw_text = "Analysis — with en-dash – and quotes “sample” • bullet"
    sanitized = sanitize_text_for_pdf(raw_text)
    assert "“" not in sanitized
    assert "•" not in sanitized
    assert "bullet" in sanitized
