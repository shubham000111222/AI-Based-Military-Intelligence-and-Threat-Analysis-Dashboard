# Architecture Decision Records (ADRs)

This document formalizes the key architectural, technical, and methodological decisions made during the design and engineering of the **AI-Based Military Intelligence and Threat Analysis Dashboard**.

---

## ADR-001: Selection of Gradient-Boosted Decision Trees (LightGBM / CatBoost) over Deep Neural Networks for Attack Prediction

- **Status:** Accepted
- **Context:** The predictive modeling objective requires multi-class classification of incident attack modalities (`attacktype1_txt`) using pre-attack tabular indicators (geography, temporal counters, weapon type, target type, perpetrator group). The feature space contains high-cardinality categorical variables, extreme class imbalance (e.g. Bombings account for ~47% of incidents whereas Kidnappings and Assassinations are much rarer), and tabular sparsity.
- **Decision:** Select Gradient-Boosted Decision Trees—specifically **LightGBM** and **Random Forest** with balanced class weights—as the primary modeling architectures, benchmarked against Multinomial Logistic Regression and Majority-Class baselines.
- **Consequences:**
  - **Pros:**
    - Superior out-of-the-box performance on tabular data with mixed numeric and high-cardinality categorical inputs.
    - Native support for balanced sample weighting, preventing rare attack types from collapsing to zero recall.
    - Fast training and low-latency inference suitable for interactive Streamlit prediction forms.
    - Direct integration with TreeSHAP for rapid, exact local and global feature attribution.
  - **Cons:**
    - GBDT models do not natively learn deep sequential temporal representations across consecutive multi-year operations without explicit manual feature engineering.

---

## ADR-002: Temporal Out-of-Time Splitting (Train $\le 2012$, Test $2013\text{--}2017$) over K-Fold Cross-Validation

- **Status:** Accepted
- **Context:** Standard machine learning workflows frequently utilize randomized K-Fold cross-validation or random train/test splits. In conflict data, political actors, weapon availability, and tactical doctrines evolve non-stationarily over decades. Random splitting allows incidents from 2016 to inform predictions for 1985, causing severe temporal lookahead leakage and artificially inflated test metrics.
- **Decision:** Mandate a strict chronological temporal split across all machine learning, forecasting, and anomaly detection evaluations:
  - **Training Set:** Incidents occurring on or before December 31, 2012 (12,260 incidents in the slim dataset).
  - **Testing / Evaluation Set:** Incidents occurring between January 1, 2013 and December 31, 2017 (2,740 incidents).
- **Consequences:**
  - **Pros:**
    - True out-of-time evaluation faithfully replicates real-world intelligence forecasting conditions.
    - Exposes how models handle emergent conflict actors (e.g., ISIS expansion post-2012) not present in historical training data.
  - **Cons:**
    - Test metric scores (e.g., Macro-F1) appear lower than randomly shuffled benchmarks due to distribution drift and emergent tactical shifts over time.

---

## ADR-003: Spherical Haversine DBSCAN over Planar Euclidean Spatial Clustering

- **Status:** Accepted
- **Context:** The geospatial threat center requires unsupervised spatial cluster discovery to identify operational hotspots across sovereign territories. Applying standard Euclidean distance ($d = \sqrt{\Delta x^2 + \Delta y^2}$) on raw latitude and longitude coordinates assumes a flat plane, resulting in severe geographic distortion that exaggerates distances near the poles and compresses them near the equator.
- **Decision:** Implement **Spherical DBSCAN** using Scikit-Learn’s `haversine` metric, converting geographic coordinates from decimal degrees to radians ($[\text{rad}] = [\text{deg}] \times \frac{\pi}{180}$) and scaling the neighborhood threshold $\varepsilon$ by the mean radius of Earth ($R = 6371.0088\text{ km}$).
- **Consequences:**
  - **Pros:**
    - Calculates true great-circle surface distances across the ellipsoidal globe regardless of latitude.
    - Eliminates false spatial distortions in high-latitude or equatorial theaters.
    - Produces geographically verifiable cluster boundaries and centroid coordinates.
  - **Cons:**
    - Requires coordinate verification and exclusion of invalid coordinates ($|\text{lat}| > 90$, $|\text{lon}| > 180$) prior to radian transformation.

---

## ADR-004: Holt-Winters Exponential Smoothing (ETS) over Complex Autoregressive Neural Networks for Threat Forecasting

- **Status:** Accepted
- **Context:** Analysts require 3-to-5 year longitudinal trajectory forecasting for global and regional conflict theaters. While deep auto-regressive networks (e.g., DeepAR, N-BEATS, Temporal Fusion Transformers) exist, annual conflict series contain relatively short sequence lengths (47 time steps), high annual variance, and structural shocks.
- **Decision:** Implement **Holt-Winters Exponential Smoothing (ETS)** with additive trend as the primary forecaster, benchmarked against Naive Last-Value and 3-Year Moving Average baselines, with 80% and 95% confidence intervals and a hard maximum horizon cap of 5 years.
- **Consequences:**
  - **Pros:**
    - High mathematical stability and rapid convergence on short annual series without overfitting.
    - Robust, mathematically rigorous confidence intervals that widen realistically over future horizons.
    - Immediate execution without requiring heavy GPU compute or deep learning framework dependencies.
  - **Cons:**
    - Cannot model exogenous socio-economic covariates (e.g., GDP fluctuations, regime changes) without switching to complex state-space formulations.

---

## ADR-005: Handling the Missing 1993 START Archival Collection Loss

- **Status:** Accepted
- **Context:** The original paper incident records for 1993 were lost in transit by the START data collection team prior to digital centralization. Only partial records were recovered, and standard practice across academic conflict research is to exclude 1993 from release datasets. Silently plotting continuous trend lines across 1992–1994 gives the false impression that global conflict dropped to near zero in 1993.
- **Decision:** 
  1. Never fabricate, synthetically impute, or hide the 1993 gap on visual charts.
  2. Annotate every longitudinal time chart across the dashboard (`01_Home`, `03_Country_Analysis`, `08_Forecasting`, `10_Group_Profiles`, `15_Data_Quality`) with a distinct amber vertical highlight and explanatory note.
  3. For continuous time-series models (ETS/SARIMA), apply linear interpolation strictly between 1992 and 1994 to maintain seasonal/trend continuity, while logging an explicit `is_interpolated=True` telemetry flag.
- **Consequences:**
  - **Pros:**
    - Preserves rigorous academic integrity and transparency regarding archival limitations.
    - Prevents downstream users from drawing erroneous historical conclusions about 1993.
  - **Cons:**
    - Requires custom visual annotation logic across all Plotly time-series figures.

---

## ADR-006: Streamlit Multipage Architecture with Offline Precomputed Artifacts for Sub-1GB Memory Footprint

- **Status:** Accepted
- **Context:** The dashboard must deploy seamlessly on resource-constrained platforms, specifically **Streamlit Community Cloud**, which enforces a strict ~1 GB container RAM limitation. Generating complex SHAP explainer objects, running iterative model training, fitting 12,000+ dense sentence embeddings, and performing multi-region backtests on the fly during a web request would instantly exceed memory limits and crash the application.
- **Decision:** Separate heavy training and model precomputations from runtime execution:
  - Scripts (`scripts/train_attack_model.py`, `scripts/evaluate_forecasts.py`, `scripts/evaluate_anomaly.py`, `scripts/build_embeddings.py`) execute offline and serialize lightweight JSON metrics, trained model pipelines (`.joblib`), and NumPy arrays into `artifacts/`.
  - The Streamlit runtime exclusively loads precomputed artifacts and cached columnar Parquet data (`data/processed/gtd_slim.parquet`) via `st.cache_data`.
- **Consequences:**
  - **Pros:**
    - Instant page load times (< 0.5s) across all 17 pages.
    - Memory footprint remains well below 450 MB, operating reliably on Streamlit Community Cloud.
  - **Cons:**
    - Model hyperparameters and backtest evaluations must be recomputed via offline scripts if the underlying raw dataset changes.

---

## ADR-007: Pure Pandas Whitelist Query Execution over Dynamic eval/exec/SQL for Conversational Intelligence

- **Status:** Accepted
- **Context:** The conversational analyst (`13_Ask_the_Analyst`) translates natural language inquiries into data queries. Generating raw SQL or dynamic Python strings and executing them via `eval()`, `exec()`, or direct SQL execution engines introduces catastrophic arbitrary code execution and injection vulnerabilities.
- **Decision:** Mandate a two-tier security architecture:
  1. **Structured JSON Query Spec:** Natural language questions are translated solely into a rigid JSON specification containing approved keys (`filters`, `group_by`, `metric`, `metric_column`, `sort`, `top_n`, `chart_type`).
  2. **Strict Whitelist Validation:** Every query specification is validated against strict security whitelists for columns, operators (`==, !=, >, >=, <, <=, in, between`), and metrics (`count, sum, mean, min, max`). Malicious patterns (`__import__`, `os.system`, `eval`, etc.) trigger immediate rejection.
  3. **Pure Pandas Execution:** Queries are executed using pure, compiled Pandas operations (`df[df[col] == val].groupby(...).agg(...)`). Dynamic evaluation (`eval`/`exec`) is strictly prohibited.
- **Consequences:**
  - **Pros:**
    - Complete protection against arbitrary code execution, script injection, and unauthorized data extraction.
    - Deterministic, easily testable execution pipeline.
  - **Cons:**
    - Queries are restricted to the expressive capability of the structured specification schema (cannot execute arbitrary multi-table joins).

---

## ADR-008: Privacy-Preserving Aggregate Transmission for LLM Report Synthesis

- **Status:** Accepted
- **Context:** The automated intelligence brief generator (`14_AI_Report`) integrates Google Gemini to synthesize executive briefings. Transmitting raw incident rows, individual casualty manifests, or localized GPS coordinates introduces unnecessary payload overhead and potential data privacy risks.
- **Decision:** Implement strict aggregate-only payload transmission:
  - The reporting module (`src/report.py`) compiles high-level aggregated statistical indicators (incident counts, fatality sums, top 5 factions, dominant tactics, longitudinal trends).
  - Individual incident rows, raw coordinates, and narrative text fields are never passed to the LLM.
- **Consequences:**
  - **Pros:**
    - Ultra-compact JSON payload (< 5 KB), minimizing API token costs and latency.
    - Preserves data privacy and eliminates confidential row-level leakage.
    - Enables exact numerical verification: the LLM is prompted to use only the provided aggregate numbers.
  - **Cons:**
    - The LLM cannot provide granular qualitative deep dives into specific individual incidents without a separate targeted search query.
