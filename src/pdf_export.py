"""
PDF export module for formatting and rendering intelligence briefs as downloadable documents.
Utilizes fpdf2 to produce structured, styled executive briefing reports.
"""

import io
import logging
import re
from typing import Any, Dict, Optional, Union

from fpdf import FPDF

logger = logging.getLogger(__name__)


def sanitize_text_for_pdf(text: str) -> str:
    """
    Sanitizes Unicode characters to standard latin-1 / ASCII equivalents
    to prevent encoding exceptions with standard core PDF fonts.
    """
    if not isinstance(text, str):
        return ""
    replacements = {
        "\u2013": "-",
        "\u2014": "--",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "*",
        "\u2026": "...",
        "\u00a0": " ",
    }
    for orig, rep in replacements.items():
        text = text.replace(orig, rep)
    # Filter out remaining unsupported non-ASCII characters
    return text.encode("latin-1", "replace").decode("latin-1")


class IntelligenceBriefPDF(FPDF):
    """Custom styled FPDF document for intelligence executive briefs."""

    def __init__(self, theatre: str = "Global Scope"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.theatre = sanitize_text_for_pdf(theatre)
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(15, 15, 15)

    def header(self):
        # Top classification header banner
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(180, 20, 20)  # Crimson security banner
        self.cell(
            0,
            5,
            "HISTORICAL RETROSPECTIVE INTELLIGENCE BRIEF // UNCLASSIFIED / EDUCATIONAL",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(120, 120, 120)
        self.cell(
            0,
            4,
            f"Scope: {self.theatre} | GTD Historical Archive (1970-2017)",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        self.line(15, 23, 195, 23)
        self.ln(6)

    def footer(self):
        self.set_y(-14)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.line(15, 283, 195, 283)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(130, 130, 130)
        page_str = f"Page {self.page_no()}"
        self.cell(0, 5, page_str, align="R", new_x="LMARGIN", new_y="TOP")
        self.cell(
            0,
            5,
            "AI-Based Military Intelligence & Threat Analysis Dashboard | Historical Retrospective",
            align="L",
            new_x="LMARGIN",
            new_y="NEXT",
        )


def generate_pdf_report(
    markdown_text: str,
    stats: Optional[Dict[str, Any]] = None,
    output_path: Optional[Union[str, io.BytesIO]] = None,
) -> bytes:
    """
    Renders an intelligence brief and statistical highlights into a PDF document.

    Returns:
        bytes: Raw PDF binary stream.
    """
    region_title = "Global Scope"
    if stats and "metadata" in stats:
        region_title = stats["metadata"].get("region", "Global Scope")

    pdf = IntelligenceBriefPDF(theatre=region_title)
    pdf.add_page()

    # Process and sanitize markdown lines
    lines = markdown_text.split("\n")

    for raw_line in lines:
        line = sanitize_text_for_pdf(raw_line).strip()
        if not line:
            pdf.ln(2)
            continue

        # Level 1 Heading: # Title
        if line.startswith("# "):
            heading_text = line[2:].strip().upper()
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(20, 30, 50)
            pdf.ln(2)
            pdf.multi_cell(0, 7, heading_text)
            pdf.ln(1)
            continue

        # Level 2 / 3 Heading: ### Heading
        if line.startswith("### ") or line.startswith("## "):
            heading_text = re.sub(r"^#+\s*", "", line).strip()
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(160, 30, 30)  # Dark crimson subsection
            pdf.ln(3)
            pdf.multi_cell(0, 6, heading_text)
            pdf.ln(1)
            continue

        # Horizontal separator
        if line.startswith("---") or line.startswith("***"):
            pdf.set_draw_color(220, 220, 220)
            pdf.set_line_width(0.2)
            pdf.line(pdf.get_x(), pdf.get_y(), 195, pdf.get_y())
            pdf.ln(2)
            continue

        # Bullet items
        if line.startswith("- ") or line.startswith("* "):
            bullet_text = line[2:].strip()
            # Clean markdown bold markers **text**
            clean_text = re.sub(r"\*\*(.*?)\*\*", r"\1", bullet_text)
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(40, 40, 40)
            pdf.cell(5, 5, "- ", align="L", new_x="RIGHT", new_y="TOP")
            pdf.multi_cell(0, 5, clean_text)
            pdf.ln(1)
            continue

        # Standard paragraph text
        clean_para = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
        clean_para = re.sub(r"\*(.*?)\*", r"\1", clean_para)
        clean_para = re.sub(r"`(.*?)`", r"\1", clean_para)

        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(0, 4.8, clean_para)
        pdf.ln(1)

    # Add appendix metadata card if stats provided
    if stats and "totals" in stats:
        totals = stats["totals"]
        pdf.ln(4)
        pdf.set_fill_color(245, 247, 250)
        pdf.set_draw_color(210, 220, 230)
        pdf.rect(15, pdf.get_y(), 180, 18, style="DF")

        curr_y = pdf.get_y() + 2
        pdf.set_xy(17, curr_y)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(30, 50, 70)
        pdf.cell(0, 4, "METRIC HIGHLIGHTS & AGGREGATE TELEMETRY:", new_x="LMARGIN", new_y="NEXT")

        pdf.set_xy(17, curr_y + 5)
        pdf.set_font("Helvetica", "", 7.5)
        metric_str = (
            f"Incidents: {totals.get('incidents', 0):,} | "
            f"Fatalities: {totals.get('fatalities', 0):,} | "
            f"Wounded: {totals.get('wounded', 0):,} | "
            f"Casualty Reporting Fidelity: {totals.get('casualty_reporting_rate_pct', 0.0)}%"
        )
        pdf.cell(0, 4, sanitize_text_for_pdf(metric_str), new_x="LMARGIN", new_y="NEXT")

    # Output binary
    pdf_bytes = pdf.output()
    if output_path is not None:
        if isinstance(output_path, (str, bytes)):
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)
        elif hasattr(output_path, "write"):
            output_path.write(pdf_bytes)

    return bytes(pdf_bytes)
