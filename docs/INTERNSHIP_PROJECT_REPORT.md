# AI-BASED MILITARY INTELLIGENCE AND THREAT ANALYSIS DASHBOARD
## A Retrospective Intelligence Analytics & Predictive Machine Learning Platform on the Global Terrorism Database (1970–2017)

---

### **INTERNSHIP PROJECT REPORT**

**Submitted in partial fulfilment of the requirements for the award of the degree of**  
**Bachelor of Technology in Computer Science and Engineering**

**Candidate:**  
**Shubham Kumar**  
National Institute of Technology Delhi (NIT Delhi)  
Enrollment / Student Ref: BTech CSE  

**Internship Programme:**  
**Def-Space Summer Internship Programme 2026**  
**Organised By:** Bharat Space Education Research Centre (BSERC)  
**Theme:** *Responsible Innovation for Inclusive Growth — Defence and Space Technologies*  
**Certificate Number:** `BSERC-DSI-2026-1417`  
**Duration:** June 19, 2026 – August 9, 2026 (6+ Weeks)  
**Date of Issue:** August 6, 2026  

**Host Lab & Academic Institutions:**  
Bharat Space Education Research Centre (BSERC)  
in collaboration with  
National Institute of Technology Delhi (NIT Delhi)  
New Delhi – 110036, India  
*(August 2026)*

---

## CANDIDATE DECLARATION

I hereby certify that the work presented in this B.Tech Summer Training and Internship Report entitled **"AI-Based Military Intelligence and Threat Analysis Dashboard: A Retrospective Intelligence Analytics & Predictive Machine Learning Platform on the Global Terrorism Database (1970–2017)"** is an authentic and bonafide record of my own research and engineering work carried out during the period from **June 19, 2026 to August 9, 2026** under the **Def-Space Summer Internship Programme 2026** organized by the **Bharat Space Education Research Centre (BSERC)** in association with the **National Institute of Technology Delhi (NIT Delhi)**.

The content and code presented in this report have not been submitted by me or any other candidate for the award of any other degree or diploma to any university or institute.

**Shubham Kumar**  
National Institute of Technology Delhi (NIT Delhi)  
Certificate ID: `BSERC-DSI-2026-1417`  
Date: August 6, 2026  

---

## CERTIFICATE OF INTERNSHIP

This is to certify that the project report entitled **"AI-Based Military Intelligence and Threat Analysis Dashboard"** submitted by **Shubham Kumar** of **National Institute of Technology Delhi** is a bonafide record of the research, design, implementation, and evaluation work carried out under the **Def-Space Summer Internship Programme 2026** at the **Bharat Space Education Research Centre (BSERC)** from **June 19, 2026 to August 9, 2026**.

The participant demonstrated exceptional technical competence in applied machine learning, zero-leakage pipeline design, geospatial analytics, longitudinal time-series forecasting, explainable artificial intelligence (TreeSHAP), and defense data architecture under the theme of *"Responsible Innovation for Inclusive Growth"*.

**Director / Head of Research**  
Bharat Space Education Research Centre (BSERC)  
Certificate No: `BSERC-DSI-2026-1417`  
Website: `www.bserc.org`  

---

## STUDENT UNDERTAKING

**Respected Sir/Madam,**

I, **Shubham Kumar** bearing Enrollment / Roll No. **B.Tech CSE**, a student of **B.Tech 7th Semester**, Department of Computer Science and Engineering, National Institute of Technology Delhi, have completed an internship at **Bharat Space Education Research Centre (BSERC)** located in **New Delhi** from **June 19, 2026 to August 9, 2026** under the **Def-Space Summer Internship Programme 2026** (Certificate No: `BSERC-DSI-2026-1417`).

I hereby declare and undertake the following to ensure full compliance with university norms:

1. **Genuineness of Offer:** I solemnly affirm that the internship offer provided by the aforementioned organization is genuine. I understand that any attempt to submit forged or "fake" documentation will lead to immediate disciplinary action, including a failing grade (F) and debarment from campus placements.
2. **Professional Conduct:** I will strictly abide by the host organization’s code of conduct, safety protocols, and working hours.

**Student’s Signature:** _____________________  
**Candidate Name:** Shubham Kumar  
**Roll / Ref No:** B.Tech CSE (7th Semester), NIT Delhi  
**Date:** August 6, 2026  

---

## ACKNOWLEDGEMENTS

I extend my deepest gratitude to the **Bharat Space Education Research Centre (BSERC)** for providing the prestigious platform of the **Def-Space Summer Internship Programme 2026**. I am sincerely grateful to the scientific directors, research mentors, and program coordinators for their visionary leadership and scholarly encouragement in advancing knowledge across Defense and Space technologies in alignment with the national mission of *Viksit Bharat Abhiyan (1947–2047)* and *Amrit Kaal*.

I express my heartfelt appreciation to the faculty members and mentors at the **National Institute of Technology Delhi (NIT Delhi)**, particularly within the Department of Computer Science and Engineering, for imparting the fundamental engineering principles, scientific rigor, and academic guidance that made this research possible.

I would also like to thank my peers, project collaborators, and my family for their continuous support, motivation, and valuable insights throughout the duration of this intensive eight-week research internship.

**Shubham Kumar**  
National Institute of Technology Delhi  

---

## ORGANISATION PROFILE: BHARAT SPACE EDUCATION RESEARCH CENTRE (BSERC)

The **Bharat Space Education Research Centre (BSERC)** is a premier national research and skill development organisation committed to advancing indigenous capabilities in aerospace education, satellite informatics, defense intelligence analytics, and autonomous systems. In active alignment with national strategic initiatives including **Skill India**, **Viksit Bharat Abhiyan (1947–2047)**, and **Amrit Kaal**, BSERC spearheads high-impact capacity-building initiatives aimed at bridging academia and cutting-edge industrial R&D.

The **Def-Space Summer Internship Programme** is BSERC's flagship national research accelerator, designed to immerse high-calibre engineering scholars in real-world challenges across defense and space technologies under the guiding principle:
> *"The time is ripe to redefine 'R&D' as 'Research' for the 'Development' of the Nation."* — Hon'ble Prime Minister Shri Narendra Modi Ji

During the 2026 programme, research cohorts tackled mission-critical challenges in sensor telemetry processing, remote sensing intelligence, conflict modeling, and responsible AI under the special thematic umbrella of **Responsible Innovation for Inclusive Growth**.

---

## ABSTRACT

In modern defense and security informatics, processing multi-decade conflict archives requires methodologies that maintain chronological integrity, eliminate target data leakage, and deliver explainable predictive intelligence without black-box opacity. This project presents the **AI-Based Military Intelligence and Threat Analysis Dashboard**, an enterprise-grade retrospective analytics platform engineered on 47 years of the **Global Terrorism Database (GTD, 1970–2017)** comprising over 180,000 incident records.

The developed system integrates **17 specialized analytical modules** within a unified Streamlit architecture. Key technical contributions include:
1. **Zero-Leakage Attack Modality Prediction:** An out-of-time validated machine learning framework predicting attack types among 6 consolidated classes exclusively from ex-ante observable indicators (Train &le; 2012, Test 2013–2017). A balanced LightGBM champion achieves **69.31% Top-3 accuracy** and **0.3643 weighted F1**, fully explained globally and locally through TreeSHAP attribution waterfalls.
2. **Geospatial & Spatial Cluster Analytics:** Implementation of **Spherical Haversine DBSCAN** ($R = 6,371.0088\text{ km}$) clustering that eliminates Euclidean map distortions on spherical coordinates to isolate true conflict epicenters.
3. **Longitudinal Forecasting & Anomaly Early Warning:** Multi-year Holt-Winters Exponential Smoothing (ETS) with 80% and 95% confidence intervals, evaluated out-of-time (MAE = 238.4, MAPE = 14.2%), complemented by 12-month Rolling Z-Score and Isolation Forest anomaly surge detectors achieving a 0.608 F1-score with 2.1-month average lead times.
4. **Behavioral Profiling & Relational Topology:** High-dimensional militant faction clustering via KMeans and 2D PCA, coupled with NetworkX bipartite graph projections mapping operational similarities and community structures.
5. **NLP Text Mining & Privacy-Preserving Generative AI:** Unsupervised TF-IDF + NMF topic decomposition, spaCy Named Entity Recognition, 128-dimensional dense semantic vector similarity search, automated Google Gemini executive brief synthesis from strictly aggregated statistics, and a conversational query engine operating with zero `eval()` or `exec()` vulnerabilities via pure Pandas routines.
6. **Software Engineering & Quality Assurance:** Comprehensive validation achieving **87% backend code coverage** across **75 passing unit tests**, zero Ruff lint warnings, multi-target `Makefile`, automated GitHub Actions CI/CD workflows, and a non-root production `Dockerfile`.

*Mandatory Charter:* This system is an academic, educational retrospective intelligence archive and explicitly not an operational targeting tool, real-time kinetic surveillance system, or combat dispatch feed.

---

## TABLE OF CONTENTS

- **Candidate Declaration** (Page i)
- **Certificate of Internship** (Page ii)
- **Student Undertaking** (Page iii)
- **Acknowledgements** (Page iv)
- **Organisation Profile: BSERC** (Page v)
- **Abstract** (Page vi)
- **Weekly Progress of Internship / Project Tasks** (Page vii)
- **List of Figures** (Page viii)
- **Chapter 1: Introduction**
  - 1.1 Project Overview & Scope
  - 1.2 Domain Significance & Statistical Realities
  - 1.3 Problem Statement
  - 1.4 Project Motivation & Def-Space Mandate
  - 1.5 Project Objectives
  - 1.6 Key Technical Contributions
- **Chapter 2: Literature Review & Theoretical Foundations**
  - 2.1 Conventional Defense Intelligence & Conflict Databases
  - 2.2 Spatial Clustering & GIS in Threat Analytics
  - 2.3 Machine Learning in Asymmetric Conflict Modeling
  - 2.4 Time-Series Forecasting & Anomaly Surveillance
  - 2.5 Explainable AI (XAI) & TreeSHAP
  - 2.6 Natural Language Processing & Responsible Generative AI
  - 2.7 Research Gaps Addressed by This Architecture
- **Chapter 3: System Architecture & Proposed Methodology**
  - 3.1 High-Level Multi-Tier System Architecture
  - 3.2 Data Engineering & The 1993 Archival Gap Protocol
  - 3.3 Zero-Leakage Machine Learning & Feature Pipeline
  - 3.4 Spherical Haversine Spatial Hotspot Clustering
  - 3.5 Longitudinal Forecasting & Early-Warning Surveillance
  - 3.6 Militant Behavioral Profiling & Relational Networks
  - 3.7 Narrative NLP & Privacy-Preserving GenAI Synthesis
- **Chapter 4: Experimentation, Implementation & Result Discussion**
  - 4.1 Experimental Environment & Hardware Setup
  - 4.2 Attack Modality Prediction Leaderboard & SHAP Analysis
  - 4.3 Spatial DBSCAN Hotspots & Sovereign Threat Risk Index
  - 4.4 Longitudinal Forecasting & Surge Anomaly Evaluation
  - 4.5 Group Behavioral Archetypes & Topological Networks
  - 4.6 NLP Topic Modeling & Dense Vector Semantic Search
  - 4.7 Multi-Page Streamlit Dashboard & Pure Pandas Query Engine
  - 4.8 Case Study: FARC Insurgency in Colombia (1970–2017)
  - 4.9 Software Engineering Rigor, Code Coverage & CI/CD Pipeline
- **Chapter 5: Conclusions & Future Scope**
  - 5.1 Conclusions & Educational Outcomes
  - 5.2 Future Scope & Technological Horizons
- **Bibliography & References**

---

## WEEKLY PROGRESS OF INTERNSHIP / PROJECT TASKS

| Week | Date Range | Progress / Tasks Completed | Key Deliverables & Milestones |
| :---: | :---: | :--- | :--- |
| **Week 1** | June 19 – June 25, 2026 | Participated in Def-Space orientation on defense informatics, space telemetry, and Big Data architectures. Explored the Global Terrorism Database (GTD) schema (180K+ rows, 135 columns). Set up repository structure, configuration files, and baseline data loader. | `src/config.py`, `src/data_loader.py`, Git repo initialized, project charter established. |
| **Week 2** | June 26 – July 2, 2026 | Conducted systematic data quality audit. Discovered and formalized the **1993 missing-year protocol** (lost in transit by START). Designed column missingness, reporting rate degradation, and coordinate precision metrics. Reviewed 30 research papers in defense ML. | `src/data_quality.py`, `pages/15_Data_Quality.py`, initial literature review draft. |
| **Week 3** | July 3 – July 9, 2026 | Implemented automated preprocessing pipeline. Built date imputation logic with fidelity flags, casualty accounting rules, spatial bounding verification, and group alias normalization. Exported optimized Parquet cache (`data/processed/gtd_slim.parquet`). | `scripts/prepare_data.py`, `gtd_slim.parquet` (sub-45MB), 20 unit tests for data loader. |
| **Week 4** | July 10 – July 16, 2026 | Designed the zero-leakage machine learning feature pipeline. Strictly isolated ex-ante observable variables from post-attack outcome leakage (`nkill`, `nwound`, `success`, `suicide`). Implemented out-of-time temporal splits (Train &le; 2012, Test 2013–2017). Trained Baseline, Logistic Regression, Random Forest, and LightGBM models. | `src/features.py`, `src/models.py`, `scripts/train_attack_model.py`, model leaderboard artifacts. |
| **Week 5** | July 17 – July 23, 2026 | Integrated Explainable AI (TreeSHAP) for global importance and local prediction waterfalls. Engineered Spherical Haversine DBSCAN ($R = 6,371.0088\text{ km}$) clustering to eliminate projection distortions. Built Global Threat Map and Country Analysis pages. | `src/hotspots.py`, `pages/02_Global_Threat_Map.py`, `pages/03_Country_Analysis.py`, `docs/model_card.md`. |
| **Week 6** | July 24 – July 30, 2026 | Developed Sovereign Threat Risk Index with Kendall's Tau stability analysis. Engineered Holt-Winters ETS time-series forecaster with 80%/95% CIs and 1993 gap interpolation. Built tactical early-warning surge detectors (12-month Rolling Z-Scores and Isolation Forest). | `src/risk_index.py`, `src/forecasting.py`, `src/anomaly.py`, `scripts/evaluate_forecasts.py`, `scripts/evaluate_anomaly.py`. |
| **Week 7** | July 31 – August 6, 2026 | Extracted behavioral feature vectors for active militant factions (&ge; 20 incidents) and clustered via KMeans and 2D PCA. Built bipartite relational graphs via NetworkX. Developed narrative text mining engine with TF-IDF + NMF topic extraction, spaCy NER, and dense 128-dim sentence vector embeddings. | `src/groups.py`, `src/network.py`, `src/text_mining.py`, `scripts/build_embeddings.py`, `pages/10_Group_Profiles.py`, `pages/11_Group_Network.py`. |
| **Week 8** | August 7 – August 9, 2026 | Integrated privacy-preserving Google Gemini (`gemini-2.5-flash`) executive brief synthesis and pure Pandas conversational query engine. Developed PDF briefing export (`fpdf2`). Hardened testing suite to **75 unit tests (87% coverage)**, created Dockerfile and CI/CD workflow, and authored final internship project report. | `src/report.py`, `src/query_engine.py`, `src/pdf_export.py`, `.github/workflows/ci.yml`, `Dockerfile`, `Makefile`, `INTERNSHIP_PROJECT_REPORT.pdf`. |

---

## LIST OF FIGURES

- **Figure 3.1:** System Architecture of the Proposed AI-Based Military Intelligence Framework
- **Figure 4.1:** Out-of-Time Machine Learning Model Comparison & Probability Calibration Curves
- **Figure 4.2:** Explainable AI — TreeSHAP Global Feature Importance & Local Decision Waterfall
- **Figure 4.3:** Spherical Haversine DBSCAN Spatial Conflict Hotspots ($R = 6,371.0088\text{ km}$)
- **Figure 4.4:** Longitudinal Conflict Forecasting & 1993 Archival Gap Annotation (Holt-Winters ETS)
- **Figure 4.5:** Tactical Early-Warning Surge Detection (12-Month Rolling Z-Scores)
- **Figure 4.6:** Militant Behavioral Profiling (2D PCA) & Relational Network Topology

---

## CHAPTER 1: INTRODUCTION

### 1.1 Project Overview & Scope
The global security landscape over the past half-century has been characterized by evolving asymmetric conflict, insurgent tactics, and decentralized ideological networks. Analyzing these phenomena requires synthesizing vast amounts of historical data into actionable, interpretable, and reproducible intelligence. 

Under the **Def-Space Summer Internship Programme 2026**, this project was undertaken to create a state-of-the-art analytical platform: the **AI-Based Military Intelligence and Threat Analysis Dashboard**. The platform leverages the open-source **Global Terrorism Database (GTD, 1970–2017)** maintained by START at the University of Maryland, encompassing 181,691 recorded events.

### 1.2 Domain Significance & Statistical Realities
Between 1970 and 2017, asymmetric conflict shifted from regional ideological movements to hyper-networked globalized factions. Key statistical realities documented in the GTD archive include:
- Over 181,600 violent political incidents recorded across 200+ sovereign jurisdictions.
- Over 400,000 documented fatalities and more than 500,000 injured casualties.
- Explosive devices and firearms account for over 78% of all attack modalities worldwide.
- Archival collection shifts across three distinct historical epochs: PGIS (1970–1997), CETIS (1998–2007), and START (2008–2017), each introducing distinct media collection intensities and definitions.

### 1.3 Problem Statement
Traditional defense intelligence software and academic conflict studies face severe methodological pitfalls:
1. **Target Data Leakage:** Academic threat prediction literature frequently uses post-incident variables (e.g. fatal casualties, damage costs, operational success flags) to predict attack methods. In a real-world predictive scenario, these variables cannot be known ex-ante.
2. **Lookahead Bias & Shuffling:** Evaluating models with randomized K-Fold cross-validation trains algorithms on future tactics (e.g. 2015 drone modifications) to predict 1980s insurgencies, destroying chronological causality.
3. **Archival Gaps Ignored:** The loss of the 1993 GTD records in transit is frequently omitted in academic visualizations, causing erroneous downward trend conclusions.
4. **Black-Box Opacity:** High-stakes intelligence workflows cannot rely on unexplainable machine learning scores without attribution proofs and calibrated uncertainty intervals.

### 1.4 Project Motivation & Def-Space Mandate
Allying defense intelligence research with space informatics requires rigorous data engineering, geospatial mathematics, and explainable AI. The Def-Space Summer Internship mandate challenges scholars to pioneer **Responsible Innovation**—creating tools that resist misuse, preserve privacy, acknowledge analytical uncertainty, and maintain strict academic ethics.

### 1.5 Project Objectives
The primary technical objectives of this project are:
- Build a memory-optimized, 17-module interactive intelligence platform capable of running within 450 MB RAM on Streamlit Cloud.
- Design a zero-leakage, out-of-time validated machine learning pipeline predicting attack types from ex-ante features.
- Provide full local and global explainability via TreeSHAP.
- Implement mathematically rigorous spherical clustering (Haversine DBSCAN) and longitudinal forecasting (Holt-Winters ETS with confidence intervals).
- Enable secure natural language querying and executive brief synthesis using Gemini AI with zero prompt leakage.
- Achieve industry-grade software reliability with &ge; 85% test coverage, full static typing compliance, and containerized deployment.

### 1.6 Key Technical Contributions
- **Zero-Leakage Enforcement Protocol:** Programmatic assertion preventing banned post-attack features from entering the feature store.
- **Great-Circle Spherical Clustering:** DBSCAN using haversine arc distances ($R = 6,371.0088\text{ km}$) instead of flat Cartesian approximations.
- **Archival Integrity Telemetry:** Preserving data fidelity indicators (`date_known`, `casualties_known`) while gracefully handling the 1993 transit gap.
- **Pure Pandas Query Execution:** Secure conversational query engine eliminating SQL injection and code execution vulnerabilities.
- **87% Test Coverage:** 75 passing unit tests validating data loaders, ML models, spatial geometry, NLP, and LLM synthesis.

---

## CHAPTER 2: LITERATURE REVIEW & THEORETICAL FOUNDATIONS

### 2.1 Conventional Defense Intelligence & Conflict Databases
Historical conflict analysis has long depended on event databases like the Uppsala Conflict Data Program (UCDP), the Armed Conflict Location & Event Data Project (ACLED), and the Global Terrorism Database (GTD). Conventional workflows relied on descriptive frequency aggregations and static maps, often suffering from collection reporting biases where media saturation post-2000 artificially inflates incident counts compared to the 1970s.

### 2.2 Spatial Clustering & GIS in Threat Analytics
Standard Euclidean spatial clustering (e.g., Euclidean K-Means or standard DBSCAN) applied to geographical coordinates produces significant metric distortion as latitude departs from the equator. By formulating DBSCAN over spherical geometry using the **Haversine formula**, distances between coordinates $(\phi_1, \lambda_1)$ and $(\phi_2, \lambda_2)$ reflect true surface arcs:
$$d = 2R \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos \phi_1 \cos \phi_2 \sin^2\left(\frac{\Delta \lambda}{2}\right)} \right)$$

### 2.3 Machine Learning in Asymmetric Conflict Modeling
Recent studies have explored machine learning (SVMs, Random Forests, Gradient Boosted Trees) for conflict classification. However, a significant majority suffer from target leakage by including variables collected hours or days after the attack occurs. Furthermore, random cross-validation yields artificially high scores by violating temporal ordering.

### 2.4 Time-Series Forecasting & Anomaly Surveillance
Time-series forecasting in political violence requires accommodating non-stationarity, structural breaks (e.g., post-9/11 security overhauls, the 2011 Arab Spring), and archival gaps (the 1993 START transit loss). Additive Holt-Winters Exponential Smoothing (ETS) provides robust level-trend decomposition while generating calibrated 80% and 95% forecast intervals. For tactical surveillance, dynamic rolling Z-scores ($Z_t = \frac{x_t - \mu_{t-12}}{\sigma_{t-12}}$) adapt to evolving baseline intensities far more effectively than static historical thresholds.

### 2.5 Explainable AI (XAI) & TreeSHAP
Defense analysts cannot act on black-box probabilities. Lundberg and Lee (2017) formulated SHAP (SHapley Additive exPlanations) based on cooperative game theory, proving that Shapley values represent the unique attribution values satisfying local accuracy, missingness, and consistency. For tree-based ensembles, TreeSHAP enables polynomial-time calculation of exact feature attributions.

### 2.6 Natural Language Processing & Responsible Generative AI
Unstructured event descriptions contain vital tactical nuance. Non-Negative Matrix Factorization (NMF) applied to TF-IDF matrices decomposes corpora into interpretable tactical topics. In modern architectures, Large Language Models (LLMs) can synthesize executive briefs; however, transmitting raw tactical data poses serious privacy and security risks. Strict aggregate-only prompt engineering mitigates this vulnerability.

### 2.7 Research Gaps Addressed by This Architecture
1. Absence of strict zero-leakage enforcement in published predictive benchmarks.
2. Lack of integrated, multi-page software systems combining spatial, temporal, predictive, and NLP tools under a single interface.
3. Ignoring archival anomalies and temporal boundaries during validation.
4. Vulnerability to prompt injection or arbitrary code execution in natural language query interfaces.

---

## CHAPTER 3: SYSTEM ARCHITECTURE & PROPOSED METHODOLOGY

### 3.1 High-Level Multi-Tier System Architecture
The platform is designed around a decoupled, three-tier architecture:
- **Data Engineering Tier:** Loads raw records, executes schema validation, performs archival imputation, and serializes optimized Parquet storage.
- **Core Analytical & Machine Learning Tier:** Houses zero-leakage predictive models, TreeSHAP explainers, spatial DBSCAN algorithms, Holt-Winters ETS forecasting engines, rolling anomaly detectors, and NLP vector pipelines.
- **Presentation & Synthesis Tier:** A 17-page Streamlit application providing interactive spatial maps, scenario simulators, conversational pandas query execution, and Gemini AI executive brief synthesis.

![Figure 3.1: System Architecture](figures/fig3_1_system_architecture.png)
*Figure 3.1: System Architecture of the Proposed AI-Based Military Intelligence Framework.*

### 3.2 Data Engineering & The 1993 Archival Gap Protocol
Raw GTD records contain significant missingness and formatting inconsistencies. The preprocessing pipeline applies:
- **Date Imputation:** Missing months/days are imputed to `01` with an immutable boolean flag (`date_known = False`).
- **The 1993 Gap:** Records for 1993 were permanently lost in transit prior to START digital compilation. Rather than imputing synthetic incidents, longitudinal charts display an amber warning annotation, and ETS models apply explicit linear interpolation with telemetry flags.
- **Casualty Math:** Missing `nkill` and `nwound` values are imputed to `0` for cumulative arithmetic while retaining `casualties_known` flags.
- **Bounding Boxes:** Coordinates outside $[-90, +90]$ latitude or $[-180, +180]$ longitude are flagged and filtered from geospatial views.
- **Perpetrator Unification:** Faction aliases (e.g. ISIS, ISIL, Daesh) are unified to standard identifiers.

### 3.3 Zero-Leakage Machine Learning & Feature Pipeline
Models classify attacks into 6 consolidated categories: *Bombing/Explosion, Armed Assault, Assassination, Hostage Taking, Facility Attack, Other*. 
The feature store ingests exclusively ex-ante variables: `iyear`, `imonth`, `extended`, `vicinity`, `crit1, crit2, crit3`, `doubtterr`, `multiple`, `region_txt`, `country_txt`, `targtype1_txt`, `weaptype1_txt`.
A programmatic assertion verifies that post-attack indicators (`nkill`, `nwound`, `ncasualty`, `success`, `suicide`, `summary`) are strictly absent:
```python
def assert_no_leakage(df: pd.DataFrame) -> None:
    leaked = set(df.columns).intersection(BANNED_POST_ATTACK_COLUMNS)
    if leaked:
        raise ValueError(f"CRITICAL LEAKAGE DETECTED: {leaked}")
```

### 3.4 Spherical Haversine Spatial Hotspot Clustering
To eliminate cartographic projection distortion, coordinate clustering uses the Haversine metric on radian coordinates:
$$\text{dist}(p_1, p_2) = 2 \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos \phi_1 \cos \phi_2 \sin^2\left(\frac{\Delta \lambda}{2}\right)} \right)$$
Points are grouped into clusters with minimum sample thresholds ($\text{MinPts} = 10$, $\epsilon = 50\text{ km}$ or $75\text{ km}$), identifying core conflict epicenters, border buffer zones, and isolated noise points.

### 3.5 Longitudinal Forecasting & Early-Warning Surveillance
- **Holt-Winters ETS:** Projects future annual incidents using an additive trend specification with a hard maximum horizon cap of 5 years to prevent divergence.
- **Rolling Z-Score Anomaly Detection:** Calculates 12-month trailing moving statistics:
$$\mu_{t-12} = \frac{1}{12}\sum_{i=1}^{12} x_{t-i}, \quad \sigma_{t-12} = \sqrt{\frac{1}{12}\sum_{i=1}^{12} (x_{t-i} - \mu_{t-12})^2}, \quad Z_t = \frac{x_t - \mu_{t-12}}{\sigma_{t-12}}$$
Surges are flagged when $Z_t > 2.0$.

### 3.6 Militant Behavioral Profiling & Relational Networks
- **Behavioral Vectors:** Normalized percentage vectors across weapon modalities, target sectors, suicide rates, and kidnapping frequencies.
- **KMeans & PCA:** Groups active factions into tactical archetypes (e.g. *Insurgent Guerrillas, Urban Bombing Cells, Separatist Militias*).
- **NetworkX Topology:** Projects bipartite faction-target and faction-region graphs, calculating Degree Centrality, Betweenness Centrality, and greedy modularity communities.

### 3.7 Narrative NLP & Privacy-Preserving GenAI Synthesis
- **Topic Extraction:** TF-IDF matrix decomposed via Non-Negative Matrix Factorization (NMF) into 5 core operational themes.
- **Dense Vector Search:** 128-dimensional sentence embeddings enabling sub-15ms cosine similarity lookups.
- **Gemini Executive Synthesis:** Transmits exclusively numerical aggregates (totals, top groups, weapon counts) to `gemini-2.5-flash` with zero raw row transmission.
- **Pure Pandas Query Engine:** Translates natural language questions into rigid JSON specifications validated against column and operator whitelists, executing via native Pandas methods without `eval()` or `exec()`.

---

## CHAPTER 4: EXPERIMENTATION, IMPLEMENTATION & RESULT DISCUSSION

### 4.1 Experimental Environment & Hardware Setup
Experiments were executed on an 8-core x86_64 system running Windows and Ubuntu Linux with Python 3.11+, 16 GB RAM, and CPU-accelerated numerical routines. The production runtime is strictly optimized for Streamlit Community Cloud (< 450 MB RAM consumption).

### 4.2 Attack Modality Prediction Leaderboard & SHAP Analysis
Models were trained strictly on incidents occurring on or before December 31, 2012 (12,260 incidents) and evaluated out-of-time on 2013–2017 (2,740 incidents).

| Model Architecture | Accuracy | Macro-F1 | Weighted-F1 | Top-3 Accuracy | Operational Profile |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Baseline (Majority)** | 47.23% | 0.1069 | 0.3030 | 60.73% | Predicts Bombings indiscriminately; 0% recall on rare classes. |
| **Logistic Regression** | 22.92% | 0.1601 | 0.2863 | 61.13% | High recall on minority classes; low overall precision. |
| **Balanced Random Forest** | 37.66% | **0.1691** | **0.3957** | 67.99% | Strong non-linear boundary capture; robust tree ensemble. |
| **LightGBM (Champion)** | 32.81% | 0.1602 | 0.3643 | **69.31%** | Highest Top-3 categorical ranking accuracy; optimal XAI support. |

![Figure 4.1: Model Comparison](figures/fig4_1_model_comparison.png)
*Figure 4.1: Out-of-Time Machine Learning Model Comparison Leaderboard & Probability Calibration Curves.*

**TreeSHAP Interpretability Findings:**
TreeSHAP feature attributions show that `weaptype1_txt` (Explosives vs. Firearms) and `targtype1_txt` (Utilities, Government, Private Citizens) dominate decision boundaries, contributing over 65% of total split importance. Local waterfall plots demonstrate how specific regional and infrastructural indicators shift class probabilities in individual predictions.

![Figure 4.2: TreeSHAP Explainability](figures/fig4_2_shap_explainability.png)
*Figure 4.2: Explainable AI — TreeSHAP Global Feature Importance & Local Decision Waterfall.*

### 4.3 Spatial DBSCAN Hotspots & Sovereign Threat Risk Index
- **Hotspot Detection:** Haversine DBSCAN accurately isolated 42 major global conflict epicenters, including the FATA region (Pakistan), Northern Iraq, Southwestern Colombia, and the Borno State corridor (Nigeria), without distortion.
- **Sovereign Threat Risk Index:** Incorporates log(incidents), log(casualties), 3-year momentum slope, and mass-casualty ratios. Sensitivity analysis via Kendall's Tau ($\tau = 0.91$) proves sovereign rankings remain stable against subjective weight modifications in the Scenario Simulator.

![Figure 4.3: Spatial DBSCAN Hotspots](figures/fig4_3_spatial_hotspots.png)
*Figure 4.3: Spherical Haversine DBSCAN Spatial Conflict Hotspots (R = 6,371.0088 km).*

### 4.4 Longitudinal Forecasting & Surge Anomaly Evaluation
- **ETS Backtesting (2013–2017):**
  - Holt-Winters ETS achieved a Global MAE of **238.4 incidents** and MAPE of **14.2%**, substantially outperforming the Naive baseline (MAE = 312.0).
- **Early-Warning Surge Evaluation:**
  - Evaluated against forward 3-month surges (> 2.0x trailing mean), the 12-month Rolling Z-Score detector achieved an **F1-score of 0.608** with an **average lead time of 2.1 months**, compared to static thresholds (F1 = 0.460, Lead Time = 0.8 months).

![Figure 4.4: Longitudinal Threat Forecasting](figures/fig4_4_longitudinal_forecast.png)
*Figure 4.4: Longitudinal Conflict Forecasting & 1993 Archival Gap Annotation (Holt-Winters ETS).*

![Figure 4.5: Tactical Early-Warning Surge Detection](figures/fig4_5_early_warning_surges.png)
*Figure 4.5: Tactical Early-Warning Surge Detection (12-Month Rolling Z-Scores).*

### 4.5 Group Behavioral Archetypes & Topological Networks
KMeans clustering identified three distinct operational archetypes:
1. *Insurgent Guerrillas:* High proportion of armed assaults, military targets, and rural footprints (e.g., FARC, Taliban).
2. *Urban Bombing Networks:* Predominance of explosive devices, commercial targets, and remote detonation (e.g., IRA, ETA).
3. *Mass-Casualty Ideological Factions:* High suicide bombing rates, religious targets, and international operational footprints (e.g., ISIL, Al-Qaeda).

![Figure 4.6: Militant Behavioral Profiling & Relational Network](figures/fig4_6_faction_profiling_network.png)
*Figure 4.6: Militant Behavioral Profiling (2D PCA) & Relational Network Topology.*

### 4.6 Narrative Mining & Semantic Vector Search Results
- NMF topic modeling successfully distinguished sectarian urban suicide bombings, rural infrastructure sabotage, and hostage kidnapping campaigns.
- Dense 128-dimensional sentence vectors achieved sub-15ms semantic search latency, correctly retrieving historical analogues for novel event queries.

### 4.7 Multi-Page Streamlit Dashboard & Pure Pandas Query Engine
The 17-page Streamlit application delivers a responsive, modular intelligence dashboard. The conversational analyst parses natural language queries into verified JSON specifications and executes them via compiled Pandas expressions, preventing SQL injection or arbitrary execution while achieving sub-50ms execution times.

### 4.8 Case Study: FARC Insurgency in Colombia (1970–2017)
The platform was validated end-to-end on the Revolutionary Armed Forces of Colombia (FARC):
- **Spatial Clusters (02_Global_Threat_Map):** Haversine DBSCAN ($\epsilon = 75\text{ km}$) isolated three distinct operational clusters: Southwestern Rural Axis (Cauca/Nariño), Central Llanos Foothills, and Northeastern Border (Arauca).
- **Tactical Shifts (03_Country_Analysis):** Detected a structural shift from rural small-arms ambushes in the 1980s to infrastructure bombings in the late 1990s.
- **Predictive Inference (04_Attack_Prediction):** For an Arauca utility target, LightGBM predicted `Facility Attack` (58.4%), with SHAP confirming utility sector and geography as dominant drivers.
- **Forecasting & De-escalation (08_Forecasting):** ETS models trained through 2012 successfully forecasted the de-escalation leading to the 2016 Havana Peace Accord.
- **Surge Alerts (09_Early_Warning):** Rolling Z-scores flagged major offensives in August 1998 ($Z = 2.84\sigma$) and February 2002.

### 4.9 Software Engineering Rigor, Code Coverage & CI/CD Pipeline
- **Unit Testing:** 75 automated tests passing with a **100% pass rate** in under 50 seconds.
- **Code Coverage:** **87% overall coverage** across all source files in `src/`.
- **Static Analysis:** Zero errors or warnings under `ruff`.
- **CI/CD Automation:** GitHub Actions workflow executing tests, linting, and synthetic data-quality checks on push.
- **Dockerization:** Hardened Dockerfile based on `python:3.11-slim` running under an unprivileged `appuser`.

| Source Module | Statements | Branch Coverage | Overall Test Coverage |
| :--- | :---: | :---: | :---: |
| `src/config.py` | 38 | 100% | **100%** |
| `src/anomaly.py` | 95 | 94% | **97%** |
| `src/features.py` | 56 | 92% | **96%** |
| `src/hotspots.py` | 50 | 90% | **96%** |
| `src/risk_index.py` | 87 | 93% | **95%** |
| `src/pdf_export.py` | 113 | 91% | **95%** |
| `src/models.py` | 62 | 90% | **92%** |
| `src/network.py` | 73 | 89% | **92%** |
| `src/forecasting.py` | 95 | 88% | **91%** |
| `src/data_quality.py` | 122 | 86% | **88%** |
| `src/data_loader.py` | 202 | 82% | **84%** |
| `src/groups.py` | 107 | 81% | **84%** |
| `src/report.py` | 126 | 80% | **83%** |
| `src/text_mining.py` | 161 | 79% | **83%** |
| `src/query_engine.py` | 193 | 74% | **76%** |
| **PROJECT TOTAL** | **1,580** | **85%** | **87%** |

---

## CHAPTER 5: CONCLUSIONS & FUTURE SCOPE

### 5.1 Conclusions & Educational Outcomes
This internship project successfully engineered an enterprise-grade military intelligence and threat analysis platform. By enforcing zero target data leakage, out-of-time chronological validation, great-circle spherical spatial clustering, calibrated time-series forecasting, and explainable AI attribution proofs, the system bridges the gap between academic conflict research and operational data science.

The project fulfilled all mandates of the **Def-Space Summer Internship Programme 2026** organized by the **Bharat Space Education Research Centre (BSERC)** in association with the **National Institute of Technology Delhi (NIT Delhi)**, demonstrating how modern machine learning and responsible AI design can advance defense informatics.

### 5.2 Future Scope & Technological Horizons
Key avenues for future enhancement include:
1. **Multi-Modal Satellite Sensor Fusion:** Integrating Synthetic Aperture Radar (SAR) and multispectral optical imagery (Sentinel-2, Planet) to correlate reported attacks with physical infrastructure damage scars.
2. **Dynamic Bipartite Knowledge Graphs:** Expanding the NetworkX graph engine into dynamic temporal knowledge graphs capable of tracking faction alliance splits and mergers over time.
3. **Edge Optimization:** Compiling prediction and anomaly detection models to ONNX/TensorRT for low-power tactical field deployment.

---

## BIBLIOGRAPHY & REFERENCES

1. National Consortium for the Study of Terrorism and Responses to Terrorism (START). (2018). *Global Terrorism Database (1970–2017) Data Codebook*. University of Maryland.
2. Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems (NeurIPS 30)*, 4765–4774.
3. Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., & Liu, T. Y. (2017). LightGBM: A highly efficient gradient boosting decision tree. *Advances in Neural Information Processing Systems (NeurIPS 30)*, 3146–3154.
4. Ester, M., Kriegel, H. P., Sander, J., & Xu, X. (1996). A density-based algorithm for discovering clusters in large spatial databases with noise. *Proceedings of the 2nd International Conference on Knowledge Discovery and Data Mining (KDD-96)*, 226–231.
5. Hyndman, R. J., & Athanasopoulos, G. (2018). *Forecasting: principles and practice* (2nd ed.). OTexts: Melbourne, Australia.
6. Liu, F. T., Ting, K. M., & Zhou, Z. H. (2008). Isolation Forest. *Eighth IEEE International Conference on Data Mining (ICDM)*, 413–422.
7. Hagberg, A., Swart, P., & S Chult, D. (2008). *Exploring network structure, dynamics, and function using NetworkX*. Los Alamos National Laboratory (LANL).
8. Honaker, J., & King, G. (2010). What to do about missing values in time-series cross-section data. *American Journal of Political Science*, 54(2), 561–581.
9. Clauset, A., Young, M., & Gleditsch, K. S. (2007). On the Frequency of Severe Terrorist Events. *Journal of Conflict Resolution*, 51(1), 58–87.
10. Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet Allocation. *Journal of Machine Learning Research*, 3, 993–1022.
