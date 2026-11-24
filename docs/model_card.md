# Model Card: Pre-Attack Tactical Classifier

### Global Terrorism Database Pre-Incident Tactic Prediction

---

## 1. Model Details

- **Model Name:** Pre-Attack Tactic Classifier (Champion: LightGBM / Balanced Random Forest)
- **Model Version:** 1.0.0
- **Model Type:** Multi-Class Gradient Boosted Decision Tree (LightGBM) & Ensemble Random Forest
- **Release Date:** November 2026
- **License:** MIT License (Research & Academic Use)
- **Developed By:** Senior ML Engineer, Military Intelligence & Threat Analytics Portfolio Project

---

## 2. Intended Use & Boundaries

### Primary Intended Use
- **Retrospective Academic Analytics:** Historical research exploring the predictability of attack tactics given ex-ante observable variables.
- **Methodological Demonstration:** Showcasing zero-leakage pipeline design, temporal backtesting, and SHAP interpretability on complex socio-political conflict data.

### Prohibited / Out-of-Scope Uses
- **Operational Military Targeting:** Strictly prohibited. The model is NOT validated for real-time tactical targeting, force protection, kinetic operations, or automated decision systems.
- **Real-Time Surveillance:** Not calibrated for continuous live streaming surveillance feeds.
- **Civilian Threat Profiling:** Must not be used to profile individuals, communities, or protected classes.

---

## 3. Training & Evaluation Data

- **Primary Source:** Global Terrorism Database (GTD) collected by the National Consortium for the Study of Terrorism and Responses to Terrorism (START), University of Maryland.
- **Temporal Coverage:** 1970–2017 (1993 missing from standard distribution due to historical archival loss).
- **Temporal Backtest Partition (Zero Leakage):**
  - **Training Partition:** Incidents recorded on or before December 31, 2012 ($iyear \le 2012$).
  - **Test / Evaluation Partition:** Incidents recorded between January 1, 2013 and December 31, 2017 ($2013 \le iyear \le 2017$).
  - **Constraint:** Strictly time-based partition; random k-fold cross-validation is forbidden to prevent temporal information leakage.

---

## 4. Input Features & Strict Zero-Leakage Controls

### Permitted Pre-Attack Covariates (9 features)
1. `iyear`: Year of incident (integer)
2. `region_txt`: Geographic theatre (categorical)
3. `country_txt`: Sovereign nation state (categorical)
4. `provstate`: Sub-national administrative unit / province (categorical)
5. `targtype1_txt`: Targeted sector (e.g. Police, Military, Government, Private Citizens)
6. `weaptype1_txt`: Weapon classification (e.g. Explosives, Firearms, Incendiary)
7. `gname`: Suspected perpetrator faction (including "Unknown")
8. `latitude` & `longitude`: Pinpoint geographic coordinates
9. `coord_missing`: Indicator flag for missing geospatial coordinates

### Prohibited Post-Attack Leakage Variables (Strictly Banned)
- `nkill` (Fatalities): Known only post-attack.
- `nwound` (Wounded count): Known only post-attack.
- `ncasualty` (Cumulative casualties): Post-event arithmetic.
- `success` (Operational success/failure): Known only post-attack.
- `suicide` (Suicide attack completion flag): Tactical execution outcome.
- `summary` (Narrative description): Text contains explicit details of attack outcome.
- `casualties_known`: Reporting metadata.

---

## 5. Performance Metrics (Temporal Out-of-Sample Test)

Evaluated strictly on test partition ($2013 \le iyear \le 2017$):

| Architecture | Accuracy | Macro-F1 | Weighted-F1 | Top-3 Accuracy |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline (Majority Class)** | 47.2% | 10.7% | 30.3% | 60.7% |
| **Multinomial Logistic Regression** | 10.7% | 10.7% | 10.4% | 53.0% |
| **Balanced Random Forest** | 35.4% | 15.6% | 32.0% | 77.2% |
| **LightGBM (Champion)** | 23.5% | **16.0%** | 25.9% | **69.3%** |

*Note: All numbers computed live during the pipeline run and saved to `artifacts/metrics.json`.*

---

## 6. Model Interpretability & Feature Attribution

- **Method:** TreeExplainer SHAP (Shapley Additive exPlanations).
- **Key Global Drivers:**
  1. `weaptype1_txt` (Explosives vs. Firearms): Dominant determinant separating Bombings from Armed Assaults.
  2. Geographic Coordinates (`latitude`, `longitude`): Strong regional clustering reflecting operational theatre tactics.
  3. `targtype1_txt` (Target Sector): Modulates tactic (e.g., Infrastructure targets correlate strongly with Facility Attacks).

---

## 7. Ethical Considerations & Limitations

1. **Reporting Biases in Source Data:**  
   The GTD reflects media coverage rather than omniscient ground truth. Digital media proliferation post-2005 heavily inflated recorded incident volume in the test partition relative to the training partition.
2. **Unclaimed Incidents ("Unknown" Perpetrators):**  
   In high-intensity conflict zones (e.g. Iraq, Syria), over 60% of attacks remain unclaimed. When `gname == "Unknown"`, model predictive power degrades significantly.
3. **Automation Bias Risk:**  
   Users must not treat model confidence scores as tactical certainty. Operational decisions based on automated outputs without human intelligence verification could result in catastrophic failure.
