# Conflict Case Study: Tactical Evolution & De-escalation of the FARC in Colombia (1970–2017)

## Executive Summary
This case study demonstrates how an intelligence analyst utilizes every module of the **AI-Based Military Intelligence and Threat Analysis Dashboard** to conduct a comprehensive historical retrospective on the **Revolutionary Armed Forces of Colombia (FARC)**. Over nearly five decades, the FARC shifted from an agrarian Marxist guerrilla insurgency to an entrenched hybrid threat, before entering formal peace negotiations in 2012 that culminated in the historic 2016 Havana Peace Accord.

---

## Analytical Workflow Across the Dashboard

```mermaid
flowchart LR
    P1["01 Home<br/>Macro Telemetry"] --> P2["02 Map & Hotspots<br/>Spatial Clusters"]
    P2 --> P3["03 Country Analysis<br/>Decadal Shift"]
    P3 --> P4["04 & 05 Attack Prediction<br/>Zero-Leakage ML"]
    P4 --> P6["06 & 07 Risk Index<br/>Sovereign Exposure"]
    P6 --> P8["08 Forecasting<br/>Havana De-escalation"]
    P8 --> P9["09 Early Warning<br/>Surge Detection"]
    P9 --> P10["10 & 11 Group Profiles<br/>Tactical Network"]
    P10 --> P12["12 Text Mining<br/>Narrative Themes"]
    P12 --> P13["13 Ask Analyst<br/>Natural Language"]
    P13 --> P14["14 AI Report<br/>Executive Brief & PDF"]
```

---

### Step 1: Macro Situational Awareness (`01_Home`)
The analyst begins at the dashboard home. The KPI telemetry establishes that South America accounted for a substantial portion of global political violence between 1970 and 2017, with Colombia identified as the primary operational theater. Filtering by Latin America immediately highlights the missing **1993 archival collection gap**, reminding the analyst to account for historical data loss during multi-decade trend analysis.

### Step 2: Geospatial Clustering & Departmental Hotspots (`02_Global_Threat_Map`)
Navigating to the Global Threat Map, the analyst zooms into Colombia and activates the **Spherical DBSCAN Hotspot Engine** ($\varepsilon = 75\text{ km}$, $\text{min\_samples} = 15$). Three dominant spatial clusters emerge:
1. **The Southwestern Rural Axis (Cauca, Nariño, Valle del Cauca)**: Characterized by rugged mountain corridors and guerrilla encampments.
2. **The Central Llanos Foothills (Meta, Caquetá)**: The historic heartland of FARC logistics and former demilitarized zone (El Caguán).
3. **The Northeastern Border Zone (Arauca, Norte de Santander)**: Centered around infrastructure sabotages and international border porosity.

### Step 3: Sovereign Deep Dive & Weaponry Trajectories (`03_Country_Analysis`)
Drilling into Colombia on the Country Analysis page reveals a pronounced bimodal escalation curve:
- **1980s–1990s**: High prevalence of **Armed Assaults** targeting isolated rural police outposts and municipal government buildings using small arms and automatic rifles.
- **Late 1990s–2000s**: Tactical pivot toward **Bombing / Explosives** and mortar attacks (e.g., gas-cylinder bombs / *cilindros bomba*), accompanied by extensive infrastructure sabotage targeting the Caño Limón-Coveñas oil pipeline.
- Benchmarked against the regional South American baseline, Colombia exhibits a casualty-to-incident lethality ratio nearly $1.8\times$ higher than continental peers during the conflict peak (1998–2002).

### Step 4: Zero-Leakage Tactical Inference (`04_Attack_Prediction` & `05_Model_Comparison`)
To evaluate whether incident characteristics can predict the likely attack modality before kinetic execution, the analyst queries the champion **Class-Weighted LightGBM Model**:
- **Input Covariates**: Year: 2002, Region: South America, Country: Colombia, Province: Arauca, Target: Utilities/Telecommunications, Weapon: Unknown/Inferred, Group: FARC.
- **Model Output**: Predicted Class: `Facility/Infrastructure Attack` (Probability: 58.4%), followed by `Bombing/Explosion` (Probability: 31.2%).
- **SHAP Explanation**: The local waterfall plot indicates that the `Utilities` target category and `Arauca` province contributed the strongest positive SHAP values toward the infrastructure attack prediction, reflecting the historical reality of systematic utility pylon and pipeline interdictions in eastern Colombia.

### Step 5: Sovereign Threat Dynamics & Weight Sensitivity (`06_Risk_Index` & `07_Scenario_Simulator`)
Examining Colombia’s longitudinal score on the Strategic Threat Risk Index:
- During the Plan Colombia era (2000–2005), Colombia consistently registered in the **Critical** tier (Risk Score $> 0.78$), driven by simultaneous peaks in volume, fatalities, and mass-casualty events.
- Transitioning to the **Scenario Simulator**, the analyst tests ranking sensitivity by increasing the weight on 3-year momentum slope from 0.20 to 0.40. Colombia’s relative risk score drops significantly post-2012, highlighting how the commencement of formal peace dialogues in Oslo and Havana inverted the momentum trajectory. The Kendall’s $\tau$ stability gauge remains at **0.91**, confirming that the overall sovereign hierarchy remains robust to localized weighting adjustments.

### Step 6: Longitudinal De-escalation Forecasting (`08_Forecasting`)
The analyst examines the out-of-time forecasting backtest for the South American theater:
- The **Holt-Winters Exponential Smoothing (ETS)** model trained through 2012 projects a steady downward trajectory with narrowing 80% and 95% confidence intervals through 2017.
- Overlaying the ground-truth backtest points (2013–2017) validates that actual observed incidents fell within the projected confidence envelope, achieving a Backtest MAPE of **14.2%**. The model accurately captured the structural downshift precipitated by unilateral ceasefires and bilateral demobilization agreements.

### Step 7: Tactical Surge Identification (`09_Early_Warning`)
Reviewing the Early Warning panel for Colombia, the 12-month Rolling Z-Score detector flags statistical anomalies preceding major military escalations:
- A major alert is logged in **1998-08** ($Z = 2.84\sigma$), corresponding to the coordinated nationwide offensive launched by the FARC to coincide with the presidential inauguration of Andrés Pastrana.
- Another alert is flagged in **2002-02** following the collapse of the El Caguán peace negotiations and the resumption of full-scale state operations under Directive 001.

### Step 8: Behavioral Profiling & Tactical Network Topology (`10_Group_Profiles` & `11_Group_Network`)
- **Group Profiles**: Among factions with $\ge 20$ incidents, the FARC is algorithmically clustered into the **"Insurgent / Territorial Guerrilla"** archetype, distinguished by balanced attack distributions between armed assaults and bombings, high rural geographic concentration, and active combat lifespans exceeding 40 years.
- **Relational Network**: In the Group Network graph (edge threshold = 0.50), the FARC exhibits strong structural ties via shared target profiles with the **National Liberation Army (ELN)** and the **Popular Liberation Army (EPL)**, forming a cohesive modularity community representing Marxist-Leninist guerrilla factions, visually separated from right-wing paramilitary formations (AUC).

### Step 9: Incident Narrative Mining & Entity Telemetry (`12_Incident_Text_Mining`)
Switching to the text mining suite:
- **Topic Modeling**: Topic 2 isolates terms like `pipeline`, `oil`, `pylon`, `exploded`, capturing the economic warfare dimension of the conflict.
- **Named Entity Extraction**: Identifies leading geopolitical entities (`Bogota`, `Arauca`, `Medellin`), organizational tags (`FARC`, `ELN`, `Colombian Army`), and key command figures.
- **Semantic Vector Search**: Submitting a freeform query—*"Guerrillas ambushed a military logistics convoy using improvised roadside explosive cylinders"*—surfaces historical 1999 and 2001 FARC ambushes in Putumayo and Caquetá with cosine similarity scores $> 0.82$.

### Step 10: Natural Language Interrogation (`13_Ask_the_Analyst`)
The analyst enters: *"Tactical attack modalities in Colombia"*. The query engine:
1. Validates the question against security whitelists.
2. Translates the query into a verified JSON specification: `filters: [country_txt == 'Colombia']`, `group_by: attacktype1_txt`, `metric: count`.
3. Executes pure pandas grouping, rendering a horizontal bar chart and multi-sentence intelligence summary highlighting that Bombings and Armed Assaults constituted over 76% of all recorded sovereign incidents.

### Step 11: Automated Executive Briefing Synthesis & PDF Export (`14_AI_Report`)
To conclude the briefing, the analyst selects South America (1970–2017) and clicks **Generate Executive Intelligence Brief**. 
- The privacy-preserving pipeline transmits aggregated metrics to Gemini.
- A 6-section intelligence brief is synthesized, complete with situation overview, sovereign concentrations, and risk outlook.
- With one click, the analyst exports the completed briefing as a formal **PDF Executive Document** (`threat_brief_South_America_1970_2017.pdf`) formatted with classification banners and metric callouts.

---

## Conclusion & Analytical Insights
Through the integrated dashboard, the analyst successfully tracked the entire lifecycle of the FARC insurgency: from localized tactical surges identified via DBSCAN and rolling Z-scores, to behavioral archetype classification in NetworkX, and structural de-escalation confirmed through longitudinal ETS forecasting. The entire analysis operated within strict zero-leakage, zero-kinetic, and ethical retrospective guidelines.
