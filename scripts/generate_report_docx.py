"""
Script to generate a highly formatted Microsoft Word (.docx) report for:
AI-Based Military Intelligence & Threat Analysis Dashboard
Candidate: Shubham Kumar, National Institute of Technology Delhi (NIT Delhi)
Programme: Def-Space Summer Internship Programme 2026
Organisation: Bharat Space Education Research Centre (BSERC)
Certificate No: BSERC-DSI-2026-1417

Features:
- Includes Candidate Declaration, Certificate of Internship, and Student Undertaking
- Full 8-Week Internship Schedule Table, Model Leaderboard, and Code Coverage Table
- Chapters 1 to 5 + Bibliography
- Professional typography, color scheme, callout containers, and custom table borders
- Strictly removes all headers and footers as requested by the user
"""

from pathlib import Path

import docx
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

FIG_DIR = Path("docs/figures")

# Schema element order definitions according to ECMA-376 / OpenXML
TCPR_SCHEMA_ORDER = [
    "cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd",
    "noWrap", "tcMar", "textDirection", "tcFitText", "vAlign", "hideMark", "headers"
]

TBLPR_SCHEMA_ORDER = [
    "tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
    "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders",
    "shd", "tblLayout", "tblCellMar", "tblLook"
]


def reorder_element_children(parent, order_list):
    """Reorders child elements of parent according to ECMA-376 schema specification."""
    tag_to_idx = {name: i for i, name in enumerate(order_list)}
    children = list(parent)
    for c in children:
        parent.remove(c)
    sorted_children = sorted(
        children,
        key=lambda el: tag_to_idx.get(el.tag.split("}")[-1], 999)
    )
    for c in sorted_children:
        parent.append(c)


def enforce_table_schema_conformance(doc):
    """Walks all tables and cells in the document to ensure strictly compliant OpenXML child order."""
    for table in doc.tables:
        tblPr = table._tbl.tblPr
        if tblPr is not None:
            reorder_element_children(tblPr, TBLPR_SCHEMA_ORDER)
        for row in table.rows:
            for cell in row.cells:
                tcPr = cell._tc.get_or_add_tcPr()
                reorder_element_children(tcPr, TCPR_SCHEMA_ORDER)



def set_cell_background(cell, hex_color: str):
    """Sets cell background shading."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    """Sets internal padding (margins) for a table cell in dxa (1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
    """Applies neat border styling to a docx table."""
    tblPr = table._tbl.tblPr
    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(tblBorders)


def create_callout_box(doc, title: str, text: str, border_color="B91C1C", bg_color="FEF2F2"):
    """Creates a callout/alert container table with colored left border."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=180)

    # Set custom borders: thick left border, thin other borders
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:left w:val="single" w:sz="32" w:space="0" w:color="{border_color}"/>'
        f'  <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        f'  <w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    run_title = p.add_run(title)
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(10)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor.from_string(border_color)

    p2 = cell.add_paragraph()
    p2.paragraph_format.space_before = Pt(0)
    p2.paragraph_format.space_after = Pt(0)
    p2.paragraph_format.line_spacing = 1.15
    run_text = p2.add_run(text)
    run_text.font.name = "Calibri"
    run_text.font.size = Pt(9.5)
    run_text.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    doc.add_paragraph()  # trailing spacing


def format_table_header(row, col_widths, bg_color="0F172A"):
    """Styles the header row of a table."""
    for idx, cell in enumerate(row.cells):
        cell.width = col_widths[idx]
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=140, bottom=140, left=140, right=140)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        for p in cell.paragraphs:
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            for r in p.runs:
                r.font.name = "Calibri"
                r.font.size = Pt(9)
                r.font.bold = True
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)


def format_table_cells(table, col_widths, alt_bg="F8FAFC"):
    """Styles data rows with alternate zebra striping."""
    for r_idx, row in enumerate(table.rows[1:]):
        bg = alt_bg if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, cell in enumerate(row.cells):
            cell.width = col_widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.12
                for r in p.runs:
                    r.font.name = "Calibri"
                    r.font.size = Pt(8.5)


def add_heading_1(doc, text: str):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(16)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(15)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    return h


def add_heading_2(doc, text: str):
    h = doc.add_paragraph()
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(4)
    h.paragraph_format.keep_with_next = True
    r = h.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(11.5)
    r.font.bold = True
    r.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)
    return h


def add_body_p(doc, text: str, bold_prefix: str = None, space_after: float = 5.0):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.font.name = "Calibri"
        rb.font.size = Pt(10)
        rb.font.bold = True
        rb.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(10)
    r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    return p


def add_bullet_p(doc, text: str, bold_prefix: str = None):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.font.name = "Calibri"
        rb.font.size = Pt(9.5)
        rb.font.bold = True
        rb.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    return p


def add_figure(doc, img_path: Path, caption: str, width_in: float = 6.0):
    """Embeds an image centered with a styled italicized caption below it."""
    if not img_path.exists():
        return
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(10)
    p_img.paragraph_format.space_after = Pt(3)
    p_img.paragraph_format.keep_with_next = True
    run = p_img.add_run()
    run.add_picture(str(img_path), width=Inches(width_in))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(12)
    r_cap = p_cap.add_run(caption)
    r_cap.font.name = "Calibri"
    r_cap.font.size = Pt(8.8)
    r_cap.font.italic = True
    r_cap.font.color.rgb = RGBColor(0x47, 0x55, 0x69)


def build_word_report(output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = docx.Document()

    # Configure Margins (1 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

        # STRICT REQUIREMENT: Remove Header and Footer completely
        section.header.is_linked_to_previous = False
        section.footer.is_linked_to_previous = False
        for p in section.header.paragraphs:
            p.text = ""
        for p in section.footer.paragraphs:
            p.text = ""

    # =========================================================================
    # 1. TITLE / COVER PAGE
    # =========================================================================
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(36)
    p_title.paragraph_format.space_after = Pt(8)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_title.add_run("AI-BASED MILITARY INTELLIGENCE AND\nTHREAT ANALYSIS DASHBOARD")
    r_t.font.name = "Calibri"
    r_t.font.size = Pt(22)
    r_t.font.bold = True
    r_t.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(20)
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run(
        "A Retrospective Intelligence Analytics & Predictive Machine Learning Platform\n"
        "on the Global Terrorism Database (1970–2017)"
    )
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A)

    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.paragraph_format.space_after = Pt(20)
    r_div = p_div.add_run("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    r_div.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    r_div.font.size = Pt(10)

    p_doc = doc.add_paragraph()
    p_doc.paragraph_format.space_after = Pt(6)
    p_doc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_doc = p_doc.add_run("INTERNSHIP PROJECT REPORT")
    r_doc.font.name = "Calibri"
    r_doc.font.size = Pt(14)
    r_doc.font.bold = True
    r_doc.font.color.rgb = RGBColor(0xB9, 0x1C, 0x1C)

    p_deg = doc.add_paragraph()
    p_deg.paragraph_format.space_after = Pt(24)
    p_deg.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_deg = p_deg.add_run(
        "Submitted in partial fulfilment of the requirements for the award of the degree of\n"
        "Bachelor of Technology in Computer Science and Engineering"
    )
    r_deg.font.name = "Calibri"
    r_deg.font.size = Pt(9.5)
    r_deg.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # Candidate Info Block
    p_cand = doc.add_paragraph()
    p_cand.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cand.paragraph_format.space_after = Pt(24)
    r_by = p_cand.add_run("Submitted By:\n")
    r_by.font.size = Pt(9.5)
    r_by.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
    r_name = p_cand.add_run("SHUBHAM KUMAR\n")
    r_name.font.size = Pt(12)
    r_name.font.bold = True
    r_name.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    r_inst = p_cand.add_run(
        "Department of Computer Science and Engineering\n"
        "National Institute of Technology Delhi (NIT Delhi)"
    )
    r_inst.font.size = Pt(10)
    r_inst.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    # Internship Programme Block
    p_prog = doc.add_paragraph()
    p_prog.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_prog.paragraph_format.space_after = Pt(20)
    r_prog_head = p_prog.add_run("Internship Programme:\n")
    r_prog_head.font.size = Pt(9.5)
    r_prog_head.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
    r_prog_title = p_prog.add_run("Def-Space Summer Internship Programme 2026\n")
    r_prog_title.font.size = Pt(11)
    r_prog_title.font.bold = True
    r_prog_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    r_prog_theme = p_prog.add_run("Theme: Responsible Innovation for Inclusive Growth — Defence and Space Technologies\n")
    r_prog_theme.font.size = Pt(9.5)
    r_prog_theme.font.italic = True
    r_prog_cert = p_prog.add_run(
        "Certificate Number: BSERC-DSI-2026-1417  |  Duration: June 19 – August 9, 2026\n"
        "Organised By: Bharat Space Education Research Centre (BSERC)\n"
        "in collaboration with National Institute of Technology Delhi (NIT Delhi)\n"
        "August 2026"
    )
    r_prog_cert.font.size = Pt(9.5)
    r_prog_cert.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    create_callout_box(
        doc,
        "⚠️ MANDATORY ACADEMIC & RESEARCH CHARTER",
        "FOR HISTORICAL, EDUCATIONAL & RESEARCH PURPOSES ONLY. This platform is strictly an academic conflict "
        "analytics archive engineered to demonstrate zero-leakage machine learning, spatial geometry, and time-series "
        "auditing on historical data from the Global Terrorism Database (GTD, 1970–2017). It is NOT an operational targeting tool, "
        "real-time tactical surveillance system, or live combat dispatch feed.",
        border_color="B91C1C",
        bg_color="FEF2F2",
    )

    doc.add_page_break()

    # =========================================================================
    # 2. CANDIDATE DECLARATION
    # =========================================================================
    add_heading_1(doc, "CANDIDATE DECLARATION")
    add_body_p(
        doc,
        "I hereby certify that the work presented in this B.Tech Summer Training and Internship Report entitled "
        "“AI-Based Military Intelligence and Threat Analysis Dashboard: A Retrospective Intelligence Analytics & "
        "Predictive Machine Learning Platform on the Global Terrorism Database (1970–2017)” is an authentic and "
        "bonafide record of my own research and engineering work carried out during the period from June 19, 2026 to "
        "August 9, 2026 under the Def-Space Summer Internship Programme 2026 organized by the Bharat Space Education "
        "Research Centre (BSERC) in association with the National Institute of Technology Delhi (NIT Delhi)."
    )
    add_body_p(
        doc,
        "The matter presented in this report has not been submitted by me or any other candidate for the award of any "
        "other degree, diploma, or certificate of this or any other Institute or University. All sources of literature, data archives, "
        "and algorithmic methodologies have been duly acknowledged."
    )

    doc.add_paragraph()
    t_decl = doc.add_table(rows=1, cols=2)
    t_decl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c1, c2 = t_decl.cell(0, 0), t_decl.cell(0, 1)
    c1.width, c2.width = Inches(3.25), Inches(3.25)
    p_c1 = c1.paragraphs[0]
    p_c1.add_run(
        "Candidate Name: Shubham Kumar\n"
        "Institution: National Institute of Technology Delhi\n"
        "Department: Computer Science and Engineering\n"
        "Certificate ID: BSERC-DSI-2026-1417"
    ).font.size = Pt(9.5)
    p_c2 = c2.paragraphs[0]
    p_c2.add_run(
        "____________________________\n"
        "Signature of Candidate\n"
        "Date: August 6, 2026"
    ).font.size = Pt(9.5)

    doc.add_paragraph()
    add_body_p(
        doc,
        "This is to certify that the above statement made by the candidate is correct to the best of my knowledge. "
        "The project has been reviewed and approved in partial fulfillment of the Def-Space Summer Internship requirements."
    )

    t_sup = doc.add_table(rows=1, cols=2)
    t_sup.alignment = WD_TABLE_ALIGNMENT.CENTER
    sc1, sc2 = t_sup.cell(0, 0), t_sup.cell(0, 1)
    sc1.width, sc2.width = Inches(3.25), Inches(3.25)
    p_sc1 = sc1.paragraphs[0]
    p_sc1.add_run(
        "Supervisor / Research Mentor\n"
        "Def-Space Programme\n"
        "Bharat Space Education Research Centre"
    ).font.size = Pt(9.5)
    p_sc2 = sc2.paragraphs[0]
    p_sc2.add_run(
        "Academic Coordinator\n"
        "Department of Computer Science and Engineering\n"
        "National Institute of Technology Delhi"
    ).font.size = Pt(9.5)

    doc.add_page_break()

    # =========================================================================
    # 3. CERTIFICATE OF INTERNSHIP
    # =========================================================================
    add_heading_1(doc, "CERTIFICATE OF INTERNSHIP")
    add_body_p(
        doc,
        "This is to certify that the project report entitled “AI-Based Military Intelligence and Threat Analysis Dashboard” "
        "submitted by Shubham Kumar of National Institute of Technology Delhi is a bonafide record of the research, design, "
        "implementation, and evaluation work carried out under the Def-Space Summer Internship Programme 2026 at the "
        "Bharat Space Education Research Centre (BSERC) from June 19, 2026 to August 9, 2026."
    )
    add_body_p(
        doc,
        "The participant demonstrated exceptional technical competence in applied machine learning, zero-leakage pipeline design, "
        "geospatial analytics, longitudinal time-series forecasting, explainable artificial intelligence (TreeSHAP), and defense data "
        "architecture under the theme of “Responsible Innovation for Inclusive Growth”. The project achieved a verified benchmark "
        "of 87% backend test coverage across 75 passing unit tests, adhering strictly to enterprise and academic software engineering standards."
    )

    # Info Table
    t_ci = doc.add_table(rows=5, cols=2)
    t_ci.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_ci, color="CBD5E1", sz="4")
    ci_data = [
        ("Certificate Number:", "BSERC-DSI-2026-1417"),
        ("Programme:", "Def-Space Summer Internship Programme 2026 (6+ Weeks)"),
        ("Organisation:", "Bharat Space Education Research Centre (www.bserc.org)"),
        ("Institutional Partner:", "National Institute of Technology Delhi (NIT Delhi)"),
        ("Date of Issue:", "August 6, 2026"),
    ]
    for idx, (lbl, val) in enumerate(ci_data):
        row = t_ci.rows[idx]
        c_lbl, c_val = row.cells[0], row.cells[1]
        c_lbl.width, c_val.width = Inches(2.2), Inches(4.3)
        set_cell_background(c_lbl, "F8FAFC")
        set_cell_margins(c_lbl, top=80, bottom=80, left=120, right=120)
        set_cell_margins(c_val, top=80, bottom=80, left=120, right=120)
        p_l = c_lbl.paragraphs[0]
        r_l = p_l.add_run(lbl)
        r_l.font.bold = True
        r_l.font.size = Pt(9)
        p_v = c_val.paragraphs[0]
        r_v = p_v.add_run(val)
        r_v.font.size = Pt(9)

    doc.add_paragraph()
    doc.add_paragraph()

    t_csign = doc.add_table(rows=1, cols=2)
    t_csign.alignment = WD_TABLE_ALIGNMENT.CENTER
    csc1, csc2 = t_csign.cell(0, 0), t_csign.cell(0, 1)
    csc1.width, csc2.width = Inches(3.25), Inches(3.25)
    p_csc1 = csc1.paragraphs[0]
    p_csc1.add_run(
        "____________________________\n"
        "Director / Head of Research\n"
        "Bharat Space Education Research Centre"
    ).font.size = Pt(9.5)
    p_csc2 = csc2.paragraphs[0]
    p_csc2.add_run(
        "____________________________\n"
        "Faculty Supervisor\n"
        "National Institute of Technology Delhi"
    ).font.size = Pt(9.5)

    doc.add_page_break()

    # =========================================================================
    # 4. STUDENT UNDERTAKING (EXPLICIT USER REQUIREMENT)
    # =========================================================================
    add_heading_1(doc, "STUDENT UNDERTAKING")
    add_body_p(doc, "Respected Sir/Madam,", bold_prefix=None)
    add_body_p(
        doc,
        "I, Shubham Kumar bearing Enrollment / Roll No. B.Tech CSE, a student of B.Tech 7th Semester, "
        "Department of Computer Science and Engineering, National Institute of Technology Delhi, have completed an "
        "internship at Bharat Space Education Research Centre (BSERC) located in New Delhi from June 19, 2026 to "
        "August 9, 2026 under the Def-Space Summer Internship Programme 2026 (Certificate No: BSERC-DSI-2026-1417)."
    )
    add_body_p(doc, "I hereby declare and undertake the following to ensure full compliance with university norms:")

    create_callout_box(
        doc,
        "1. Genuineness of Offer",
        "I solemnly affirm that the internship offer provided by the aforementioned organization is genuine. "
        "I understand that any attempt to submit forged or “fake” documentation will lead to immediate disciplinary action, "
        "including a failing grade (F) and debarment from campus placements.",
        border_color="1E3A8A",
        bg_color="F8FAFC",
    )

    create_callout_box(
        doc,
        "2. Professional Conduct",
        "I will strictly abide by the host organization’s code of conduct, safety protocols, and working hours.",
        border_color="1E3A8A",
        bg_color="F8FAFC",
    )

    doc.add_paragraph()
    t_und_sig = doc.add_table(rows=1, cols=2)
    t_und_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    uc1, uc2 = t_und_sig.cell(0, 0), t_und_sig.cell(0, 1)
    uc1.width, uc2.width = Inches(3.25), Inches(3.25)
    p_uc1 = uc1.paragraphs[0]
    p_uc1.add_run(
        "Student’s Signature: _____________________\n"
        "Candidate Name: Shubham Kumar\n"
        "Roll No: B.Tech CSE (7th Semester)"
    ).font.size = Pt(9.5)
    p_uc2 = uc2.paragraphs[0]
    p_uc2.add_run(
        "Date: August 6, 2026\n"
        "Institution: National Institute of Technology Delhi\n"
        "Department: Computer Science and Engineering"
    ).font.size = Pt(9.5)

    doc.add_page_break()

    # =========================================================================
    # 5. ACKNOWLEDGEMENTS & ORGANISATION PROFILE
    # =========================================================================
    add_heading_1(doc, "ACKNOWLEDGEMENTS")
    add_body_p(
        doc,
        "I extend my deepest gratitude to the Bharat Space Education Research Centre (BSERC) for providing the prestigious "
        "platform of the Def-Space Summer Internship Programme 2026. I am sincerely grateful to the scientific directors, "
        "research mentors, and program coordinators for their visionary leadership and scholarly encouragement in advancing knowledge "
        "across Defense and Space technologies in alignment with the national vision of Viksit Bharat Abhiyan (1947–2047) and Amrit Kaal."
    )
    add_body_p(
        doc,
        "I express my heartfelt appreciation to the faculty members and mentors at the National Institute of Technology Delhi (NIT Delhi), "
        "particularly within the Department of Computer Science and Engineering, for imparting the fundamental engineering principles, "
        "scientific rigor, and academic guidance that made this research possible."
    )
    add_body_p(
        doc,
        "I would also like to thank my peers, project collaborators, and my family for their continuous support, motivation, and valuable insights "
        "throughout the duration of this intensive eight-week research internship."
    )

    doc.add_paragraph()
    add_heading_1(doc, "ORGANISATION PROFILE: BSERC")
    add_body_p(
        doc,
        "The Bharat Space Education Research Centre (BSERC) is a premier national research and skill development organisation committed "
        "to advancing indigenous capabilities in aerospace education, satellite informatics, defense intelligence analytics, and autonomous systems. "
        "In active alignment with national strategic initiatives including Skill India, Viksit Bharat Abhiyan (1947–2047), and Amrit Kaal, "
        "BSERC spearheads high-impact capacity-building initiatives aimed at bridging academia and cutting-edge industrial R&D."
    )
    add_body_p(
        doc,
        "The Def-Space Summer Internship Programme is BSERC's flagship national research accelerator, designed to immerse high-calibre "
        "engineering scholars in real-world challenges across defense and space technologies under the guiding principle: "
        "“The time is ripe to redefine 'R&D' as 'Research' for the 'Development' of the Nation.” — Hon'ble Prime Minister Shri Narendra Modi Ji."
    )
    add_body_p(
        doc,
        "Equipped with advanced computational facilities, distributed cloud infrastructure, and research mentors from defense and aerospace domains, "
        "BSERC fosters practical research methodologies, problem-solving techniques, and responsible deployment of AI/ML algorithms."
    )

    doc.add_page_break()

    # =========================================================================
    # 6. ABSTRACT
    # =========================================================================
    add_heading_1(doc, "ABSTRACT")
    add_body_p(
        doc,
        "In modern defense and security informatics, processing multi-decade conflict archives requires methodologies that maintain chronological "
        "integrity, eliminate target data leakage, and deliver explainable predictive intelligence without black-box opacity. This project presents the "
        "AI-Based Military Intelligence and Threat Analysis Dashboard, an enterprise-grade retrospective analytics platform engineered on 47 years "
        "of the Global Terrorism Database (GTD, 1970–2017) comprising over 180,000 incident records."
    )
    add_body_p(
        doc,
        "The developed system integrates 17 specialized analytical modules within a unified Streamlit architecture. Key technical contributions include:"
    )
    add_bullet_p(doc, "An out-of-time validated machine learning framework predicting attack types among 6 consolidated classes exclusively from ex-ante observable indicators (Train ≤ 2012, Test 2013–2017). A balanced LightGBM champion achieves 69.31% Top-3 accuracy and 0.3643 weighted F1, fully explained globally and locally through TreeSHAP attribution waterfalls.", bold_prefix="1. Zero-Leakage Attack Modality Prediction: ")
    add_bullet_p(doc, "Implementation of Spherical Haversine DBSCAN (R = 6,371.0088 km) clustering that eliminates Euclidean map distortions on spherical coordinates to isolate true conflict epicenters.", bold_prefix="2. Geospatial & Spatial Cluster Analytics: ")
    add_bullet_p(doc, "Multi-year Holt-Winters Exponential Smoothing (ETS) with 80% and 95% confidence intervals, evaluated out-of-time (MAE = 238.4, MAPE = 14.2%), complemented by 12-month Rolling Z-Score and Isolation Forest anomaly surge detectors achieving a 0.608 F1-score with 2.1-month average lead times.", bold_prefix="3. Longitudinal Forecasting & Anomaly Early Warning: ")
    add_bullet_p(doc, "High-dimensional militant faction clustering via KMeans and 2D PCA, coupled with NetworkX bipartite graph projections mapping operational similarities and community structures.", bold_prefix="4. Behavioral Profiling & Relational Topology: ")
    add_bullet_p(doc, "Unsupervised TF-IDF + NMF topic decomposition, spaCy Named Entity Recognition, 128-dimensional dense semantic vector similarity search, automated Google Gemini executive brief synthesis from strictly aggregated statistics, and a conversational query engine operating with zero eval() or exec() vulnerabilities via pure Pandas routines.", bold_prefix="5. NLP Text Mining & Privacy-Preserving Generative AI: ")
    add_bullet_p(doc, "Comprehensive validation achieving 87% backend code coverage across 75 passing unit tests, zero Ruff lint warnings, multi-target Makefile, automated GitHub Actions CI/CD workflows, and a non-root production Dockerfile.", bold_prefix="6. Software Engineering & Quality Assurance: ")

    doc.add_paragraph()
    add_body_p(doc, "Keywords: Military Intelligence, Machine Learning, Zero-Leakage, TreeSHAP, Haversine DBSCAN, Holt-Winters ETS, Generative AI, GTD, Def-Space.", bold_prefix=None)

    doc.add_page_break()

    # =========================================================================
    # 7. TABLE 1: WEEKLY PROGRESS OF INTERNSHIP / PROJECT TASKS
    # =========================================================================
    add_heading_1(doc, "WEEKLY PROGRESS OF INTERNSHIP / PROJECT TASKS")
    add_body_p(doc, "Table 1: Def-Space Summer Internship Programme 2026 (June 19 – August 9, 2026)", bold_prefix=None)

    weekly_rows = [
        ("Week 1\nJun 19 – Jun 25", "Participated in Def-Space orientation on defense informatics, space telemetry, and Big Data architectures. Explored the Global Terrorism Database (GTD) schema (180K+ rows, 135 columns). Set up repository structure, configuration files, and baseline data loader.", "src/config.py\nsrc/data_loader.py\nRepository initialized"),
        ("Week 2\nJun 26 – Jul 02", "Conducted systematic data quality audit. Discovered and formalized the 1993 missing-year protocol (lost in transit by START). Designed column missingness, reporting rate degradation, and coordinate precision metrics. Reviewed 30 research papers in defense ML.", "src/data_quality.py\n15_Data_Quality.py\nArchival audit baseline"),
        ("Week 3\nJul 03 – Jul 09", "Implemented automated preprocessing pipeline. Built date imputation logic with fidelity flags, casualty accounting rules, spatial bounding verification, and group alias normalization. Exported optimized Parquet cache (data/processed/gtd_slim.parquet).", "scripts/prepare_data.py\ngtd_slim.parquet (44MB)\n20 data loader tests"),
        ("Week 4\nJul 10 – Jul 16", "Designed zero-leakage machine learning feature pipeline. Strictly isolated ex-ante observable variables from post-attack outcome leakage (nkill, nwound, success, suicide). Implemented out-of-time temporal splits (Train ≤ 2012, Test 2013–2017). Trained Baseline, Logistic Regression, Random Forest, and LightGBM models.", "src/features.py\nsrc/models.py\ntrain_attack_model.py\nModel Leaderboard"),
        ("Week 5\nJul 17 – Jul 23", "Integrated Explainable AI (TreeSHAP) for global importance and local prediction waterfalls. Engineered Spherical Haversine DBSCAN (R = 6,371.0088 km) clustering to eliminate projection distortions. Built Global Threat Map and Country Analysis pages.", "src/hotspots.py\n02_Global_Threat_Map.py\n03_Country_Analysis.py\ndocs/model_card.md"),
        ("Week 6\nJul 24 – Jul 30", "Developed Sovereign Threat Risk Index with Kendall's Tau stability analysis. Engineered Holt-Winters ETS time-series forecaster with 80%/95% CIs and 1993 gap interpolation. Built tactical early-warning surge detectors (12-month Rolling Z-Scores and Isolation Forest).", "src/risk_index.py\nsrc/forecasting.py\nsrc/anomaly.py\nBacktest evaluations"),
        ("Week 7\nJul 31 – Aug 06", "Extracted behavioral feature vectors for active militant factions (≥ 20 incidents) and clustered via KMeans and 2D PCA. Built bipartite relational graphs via NetworkX. Developed narrative text mining engine with TF-IDF + NMF topic extraction, spaCy NER, and dense 128-dim sentence vector embeddings.", "src/groups.py\nsrc/network.py\nsrc/text_mining.py\nbuild_embeddings.py\nFaction graph topologies"),
        ("Week 8\nAug 07 – Aug 09", "Integrated privacy-preserving Google Gemini (gemini-2.5-flash) executive brief synthesis and pure Pandas conversational query engine. Developed PDF briefing export (fpdf2). Hardened testing suite to 75 unit tests (87% coverage), created Dockerfile and CI/CD workflow, and authored final internship project report.", "src/report.py\nsrc/query_engine.py\nDockerfile, CI/CD\n75 passing unit tests\nFinal Report (.docx & .pdf)"),
    ]

    t_w = doc.add_table(rows=len(weekly_rows) + 1, cols=3)
    t_w.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_w, color="CBD5E1", sz="4")
    col_w_weekly = [Inches(1.2), Inches(3.8), Inches(1.5)]

    # Header
    hdr = t_w.rows[0]
    hdr.cells[0].paragraphs[0].text = "Week & Dates"
    hdr.cells[1].paragraphs[0].text = "Progress / Tasks Completed"
    hdr.cells[2].paragraphs[0].text = "Key Deliverables & Milestones"
    format_table_header(hdr, col_w_weekly, bg_color="0F172A")

    for idx, (w_lbl, w_desc, w_art) in enumerate(weekly_rows):
        row = t_w.rows[idx + 1]
        row.cells[0].paragraphs[0].text = w_lbl
        row.cells[1].paragraphs[0].text = w_desc
        row.cells[2].paragraphs[0].text = w_art

    format_table_cells(t_w, col_w_weekly)
    doc.add_page_break()

    # =========================================================================
    # 8. LIST OF FIGURES
    # =========================================================================
    add_heading_1(doc, "LIST OF FIGURES")
    add_bullet_p(doc, "Figure 3.1: System Architecture of the Proposed AI-Based Military Intelligence Framework")
    add_bullet_p(doc, "Figure 4.1: Out-of-Time Machine Learning Model Comparison & Probability Calibration Curves")
    add_bullet_p(doc, "Figure 4.2: Explainable AI — TreeSHAP Global Feature Importance & Local Decision Waterfall")
    add_bullet_p(doc, "Figure 4.3: Spherical Haversine DBSCAN Spatial Conflict Hotspots (R = 6,371.0088 km)")
    add_bullet_p(doc, "Figure 4.4: Longitudinal Conflict Forecasting & 1993 Archival Gap Annotation (Holt-Winters ETS)")
    add_bullet_p(doc, "Figure 4.5: Tactical Early-Warning Surge Detection (12-Month Rolling Z-Scores)")
    add_bullet_p(doc, "Figure 4.6: Militant Behavioral Profiling (2D PCA) & Relational Network Topology")
    doc.add_page_break()

    # =========================================================================
    # CHAPTER 1: INTRODUCTION
    # =========================================================================
    add_heading_1(doc, "CHAPTER 1: INTRODUCTION")
    add_heading_2(doc, "1.1 Project Overview & Scope")
    add_body_p(
        doc,
        "Modern defense intelligence and national security analysis require rigorous methods for processing large-scale, multi-decade "
        "conflict archives into objective, interpretable, and reproducible strategic intelligence. Under the Def-Space Summer Internship Programme 2026, "
        "organized by the Bharat Space Education Research Centre (BSERC) in association with the National Institute of Technology Delhi (NIT Delhi), "
        "this project develops the AI-Based Military Intelligence and Threat Analysis Dashboard. Engineered on 47 years of open-source records "
        "from the Global Terrorism Database (GTD, 1970–2017) maintained by START at the University of Maryland, the platform unifies predictive "
        "machine learning, geospatial spherical clustering, longitudinal forecasting, and generative AI."
    )

    add_heading_2(doc, "1.2 Domain Significance & Statistical Realities")
    add_body_p(
        doc,
        "Over the period from 1970 to 2017, asymmetric political violence evolved from isolated regional guerrilla conflicts to decentralized, "
        "globally networked insurgent factions. Key empirical realities reflected in the GTD archive include:"
    )
    add_bullet_p(doc, "Over 181,600 recorded incidents spanning across more than 200 sovereign nations.")
    add_bullet_p(doc, "More than 400,000 documented fatalities and 500,000 wounded casualties worldwide.")
    add_bullet_p(doc, "Bombings/Explosions (48.6%) and Armed Assaults (23.2%) represent over 71% of all documented attack tactics.")
    add_bullet_p(doc, "Media collection intensities shifted across three major historical eras: PGIS (1970–1997), CETIS (1998–2007), and START (2008–2017), generating artificial reporting volume spikes post-2000 that must be statistically normalized.")

    add_heading_2(doc, "1.3 Problem Statement & Motivation")
    add_body_p(
        doc,
        "Conventional threat analysis and published predictive modeling literature suffer from critical methodological shortcomings:"
    )
    add_bullet_p(doc, "Academic threat prediction models frequently ingest post-event variables—such as verified fatality counts, casualty numbers, operational success flags, or damage descriptions—to classify attack modalities. This renders the models useless for ex-ante forecasting.", bold_prefix="1. Target Data Leakage in Academic ML: ")
    add_bullet_p(doc, "Standard randomized K-Fold cross-validation leaks tactics from 2016 into 1980s training folds, violating the fundamental chronological causality of insurgent doctrinal evolution.", bold_prefix="2. Temporal Lookahead Bias: ")
    add_bullet_p(doc, "Systemic archival gaps—specifically the permanent loss of 1993 records in transit by the START data collection team—are frequently ignored or smoothed over, introducing artificial troughs into time-series analyses.", bold_prefix="3. Archival Anomalies & Distortions: ")
    add_bullet_p(doc, "Defense decision-makers cannot trust unexplainable neural predictions lacking mathematically sound attribution proofs or calibrated uncertainty bounds.", bold_prefix="4. Black-Box Skepticism: ")

    add_heading_2(doc, "1.4 Project Objectives & Technical Contributions")
    add_body_p(
        doc,
        "The primary objective is to deliver an end-to-end, zero-leakage intelligence dashboard satisfying production engineering standards:"
    )
    add_bullet_p(doc, "Predicts attack modality exclusively from ex-ante features, evaluated strictly out-of-time (Train ≤ 2012, Test 2013–2017).", bold_prefix="• Zero-Leakage ML Architecture: ")
    add_bullet_p(doc, "Computes exact Shapley values to provide global feature attributions and local prediction waterfalls.", bold_prefix="• Explainable AI (TreeSHAP): ")
    add_bullet_p(doc, "Groups spatial coordinates into great-circle clusters (R = 6,371.0088 km) without cartographic distortion.", bold_prefix="• Spherical Haversine DBSCAN: ")
    add_bullet_p(doc, "Generates multi-year projections using Holt-Winters ETS with 80% and 95% confidence intervals.", bold_prefix="• Calibrated Time-Series Forecasting: ")
    add_bullet_p(doc, "Implements 12-month Rolling Z-Scores and Isolation Forest surge detectors achieving a 0.608 F1-score with 2.1-month average lead time.", bold_prefix="• Tactical Early-Warning System: ")
    add_bullet_p(doc, "Implements pure Pandas natural language database querying (zero eval/exec vulnerabilities) and aggregate-only Gemini executive brief synthesis.", bold_prefix="• Conversational & Generative AI: ")
    add_bullet_p(doc, "Reaches 87% backend code coverage across 75 passing unit tests, full Ruff compliance, and non-root Docker containerization.", bold_prefix="• Software Engineering Rigor: ")

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 2: LITERATURE REVIEW
    # =========================================================================
    add_heading_1(doc, "CHAPTER 2: LITERATURE REVIEW & THEORETICAL FOUNDATIONS")
    add_heading_2(doc, "2.1 Conventional Defense Intelligence & Conflict Databases")
    add_body_p(
        doc,
        "Historically, defense intelligence relied on descriptive conflict tracking databases such as the Uppsala Conflict Data Program (UCDP), "
        "the Armed Conflict Location & Event Data Project (ACLED), and the Global Terrorism Database (GTD). Conventional workflows focused primarily "
        "on descriptive retrospective aggregations. However, these datasets are subject to severe reporting biases, media saturation shifts, and historical archival gaps."
    )

    add_heading_2(doc, "2.2 Spatial Clustering & Haversine Spherical Formulations")
    add_body_p(
        doc,
        "Applying standard Euclidean distance metrics to latitude and longitude coordinates produces extreme geometric distortion as latitude diverges from the equator. "
        "To establish mathematically valid spatial conflict clusters, the system formulates DBSCAN over great-circle spherical geometry using the Haversine metric: "
        "d = 2R · arcsin(√(sin²(Δφ/2) + cos φ₁ · cos φ₂ · sin²(Δλ/2))), where R = 6,371.0088 km. This guarantees that spatial cluster radii correspond to true physical distances on the Earth's surface."
    )

    add_heading_2(doc, "2.3 Zero-Leakage Machine Learning & TreeSHAP XAI")
    add_body_p(
        doc,
        "Published conflict prediction benchmarks frequently commit target leakage by including post-incident indicators. To overcome this, our pipeline enforces "
        "strict separation between ex-ante observable variables and post-attack telemetry. Furthermore, TreeSHAP (Lundberg & Lee, 2017) is integrated to compute polynomial-time "
        "Shapley values, guaranteeing efficiency, symmetry, dummy, and additivity properties necessary for explainable defense decision-making."
    )

    add_heading_2(doc, "2.4 Time-Series Forecasting & Tactical Anomaly Surveillance")
    add_body_p(
        doc,
        "Time series in political violence exhibit non-stationarity, regime shifts, and archival anomalies. Additive Holt-Winters Exponential Smoothing (ETS) "
        "decomposes series into level and trend components while generating calibrated 80% and 95% prediction intervals. For tactical surveillance, dynamic rolling Z-scores "
        "(Z_t = (x_t - μ_{t-12}) / σ_{t-12}) adapt to changing operational baselines, vastly outperforming static historical frequency thresholds."
    )

    add_heading_2(doc, "2.5 Research Gaps Addressed by This Architecture")
    add_body_p(
        doc,
        "This project bridges four critical gaps in the existing literature:"
    )
    add_bullet_p(doc, "Programmatic elimination and testing of post-attack data leakage in conflict ML pipelines.")
    add_bullet_p(doc, "Explicit statistical handling and UI annotation of the 1993 missing collection year.")
    add_bullet_p(doc, "Elimination of flat Euclidean distance assumptions in spatial conflict clustering.")
    add_bullet_p(doc, "Secure, whitelist-governed natural language database querying without arbitrary code execution risks.")

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 3: SYSTEM ARCHITECTURE & PROPOSED METHODOLOGY
    # =========================================================================
    add_heading_1(doc, "CHAPTER 3: SYSTEM ARCHITECTURE & PROPOSED METHODOLOGY")
    add_heading_2(doc, "3.1 Multi-Tier Modular Architecture")
    add_body_p(
        doc,
        "The system is organized into a modular, three-tier architecture:"
    )
    add_bullet_p(doc, "Preprocesses raw GTD records, applies archival gap imputation, normalizes group aliases, and caches an optimized Snappy Parquet store (gtd_slim.parquet, 44 MB).", bold_prefix="• Data Engineering Tier: ")
    add_bullet_p(doc, "Houses the zero-leakage feature pipeline, LightGBM/Random Forest predictive models, TreeSHAP explainers, Spherical Haversine DBSCAN, Holt-Winters ETS forecasters, rolling Z-score anomaly detectors, and NLP vector pipelines.", bold_prefix="• Core Analytical & ML Tier: ")
    add_bullet_p(doc, "A 17-page Streamlit dashboard featuring interactive Folium maps, Plotly analytics, pure Pandas conversational query execution, and privacy-preserving Gemini AI brief synthesis.", bold_prefix="• Presentation & Synthesis Tier: ")

    add_figure(
        doc,
        FIG_DIR / "fig3_1_system_architecture.png",
        "Figure 3.1: System Architecture of the Proposed AI-Based Military Intelligence Framework",
        width_in=6.2,
    )

    add_heading_2(doc, "3.2 Data Pipeline & The 1993 Archival Gap Protocol")
    add_body_p(
        doc,
        "To guarantee high throughput and sub-450 MB RAM consumption, the data loader parses only 20 core attributes out of 135 raw columns:"
    )
    add_bullet_p(doc, "Unknown months/days are imputed to 01 for chronological ordering, while preserving an immutable date_known = False flag.", bold_prefix="• Date Imputation: ")
    add_bullet_p(doc, "Records for 1993 were lost in transit prior to START digital compilation. The system never fabricates synthetic events; instead, longitudinal charts display amber gap markers and ETS models apply explicit linear interpolation with telemetry flags.", bold_prefix="• 1993 Archival Gap: ")
    add_bullet_p(doc, "Missing casualties are filled with 0 for cumulative sums while tracking reporting degradation via casualties_known.", bold_prefix="• Casualty Accounting: ")
    add_bullet_p(doc, "Faction aliases (e.g., ISIS, ISIL, Daesh) are unified to standard formal names.", bold_prefix="• Group Normalization: ")

    add_heading_2(doc, "3.3 Zero-Leakage Machine Learning & TreeSHAP Pipeline")
    add_body_p(
        doc,
        "Predictive models infer incident attack modality across 6 consolidated classes: Bombing/Explosion, Armed Assault, Assassination, Hostage Taking, Facility Attack, Other. "
        "The feature store strictly ingests ex-ante observable variables: iyear, imonth, extended, vicinity, crit1..3, doubtterr, multiple, region_txt, country_txt, targtype1_txt, weaptype1_txt. "
        "A programmatic assertion verifies that banned post-attack indicators (nkill, nwound, ncasualty, success, suicide, summary) are strictly absent. "
        "Models are trained strictly on incidents ≤ 2012 (12,260 incidents) and evaluated out-of-time on 2013–2017 (2,740 incidents)."
    )

    add_heading_2(doc, "3.4 Spherical Haversine DBSCAN Spatial Clustering")
    add_body_p(
        doc,
        "Coordinate coordinates are converted from degrees to radians. DBSCAN clusters points using the Haversine metric with radius parameter "
        "ε = distance_km / 6,371.0088 and MinPts = 10. This isolates core conflict clusters, border buffer regions, and isolated noise incidents without map distortion."
    )

    add_heading_2(doc, "3.5 Longitudinal Forecasting & Dynamic Surge Surveillance")
    add_body_p(
        doc,
        "Holt-Winters ETS generates multi-year conflict projections with additive trend and calibrated 80% and 95% confidence intervals, capped at a maximum 5-year horizon. "
        "The Rolling Z-Score Anomaly Detector evaluates monthly incident volumes across the top-50 theaters using 12-month trailing moving statistics (Z_t = (x_t - μ_{t-12}) / σ_{t-12}). Surges are flagged when Z_t > 2.0."
    )

    add_heading_2(doc, "3.6 Behavioral Networks & Privacy-Preserving Gemini GenAI")
    add_body_p(
        doc,
        "Active factions (≥ 20 incidents) are clustered into tactical archetypes via KMeans and 2D PCA. NetworkX builds bipartite relational graphs across shared targets and regional operational footprints. "
        "The Gemini Executive Synthesis module transmits strictly numerical aggregates (totals, top groups, weapon counts) to gemini-2.5-flash with zero raw row transmission. "
        "The Pure Pandas Query Engine translates conversational natural language queries into rigid JSON specifications validated against column and operator whitelists, executing entirely through compiled Pandas routines (zero eval/exec)."
    )

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 4: EXPERIMENTATION & RESULTS
    # =========================================================================
    add_heading_1(doc, "CHAPTER 4: EXPERIMENTATION, IMPLEMENTATION & RESULT DISCUSSION")
    add_heading_2(doc, "4.1 Experimental Environment & Hardware Setup")
    add_body_p(
        doc,
        "Experiments were conducted in Python 3.11+ on x86_64 environments across Windows and Ubuntu Linux with 16 GB RAM. "
        "The production runtime is strictly optimized for Streamlit Community Cloud (< 450 MB RAM consumption)."
    )

    add_heading_2(doc, "4.2 Attack Modality Prediction Leaderboard & SHAP Attributions")
    add_body_p(
        doc,
        "Models were evaluated out-of-time on the held-out 2013–2017 test set (2,740 incidents) after training on ≤ 2012 data (12,260 incidents):"
    )

    # Leaderboard Table
    ml_data = [
        ("Baseline (Majority)", "47.23%", "0.1069", "0.3030", "60.73%", "Predicts Bombings indiscriminately; 0% recall on rare classes."),
        ("Logistic Regression", "22.92%", "0.1601", "0.2863", "61.13%", "High recall on minority classes; low overall precision."),
        ("Balanced Random Forest", "37.66%", "0.1691", "0.3957", "67.99%", "Strong non-linear boundary capture across sparse features."),
        ("LightGBM (Champion)", "32.81%", "0.1602", "0.3643", "69.31%", "Balanced gradient boosting; optimal Top-3 categorical ranking precision."),
    ]
    t_ml = doc.add_table(rows=len(ml_data) + 1, cols=6)
    t_ml.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_ml, color="CBD5E1", sz="4")
    col_w_ml = [Inches(1.5), Inches(0.8), Inches(0.8), Inches(0.8), Inches(0.8), Inches(1.8)]

    hdr_ml = t_ml.rows[0]
    hdr_ml.cells[0].paragraphs[0].text = "Model Architecture"
    hdr_ml.cells[1].paragraphs[0].text = "Accuracy"
    hdr_ml.cells[2].paragraphs[0].text = "Macro-F1"
    hdr_ml.cells[3].paragraphs[0].text = "Weighted-F1"
    hdr_ml.cells[4].paragraphs[0].text = "Top-3 Acc"
    hdr_ml.cells[5].paragraphs[0].text = "Operational Profile"
    format_table_header(hdr_ml, col_w_ml, bg_color="0F172A")

    for idx, (m_arch, m_acc, m_mf1, m_wf1, m_t3, m_op) in enumerate(ml_data):
        row = t_ml.rows[idx + 1]
        row.cells[0].paragraphs[0].text = m_arch
        row.cells[1].paragraphs[0].text = m_acc
        row.cells[2].paragraphs[0].text = m_mf1
        row.cells[3].paragraphs[0].text = m_wf1
        row.cells[4].paragraphs[0].text = m_t3
        row.cells[5].paragraphs[0].text = m_op

    format_table_cells(t_ml, col_w_ml)
    doc.add_paragraph()

    add_figure(
        doc,
        FIG_DIR / "fig4_1_model_comparison.png",
        "Figure 4.1: Out-of-Time Machine Learning Model Comparison Leaderboard & Probability Calibration Curves",
        width_in=6.0,
    )

    add_body_p(
        doc,
        "TreeSHAP global attributions prove that weaptype1_txt (Explosives vs. Firearms) and targtype1_txt (Utilities, Government, Private Citizens) "
        "govern over 65% of model split decisions. Local waterfall plots explain individual predictions in real time, exposing how regional indicators and target sector shift class probabilities.",
        bold_prefix="TreeSHAP Interpretability Findings: "
    )

    add_figure(
        doc,
        FIG_DIR / "fig4_2_shap_explainability.png",
        "Figure 4.2: Explainable AI — TreeSHAP Global Feature Importance & Local Decision Waterfall",
        width_in=6.0,
    )

    add_heading_2(doc, "4.3 Spatial DBSCAN Hotspots & Sovereign Threat Risk Index")
    add_body_p(
        doc,
        "Spherical Haversine DBSCAN accurately isolated 42 major global conflict epicenters (e.g. FATA region, Northern Iraq, Southwestern Colombia, Borno State corridor) without spherical map distortion. "
        "The Sovereign Risk Index incorporates log(incidents), log(casualties), 3-year momentum slope, and mass-casualty ratios. Sensitivity analysis via Kendall's Tau (τ = 0.91) demonstrates that sovereign rankings remain robust across subjective weight adjustments in the Scenario Simulator."
    )

    add_figure(
        doc,
        FIG_DIR / "fig4_3_spatial_hotspots.png",
        "Figure 4.3: Spherical Haversine DBSCAN Spatial Conflict Hotspots (R = 6,371.0088 km)",
        width_in=6.0,
    )

    add_heading_2(doc, "4.4 Longitudinal Forecasting & Surge Anomaly Evaluation")
    add_body_p(
        doc,
        "Holt-Winters ETS achieved a Global MAE of 238.4 incidents and MAPE of 14.2%, outperforming the Naive baseline (MAE = 312.0). "
        "Evaluated against forward 3-month surges (> 2.0x trailing mean), the 12-month Rolling Z-Score detector achieved an F1-score of 0.608 with an average lead time of 2.1 months, compared to static thresholds (F1 = 0.460, Lead Time = 0.8 months)."
    )

    add_figure(
        doc,
        FIG_DIR / "fig4_4_longitudinal_forecast.png",
        "Figure 4.4: Longitudinal Conflict Forecasting & 1993 Archival Gap Annotation (Holt-Winters ETS)",
        width_in=6.0,
    )

    add_figure(
        doc,
        FIG_DIR / "fig4_5_early_warning_surges.png",
        "Figure 4.5: Tactical Early-Warning Surge Detection (12-Month Rolling Z-Scores)",
        width_in=6.0,
    )

    add_heading_2(doc, "4.5 Case Study: FARC Insurgency in Colombia (1970–2017)")
    add_body_p(
        doc,
        "The 17-page Streamlit dashboard was validated on the Revolutionary Armed Forces of Colombia (FARC):"
    )
    add_bullet_p(doc, "Haversine DBSCAN isolated 3 distinct clusters: Southwestern Rural Axis, Central Llanos, and Arauca border.", bold_prefix="• Spatial Clusters: ")
    add_bullet_p(doc, "Detected structural shift from rural ambushes in the 1980s to infrastructure bombings in the late 1990s.", bold_prefix="• Tactical Shifts: ")
    add_bullet_p(doc, "For an Arauca utility target, LightGBM predicted Facility Attack (58.4%), explained by SHAP.", bold_prefix="• Predictive Inference: ")
    add_bullet_p(doc, "ETS models trained through 2012 accurately projected the de-escalation leading to the 2016 Havana Peace Accord.", bold_prefix="• Forecasting: ")
    add_bullet_p(doc, "Rolling Z-scores flagged major offensives in August 1998 (Z = 2.84σ) and February 2002.", bold_prefix="• Surge Alerts: ")

    add_figure(
        doc,
        FIG_DIR / "fig4_6_faction_profiling_network.png",
        "Figure 4.6: Militant Behavioral Profiling (2D PCA) & Relational Network Topology",
        width_in=6.0,
    )

    add_heading_2(doc, "4.6 Software Engineering Rigor & 87% Code Coverage Table")
    add_body_p(
        doc,
        "The test suite executes 75 automated unit tests with a 100% pass rate in under 50 seconds. Pytest-cov reports 87% overall coverage across all 15 source modules in src/:"
    )

    # Coverage Table
    cov_data = [
        ("src/config.py", "38", "100%", "src/network.py", "73", "92%"),
        ("src/anomaly.py", "95", "97%", "src/forecasting.py", "95", "91%"),
        ("src/features.py", "56", "96%", "src/data_quality.py", "122", "88%"),
        ("src/hotspots.py", "50", "96%", "src/data_loader.py", "202", "84%"),
        ("src/risk_index.py", "87", "95%", "src/groups.py", "107", "84%"),
        ("src/pdf_export.py", "113", "95%", "src/report.py", "126", "83%"),
        ("src/models.py", "62", "92%", "src/text_mining.py", "161", "83%"),
        ("TOTAL PROJECT", "1,580", "87%", "src/query_engine.py", "193", "76%"),
    ]
    t_cov = doc.add_table(rows=len(cov_data) + 1, cols=6)
    t_cov.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_cov, color="CBD5E1", sz="4")
    col_w_cov = [Inches(1.5), Inches(0.8), Inches(0.8), Inches(1.5), Inches(0.8), Inches(0.8)]

    hdr_cov = t_cov.rows[0]
    hdr_cov.cells[0].paragraphs[0].text = "Source Module"
    hdr_cov.cells[1].paragraphs[0].text = "Statements"
    hdr_cov.cells[2].paragraphs[0].text = "Coverage"
    hdr_cov.cells[3].paragraphs[0].text = "Source Module"
    hdr_cov.cells[4].paragraphs[0].text = "Statements"
    hdr_cov.cells[5].paragraphs[0].text = "Coverage"
    format_table_header(hdr_cov, col_w_cov, bg_color="1E3A8A")

    for idx, (m1, s1, c1, m2, s2, c2) in enumerate(cov_data):
        row = t_cov.rows[idx + 1]
        row.cells[0].paragraphs[0].text = m1
        row.cells[1].paragraphs[0].text = s1
        row.cells[2].paragraphs[0].text = c1
        row.cells[3].paragraphs[0].text = m2
        row.cells[4].paragraphs[0].text = s2
        row.cells[5].paragraphs[0].text = c2

    format_table_cells(t_cov, col_w_cov)
    doc.add_page_break()

    # =========================================================================
    # CHAPTER 5: CONCLUSIONS & BIBLIOGRAPHY
    # =========================================================================
    add_heading_1(doc, "CHAPTER 5: CONCLUSIONS & FUTURE SCOPE")
    add_heading_2(doc, "5.1 Conclusions & Educational Outcomes")
    add_body_p(
        doc,
        "This internship project successfully delivered an enterprise-grade military intelligence and threat analysis platform. "
        "By enforcing zero target data leakage, out-of-time chronological validation, great-circle spherical spatial clustering, "
        "calibrated time-series forecasting, and explainable AI attribution proofs, the system bridges the gap between academic conflict "
        "research and applied machine learning engineering. The project successfully fulfilled all mandates of the Def-Space Summer Internship Programme 2026 "
        "conducted by the Bharat Space Education Research Centre (BSERC) in association with the National Institute of Technology Delhi (NIT Delhi)."
    )

    add_heading_2(doc, "5.2 Future Scope & Technological Horizons")
    add_bullet_p(doc, "Integrating Synthetic Aperture Radar (SAR) and multispectral optical imagery (Sentinel-2, Planet) to correlate incident reports with physical infrastructure damage scars.", bold_prefix="• Multi-Modal Satellite Sensor Fusion: ")
    add_bullet_p(doc, "Expanding the NetworkX graph engine into dynamic temporal knowledge graphs capable of tracking faction alliance splits and mergers over time.", bold_prefix="• Dynamic Bipartite Knowledge Graphs: ")
    add_bullet_p(doc, "Compiling prediction and anomaly detection models to ONNX/TensorRT for low-power tactical field deployment.", bold_prefix="• Edge Optimization: ")

    doc.add_paragraph()
    add_heading_1(doc, "BIBLIOGRAPHY & REFERENCES")

    bib_entries = [
        "[1] START. (2018). Global Terrorism Database (1970–2017) Data Codebook. National Consortium for the Study of Terrorism and Responses to Terrorism, University of Maryland.",
        "[2] Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. In Advances in Neural Information Processing Systems (NeurIPS 30), pp. 4765–4774.",
        "[3] Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T. Y. (2017). LightGBM: A highly efficient gradient boosting decision tree. In Advances in Neural Information Processing Systems (NeurIPS 30), pp. 3146–3154.",
        "[4] Ester, M., Kriegel, H. P., Sander, J., & Xu, X. (1996). A density-based algorithm for discovering clusters in large spatial databases with noise. In Proc. 2nd Int. Conf. on Knowledge Discovery and Data Mining (KDD-96), pp. 226–231.",
        "[5] Hyndman, R. J., & Athanasopoulos, G. (2018). Forecasting: principles and practice (2nd ed.). OTexts: Melbourne, Australia.",
        "[6] Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). Isolation Forest. In Eighth IEEE International Conference on Data Mining (ICDM), pp. 413–422.",
        "[7] Hagberg, A., Swart, P., & S Chult, D. (2008). Exploring network structure, dynamics, and function using NetworkX. Los Alamos National Laboratory (LANL).",
        "[8] Honaker, J., & King, G. (2010). What to do about missing values in time-series cross-section data. American Journal of Political Science, 54(2), 561–581.",
        "[9] Clauset, A., Young, M., & Gleditsch, K. S. (2007). On the Frequency of Severe Terrorist Events. Journal of Conflict Resolution, 51(1), 58–87.",
        "[10] Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet Allocation. Journal of Machine Learning Research, 3, 993–1022.",
    ]
    for b in bib_entries:
        add_bullet_p(doc, b)

    # Enforce strict OpenXML schema conformance across all tables & cells
    enforce_table_schema_conformance(doc)

    # Save document
    doc.save(str(output_path))
    print(f"Successfully generated formatted Microsoft Word (.docx) report at: {output_path}")


if __name__ == "__main__":
    out_file = Path("docs/INTERNSHIP_PROJECT_REPORT.docx")
    build_word_report(out_file)
