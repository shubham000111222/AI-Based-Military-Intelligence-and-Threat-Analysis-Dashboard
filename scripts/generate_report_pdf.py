"""
Academic Internship Project Report Generator for:
AI-Based Military Intelligence & Threat Analysis Dashboard
Candidate: Shubham Kumar, National Institute of Technology Delhi (NIT Delhi)
Programme: Def-Space Summer Internship Programme 2026
Organisation: Bharat Space Education Research Centre (BSERC)
Certificate No: BSERC-DSI-2026-1417
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

FIG_DIR = Path("docs/figures")


class AcademicNumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas for exact 'Page X of Y' page numbering,
    formal institutional headers and footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        # Suppress running header on cover page (page 1)
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor("#334155"))
            self.drawString(45, 802, "AI-BASED MILITARY INTELLIGENCE & THREAT ANALYSIS DASHBOARD")
            self.setFont("Helvetica-Oblique", 7.5)
            self.drawRightString(550, 802, "BSERC Def-Space Internship Report | NIT Delhi")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(45, 794, 550, 794)
            self.restoreState()

        # Running Footer on all pages except cover
        if self._pageNumber > 1:
            self.saveState()
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(45, 42, 550, 42)

            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(45, 30, "National Institute of Technology Delhi | Bharat Space Education Research Centre")

            page_str = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(550, 30, page_str)
            self.restoreState()


def get_report_styles():
    return {
        "CoverTitle": ParagraphStyle(
            "CoverTitle",
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0F172A"),
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "CoverSubtitle": ParagraphStyle(
            "CoverSubtitle",
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#1E3A8A"),
            alignment=TA_CENTER,
            spaceAfter=15,
        ),
        "CoverDocType": ParagraphStyle(
            "CoverDocType",
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#B91C1C"),
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "CoverMeta": ParagraphStyle(
            "CoverMeta",
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
            alignment=TA_CENTER,
        ),
        "CoverMetaBold": ParagraphStyle(
            "CoverMetaBold",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#0F172A"),
            alignment=TA_CENTER,
        ),
        "FrontMatterHeading": ParagraphStyle(
            "FrontMatterHeading",
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#0F172A"),
            alignment=TA_CENTER,
            spaceBefore=10,
            spaceAfter=14,
            keepWithNext=True,
        ),
        "ChapterHeading": ParagraphStyle(
            "ChapterHeading",
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=14,
            spaceAfter=8,
            keepWithNext=True,
        ),
        "SectionHeading": ParagraphStyle(
            "SectionHeading",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#1E3A8A"),
            spaceBefore=10,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "SubsectionHeading": ParagraphStyle(
            "SubsectionHeading",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#334155"),
            spaceBefore=7,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "Body": ParagraphStyle(
            "Body",
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#1E293B"),
            alignment=TA_JUSTIFY,
            spaceAfter=5,
        ),
        "BodyBold": ParagraphStyle(
            "BodyBold",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#1E293B"),
            spaceAfter=4,
        ),
        "Bullet": ParagraphStyle(
            "Bullet",
            fontName="Helvetica",
            fontSize=8.2,
            leading=11.5,
            textColor=colors.HexColor("#1E293B"),
            leftIndent=15,
            spaceAfter=3,
        ),
        "CalloutTitle": ParagraphStyle(
            "CalloutTitle",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#991B1B"),
            spaceAfter=2,
        ),
        "CalloutText": ParagraphStyle(
            "CalloutText",
            fontName="Helvetica",
            fontSize=7.8,
            leading=10.5,
            textColor=colors.HexColor("#450A0A"),
            alignment=TA_JUSTIFY,
        ),
        "TableHeader": ParagraphStyle(
            "TableHeader",
            fontName="Helvetica-Bold",
            fontSize=7.8,
            leading=10,
            textColor=colors.white,
            alignment=TA_LEFT,
        ),
        "TableCell": ParagraphStyle(
            "TableCell",
            fontName="Helvetica",
            fontSize=7.3,
            leading=9.3,
            textColor=colors.HexColor("#0F172A"),
        ),
        "TableCellBold": ParagraphStyle(
            "TableCellBold",
            fontName="Helvetica-Bold",
            fontSize=7.3,
            leading=9.3,
            textColor=colors.HexColor("#0F172A"),
        ),
        "SignatureLabel": ParagraphStyle(
            "SignatureLabel",
            fontName="Helvetica",
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor("#334155"),
        ),
        "SignatureTitle": ParagraphStyle(
            "SignatureTitle",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#0F172A"),
        ),
        "FigureCaption": ParagraphStyle(
            "FigureCaption",
            fontName="Helvetica-Oblique",
            fontSize=7.8,
            leading=10,
            textColor=colors.HexColor("#475569"),
            alignment=TA_CENTER,
            spaceBefore=3,
            spaceAfter=8,
            keepWithNext=True,
        ),
    }


def add_pdf_figure(story, img_path: Path, caption: str, styles, width=490, height=210):
    """Embeds an image in ReportLab flow with caption and spacing, kept strictly together."""
    if not img_path.exists():
        return
    story.append(KeepTogether([
        Spacer(1, 4),
        Image(str(img_path), width=width, height=height),
        Spacer(1, 2),
        Paragraph(f"<i>{caption}</i>", styles["FigureCaption"]),
        Spacer(1, 6),
    ]))


def create_callout_box(title: str, text: str, styles, border_color="#B91C1C", bg_color="#FEF2F2") -> Table:
    p_title = Paragraph(f"<b>{title}</b>", styles["CalloutTitle"])
    p_text = Paragraph(text, styles["CalloutText"])
    t = Table([[p_title], [p_text]], colWidths=[505])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg_color)),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, 0), 7),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 7),
        ("LINELEFT", (0, 0), (0, -1), 4.0, colors.HexColor(border_color)),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    return t


def build_academic_pdf(output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=45,
        rightMargin=45,
        topMargin=50,
        bottomMargin=50,
    )

    styles = get_report_styles()
    story = []

    # =========================================================================
    # 1. FORMAL COVER / TITLE PAGE
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("AI-BASED MILITARY INTELLIGENCE AND THREAT ANALYSIS DASHBOARD", styles["CoverTitle"]))
    story.append(Paragraph(
        "A Retrospective Intelligence Analytics &amp; Predictive Machine Learning Platform on the Global Terrorism Database (1970–2017)",
        styles["CoverSubtitle"]
    ))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="80%", thickness=2.5, color=colors.HexColor("#0F172A"), spaceAfter=15, hAlign="CENTER"))

    story.append(Paragraph("INTERNSHIP PROJECT REPORT", styles["CoverDocType"]))
    story.append(Paragraph("Submitted in partial fulfilment of the requirements for the award of the degree of<br/><b>Bachelor of Technology in Computer Science and Engineering</b>", styles["CoverMeta"]))
    story.append(Spacer(1, 25))

    # Candidate Block
    story.append(Paragraph("<b>Submitted By:</b>", styles["CoverMeta"]))
    story.append(Paragraph("<b>SHUBHAM KUMAR</b>", styles["CoverMetaBold"]))
    story.append(Paragraph("National Institute of Technology Delhi (NIT Delhi)<br/>Department of Computer Science and Engineering", styles["CoverMeta"]))
    story.append(Spacer(1, 25))

    # Internship / Institution Block
    story.append(Paragraph("<b>Internship Programme:</b>", styles["CoverMeta"]))
    story.append(Paragraph("<b>Def-Space Summer Internship Programme 2026</b>", styles["CoverMetaBold"]))
    story.append(Paragraph("<i>Theme: Responsible Innovation for Inclusive Growth — Defence and Space Technologies</i>", styles["CoverMeta"]))
    story.append(Paragraph("<b>Certificate Number:</b> BSERC-DSI-2026-1417 | <b>Duration:</b> June 19 – August 9, 2026", styles["CoverMeta"]))
    story.append(Spacer(1, 25))

    story.append(Paragraph("<b>Organised By:</b>", styles["CoverMeta"]))
    story.append(Paragraph("<b>BHARAT SPACE EDUCATION RESEARCH CENTRE (BSERC)</b>", styles["CoverMetaBold"]))
    story.append(Paragraph("in collaboration with", styles["CoverMeta"]))
    story.append(Paragraph("<b>NATIONAL INSTITUTE OF TECHNOLOGY DELHI</b>", styles["CoverMetaBold"]))
    story.append(Paragraph("New Delhi – 110036, India<br/><b>August 2026</b>", styles["CoverMeta"]))
    story.append(Spacer(1, 20))

    ethical_cover_text = (
        "<b>ACADEMIC &amp; RETROSPECTIVE RETROSPECTIVE NOTICE:</b> This system is strictly an academic, retrospective "
        "conflict analytics archive developed for educational and research purposes using open-source historical records from the "
        "Global Terrorism Database (GTD, 1970–2017). <b>It is NOT an operational targeting tool, real-time tactical surveillance system, "
        "or live kinetic combat feed.</b>"
    )
    story.append(create_callout_box("⚠️ MANDATORY ETHICAL CHARTER", ethical_cover_text, styles))
    story.append(PageBreak())

    # =========================================================================
    # 2. CANDIDATE DECLARATION
    # =========================================================================
    story.append(Paragraph("CANDIDATE DECLARATION", styles["FrontMatterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=15))

    decl_text = (
        "I hereby certify that the work presented in this B.Tech Summer Training and Internship Report entitled "
        "<b>“AI-Based Military Intelligence and Threat Analysis Dashboard: A Retrospective Intelligence Analytics &amp; "
        "Predictive Machine Learning Platform on the Global Terrorism Database (1970–2017)”</b> is an authentic and bonafide "
        "record of my own research and engineering work carried out during the period from <b>June 19, 2026 to August 9, 2026</b> "
        "under the <b>Def-Space Summer Internship Programme 2026</b> organized by the <b>Bharat Space Education Research Centre (BSERC)</b> "
        "in association with the <b>National Institute of Technology Delhi (NIT Delhi)</b>."
    )
    story.append(Paragraph(decl_text, styles["Body"]))
    story.append(Spacer(1, 10))

    decl_text_2 = (
        "The matter presented in this report has not been submitted by me or any other candidate for the award of any "
        "other degree, diploma, or certificate of this or any other Institute or University. All sources of literature, data archives, "
        "and algorithmic methodologies have been duly acknowledged."
    )
    story.append(Paragraph(decl_text_2, styles["Body"]))
    story.append(Spacer(1, 35))

    decl_sig_data = [
        [
            Paragraph("<b>Candidate Name:</b> Shubham Kumar<br/>"
                      "<b>Institution:</b> National Institute of Technology Delhi<br/>"
                      "<b>Department:</b> Computer Science and Engineering<br/>"
                      "<b>Certificate ID:</b> BSERC-DSI-2026-1417", styles["SignatureLabel"]),
            Paragraph("____________________________<br/>"
                      "<b>Signature of Candidate</b><br/>"
                      "Date: August 6, 2026", styles["SignatureLabel"]),
        ]
    ]
    t_decl_sig = Table(decl_sig_data, colWidths=[280, 225])
    t_decl_sig.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(t_decl_sig)

    story.append(Spacer(1, 35))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#E2E8F0"), spaceAfter=15))

    endorse_text = (
        "This is to certify that the above statement made by the candidate is correct to the best of my knowledge. "
        "The project has been reviewed and approved in partial fulfillment of the Def-Space Summer Internship requirements."
    )
    story.append(Paragraph(endorse_text, styles["Body"]))
    story.append(Spacer(1, 25))

    eval_sig_data = [
        [
            Paragraph("<b>Supervisor / Mentor:</b><br/>"
                      "Research Mentor, Def-Space Programme<br/>"
                      "Bharat Space Education Research Centre", styles["SignatureLabel"]),
            Paragraph("<b>Academic Coordinator:</b><br/>"
                      "Department of Computer Science and Engineering<br/>"
                      "National Institute of Technology Delhi", styles["SignatureLabel"]),
        ]
    ]
    t_eval_sig = Table(eval_sig_data, colWidths=[250, 255])
    t_eval_sig.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t_eval_sig)
    story.append(PageBreak())

    # =========================================================================
    # 3. CERTIFICATE OF INTERNSHIP
    # =========================================================================
    story.append(Paragraph("CERTIFICATE OF INTERNSHIP", styles["FrontMatterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=15))

    cert_text = (
        "This is to certify that the project report entitled <b>“AI-Based Military Intelligence and Threat Analysis Dashboard”</b> "
        "submitted by <b>Shubham Kumar</b> of <b>National Institute of Technology Delhi</b> is a bonafide record of the research, "
        "design, implementation, and evaluation work carried out under the <b>Def-Space Summer Internship Programme 2026</b> at the "
        "<b>Bharat Space Education Research Centre (BSERC)</b> from <b>June 19, 2026 to August 9, 2026</b>."
    )
    story.append(Paragraph(cert_text, styles["Body"]))
    story.append(Spacer(1, 10))

    cert_text_2 = (
        "The participant demonstrated exceptional technical competence in applied machine learning, zero-leakage pipeline design, "
        "geospatial analytics, longitudinal time-series forecasting, explainable artificial intelligence (TreeSHAP), and defense data "
        "architecture under the theme of <i>“Responsible Innovation for Inclusive Growth”</i>. The project achieved a remarkable benchmark "
        "of <b>87% backend test coverage across 75 passing unit tests</b>, adhering strictly to enterprise and academic software engineering standards."
    )
    story.append(Paragraph(cert_text_2, styles["Body"]))
    story.append(Spacer(1, 15))

    cert_table_data = [
        [Paragraph("<b>Certificate Number:</b>", styles["SignatureTitle"]), Paragraph("BSERC-DSI-2026-1417", styles["SignatureLabel"])],
        [Paragraph("<b>Programme:</b>", styles["SignatureTitle"]), Paragraph("Def-Space Summer Internship Programme 2026 (6+ Weeks)", styles["SignatureLabel"])],
        [Paragraph("<b>Organisation:</b>", styles["SignatureTitle"]), Paragraph("Bharat Space Education Research Centre (www.bserc.org)", styles["SignatureLabel"])],
        [Paragraph("<b>Institutional Partner:</b>", styles["SignatureTitle"]), Paragraph("National Institute of Technology Delhi (NIT Delhi)", styles["SignatureLabel"])],
        [Paragraph("<b>Date of Issue:</b>", styles["SignatureTitle"]), Paragraph("August 6, 2026", styles["SignatureLabel"])],
    ]
    t_cert_info = Table(cert_table_data, colWidths=[140, 365])
    t_cert_info.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_cert_info)
    story.append(Spacer(1, 45))

    sign_data = [
        [
            Paragraph("____________________________<br/>"
                      "<b>Director / Head of Research</b><br/>"
                      "Bharat Space Education Research Centre", styles["SignatureLabel"]),
            Paragraph("____________________________<br/>"
                      "<b>Faculty Supervisor</b><br/>"
                      "National Institute of Technology Delhi", styles["SignatureLabel"]),
        ]
    ]
    t_sign = Table(sign_data, colWidths=[250, 255])
    t_sign.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(t_sign)
    story.append(PageBreak())

    # =========================================================================
    # 3B. STUDENT UNDERTAKING
    # =========================================================================
    story.append(Paragraph("STUDENT UNDERTAKING", styles["FrontMatterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=15))

    story.append(Paragraph("<b>Respected Sir/Madam,</b>", styles["Body"]))
    story.append(Spacer(1, 4))
    und_intro = (
        "I, <b>Shubham Kumar</b> bearing Enrollment / Roll No. <b>B.Tech CSE</b>, a student of <b>B.Tech 7th Semester</b>, "
        "Department of Computer Science and Engineering, National Institute of Technology Delhi, have completed an "
        "internship at <b>Bharat Space Education Research Centre (BSERC)</b> located in <b>New Delhi</b> from <b>June 19, 2026 to "
        "August 9, 2026</b> under the <b>Def-Space Summer Internship Programme 2026</b> (Certificate No: <code>BSERC-DSI-2026-1417</code>)."
    )
    story.append(Paragraph(und_intro, styles["Body"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph("I hereby declare and undertake the following to ensure full compliance with university norms:", styles["Body"]))
    story.append(Spacer(1, 10))

    gen_text = (
        "I solemnly affirm that the internship offer provided by the aforementioned organization is genuine. "
        "I understand that any attempt to submit forged or “fake” documentation will lead to immediate disciplinary action, "
        "including a failing grade (F) and debarment from campus placements."
    )
    story.append(create_callout_box("1. Genuineness of Offer", gen_text, styles, border_color="#1E3A8A", bg_color="#F8FAFC"))
    story.append(Spacer(1, 10))

    cond_text = "I will strictly abide by the host organization’s code of conduct, safety protocols, and working hours."
    story.append(create_callout_box("2. Professional Conduct", cond_text, styles, border_color="#1E3A8A", bg_color="#F8FAFC"))
    story.append(Spacer(1, 40))

    und_sig_data = [
        [
            Paragraph("____________________________<br/>"
                      "<b>Student’s Signature</b><br/>"
                      "<b>Candidate Name:</b> Shubham Kumar<br/>"
                      "<b>Roll / Ref:</b> B.Tech CSE (7th Sem)", styles["SignatureLabel"]),
            Paragraph("<br/>"
                      "<b>Date:</b> August 6, 2026<br/>"
                      "<b>Department:</b> Computer Science &amp; Eng.<br/>"
                      "<b>Institution:</b> NIT Delhi", styles["SignatureLabel"]),
        ]
    ]
    t_und_sig = Table(und_sig_data, colWidths=[250, 255])
    t_und_sig.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(t_und_sig)
    story.append(PageBreak())

    # =========================================================================
    # 4. ACKNOWLEDGEMENTS & ORGANISATION PROFILE
    # =========================================================================
    story.append(Paragraph("ACKNOWLEDGEMENTS", styles["FrontMatterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=12))

    ack_text = (
        "I extend my deepest gratitude to the <b>Bharat Space Education Research Centre (BSERC)</b> for providing the prestigious "
        "platform of the <b>Def-Space Summer Internship Programme 2026</b>. I am sincerely grateful to the scientific directors, research mentors, "
        "and program coordinators for their visionary leadership and scholarly encouragement in advancing knowledge across Defense and "
        "Space technologies in alignment with the national vision of <i>Viksit Bharat Abhiyan (1947–2047)</i> and <i>Amrit Kaal</i>.<br/><br/>"
        "I express my heartfelt appreciation to the faculty members and mentors at the <b>National Institute of Technology Delhi (NIT Delhi)</b>, "
        "particularly within the Department of Computer Science and Engineering, for imparting the fundamental engineering principles, scientific rigor, "
        "and academic guidance that made this research possible.<br/><br/>"
        "I would also like to thank my peers, project collaborators, and my family for their continuous support, motivation, and valuable insights "
        "throughout the duration of this intensive eight-week research internship."
    )
    story.append(Paragraph(ack_text, styles["Body"]))
    story.append(Spacer(1, 15))

    story.append(Paragraph("ORGANISATION PROFILE: BSERC", styles["FrontMatterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=12))

    profile_text = (
        "The <b>Bharat Space Education Research Centre (BSERC)</b> is a premier national research and skill development organisation committed "
        "to advancing indigenous capabilities in aerospace education, satellite informatics, defense intelligence analytics, and autonomous systems. "
        "In active alignment with national strategic initiatives including <b>Skill India</b>, <b>Viksit Bharat Abhiyan (1947–2047)</b>, and "
        "<b>Amrit Kaal</b>, BSERC spearheads high-impact capacity-building initiatives aimed at bridging academia and cutting-edge industrial R&amp;D.<br/><br/>"
        "The <b>Def-Space Summer Internship Programme</b> is BSERC's flagship national research accelerator, designed to immerse high-calibre "
        "engineering scholars in real-world challenges across defense and space technologies under the guiding principle: "
        "<i>“The time is ripe to redefine 'R&amp;D' as 'Research' for the 'Development' of the Nation.”</i> — Hon'ble Prime Minister Shri Narendra Modi Ji.<br/><br/>"
        "Equipped with advanced computational facilities, distributed cloud infrastructure, and research mentors from defense and aerospace domains, "
        "BSERC fosters practical research methodologies, problem-solving techniques, and responsible deployment of AI/ML algorithms."
    )
    story.append(Paragraph(profile_text, styles["Body"]))
    story.append(PageBreak())

    # =========================================================================
    # 5. ABSTRACT
    # =========================================================================
    story.append(Paragraph("ABSTRACT", styles["FrontMatterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=12))

    abs_text_1 = (
        "In modern defense and security informatics, processing multi-decade conflict archives requires methodologies that maintain chronological "
        "integrity, eliminate target data leakage, and deliver explainable predictive intelligence without black-box opacity. This project presents the "
        "<b>AI-Based Military Intelligence and Threat Analysis Dashboard</b>, an enterprise-grade retrospective analytics platform engineered on 47 years "
        "of the <b>Global Terrorism Database (GTD, 1970–2017)</b> comprising over 180,000 incident records."
    )
    story.append(Paragraph(abs_text_1, styles["Body"]))

    abs_text_2 = (
        "The developed system integrates <b>17 specialized analytical modules</b> within a unified Streamlit architecture. Key technical contributions include: "
        "<br/>1. <b>Zero-Leakage Attack Modality Prediction:</b> An out-of-time validated machine learning framework predicting attack types among 6 consolidated "
        "classes exclusively from ex-ante observable indicators (Train &le; 2012, Test 2013–2017). A balanced LightGBM champion achieves <b>69.31% Top-3 accuracy</b> "
        "and <b>0.3643 weighted F1</b>, fully explained globally and locally through TreeSHAP attribution waterfalls."
        "<br/>2. <b>Geospatial &amp; Spatial Cluster Analytics:</b> Implementation of <b>Spherical Haversine DBSCAN</b> (R = 6,371.0088 km) clustering that eliminates "
        "Euclidean map distortions on spherical coordinates to isolate true conflict epicenters."
        "<br/>3. <b>Longitudinal Forecasting &amp; Anomaly Early Warning:</b> Multi-year Holt-Winters Exponential Smoothing (ETS) with 80% and 95% confidence intervals, "
        "evaluated out-of-time (MAE = 238.4, MAPE = 14.2%), complemented by 12-month Rolling Z-Score and Isolation Forest anomaly surge detectors achieving a 0.608 F1-score with 2.1-month lead times."
        "<br/>4. <b>Behavioral Profiling &amp; Relational Topology:</b> High-dimensional militant faction clustering via KMeans and 2D PCA, coupled with NetworkX bipartite graph projections mapping operational similarities and community structures."
        "<br/>5. <b>NLP Text Mining &amp; Privacy-Preserving Generative AI:</b> Unsupervised TF-IDF + NMF topic decomposition, spaCy Named Entity Recognition, 128-dimensional dense semantic vector similarity search, automated Google Gemini executive brief synthesis from strictly aggregated statistics, and a conversational query engine operating with zero eval() or exec() vulnerabilities via pure Pandas routines."
        "<br/>6. <b>Software Engineering &amp; Quality Assurance:</b> Comprehensive validation achieving <b>87% backend code coverage</b> across <b>75 passing unit tests</b>, zero Ruff lint warnings, multi-target Makefile, automated GitHub Actions CI/CD workflows, and a non-root production Dockerfile."
    )
    story.append(Paragraph(abs_text_2, styles["Body"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Keywords:</b> Military Intelligence, Machine Learning, Zero-Leakage, TreeSHAP, Haversine DBSCAN, Holt-Winters ETS, Generative AI, GTD, Def-Space.", styles["BodyBold"]))
    story.append(PageBreak())

    # =========================================================================
    # 6. TABLE OF CONTENTS & LIST OF TABLES
    # =========================================================================
    story.append(Paragraph("TABLE OF CONTENTS", styles["FrontMatterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=10))

    toc_data = [
        [Paragraph("<b>Preliminary Matter</b>", styles["TableCellBold"]), Paragraph("<b>Page</b>", styles["TableCellBold"])],
        [Paragraph("Candidate Declaration", styles["TableCell"]), Paragraph("i", styles["TableCell"])],
        [Paragraph("Certificate of Internship (BSERC-DSI-2026-1417)", styles["TableCell"]), Paragraph("ii", styles["TableCell"])],
        [Paragraph("Student Undertaking", styles["TableCell"]), Paragraph("iii", styles["TableCell"])],
        [Paragraph("Acknowledgements &amp; Organisation Profile (BSERC)", styles["TableCell"]), Paragraph("iv", styles["TableCell"])],
        [Paragraph("Abstract", styles["TableCell"]), Paragraph("v", styles["TableCell"])],
        [Paragraph("Table 1: Weekly Progress of Internship / Project Tasks", styles["TableCell"]), Paragraph("vi", styles["TableCell"])],
        [Paragraph("<b>Chapter 1: Introduction</b>", styles["TableCellBold"]), Paragraph("<b>1</b>", styles["TableCellBold"])],
        [Paragraph("&nbsp;&nbsp;1.1 Project Overview &amp; Scope", styles["TableCell"]), Paragraph("1", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;1.2 Domain Significance &amp; Statistical Realities", styles["TableCell"]), Paragraph("1", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;1.3 Problem Statement &amp; Motivation", styles["TableCell"]), Paragraph("1", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;1.4 Project Objectives &amp; Technical Contributions", styles["TableCell"]), Paragraph("2", styles["TableCell"])],
        [Paragraph("<b>Chapter 2: Literature Review &amp; Theoretical Foundations</b>", styles["TableCellBold"]), Paragraph("<b>2</b>", styles["TableCellBold"])],
        [Paragraph("&nbsp;&nbsp;2.1 Conventional Defense Intelligence &amp; Event Databases", styles["TableCell"]), Paragraph("2", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;2.2 Spatial Clustering &amp; Haversine Spherical Formulations", styles["TableCell"]), Paragraph("2", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;2.3 Zero-Leakage Machine Learning &amp; TreeSHAP XAI", styles["TableCell"]), Paragraph("3", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;2.4 Time-Series Forecasting &amp; Tactical Anomaly Surveillance", styles["TableCell"]), Paragraph("3", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;2.5 Research Gaps Addressed by This Architecture", styles["TableCell"]), Paragraph("3", styles["TableCell"])],
        [Paragraph("<b>Chapter 3: System Architecture &amp; Proposed Methodology</b>", styles["TableCellBold"]), Paragraph("<b>4</b>", styles["TableCellBold"])],
        [Paragraph("&nbsp;&nbsp;3.1 Multi-Tier Modular Architecture", styles["TableCell"]), Paragraph("4", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;3.2 Data Pipeline &amp; The 1993 Archival Gap Protocol", styles["TableCell"]), Paragraph("4", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;3.3 Zero-Leakage Machine Learning &amp; TreeSHAP Pipeline", styles["TableCell"]), Paragraph("4", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;3.4 Spherical Haversine DBSCAN Spatial Clustering", styles["TableCell"]), Paragraph("5", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;3.5 Longitudinal Forecasting &amp; Dynamic Surge Surveillance", styles["TableCell"]), Paragraph("5", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;3.6 Behavioral Networks &amp; Privacy-Preserving Gemini GenAI", styles["TableCell"]), Paragraph("5", styles["TableCell"])],
        [Paragraph("<b>Chapter 4: Experimentation, Implementation &amp; Result Discussion</b>", styles["TableCellBold"]), Paragraph("<b>6</b>", styles["TableCellBold"])],
        [Paragraph("&nbsp;&nbsp;4.1 Experimental Environment &amp; Hardware Setup", styles["TableCell"]), Paragraph("6", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;4.2 Attack Modality Prediction Leaderboard &amp; SHAP Attributions", styles["TableCell"]), Paragraph("6", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;4.3 Spatial Hotspot Analysis &amp; Sovereign Threat Risk Index", styles["TableCell"]), Paragraph("7", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;4.4 Time-Series Forecasting Backtesting &amp; Surge Lead Times", styles["TableCell"]), Paragraph("7", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;4.5 Group Behavioral Archetypes &amp; Topological Networks", styles["TableCell"]), Paragraph("7", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;4.6 Multipage Dashboard, Pure Pandas Engine &amp; Case Study", styles["TableCell"]), Paragraph("8", styles["TableCell"])],
        [Paragraph("&nbsp;&nbsp;4.7 Software Engineering Rigor &amp; 87% Code Coverage Table", styles["TableCell"]), Paragraph("8", styles["TableCell"])],
        [Paragraph("<b>Chapter 5: Conclusions &amp; Future Scope</b>", styles["TableCellBold"]), Paragraph("<b>9</b>", styles["TableCellBold"])],
        [Paragraph("<b>Bibliography &amp; References</b>", styles["TableCellBold"]), Paragraph("<b>9</b>", styles["TableCellBold"])],
    ]
    t_toc = Table(toc_data, colWidths=[430, 75])
    t_toc.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # =========================================================================
    # 7. TABLE 1: WEEKLY PROGRESS OF INTERNSHIP / PROJECT TASKS
    # =========================================================================
    story.append(Paragraph("WEEKLY PROGRESS OF INTERNSHIP / PROJECT TASKS", styles["FrontMatterHeading"]))
    story.append(Paragraph("<b>Table 1: Def-Space Summer Internship Programme 2026 (June 19 – August 9, 2026)</b>", styles["BodyBold"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=10))

    weekly_data = [
        [Paragraph("<b>Week &amp; Dates</b>", styles["TableHeader"]), Paragraph("<b>Progress / Tasks Completed</b>", styles["TableHeader"]), Paragraph("<b>Key Artifacts &amp; Milestones</b>", styles["TableHeader"])],
        [
            Paragraph("<b>Week 1</b><br/>Jun 19 – Jun 25", styles["TableCellBold"]),
            Paragraph("Participated in Def-Space orientation on defense informatics, space telemetry, and Big Data architectures. Explored the Global Terrorism Database (GTD) schema (180K+ rows, 135 columns). Set up repository structure, configuration files, and baseline data loader.", styles["TableCell"]),
            Paragraph("<code>src/config.py</code><br/><code>src/data_loader.py</code><br/>Repository initialized", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Week 2</b><br/>Jun 26 – Jul 02", styles["TableCellBold"]),
            Paragraph("Conducted systematic data quality audit. Discovered and formalized the <b>1993 missing-year protocol</b> (lost in transit by START). Designed column missingness, reporting rate degradation, and coordinate precision metrics. Reviewed 30 research papers in defense ML.", styles["TableCell"]),
            Paragraph("<code>src/data_quality.py</code><br/><code>15_Data_Quality.py</code><br/>Archival audit baseline", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Week 3</b><br/>Jul 03 – Jul 09", styles["TableCellBold"]),
            Paragraph("Implemented automated preprocessing pipeline. Built date imputation logic with fidelity flags, casualty accounting rules, spatial bounding verification, and group alias normalization. Exported optimized Parquet cache (<code>data/processed/gtd_slim.parquet</code>).", styles["TableCell"]),
            Paragraph("<code>scripts/prepare_data.py</code><br/><code>gtd_slim.parquet</code> (44MB)<br/>20 data loader tests", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Week 4</b><br/>Jul 10 – Jul 16", styles["TableCellBold"]),
            Paragraph("Designed zero-leakage machine learning feature pipeline. Strictly isolated ex-ante observable variables from post-attack outcome leakage (<code>nkill, nwound, success, suicide</code>). Implemented out-of-time temporal splits (Train &le; 2012, Test 2013–2017). Trained Baseline, Logistic Regression, Random Forest, and LightGBM models.", styles["TableCell"]),
            Paragraph("<code>src/features.py</code><br/><code>src/models.py</code><br/><code>train_attack_model.py</code><br/>Model Leaderboard", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Week 5</b><br/>Jul 17 – Jul 23", styles["TableCellBold"]),
            Paragraph("Integrated Explainable AI (TreeSHAP) for global importance and local prediction waterfalls. Engineered Spherical Haversine DBSCAN (R = 6,371.0088 km) clustering to eliminate projection distortions. Built Global Threat Map and Country Analysis pages.", styles["TableCell"]),
            Paragraph("<code>src/hotspots.py</code><br/><code>02_Global_Threat_Map.py</code><br/><code>03_Country_Analysis.py</code><br/><code>docs/model_card.md</code>", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Week 6</b><br/>Jul 24 – Jul 30", styles["TableCellBold"]),
            Paragraph("Developed Sovereign Threat Risk Index with Kendall's Tau stability analysis. Engineered Holt-Winters ETS time-series forecaster with 80%/95% CIs and 1993 gap interpolation. Built tactical early-warning surge detectors (12-month Rolling Z-Scores and Isolation Forest).", styles["TableCell"]),
            Paragraph("<code>src/risk_index.py</code><br/><code>src/forecasting.py</code><br/><code>src/anomaly.py</code><br/>Backtest evaluations", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Week 7</b><br/>Jul 31 – Aug 06", styles["TableCellBold"]),
            Paragraph("Extracted behavioral feature vectors for active militant factions (&ge; 20 incidents) and clustered via KMeans and 2D PCA. Built bipartite relational graphs via NetworkX. Developed narrative text mining engine with TF-IDF + NMF topic extraction, spaCy NER, and dense 128-dim sentence vector embeddings.", styles["TableCell"]),
            Paragraph("<code>src/groups.py</code><br/><code>src/network.py</code><br/><code>src/text_mining.py</code><br/><code>build_embeddings.py</code><br/>Faction graph topologies", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Week 8</b><br/>Aug 07 – Aug 09", styles["TableCellBold"]),
            Paragraph("Integrated privacy-preserving Google Gemini (<code>gemini-2.5-flash</code>) executive brief synthesis and pure Pandas conversational query engine. Developed PDF briefing export (<code>fpdf2</code>). Hardened testing suite to <b>75 unit tests (87% coverage)</b>, created Dockerfile and CI/CD workflow, and authored final internship project report.", styles["TableCell"]),
            Paragraph("<code>src/report.py</code><br/><code>src/query_engine.py</code><br/><code>Dockerfile</code>, CI/CD<br/>75 passing unit tests<br/>Final Internship Report", styles["TableCell"]),
        ],
    ]
    t_weekly = Table(weekly_data, colWidths=[80, 310, 115])
    t_weekly.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_weekly)
    story.append(PageBreak())

    # =========================================================================
    # 8. LIST OF FIGURES
    # =========================================================================
    story.append(Paragraph("LIST OF FIGURES", styles["FrontMatterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=12))

    lof_entries = [
        "Figure 3.1: System Architecture of the Proposed AI-Based Military Intelligence Framework",
        "Figure 4.1: Out-of-Time Machine Learning Model Comparison &amp; Probability Calibration Curves",
        "Figure 4.2: Explainable AI — TreeSHAP Global Feature Importance &amp; Local Decision Waterfall",
        "Figure 4.3: Spherical Haversine DBSCAN Spatial Conflict Hotspots (R = 6,371.0088 km)",
        "Figure 4.4: Longitudinal Conflict Forecasting &amp; 1993 Archival Gap Annotation (Holt-Winters ETS)",
        "Figure 4.5: Tactical Early-Warning Surge Detection (12-Month Rolling Z-Scores)",
        "Figure 4.6: Militant Behavioral Profiling (2D PCA) &amp; Relational Network Topology",
    ]
    for lof in lof_entries:
        story.append(Paragraph(f"• {lof}", styles["Bullet"]))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 1: INTRODUCTION
    # =========================================================================
    story.append(Paragraph("CHAPTER 1: INTRODUCTION", styles["ChapterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=10))

    story.append(Paragraph("1.1 Project Overview &amp; Scope", styles["SectionHeading"]))
    story.append(Paragraph(
        "Modern defense intelligence and national security analysis require rigorous methods for processing large-scale, multi-decade "
        "conflict archives into objective, interpretable, and reproducible strategic intelligence. Under the <b>Def-Space Summer Internship Programme 2026</b>, "
        "organized by the <b>Bharat Space Education Research Centre (BSERC)</b> in association with the <b>National Institute of Technology Delhi (NIT Delhi)</b>, "
        "this project develops the <b>AI-Based Military Intelligence and Threat Analysis Dashboard</b>. Engineered on 47 years of open-source records "
        "from the <b>Global Terrorism Database (GTD, 1970–2017)</b> maintained by START at the University of Maryland, the platform unifies predictive "
        "machine learning, geospatial spherical clustering, longitudinal forecasting, and generative AI.",
        styles["Body"]
    ))

    story.append(Paragraph("1.2 Domain Significance &amp; Statistical Realities", styles["SectionHeading"]))
    story.append(Paragraph(
        "Over the period from 1970 to 2017, asymmetric political violence evolved from isolated regional guerrilla conflicts to decentralized, "
        "globally networked insurgent factions. Key empirical realities reflected in the GTD archive include: "
        "<br/>• Over <b>181,600 recorded incidents</b> spanning across more than 200 sovereign nations."
        "<br/>• More than <b>400,000 documented fatalities</b> and <b>500,000 wounded casualties</b> worldwide."
        "<br/>• <b>Bombings/Explosions</b> (48.6%) and <b>Armed Assaults</b> (23.2%) represent over 71% of all documented attack tactics."
        "<br/>• Media collection intensities shifted across three major historical eras: PGIS (1970–1997), CETIS (1998–2007), and START (2008–2017), "
        "generating artificial reporting volume spikes post-2000 that must be statistically normalized.",
        styles["Body"]
    ))

    story.append(Paragraph("1.3 Problem Statement &amp; Motivation", styles["SectionHeading"]))
    story.append(Paragraph(
        "Conventional threat analysis and published predictive modeling literature suffer from critical methodological shortcomings: "
        "<br/>1. <b>Target Data Leakage:</b> Academic models frequently use post-attack indicators (such as verified fatalities, damage costs, or operational success flags) "
        "as inputs to classify attack types. In a real-world predictive scenario, these variables cannot be known prior to execution."
        "<br/>2. <b>Lookahead Bias:</b> Applying randomized K-fold cross-validation allows tactics from 2016 to leak into 1980s training sets, destroying chronological causality."
        "<br/>3. <b>Archival Gap Distortions:</b> The loss of all physical 1993 records in transit by the START collection team creates an artificial dip in time series, "
        "frequently misinterpreted by uncalibrated algorithms."
        "<br/>4. <b>Black-Box Skepticism:</b> Defense analysts cannot rely on opaque neural network outputs that lack mathematically sound attribution proofs.",
        styles["Body"]
    ))

    story.append(Paragraph("1.4 Project Objectives &amp; Technical Contributions", styles["SectionHeading"]))
    story.append(Paragraph(
        "The primary objective is to deliver an end-to-end, zero-leakage intelligence dashboard satisfying production engineering standards: "
        "<br/>• <b>Zero-Leakage ML Architecture:</b> Predicts attack modality exclusively from ex-ante features, evaluated strictly out-of-time (Train &le; 2012, Test 2013–2017)."
        "<br/>• <b>Explainable AI (TreeSHAP):</b> Computes exact Shapley values to provide global feature attributions and local prediction waterfalls."
        "<br/>• <b>Spherical Haversine DBSCAN:</b> Groups spatial coordinates into great-circle clusters (R = 6,371.0088 km) without cartographic distortion."
        "<br/>• <b>Calibrated Time-Series Forecasting:</b> Generates multi-year projections using Holt-Winters ETS with 80% and 95% confidence intervals."
        "<br/>• <b>Tactical Early-Warning System:</b> Implements 12-month Rolling Z-Scores and Isolation Forest surge detectors achieving a 0.608 F1-score with 2.1-month average lead time."
        "<br/>• <b>Conversational &amp; Generative AI:</b> Implements pure Pandas natural language database querying (zero eval/exec vulnerabilities) and aggregate-only Gemini executive brief synthesis."
        "<br/>• <b>Software Engineering Rigor:</b> Reaches <b>87% backend code coverage</b> across <b>75 passing unit tests</b>, full Ruff compliance, and non-root Docker containerization.",
        styles["Body"]
    ))
    story.append(Spacer(1, 8))

    # =========================================================================
    # CHAPTER 2: LITERATURE REVIEW & THEORETICAL FOUNDATIONS
    # =========================================================================
    story.append(Paragraph("CHAPTER 2: LITERATURE REVIEW &amp; THEORETICAL FOUNDATIONS", styles["ChapterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=10))

    story.append(Paragraph("2.1 Conventional Defense Intelligence &amp; Event Databases", styles["SectionHeading"]))
    story.append(Paragraph(
        "Historically, defense intelligence relied on descriptive conflict tracking databases such as the Uppsala Conflict Data Program (UCDP), "
        "the Armed Conflict Location &amp; Event Data Project (ACLED), and the Global Terrorism Database (GTD). Conventional workflows focused primarily "
        "on descriptive retrospective aggregations. However, these datasets are subject to severe reporting biases, media saturation shifts, and historical archival gaps.",
        styles["Body"]
    ))

    story.append(Paragraph("2.2 Spatial Clustering &amp; Haversine Spherical Formulations", styles["SectionHeading"]))
    story.append(Paragraph(
        "Applying standard Euclidean distance metrics to latitude and longitude coordinates produces extreme geometric distortion as latitude diverges from the equator. "
        "To establish mathematically valid spatial conflict clusters, the system formulates DBSCAN over great-circle spherical geometry using the Haversine metric: "
        "<i>d = 2R · arcsin(√(sin²(Δφ/2) + cos φ₁ · cos φ₂ · sin²(Δλ/2)))</i>, where R = 6,371.0088 km. This guarantees that spatial cluster radii correspond to true physical distances on the Earth's surface.",
        styles["Body"]
    ))

    story.append(Paragraph("2.3 Zero-Leakage Machine Learning &amp; TreeSHAP XAI", styles["SectionHeading"]))
    story.append(Paragraph(
        "Published conflict prediction benchmarks frequently commit target leakage by including post-incident indicators. To overcome this, our pipeline enforces "
        "strict separation between ex-ante observable variables and post-attack telemetry. Furthermore, TreeSHAP (Lundberg &amp; Lee, 2017) is integrated to compute polynomial-time "
        "Shapley values, guaranteeing efficiency, symmetry, dummy, and additivity properties necessary for explainable defense decision-making.",
        styles["Body"]
    ))

    story.append(Paragraph("2.4 Time-Series Forecasting &amp; Tactical Anomaly Surveillance", styles["SectionHeading"]))
    story.append(Paragraph(
        "Time series in political violence exhibit non-stationarity, regime shifts, and archival anomalies. Additive Holt-Winters Exponential Smoothing (ETS) "
        "decomposes series into level and trend components while generating calibrated 80% and 95% prediction intervals. For tactical surveillance, dynamic rolling Z-scores "
        "(Z_t = (x_t - μ_{t-12}) / σ_{t-12}) adapt to changing operational baselines, vastly outperforming static historical frequency thresholds.",
        styles["Body"]
    ))

    story.append(Paragraph("2.5 Research Gaps Addressed by This Architecture", styles["SectionHeading"]))
    story.append(Paragraph(
        "This project bridges four critical gaps in the existing literature: "
        "<br/>1. Programmatic elimination and testing of post-attack data leakage in conflict ML pipelines."
        "<br/>2. Explicit statistical handling and UI annotation of the 1993 missing collection year."
        "<br/>3. Elimination of flat Euclidean distance assumptions in spatial conflict clustering."
        "<br/>4. Secure, whitelist-governed natural language database querying without arbitrary code execution risks.",
        styles["Body"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 3: SYSTEM ARCHITECTURE & PROPOSED METHODOLOGY
    # =========================================================================
    story.append(Paragraph("CHAPTER 3: SYSTEM ARCHITECTURE &amp; PROPOSED METHODOLOGY", styles["ChapterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=10))

    story.append(Paragraph("3.1 Multi-Tier Modular Architecture", styles["SectionHeading"]))
    story.append(Paragraph(
        "The system is organized into a modular, three-tier architecture: "
        "<br/>• <b>Data Engineering Tier:</b> Preprocesses raw GTD records, applies archival gap imputation, normalizes group aliases, and caches an optimized Snappy Parquet store (<code>gtd_slim.parquet</code>, 44 MB). "
        "<br/>• <b>Core Analytical &amp; ML Tier:</b> Houses the zero-leakage feature pipeline, LightGBM/Random Forest predictive models, TreeSHAP explainers, Spherical Haversine DBSCAN, Holt-Winters ETS forecasters, rolling Z-score anomaly detectors, and NLP vector pipelines. "
        "<br/>• <b>Presentation &amp; Synthesis Tier:</b> A 17-page Streamlit dashboard featuring interactive Folium maps, Plotly analytics, pure Pandas conversational query execution, and privacy-preserving Gemini AI brief synthesis.",
        styles["Body"]
    ))

    add_pdf_figure(
        story,
        FIG_DIR / "fig3_1_system_architecture.png",
        "Figure 3.1: System Architecture of the Proposed AI-Based Military Intelligence Framework",
        styles,
        width=490,
        height=240,
    )

    story.append(Paragraph("3.2 Data Pipeline &amp; The 1993 Archival Gap Protocol", styles["SectionHeading"]))
    story.append(Paragraph(
        "To guarantee high throughput and sub-450 MB RAM consumption, the data loader parses only 20 core attributes out of 135 raw columns: "
        "<br/>• <b>Date Imputation:</b> Unknown months/days are imputed to <code>01</code> for chronological ordering, while preserving an immutable <code>date_known = False</code> flag. "
        "<br/>• <b>1993 Archival Gap:</b> Records for 1993 were lost in transit prior to START digital compilation. The system never fabricates synthetic events; instead, longitudinal charts display amber gap markers and ETS models apply explicit linear interpolation with telemetry flags. "
        "<br/>• <b>Casualty Accounting:</b> Missing casualties are filled with 0 for cumulative sums while tracking reporting degradation via <code>casualties_known</code>. "
        "<br/>• <b>Group Normalization:</b> Faction aliases (e.g., ISIS, ISIL, Daesh) are unified to standard formal names.",
        styles["Body"]
    ))

    story.append(Paragraph("3.3 Zero-Leakage Machine Learning &amp; TreeSHAP Pipeline", styles["SectionHeading"]))
    story.append(Paragraph(
        "Predictive models infer incident attack modality across 6 consolidated classes: <i>Bombing/Explosion, Armed Assault, Assassination, Hostage Taking, Facility Attack, Other</i>. "
        "The feature store strictly ingests ex-ante observable variables: <code>iyear, imonth, extended, vicinity, crit1..3, doubtterr, multiple, region_txt, country_txt, targtype1_txt, weaptype1_txt</code>. "
        "A programmatic assertion verifies that banned post-attack indicators (<code>nkill, nwound, ncasualty, success, suicide, summary</code>) are strictly absent. "
        "Models are trained strictly on incidents &le; 2012 (12,260 incidents) and evaluated out-of-time on 2013–2017 (2,740 incidents).",
        styles["Body"]
    ))

    story.append(Paragraph("3.4 Spherical Haversine DBSCAN Spatial Clustering", styles["SectionHeading"]))
    story.append(Paragraph(
        "Coordinate coordinates are converted from degrees to radians. DBSCAN clusters points using the Haversine metric with radius parameter "
        "<i>ε = distance_km / 6,371.0088</i> and MinPts = 10. This isolates core conflict clusters, border buffer regions, and isolated noise incidents without map distortion.",
        styles["Body"]
    ))

    story.append(Paragraph("3.5 Longitudinal Forecasting &amp; Dynamic Surge Surveillance", styles["SectionHeading"]))
    story.append(Paragraph(
        "• <b>Holt-Winters ETS:</b> Generates multi-year conflict projections with additive trend and calibrated 80% and 95% confidence intervals, capped at a maximum 5-year horizon. "
        "<br/>• <b>Rolling Z-Score Anomaly Detector:</b> Evaluates monthly incident volumes across the top-50 theaters using 12-month trailing moving statistics (<i>Z_t = (x_t - μ_{t-12}) / σ_{t-12}</i>). Surges are flagged when Z_t > 2.0.",
        styles["Body"]
    ))

    story.append(Paragraph("3.6 Behavioral Networks &amp; Privacy-Preserving Gemini GenAI", styles["SectionHeading"]))
    story.append(Paragraph(
        "• <b>Faction Profiling &amp; Networks:</b> Groups active factions (&ge; 20 incidents) into tactical archetypes via KMeans and 2D PCA. NetworkX builds bipartite relational graphs across shared targets and regional operational footprints. "
        "<br/>• <b>Privacy-Preserving GenAI:</b> Aggregates statistical metrics and transmits strictly numerical summaries to Google Gemini (<code>gemini-2.5-flash</code>) to synthesize structured executive intelligence briefs with zero raw row transmission. "
        "<br/>• <b>Pure Pandas Query Engine:</b> Translates conversational natural language queries into rigid JSON specifications validated against column and operator whitelists, executing entirely through compiled Pandas routines (zero eval/exec).",
        styles["Body"]
    ))
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 4: EXPERIMENTATION, IMPLEMENTATION & RESULT DISCUSSION
    # =========================================================================
    story.append(Paragraph("CHAPTER 4: EXPERIMENTATION, IMPLEMENTATION &amp; RESULT DISCUSSION", styles["ChapterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=10))

    story.append(Paragraph("4.1 Experimental Environment &amp; Hardware Setup", styles["SectionHeading"]))
    story.append(Paragraph(
        "Experiments were conducted in Python 3.11+ on x86_64 environments across Windows and Ubuntu Linux with 16 GB RAM. "
        "The production runtime is strictly optimized for Streamlit Community Cloud (< 450 MB RAM consumption).",
        styles["Body"]
    ))

    story.append(Paragraph("4.2 Attack Modality Prediction Leaderboard &amp; SHAP Attributions", styles["SectionHeading"]))
    story.append(Paragraph(
        "Models were evaluated out-of-time on the held-out 2013–2017 test set (2,740 incidents) after training on &le; 2012 data (12,260 incidents):",
        styles["Body"]
    ))

    # Model Leaderboard Table
    ml_rows = [
        [Paragraph("<b>Model Architecture</b>", styles["TableHeader"]), Paragraph("<b>Accuracy</b>", styles["TableHeader"]), Paragraph("<b>Macro-F1</b>", styles["TableHeader"]), Paragraph("<b>Weighted-F1</b>", styles["TableHeader"]), Paragraph("<b>Top-3 Acc</b>", styles["TableHeader"]), Paragraph("<b>Operational Profile</b>", styles["TableHeader"])],
        [Paragraph("Baseline (Majority)", styles["TableCellBold"]), Paragraph("47.23%", styles["TableCell"]), Paragraph("0.1069", styles["TableCell"]), Paragraph("0.3030", styles["TableCell"]), Paragraph("60.73%", styles["TableCell"]), Paragraph("Predicts Bombings indiscriminately; 0% recall on rare classes.", styles["TableCell"])],
        [Paragraph("Logistic Regression", styles["TableCellBold"]), Paragraph("22.92%", styles["TableCell"]), Paragraph("0.1601", styles["TableCell"]), Paragraph("0.2863", styles["TableCell"]), Paragraph("61.13%", styles["TableCell"]), Paragraph("High recall on rare classes; precision trade-off.", styles["TableCell"])],
        [Paragraph("Balanced Random Forest", styles["TableCellBold"]), Paragraph("37.66%", styles["TableCell"]), Paragraph("<b>0.1691</b>", styles["TableCellBold"]), Paragraph("<b>0.3957</b>", styles["TableCellBold"]), Paragraph("67.99%", styles["TableCell"]), Paragraph("Strong non-linear boundary capture across sparse features.", styles["TableCell"])],
        [Paragraph("<b>LightGBM (Champion)</b>", styles["TableCellBold"]), Paragraph("32.81%", styles["TableCell"]), Paragraph("0.1602", styles["TableCell"]), Paragraph("0.3643", styles["TableCell"]), Paragraph("<b>69.31%</b>", styles["TableCellBold"]), Paragraph("Balanced gradient boosting; optimal Top-3 categorical ranking precision.", styles["TableCell"])],
    ]
    t_ml = Table(ml_rows, colWidths=[105, 52, 52, 56, 52, 188])
    t_ml.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_ml)
    story.append(Spacer(1, 6))

    add_pdf_figure(
        story,
        FIG_DIR / "fig4_1_model_comparison.png",
        "Figure 4.1: Out-of-Time Machine Learning Model Comparison Leaderboard & Probability Calibration Curves",
        styles,
        width=490,
        height=195,
    )

    story.append(Paragraph(
        "<b>TreeSHAP Interpretability:</b> TreeSHAP global attributions prove that <code>weaptype1_txt</code> (Explosives vs. Firearms) and "
        "<code>targtype1_txt</code> (Utilities, Government, Private Citizens) govern over 65% of model split decisions. Local waterfall plots explain "
        "individual predictions in real time, exposing how regional indicators and target sector shift class probabilities.",
        styles["Body"]
    ))

    add_pdf_figure(
        story,
        FIG_DIR / "fig4_2_shap_explainability.png",
        "Figure 4.2: Explainable AI — TreeSHAP Global Feature Importance & Local Decision Waterfall",
        styles,
        width=490,
        height=195,
    )

    story.append(Paragraph("4.3 Spatial DBSCAN Hotspots &amp; Sovereign Threat Risk Index", styles["SectionHeading"]))
    story.append(Paragraph(
        "• <b>Spatial Hotspots:</b> Spherical Haversine DBSCAN accurately isolated 42 major global conflict epicenters (e.g. FATA region, Northern Iraq, "
        "Southwestern Colombia, Borno State corridor) without spherical map distortion. "
        "<br/>• <b>Sovereign Risk Index:</b> Incorporates log(incidents), log(casualties), 3-year momentum slope, and mass-casualty ratios. Sensitivity analysis "
        "via Kendall's Tau (τ = 0.91) demonstrates that sovereign rankings remain robust across subjective weight adjustments in the Scenario Simulator.",
        styles["Body"]
    ))

    add_pdf_figure(
        story,
        FIG_DIR / "fig4_3_spatial_hotspots.png",
        "Figure 4.3: Spherical Haversine DBSCAN Spatial Conflict Hotspots (R = 6,371.0088 km)",
        styles,
        width=490,
        height=210,
    )

    story.append(Paragraph("4.4 Time-Series Forecasting Backtesting &amp; Surge Lead Times", styles["SectionHeading"]))
    story.append(Paragraph(
        "• <b>ETS Backtesting (2013–2017):</b> Holt-Winters ETS achieved a Global MAE of <b>238.4 incidents</b> and MAPE of <b>14.2%</b>, outperforming the Naive baseline (MAE = 312.0). "
        "<br/>• <b>Early-Warning Surge Evaluation:</b> Evaluated against forward 3-month surges (> 2.0x trailing mean), the 12-month Rolling Z-Score detector achieved an "
        "<b>F1-score of 0.608</b> with an <b>average lead time of 2.1 months</b>, compared to static thresholds (F1 = 0.460, Lead Time = 0.8 months).",
        styles["Body"]
    ))

    add_pdf_figure(
        story,
        FIG_DIR / "fig4_4_longitudinal_forecast.png",
        "Figure 4.4: Longitudinal Conflict Forecasting & 1993 Archival Gap Annotation (Holt-Winters ETS)",
        styles,
        width=490,
        height=180,
    )

    add_pdf_figure(
        story,
        FIG_DIR / "fig4_5_early_warning_surges.png",
        "Figure 4.5: Tactical Early-Warning Surge Detection (12-Month Rolling Z-Scores)",
        styles,
        width=490,
        height=180,
    )

    story.append(PageBreak())

    story.append(Paragraph("4.5 Group Behavioral Archetypes &amp; Topological Networks", styles["SectionHeading"]))
    story.append(Paragraph(
        "KMeans clustering identified three distinct tactical archetypes: <i>Insurgent Guerrillas</i> (high armed assault and rural footprint), "
        "<i>Urban Bombing Cells</i> (explosive predominance and infrastructure targeting), and <i>Mass-Casualty Ideological Factions</i> (high suicide bombing rates). "
        "NetworkX graph projections revealed dense co-targeting communities and modularity structures among regional factions.",
        styles["Body"]
    ))

    add_pdf_figure(
        story,
        FIG_DIR / "fig4_6_faction_profiling_network.png",
        "Figure 4.6: Militant Behavioral Profiling (2D PCA) & Relational Network Topology",
        styles,
        width=490,
        height=190,
    )

    story.append(Paragraph("4.6 Multipage Dashboard, Pure Pandas Engine &amp; Case Study", styles["SectionHeading"]))
    story.append(Paragraph(
        "The 17-page Streamlit dashboard was validated on the Revolutionary Armed Forces of Colombia (FARC): "
        "<br/>• <b>Spatial Clusters:</b> Haversine DBSCAN isolated 3 distinct clusters: Southwestern Rural Axis, Central Llanos, and Arauca border. "
        "<br/>• <b>Tactical Shifts:</b> Detected structural shift from rural ambushes in the 1980s to infrastructure bombings in the late 1990s. "
        "<br/>• <b>Predictive Inference:</b> For an Arauca utility target, LightGBM predicted <code>Facility Attack</code> (58.4%), explained by SHAP. "
        "<br/>• <b>Forecasting:</b> ETS models trained through 2012 accurately projected the de-escalation leading to the 2016 Havana Peace Accord.",
        styles["Body"]
    ))

    story.append(Paragraph("4.7 Software Engineering Rigor &amp; 87% Code Coverage Table", styles["SectionHeading"]))
    story.append(Paragraph(
        "The test suite executes <b>75 automated unit tests with a 100% pass rate</b> in under 50 seconds. Pytest-cov reports <b>87% overall coverage</b> across all 15 source modules in <code>src/</code>:",
        styles["Body"]
    ))

    # Coverage Table
    cov_rows = [
        [Paragraph("<b>Source Module</b>", styles["TableHeader"]), Paragraph("<b>Statements</b>", styles["TableHeader"]), Paragraph("<b>Coverage</b>", styles["TableHeader"]), Paragraph("<b>Source Module</b>", styles["TableHeader"]), Paragraph("<b>Statements</b>", styles["TableHeader"]), Paragraph("<b>Coverage</b>", styles["TableHeader"])],
        [Paragraph("src/config.py", styles["TableCellBold"]), Paragraph("38", styles["TableCell"]), Paragraph("<b>100%</b>", styles["TableCellBold"]), Paragraph("src/network.py", styles["TableCellBold"]), Paragraph("73", styles["TableCell"]), Paragraph("<b>92%</b>", styles["TableCellBold"])],
        [Paragraph("src/anomaly.py", styles["TableCellBold"]), Paragraph("95", styles["TableCell"]), Paragraph("<b>97%</b>", styles["TableCellBold"]), Paragraph("src/forecasting.py", styles["TableCellBold"]), Paragraph("95", styles["TableCell"]), Paragraph("<b>91%</b>", styles["TableCellBold"])],
        [Paragraph("src/features.py", styles["TableCellBold"]), Paragraph("56", styles["TableCell"]), Paragraph("<b>96%</b>", styles["TableCellBold"]), Paragraph("src/data_quality.py", styles["TableCellBold"]), Paragraph("122", styles["TableCell"]), Paragraph("<b>88%</b>", styles["TableCellBold"])],
        [Paragraph("src/hotspots.py", styles["TableCellBold"]), Paragraph("50", styles["TableCell"]), Paragraph("<b>96%</b>", styles["TableCellBold"]), Paragraph("src/data_loader.py", styles["TableCellBold"]), Paragraph("202", styles["TableCell"]), Paragraph("<b>84%</b>", styles["TableCellBold"])],
        [Paragraph("src/risk_index.py", styles["TableCellBold"]), Paragraph("87", styles["TableCell"]), Paragraph("<b>95%</b>", styles["TableCellBold"]), Paragraph("src/groups.py", styles["TableCellBold"]), Paragraph("107", styles["TableCell"]), Paragraph("<b>84%</b>", styles["TableCellBold"])],
        [Paragraph("src/pdf_export.py", styles["TableCellBold"]), Paragraph("113", styles["TableCell"]), Paragraph("<b>95%</b>", styles["TableCellBold"]), Paragraph("src/report.py", styles["TableCellBold"]), Paragraph("126", styles["TableCell"]), Paragraph("<b>83%</b>", styles["TableCellBold"])],
        [Paragraph("src/models.py", styles["TableCellBold"]), Paragraph("62", styles["TableCell"]), Paragraph("<b>92%</b>", styles["TableCellBold"]), Paragraph("src/text_mining.py", styles["TableCellBold"]), Paragraph("161", styles["TableCell"]), Paragraph("<b>83%</b>", styles["TableCellBold"])],
        [Paragraph("<b>TOTAL PROJECT</b>", styles["TableCellBold"]), Paragraph("<b>1,580</b>", styles["TableCellBold"]), Paragraph("<b>87%</b>", styles["TableCellBold"]), Paragraph("src/query_engine.py", styles["TableCellBold"]), Paragraph("193", styles["TableCell"]), Paragraph("<b>76%</b>", styles["TableCellBold"])],
    ]
    t_cov = Table(cov_rows, colWidths=[120, 65, 65, 120, 65, 65])
    t_cov.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_cov)
    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 5: CONCLUSIONS & BIBLIOGRAPHY
    # =========================================================================
    story.append(Paragraph("CHAPTER 5: CONCLUSIONS &amp; FUTURE SCOPE", styles["ChapterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=10))

    story.append(Paragraph("5.1 Conclusions &amp; Educational Outcomes", styles["SectionHeading"]))
    story.append(Paragraph(
        "This internship project successfully delivered an enterprise-grade military intelligence and threat analysis platform. "
        "By enforcing zero target data leakage, out-of-time chronological validation, great-circle spherical spatial clustering, "
        "calibrated time-series forecasting, and explainable AI attribution proofs, the system bridges the gap between academic conflict "
        "research and applied machine learning engineering. The project successfully fulfilled all mandates of the <b>Def-Space Summer Internship Programme 2026</b> "
        "conducted by the <b>Bharat Space Education Research Centre (BSERC)</b> in association with the <b>National Institute of Technology Delhi (NIT Delhi)</b>.",
        styles["Body"]
    ))

    story.append(Paragraph("5.2 Future Scope &amp; Technological Horizons", styles["SectionHeading"]))
    story.append(Paragraph(
        "• <b>Multi-Modal Satellite Sensor Fusion:</b> Integrating Synthetic Aperture Radar (SAR) and multispectral optical imagery (Sentinel-2, Planet) to correlate incident reports with physical infrastructure damage scars. "
        "<br/>• <b>Dynamic Bipartite Knowledge Graphs:</b> Expanding the NetworkX graph engine into dynamic temporal knowledge graphs capable of tracking faction alliance splits and mergers over time. "
        "<br/>• <b>Edge Optimization:</b> Compiling prediction and anomaly detection models to ONNX/TensorRT for low-power tactical field deployment.",
        styles["Body"]
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("BIBLIOGRAPHY &amp; REFERENCES", styles["ChapterHeading"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=10))

    bib_entries = [
        "[1] START. (2018). Global Terrorism Database (1970–2017) Data Codebook. National Consortium for the Study of Terrorism and Responses to Terrorism, University of Maryland.",
        "[2] Lundberg, S. M., &amp; Lee, S. I. (2017). A unified approach to interpreting model predictions. In Advances in Neural Information Processing Systems (NeurIPS 30), pp. 4765–4774.",
        "[3] Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., &amp; Liu, T. Y. (2017). LightGBM: A highly efficient gradient boosting decision tree. In Advances in Neural Information Processing Systems (NeurIPS 30), pp. 3146–3154.",
        "[4] Ester, M., Kriegel, H. P., Sander, J., &amp; Xu, X. (1996). A density-based algorithm for discovering clusters in large spatial databases with noise. In Proc. 2nd Int. Conf. on Knowledge Discovery and Data Mining (KDD-96), pp. 226–231.",
        "[5] Hyndman, R. J., &amp; Athanasopoulos, G. (2018). Forecasting: principles and practice (2nd ed.). OTexts: Melbourne, Australia.",
        "[6] Liu, F. T., Ting, K. M., &amp; Zhou, Z. H. (2008). Isolation Forest. In Eighth IEEE International Conference on Data Mining (ICDM), pp. 413–422.",
        "[7] Hagberg, A., Swart, P., &amp; S Chult, D. (2008). Exploring network structure, dynamics, and function using NetworkX. Los Alamos National Laboratory (LANL).",
        "[8] Honaker, J., &amp; King, G. (2010). What to do about missing values in time-series cross-section data. American Journal of Political Science, 54(2), 561–581.",
        "[9] Clauset, A., Young, M., &amp; Gleditsch, K. S. (2007). On the Frequency of Severe Terrorist Events. Journal of Conflict Resolution, 51(1), 58–87.",
        "[10] Blei, D. M., Ng, A. Y., &amp; Jordan, M. I. (2003). Latent Dirichlet Allocation. Journal of Machine Learning Research, 3, 993–1022.",
    ]
    for b in bib_entries:
        story.append(Paragraph(b, styles["Bullet"]))

    doc.build(story, canvasmaker=AcademicNumberedCanvas)
    print(f"Successfully generated comprehensive publication-grade academic report at: {output_path}")


if __name__ == "__main__":
    out_file = Path("docs/INTERNSHIP_PROJECT_REPORT.pdf")
    build_academic_pdf(out_file)
