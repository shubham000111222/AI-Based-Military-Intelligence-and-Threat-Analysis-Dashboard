# Executive & Technical Presentation Slide Deck Outline

**Project Title:** AI-Based Military Intelligence & Threat Analysis Dashboard  
**Subtitle:** A Historical Retrospective Intelligence Analytics & Predictive Machine Learning Platform on the Global Terrorism Database (1970–2017)  
**Presenter:** Senior Machine Learning Engineer / Intelligence Systems Architect  
**Duration:** 25–30 Minutes  

---

## Slide 1: Title & Executive Scope
- **Headline:** AI-Based Military Intelligence & Threat Analysis Dashboard
- **Tagline:** Turning Decades of Unstructured Historical Conflict Data into Actionable Strategic Retrospectives.
- **Presenter Information:** Senior ML Engineer & Systems Architect.
- **Mandatory Ethical Framing:** 
  - Strictly an educational, historical research platform.
  - Retrospective statistical modeling on open-source archives (1970–2017).
  - Explicitly NOT an operational targeting tool, live surveillance feed, or tactical deployment system.

---

## Slide 2: The Intelligence Challenge
- **Data Complexity:** Over 180,000 historical global incident records across 47 years with heterogeneous reporting fidelity.
- **The Analytical Hurdle:** Transitioning from passive tabular querying to predictive risk indexing, tactical anomaly detection, and longitudinal forecasting.
- **Common Pitfalls in Threat Modeling:**
  - Target data leakage (using post-attack outcomes to predict attack modality).
  - Random train/test splits violating temporal causality.
  - Ignoring systemic archival collection gaps and historical media biases.

---

## Slide 3: The GTD Data Foundation & The 1993 Archival Gap
- **Dataset:** Global Terrorism Database (GTD) compiled by the National Consortium for the Study of Terrorism and Responses to Terrorism (START).
- **Core Coverage:** 1970 through 2017 across 200+ sovereign nations.
- **The Critical 1993 Archival Gap:**
  - Original paper records for 1993 were lost in physical transit prior to digital centralization.
  - Never fabricate or silently drop: every time chart in the dashboard annotates the 1993 collection gap with a distinct amber visual marker.
  - Time-series forecasters apply linear interpolation with explicit flag tracking to maintain structural continuity.

---

## Slide 4: System Architecture & Zero-Leakage Pipeline
- **Architectural Workflow:**
  - Ingestion -> Hygiene & Imputation -> Feature Extraction -> Offline Training -> Serialized Artifacts -> Streamlit Multipage Engine.
- **Sub-1 GB Memory Design:**
  - Columnar Snappy Parquet caching via `st.cache_data`.
  - Offline precomputations for LightGBM models, SHAP explainers, ETS backtests, and sentence embeddings.
  - Sub-second UI response times on constrained Streamlit Community Cloud instances.
- **Continuous Integration:** Automated GitHub Actions pipeline verifying linting (Ruff), test coverage (87% with pytest-cov), and synthetic smoke testing.

---

## Slide 5: Geospatial Threat Intelligence & Spherical DBSCAN
- **Interactive Geospatial Center:** Global Plotly scatter choropleth with multi-dimensional filtering and annual progression animation.
- **Spherical Haversine DBSCAN Hotspot Engine:**
  - Standard Euclidean clustering distorts geographical distances across latitudes.
  - Converts latitude/longitude degrees to radians and applies spherical Haversine metric with Earth radius $R = 6371.0088\text{ km}$.
  - Identifies dense spatial attack clusters, centroid coordinates, and casualty impact radii.

---

## Slide 6: Zero-Leakage Attack Type Prediction
- **The Machine Learning Task:** Multi-class classification predicting attack modality (`attacktype1_txt`) among 6 consolidated classes.
- **Strict Leakage Prevention:**
  - Predicts using ONLY pre-attack indicators: Year, Region, Country, Province, Target Category, Weapon Modality, Group Identity, and Coordinates.
  - Strictly bans post-attack features: `nkill`, `nwound`, `success`, `suicide`, `summary`.
- **Temporal Out-of-Time Splitting:**
  - Training Set: $\le 2012$ (12,260 incidents).
  - Test Set: $2013\text{--}2017$ (2,740 incidents).
  - Eliminates temporal data contamination inherent in standard random K-fold splits.

---

## Slide 7: Model Comparison & Explainable AI (SHAP)
- **Model Leaderboard:**
  - Baseline (Majority Class): 47.23% Acc / 0.1069 Macro-F1 / 60.73% Top-3 Acc.
  - Logistic Regression (Balanced): 22.92% Acc / 0.1601 Macro-F1 / 61.13% Top-3 Acc.
  - Random Forest (Balanced): 37.66% Acc / 0.1691 Macro-F1 / 67.99% Top-3 Acc.
  - **LightGBM (Champion)**: 32.81% Acc / 0.1602 Macro-F1 / **69.31% Top-3 Acc**.
- **Model Explainability:**
  - Global Feature Importance: Target type and Weapon category dominate decision boundaries.
  - Local SHAP Decision Waterfalls: Real-time per-prediction factor attribution explaining *why* a specific modality was predicted.

---

## Slide 8: Strategic Risk Index & Scenario Sensitivity Simulator
- **Composite Sovereign Risk Score:**
  - Weighted combination of: Normalized Log(Incidents) [30%], Normalized Log(Casualties) [30%], 3-Year Trend Slope [20%], and Mass-Casualty Ratio [20%].
  - Quantile-based threat tiers: Low, Medium, High, and Critical.
- **Interactive Scenario Simulator:**
  - Dynamic sliders for component weights and casualty caps with real-time sovereign re-ranking.
  - **Kendall's Tau ($\tau$) Stability Benchmark:** Measures ranking robustness against changing analytical assumptions.

---

## Slide 9: Longitudinal Forecasting & Tactical Early Warning
- **Longitudinal Forecasting:**
  - Holt-Winters Exponential Smoothing (ETS) with 80% and 95% confidence intervals.
  - Evaluated via strict 2013–2017 out-of-time backtesting against Naive and Moving Average baselines (MAE/MAPE tracking).
  - Hard 5-year maximum forecast horizon cap to reflect geopolitical unpredictability.
- **Tactical Early Warning (Surge Detection):**
  - Monthly panel monitoring for top-50 conflict theaters.
  - 12-month Rolling Z-Scores ($Z \ge 2.0\sigma$) and Isolation Forest anomaly detectors.
  - Ground-truth evaluation against forward 3-month surge thresholds ($> 2.0\times$ trailing mean).

---

## Slide 10: Faction Behavioral Profiling & Relational Network Graphs
- **Behavioral Archetype Discovery:**
  - Vectorizes factions with $\ge 20$ attacks across tactics, targets, regional footprints, and casualty lethality.
  - KMeans clustering with PCA 2D projections reveals distinct operational doctrines (e.g., Mass-Casualty Sectarian, Rural Insurgent, Urban Sabotage).
- **NetworkX Relational Topology:**
  - Graph modalities: Shared Target Profiles, Shared Regional Footprints, and Co-claimed Incidents.
  - Degree and betweenness centrality identify ideological bridges and core actors.
  - Greedy modularity community detection isolates operational clusters.
  - Mandatory disclaimer: Graph edges represent statistical similarities, not proven operational alliances.

---

## Slide 11: Narrative Text Mining & Conversational GenAI Analyst
- **Incident Text Mining:**
  - Unsupervised NMF topic decomposition discovers 5 latent tactical vocabularies from narrative summaries.
  - spaCy Named Entity Recognition extracts GPE locations, ORG militant actors, and PERSON targets.
  - Semantic similarity search retrieves historical analogous incidents via dense vector embeddings.
- **Conversational Analyst (`Ask the Analyst`):**
  - Natural language translation to structured JSON query specs via Google Gemini (`gemini-2.5-flash`).
  - Strict security whitelist validation on columns, operators, and metrics.
  - Pure pandas execution (strictly zero `eval`/`exec`) generating 2-3 sentence summaries and Plotly visuals.
- **Automated Intelligence Reports:**
  - Aggregates transmitted without raw records; one-click executive PDF export via `fpdf2`.

---

## Slide 12: Production Engineering & Responsible AI Principles
- **Engineering Rigor:**
  - 75 automated unit tests passing (100% pass rate).
  - 87% test coverage across all `src/` modules.
  - Zero Ruff linting warnings.
  - Multi-platform `Makefile`, GitHub Actions CI/CD, and hardened non-root `Dockerfile`.
- **Core Responsible AI Takeaways:**
  - Open and transparent accounting for data collection bias across eras (PGIS, CETIS, START).
  - Respect for the non-operational, educational boundaries of predictive models.
  - Human-in-the-loop oversight on all statistical and machine learning outputs.
