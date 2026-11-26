"""
Generates an Executive 4-Page Interview Brief & Cheat-Sheet PDF for:
AI-Based Military Intelligence & Threat Analysis Dashboard
Candidate: Shubham Kumar, B.Tech CSE (7th Semester), NIT Delhi
Host Organisation: Bharat Space Education Research Centre (BSERC), New Delhi
Def-Space Summer Internship Programme 2026 (Certificate: BSERC-DSI-2026-1417)
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

FIG_DIR = Path("docs/figures")


class InterviewNumberedCanvas(canvas.Canvas):
    """Two-pass canvas for exact 'Page X of Y' numbering and running interview headers."""
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
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Top Running Header (Pages 2-4)
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor("#003366"))
            self.drawString(36, 810, "EXECUTIVE INTERVIEW BRIEF | AI-BASED MILITARY INTELLIGENCE DASHBOARD")
            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(559, 810, "Candidate: Shubham Kumar (NIT Delhi / BSERC)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(36, 804, 559, 804)
            self.restoreState()

        # Running Footer (All Pages)
        self.saveState()
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(36, 32, 559, 32)

        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(36, 22, "National Institute of Technology Delhi | Bharat Space Education Research Centre (BSERC)")
        self.setFont("Helvetica-Bold", 7.5)
        self.drawRightString(559, 22, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def get_interview_styles():
    return {
        "Title": ParagraphStyle(
            "Title",
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=19,
            textColor=colors.HexColor("#002B49"),
            alignment=TA_LEFT,
        ),
        "Subtitle": ParagraphStyle(
            "Subtitle",
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#B91C1C"),
            alignment=TA_LEFT,
        ),
        "CandidateBanner": ParagraphStyle(
            "CandidateBanner",
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#334155"),
            alignment=TA_RIGHT,
        ),
        "SectionHeader": ParagraphStyle(
            "SectionHeader",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#003366"),
            spaceBefore=4,
            spaceAfter=3,
        ),
        "SubSectionHeader": ParagraphStyle(
            "SubSectionHeader",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=3,
            spaceAfter=2,
        ),
        "Body": ParagraphStyle(
            "Body",
            fontName="Helvetica",
            fontSize=7.8,
            leading=10.5,
            textColor=colors.HexColor("#1E293B"),
            alignment=TA_JUSTIFY,
        ),
        "BodyBold": ParagraphStyle(
            "BodyBold",
            fontName="Helvetica-Bold",
            fontSize=7.8,
            leading=10.5,
            textColor=colors.HexColor("#0F172A"),
        ),
        "Bullet": ParagraphStyle(
            "Bullet",
            fontName="Helvetica",
            fontSize=7.8,
            leading=10.5,
            textColor=colors.HexColor("#1E293B"),
            leftIndent=10,
            spaceAfter=2,
        ),
        "QAQuestion": ParagraphStyle(
            "QAQuestion",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#003366"),
            spaceBefore=2,
            spaceAfter=1,
        ),
        "QAAnswer": ParagraphStyle(
            "QAAnswer",
            fontName="Helvetica",
            fontSize=7.5,
            leading=10.2,
            textColor=colors.HexColor("#1E293B"),
            alignment=TA_JUSTIFY,
            spaceAfter=3,
        ),
        "FigureCaption": ParagraphStyle(
            "FigureCaption",
            fontName="Helvetica-Oblique",
            fontSize=6.8,
            leading=8.5,
            textColor=colors.HexColor("#475569"),
            alignment=TA_CENTER,
            spaceAfter=3,
        ),
        "TableHead": ParagraphStyle(
            "TableHead",
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9.5,
            textColor=colors.white,
            alignment=TA_CENTER,
        ),
        "TableCell": ParagraphStyle(
            "TableCell",
            fontName="Helvetica",
            fontSize=7.2,
            leading=9.2,
            textColor=colors.HexColor("#0F172A"),
            alignment=TA_LEFT,
        ),
        "TableCellCenter": ParagraphStyle(
            "TableCellCenter",
            fontName="Helvetica",
            fontSize=7.2,
            leading=9.2,
            textColor=colors.HexColor("#0F172A"),
            alignment=TA_CENTER,
        ),
        "CalloutTitle": ParagraphStyle(
            "CalloutTitle",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#B91C1C"),
            spaceAfter=2,
        ),
        "CalloutText": ParagraphStyle(
            "CalloutText",
            fontName="Helvetica",
            fontSize=7.5,
            leading=10.2,
            textColor=colors.HexColor("#334155"),
            alignment=TA_JUSTIFY,
        ),
    }


def make_callout(title: str, text: str, styles, border_color="#B91C1C", bg_color="#FEF2F2", width=523) -> Table:
    p_title = Paragraph(f"<b>{title}</b>", styles["CalloutTitle"])
    p_text = Paragraph(text, styles["CalloutText"])
    t = Table([[p_title], [p_text]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg_color)),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 5),
        ("LINELEFT", (0, 0), (0, -1), 3.5, colors.HexColor(border_color)),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    return t


def build_interview_brief_pdf(output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = get_interview_styles()
    story = []

    # =========================================================================
    # PAGE 1: EXECUTIVE OVERVIEW & 60-SECOND ELEVATOR PITCH
    # =========================================================================
    header_data = [
        [
            Paragraph("<b>AI-BASED MILITARY INTELLIGENCE & THREAT ANALYSIS DASHBOARD</b>", styles["Title"]),
            Paragraph(
                "<b>Candidate:</b> Shubham Kumar<br/>"
                "<b>Institute:</b> NIT Delhi (B.Tech CSE, 7th Sem)<br/>"
                "<b>Internship:</b> BSERC Def-Space 2026<br/>"
                "<b>Cert ID:</b> BSERC-DSI-2026-1417",
                styles["CandidateBanner"]
            )
        ]
    ]
    t_hdr = Table(header_data, colWidths=[363, 160])
    t_hdr.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(t_hdr)

    story.append(Paragraph("<b>Retrospective Intelligence Analytics & Predictive Machine Learning on the Global Terrorism Database (1970–2017)</b>", styles["Subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#003366"), spaceBefore=3, spaceAfter=5))

    # 60-Second Elevator Pitch
    pitch_text = (
        "<b>When asked: 'Tell me about your project':</b><br/>"
        "<i>'I engineered an enterprise-grade defense intelligence and threat analysis platform that transforms 181,691 historical conflict incidents "
        "(1970–2017) into actionable strategic foresight. Built during my Def-Space Internship at BSERC and NIT Delhi, the system features a "
        "<b>zero-leakage pre-attack classifier</b> (LightGBM, 80.5% Accuracy, 98.1% Top-3 Accuracy) with <b>TreeSHAP explainability</b>, "
        "<b>spherical Haversine DBSCAN</b> conflict clustering, 5-year <b>Holt-Winters time-series forecasting</b>, and automated <b>12-month rolling surge detection</b>. "
        "The entire platform is deployed as a 17-page interactive Streamlit application with a pure-Pandas NLP query engine, 87% test coverage, and a sub-3-second boot time.'</i>"
    )
    story.append(make_callout("🎯 THE 60-SECOND ELEVATOR PITCH", pitch_text, styles, border_color="#003366", bg_color="#F0F7FF"))
    story.append(Spacer(1, 5))

    # Architecture Overview & Embed Figure 3.1
    story.append(Paragraph("<b>1. Production 3-Tier Architecture</b>", styles["SectionHeader"]))
    story.append(Paragraph(
        "The system decouples data ingestion, offline machine learning precomputation, and runtime presentation. This allows the live dashboard to run in "
        "<b>< 450 MB RAM</b> on low-power edge machines or cloud instances without re-training models on user interactions.",
        styles["Body"]
    ))
    story.append(Spacer(1, 3))

    if (FIG_DIR / "fig3_1_system_architecture.png").exists():
        story.append(Image(str(FIG_DIR / "fig3_1_system_architecture.png"), width=515, height=140))
        story.append(Paragraph("<i>Figure 1.1: End-to-end decoupled 3-tier enterprise architecture from raw GTD ingestion to Streamlit presentation.</i>", styles["FigureCaption"]))

    # Core Engineering Specs Table
    story.append(Paragraph("<b>2. Key Architectural & Software Engineering Specs</b>", styles["SectionHeader"]))
    specs_data = [
        [
            Paragraph("<b>Component / Metric</b>", styles["TableHead"]),
            Paragraph("<b>Implementation Details</b>", styles["TableHead"]),
            Paragraph("<b>Interview Defense Defense Justification</b>", styles["TableHead"]),
        ],
        [
            Paragraph("<b>Dataset Scale</b>", styles["TableCell"]),
            Paragraph("181,691 incidents (1970–2017), 135 raw → 29 slim features", styles["TableCell"]),
            Paragraph("Full official START GTD archive, filtered to 20 core analytical columns", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Leakage Prevention</b>", styles["TableCell"]),
            Paragraph("Banned outcome features (`nkill`, `nwound`, `success`, `suicide`)", styles["TableCell"]),
            Paragraph("Guarantees model strictly ingests pre-attack observable intelligence", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Temporal Split</b>", styles["TableCell"]),
            Paragraph("Train $\\le$ 2012 (113,300 rows) | Test 2013–2017 (68,391 rows)", styles["TableCell"]),
            Paragraph("Simulates real-world deployment; k-fold CV causes future-to-past leakage", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Software Rigor</b>", styles["TableCell"]),
            Paragraph("75 unit tests (100% pass), 87% coverage (`pytest-cov`), Ruff", styles["TableCell"]),
            Paragraph("Enterprise CI/CD quality (`.github/workflows/ci.yml`), Dockerized", styles["TableCell"]),
        ],
        [
            Paragraph("<b>Memory Footprint</b>", styles["TableCell"]),
            Paragraph("< 450 MB runtime RAM, Snappy columnar Parquet caching", styles["TableCell"]),
            Paragraph("Boots in < 3s on Streamlit Community Cloud and tactical edge laptops", styles["TableCell"]),
        ],
    ]
    t_specs = Table(specs_data, colWidths=[110, 205, 208])
    t_specs.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_specs)

    # Mandatory Ethical Charter
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<b>Ethical Research Charter:</b> This system is strictly an academic, retrospective conflict research tool. It contains "
        "<b>zero real-time kinetic targeting capabilities</b>, does not process classified signals telemetry, and enforces historical bias auditing.",
        styles["Body"]
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: MACHINE LEARNING, ZERO-LEAKAGE PIPELINE & EXPLAINABLE AI
    # =========================================================================
    story.append(Paragraph("<b>02 · PRE-ATTACK ML CLASSIFICATION & EXPLAINABLE AI (XAI)</b>", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1.0, color=colors.HexColor("#003366"), spaceBefore=2, spaceAfter=4))

    story.append(Paragraph(
        "<b>The Tactical ML Task:</b> Given observable pre-attack covariates (geographic region, target category, weapon type, perpetrator affiliation), "
        "predict the <b>tactical attack modality</b> across 6 primary classes (<i>Bombing/Explosion</i>, <i>Armed Assault</i>, <i>Assassination</i>, "
        "<i>Facility Attack</i>, <i>Kidnapping</i>, <i>Other</i>).",
        styles["Body"]
    ))
    story.append(Spacer(1, 3))

    # Side-by-side: Model Comparison Table & Model Fig 4.1
    ml_table_data = [
        [
            Paragraph("<b>Model Architecture</b>", styles["TableHead"]),
            Paragraph("<b>Accuracy</b>", styles["TableHead"]),
            Paragraph("<b>Macro-F1</b>", styles["TableHead"]),
            Paragraph("<b>Top-3 Acc</b>", styles["TableHead"]),
            Paragraph("<b>Operational Takeaway</b>", styles["TableHead"]),
        ],
        [
            Paragraph("Baseline (Majority Class)", styles["TableCell"]),
            Paragraph("51.58%", styles["TableCellCenter"]),
            Paragraph("0.1134", styles["TableCellCenter"]),
            Paragraph("65.88%", styles["TableCellCenter"]),
            Paragraph("Predicts Bombing indiscriminately; zero minority skill", styles["TableCell"]),
        ],
        [
            Paragraph("Multinomial Logistic Reg.", styles["TableCell"]),
            Paragraph("78.38%", styles["TableCellCenter"]),
            Paragraph("0.5903", styles["TableCellCenter"]),
            Paragraph("97.02%", styles["TableCellCenter"]),
            Paragraph("Strong linear baseline; calibrated via SAGA solver", styles["TableCell"]),
        ],
        [
            Paragraph("Balanced Random Forest", styles["TableCell"]),
            Paragraph("<b>80.93%</b>", styles["TableCellCenter"]),
            Paragraph("0.6154", styles["TableCellCenter"]),
            Paragraph("97.09%", styles["TableCellCenter"]),
            Paragraph("100 estimators; robust against class imbalance", styles["TableCell"]),
        ],
        [
            Paragraph("<b>LightGBM (Champion)</b>", styles["TableCell"]),
            Paragraph("<b>80.53%</b>", styles["TableCellCenter"]),
            Paragraph("<b>0.6331</b>", styles["TableCellCenter"]),
            Paragraph("<b>98.12%</b>", styles["TableCellCenter"]),
            Paragraph("<b>Highest Macro-F1 & Top-3; sub-10ms latency</b>", styles["TableCell"]),
        ],
    ]
    t_ml = Table(ml_table_data, colWidths=[120, 52, 55, 60, 236])
    t_ml.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_ml)
    story.append(Spacer(1, 3))

    if (FIG_DIR / "fig4_1_model_comparison.png").exists():
        story.append(Image(str(FIG_DIR / "fig4_1_model_comparison.png"), width=515, height=130))
        story.append(Paragraph("<i>Figure 2.1: Out-of-time model benchmark leaderboard & multi-class probability calibration curves.</i>", styles["FigureCaption"]))

    # TreeSHAP Explainability
    story.append(Paragraph("<b>TreeSHAP Interpretability: Explaining Decisions to Defense Commanders</b>", styles["SubSectionHeader"]))
    story.append(Paragraph(
        "A black-box model is useless in high-stakes defense intelligence. We integrated <b>TreeSHAP (SHapley Additive exPlanations)</b> to compute exact additive "
        "feature contributions. Global importance reveals that <code>weaptype1_txt</code> and <code>targtype1_txt</code> account for >65% of split gain. "
        "Local waterfall plots explain individual predictions, showing commanders exactly which tactical cues shifted risk probabilities.",
        styles["Body"]
    ))
    story.append(Spacer(1, 3))

    if (FIG_DIR / "fig4_2_shap_explainability.png").exists():
        story.append(Image(str(FIG_DIR / "fig4_2_shap_explainability.png"), width=515, height=125))
        story.append(Paragraph("<i>Figure 2.2: Global TreeSHAP feature attributions and local prediction waterfall decomposing class probabilities.</i>", styles["FigureCaption"]))

    # Interview Defense Box: ML Questions
    qa_ml = (
        "<b>Q1: Why did you use an out-of-time temporal split rather than 5-fold cross-validation?</b><br/>"
        "<b>Answer:</b> <i>'Conflict data has severe temporal auto-correlation. In real life, an analyst trains on historical data and predicts the future. "
        "Standard k-fold cross-validation shuffles data across time, letting models learn from 2017 events to predict 2013, creating massive look-ahead leakage. "
        "Our split (Train $\\le$ 2012, Test 2013–2017) strictly simulates operational deployment.'</i><br/>"
        "<b>Q2: Why choose LightGBM over deep learning (e.g. MLP or Transformers)?</b><br/>"
        "<b>Answer:</b> <i>'Tabular conflict data is dominated by high-cardinality categorical features (provinces, weapons, targets) where Gradient Boosted Decision Trees "
        "(GBDTs) consistently beat deep networks without needing heavy embedding layers. LightGBM trains in seconds, handles sparsity natively, and supports exact TreeSHAP.'</i>"
    )
    story.append(make_callout("💡 TOP MACHINE LEARNING INTERVIEW DEFENSE", qa_ml, styles, border_color="#B91C1C", bg_color="#FEF2F2"))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: GEOSPATIAL CLUSTERING, FORECASTING & SURGE SURVEILLANCE
    # =========================================================================
    story.append(Paragraph("<b>03 · GEOSPATIAL CLUSTERING, FORECASTING & EARLY WARNING</b>", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1.0, color=colors.HexColor("#003366"), spaceBefore=2, spaceAfter=4))

    # 2x2 Grid of Technical Figures: Spatial & Forecast
    col_w = 255
    fig_w = 250
    fig_h = 105

    row1_data = [
        [
            Paragraph("<b>A. Spherical Haversine DBSCAN Hotspots</b>", styles["SubSectionHeader"]),
            Paragraph("<b>B. Longitudinal Holt-Winters ETS Forecast</b>", styles["SubSectionHeader"]),
        ],
        [
            Image(str(FIG_DIR / "fig4_3_spatial_hotspots.png"), width=fig_w, height=fig_h) if (FIG_DIR / "fig4_3_spatial_hotspots.png").exists() else Paragraph("N/A", styles["Body"]),
            Image(str(FIG_DIR / "fig4_4_longitudinal_forecast.png"), width=fig_w, height=fig_h) if (FIG_DIR / "fig4_4_longitudinal_forecast.png").exists() else Paragraph("N/A", styles["Body"]),
        ],
        [
            Paragraph("<i>Figure 3.1: Great-circle spatial clusters ($R=6,371\\text{ km}$) eliminating planar map distortion.</i>", styles["FigureCaption"]),
            Paragraph("<i>Figure 3.2: 1970–2017 conflict trajectory, 1993 missing archival gap, & 5-year ETS forecast with 95% CIs.</i>", styles["FigureCaption"]),
        ],
        [
            Paragraph(
                "• Uses great-circle distance $\\text{haversine}(\\phi_1, \\phi_2, \\Delta\\lambda)$ to cluster dense conflict epicenters without polar distortion.<br/>"
                "• Epsilon $= 100\\text{ km}$, MinPts $= 15$. Isolates 42 major global conflict corridors while classifying dispersed events as noise.",
                styles["Body"]
            ),
            Paragraph(
                "• Damped additive Holt-Winters Exponential Smoothing (ETS) models level, trend, and dampening factor $\\phi = 0.95$.<br/>"
                "• Backtesting on 2013–2017: Global MAE of 3,799.1 incidents (25.9% MAPE), beating Naive baseline (MAE 5,156.2, 36.2% MAPE).",
                styles["Body"]
            ),
        ],
    ]
    t_row1 = Table(row1_data, colWidths=[col_w, col_w])
    t_row1.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    story.append(t_row1)
    story.append(Spacer(1, 4))

    # Row 2: Surge Surveillance & Faction Relational Networks
    row2_data = [
        [
            Paragraph("<b>C. Tactical Early Warning Surge Timeline</b>", styles["SubSectionHeader"]),
            Paragraph("<b>D. Behavioral Profiling & Relational Network</b>", styles["SubSectionHeader"]),
        ],
        [
            Image(str(FIG_DIR / "fig4_5_early_warning_surges.png"), width=fig_w, height=fig_h) if (FIG_DIR / "fig4_5_early_warning_surges.png").exists() else Paragraph("N/A", styles["Body"]),
            Image(str(FIG_DIR / "fig4_6_faction_profiling_network.png"), width=fig_w, height=fig_h) if (FIG_DIR / "fig4_6_faction_profiling_network.png").exists() else Paragraph("N/A", styles["Body"]),
        ],
        [
            Paragraph("<i>Figure 3.3: 12-Month Rolling $Z$-score timeline flagging $+2.0\\sigma$ tactical surge alert spikes.</i>", styles["FigureCaption"]),
            Paragraph("<i>Figure 3.4: KMeans 2D PCA tactical space & NetworkX bipartite faction-target relational topology.</i>", styles["FigureCaption"]),
        ],
        [
            Paragraph(
                "• Standardized monthly incident velocity $Z_t = (x_t - \\mu_{12}) / \\sigma_{12}$.<br/>"
                "• Surge alerts triggered at $Z \\ge +2.0\\sigma$. Achieves 1.8-month average lead time, beating static thresholds (0.8 months).",
                styles["Body"]
            ),
            Paragraph(
                "• 2D PCA over attack vectors identifies 3 distinct tactical archetypes: <i>Insurgent Guerrillas</i>, <i>Bombing Cells</i>, and <i>Infrastructure Attackers</i>.<br/>"
                "• NetworkX graph maps co-targeting communities and modularity structures.",
                styles["Body"]
            ),
        ],
    ]
    t_row2 = Table(row2_data, colWidths=[col_w, col_w])
    t_row2.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    story.append(t_row2)
    story.append(Spacer(1, 4))

    # Interview Defense Box: Time Series & Spatial
    qa_geo = (
        "<b>Q3: How did you handle the missing year 1993 in the Global Terrorism Database?</b><br/>"
        "<b>Answer:</b> <i>'1993 paper incident records were lost in transit prior to START digitizing the archive. Rather than fabricating data via linear "
        "interpolation—which would distort historical accuracy—we explicitly annotate 1993 as an archival gap across all plots and code a missing-step "
        "handling routine in statsmodels ETS that bridges the gap without biasing historical seasonal weights.'</i><br/>"
        "<b>Q4: Why use Haversine metric instead of standard Euclidean distance for DBSCAN?</b><br/>"
        "<b>Answer:</b> <i>'Euclidean distance treats latitude and longitude as flat coordinates, distorting distances as you move away from the equator. "
        "Haversine computes the true Great-Circle arc distance over spherical Earth ($R=6,371.0088\\text{ km}$), ensuring that an epsilon of 100 km represents "
        "the exact same physical ground radius in Norway as it does in Colombia.'</i>"
    )
    story.append(make_callout("💡 TIME-SERIES & SPATIAL INTERVIEW DEFENSE", qa_geo, styles, border_color="#003366", bg_color="#F0F7FF"))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: PRODUCTION ENGINEERING & TOP 6 INTERVIEW DEFENSE QUESTIONS
    # =========================================================================
    story.append(Paragraph("<b>04 · PRODUCTION ENGINEERING & TOP 6 INTERVIEW QUESTIONS</b>", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1.0, color=colors.HexColor("#003366"), spaceBefore=2, spaceAfter=4))

    story.append(Paragraph(
        "<b>Production Engineering Highlights:</b> Built with enterprise software principles: <b>75 automated tests (87% coverage)</b> via <code>pytest</code>, "
        "strict typing, modular architecture (<code>src/</code> with 15 engines), hardened non-root <code>Dockerfile</code>, and a <b>pure-Pandas natural-language query engine</b> "
        "that enforces rigid JSON specifications with zero dynamic SQL or <code>eval()</code> injection risks.",
        styles["Body"]
    ))
    story.append(Spacer(1, 3))

    # TOP 6 INTERVIEW QUESTIONS & ANSWERS
    top_qa = [
        (
            "1. Walk me through the end-to-end flow of your dashboard.",
            "The system ingests 181k raw GTD rows into a clean 29-column Snappy Parquet file. Offline batch scripts precompute LightGBM models, TreeSHAP explainer matrices, "
            "Holt-Winters forecasts, and rolling Z-score alerts into artifacts/. The Streamlit application boots in < 3 seconds by caching these artifacts, "
            "routing analytical queries across 17 dedicated pages through a pure-Pandas engine."
        ),
        (
            "2. What was the most critical data engineering challenge you solved?",
            "Target data leakage. In conflict databases, casualty counts (`nkill`, `nwound`) and operation outcomes (`success`, `suicide`) are only known *after* an attack occurs. "
            "If included in a pre-attack classifier, models exhibit artificial 99% accuracy but fail completely in real life. I implemented automated test assertions "
            "(`assert_no_leakage`) that mathematically reject any model pipeline referencing post-incident fields."
        ),
        (
            "3. How does your system support an actual military or defense intelligence commander?",
            "Commanders do not need raw data; they need decision support. Our dashboard provides three pillars: (1) Tactical foresight via pre-attack modality probabilities; "
            "(2) Explainability via SHAP waterfalls showing which environmental indicators drove the threat score; and (3) Operational lead time via rolling Z-score surge alerts "
            "that provide an average 1.8-month early-warning window before escalation."
        ),
        (
            "4. How did you validate your models against historical ground truth?",
            "I conducted an in-depth validation case study on the FARC insurgency in Colombia (1980–2017). Haversine DBSCAN accurately isolated their three historical operational axes "
            "(Southwestern Rural, Central Llanos, Arauca corridor). Longitudinal ETS accurately forecasted the sharp de-escalation in violence following the 2016 Havana Peace Accord, "
            "and LightGBM correctly identified their tactical pivot toward infrastructure bombings in the late 1990s."
        ),
        (
            "5. What are the key analytical limitations and known biases of your system?",
            "First, media reporting drift: violence reports post-2000 increase partly due to internet news proliferation rather than raw physical increases. "
            "Second, over 40% of incidents globally lack confirmed organizational attribution. Third, statistical correlation is not military causality; our models "
            "are retrospective decision-support tools, explicitly barred from autonomous kinetic targeting."
        ),
        (
            "6. If you had another six months, what would you engineer next?",
            "Two high-impact extensions: (1) Multi-modal satellite fusion—integrating Synthetic Aperture Radar (SAR) and optical Sentinel-2 imagery to verify physical infrastructure "
            "damage scars; and (2) Dynamic temporal knowledge graphs using GNNs to model faction alliance splits and mergers over time."
        ),
    ]

    for q, a in top_qa:
        story.append(Paragraph(f"<b>{q}</b>", styles["QAQuestion"]))
        story.append(Paragraph(f"<b>Defense:</b> <i>'{a}'</i>", styles["QAAnswer"]))

    story.append(Spacer(1, 2))

    # Candidate Verification & Quick Contact Box
    contact_data = [
        [
            Paragraph(
                "<b>Candidate:</b> Shubham Kumar | B.Tech CSE (7th Sem), National Institute of Technology Delhi (NIT Delhi)<br/>"
                "<b>Def-Space Internship 2026:</b> Bharat Space Education Research Centre (BSERC), New Delhi | Verification No: <code>BSERC-DSI-2026-1417</code><br/>"
                "<b>GitHub:</b> github.com/shubham000111222/AI-Based-Military-Intelligence-and-Threat-Analysis-Dashboard<br/>"
                "<b>Email:</b> yshubham0103@gmail.com | <b>Live Dashboard:</b> <code>streamlit run app.py</code> (Port 8501)",
                styles["TableCell"]
            )
        ]
    ]
    t_contact = Table(contact_data, colWidths=[523])
    t_contact.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ("BOX", (0, 0), (-1, -1), 1.0, colors.HexColor("#003366")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_contact)

    doc.build(story, canvasmaker=InterviewNumberedCanvas)
    print(f"Successfully generated 4-page Executive Interview Brief PDF at: {output_path}")


if __name__ == "__main__":
    out_file = Path("docs/INTERVIEW_PROJECT_BRIEF.pdf")
    build_interview_brief_pdf(out_file)
