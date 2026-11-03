# WFP & Partner Humanitarian MEAL Operations & Data Analytics Suite
### Professional Portfolio Project for M&E & Data Assistant Position

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458.svg)](https://pandas.pydata.org/)
[![WFP Corporate CARI](https://img.shields.io/badge/Standards-WFP%20CARI%20%2F%20RAM-0072CE.svg)](https://www.wfp.org/)
[![UN OCHA 4Ws](https://img.shields.io/badge/Interoperability-UN%20OCHA%204Ws-E57200.svg)](https://www.unocha.org/)
[![DHIS2 Standard](https://img.shields.io/badge/API-DHIS2%20DataValueSets-2B88D8.svg)](https://dhis2.org/)

---

## 📌 Executive Summary

This end-to-end humanitarian Monitoring, Evaluation, Accountability, and Learning (**MEAL**) portfolio suite was specifically engineered to demonstrate **100% technical competency alignment** with the hiring standards of the **UN World Food Programme (WFP)** and humanitarian partner organizations (**Terre des hommes - Tdh**, **Sun Community Health - SCH**, **Shwe Kyun Thar Network - SKT**, **Myanmar Youth Stars - MYS**, and **Best Shelter**).

Simulating an emergency food and cash transfer response covering **4 Myanmar operational hubs** (*Mandalay, Dawei, Lashio, Bogale*), it demonstrates end-to-end data lifecycle capabilities: from **mobile survey ingestion**, **automated Data Quality Assurance (DQA)**, **Enumerator Fraud Forensics (Benford's Law & GPS checks)**, **Official WFP Corporate CARI Food Security 4-point scale**, **Sex, Age, Disability Disaggregation (SADD)**, to an interactive **Geospatial GIS Map**, **Executive LogFrame Indicator Tracking Table (ITT)**, **Complaints & Feedback Response Mechanism (CFRM)**, and **UN OCHA 4Ws / DHIS2 Interoperability exports**.

---

## 🎯 Key M&E & Data Competencies Demonstrated

| Humanitarian Competency | Standard / Framework | Implementation in this Portfolio |
| :--- | :--- | :--- |
| **Official WFP CARI Engine** | WFP Corporate RAM / VAM Guidance | Synthesizes Current Consumption (FCS) and Coping Capacity (Food Expenditure Share + Livelihood Coping Strategies - LCS) into the official 4-point Food Security Index (FSI) & Corporate Console Matrix. |
| **Enumerator Fraud Forensics** | UN / INGO Survey Quality Assurance | Programmatic auditing applying **Benford's Law first-digit analysis** ($\chi^2$ test), interview duration speed-run detection (< 7 min), and GPS teleportation velocity checks (> 50 km/h) to generate an automated **Enumerator Trust Scorecard (0-100%)**. |
| **Automated DQA & Cleaning** | USAID / Global Fund DQA Guidelines | Python pipeline that cleans raw survey records, eliminating duplicates, fixing 7-day recall boundary violations, resolving logical contradictions, and generating a transparent `dqa_audit_log.csv`. |
| **Geospatial GIS Mapping** | MIMU P-Code Standard (Admin 1-3) | Interactive GPS map color-coding households by CARI Food Insecurity phases across Myanmar hubs (Mandalay `MMR004001`, Dawei `MMR007001`, Lashio `MMR014001`, Bogale `MMR017006`). |
| **UN OCHA 4Ws Cluster Matrix** | UN OCHA Cluster Matrix (Who, What, Where, When) | Automated generation and export of 4Ws matrix with MIMU P-codes, activity modalities, disaggregated beneficiaries reached, and funding sources. |
| **DHIS2 Interoperability** | DHIS2 Web API Standard | Formats monthly indicators into standard `dataValueSets` JSON payload ready for direct POST integration with national HMIS / DHIS2 servers (Sun Community Health / Global Fund). |
| **LogFrame Results Framework & ITT** | Donor LogFrame (ECHO, WFP, USAID) | Dynamic Indicator Tracking Table with Baseline, Annual Target, Actual Achieved numbers, % Achievement rate, and automated RAG (Red-Amber-Green) monitoring status. |
| **Accountability & CFRM (AAP)** | Core Humanitarian Standard (CHS) / IASC | Complaints and Feedback Tracking Module monitoring intake channels, 5-category IASC classification, SLA compliance, and strict 24-hr PSEA safeguarding escalation. |
| **SADD Disaggregation** | IASC Gender & Inclusion Standards | Routine disaggregation across all indicators by Gender of Household Head (Female-headed vs Male-headed), Disability status (Persons with Disabilities - PwD), and Vulnerability (Under-5 children, PLW). |

---

## 📂 Project Architecture

```
wfp_meal_data_portfolio/
├── app.py                         # Enterprise Streamlit MEAL Operations Dashboard (7 Tabs)
├── generate_sample_data.py        # Realistic Humanitarian Data Generator (460 HHs across 4 hubs)
├── run_dashboard.bat              # One-click Windows launcher for interactive dashboard
├── requirements.txt               # Python package dependencies
│
├── src/                           # Modular Humanitarian Data Pipelines
│   ├── cari_engine.py             # Official WFP Corporate CARI 4-point scale algorithm & matrix
│   ├── enumerator_audit_engine.py # Benford's Law, duration speeders, GPS velocity & Trust Scorecard
│   ├── cluster_interop.py         # UN OCHA 4Ws Matrix & DHIS2 DataValueSets JSON exporter
│   ├── dqa_cleaning_pipeline.py   # Automated survey cleaning, deduplication & audit log
│   ├── wfp_indicators.py          # WFP FCS, rCSI, SADD, and ITT calculations
│   └── cfrm_tracker.py            # AAP / CFRM feedback analysis & PSEA escalation
│
├── data/
│   ├── raw/                       # Simulated raw exports with real-world human errors
│   │   ├── raw_kobo_pdm_survey.csv
│   │   ├── raw_distribution_register.csv
│   │   ├── raw_cfrm_tickets.csv
│   │   └── project_logframe_targets.csv
│   │
│   ├── cleaned/                   # Post-DQA verified data & audit trail
│   │   ├── cleaned_kobo_pdm_survey.csv
│   │   └── dqa_audit_log.csv
│   │
│   └── indicators/                # Enriched analytical tables
│       ├── pdm_with_wfp_indicators.csv
│       ├── wfp_cari_summary_matrix.csv
│       ├── indicator_tracking_table.csv
│       └── cfrm_performance_summary.csv
│
└── reports/                       # Humanitarian Export Deliverables
    ├── ocha_4ws_humanitarian_matrix.csv
    └── dhis2_datavaluesets_export.json
```

---

## 🚀 How to Run the Platform Locally

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Windows / macOS / Linux

### Option 1: One-Click Desktop Launcher (Windows)
Double-click `run_dashboard.bat`. It will automatically activate the virtual environment and open the interactive operations portal in your default browser at `http://localhost:8501`.

### Option 2: Command Line
```bash
# 1. Clone repository and navigate to folder
cd wfp_meal_data_portfolio

# 2. Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. (Optional) Re-run data generation and analytical pipelines
python generate_sample_data.py
python src/dqa_cleaning_pipeline.py
python src/wfp_indicators.py
python src/cluster_interop.py
python src/enumerator_audit_engine.py

# 4. Launch the Operations Center Dashboard
streamlit run app.py
```

---

## 📊 Detailed Methodology & Technical Notes

### 1. WFP Corporate CARI (Consolidated Approach for Reporting Indicators)
- **Current Consumption Domain:** Food Consumption Score (FCS) categorized into Code 1 (Acceptable $>35$), Code 3 (Borderline $21.5 - 35$), and Code 4 (Poor $\le 21$).
- **Coping Capacity Domain:**
  - *Economic Vulnerability:* Food Expenditure Share (FES) categorized into Code 1 ($<50\%$), Code 2 ($50-65\%$), Code 3 ($65-75\%$), Code 4 ($\ge 75\%$).
  - *Asset Depletion:* Livelihood Coping Strategies (LCS-FS) categorized into Code 1 (None), Code 2 (Stress: sold non-productive assets, spent savings), Code 3 (Crisis: sold productive assets, reduced health exp), Code 4 (Emergency: sold land/house, begged).
- **Food Security Index (FSI):** Composite 4-point scale identifying total food insecure populations (Phases 3 & 4).

### 2. Enumerator Fraud Forensics & Benford's Law
- Calculates first significant digit distribution on household food expenditure.
- Computes Chi-Square statistic:
  $$\chi^2 = \sum_{d=1}^{9} \frac{(O_d - E_d)^2}{E_d}$$
  where $E_d = N \cdot \log_{10}(1 + 1/d)$. Flags fabrication when $p < 0.01$.
- Calculates speed-run outliers ($< 7$ min) and Haversine velocity between consecutive survey GPS points ($> 50$ km/h impossible travel).

### 3. Cluster Interoperability
- **UN OCHA 4Ws:** Complete matrix mapping implementing partners, cluster sectors, activities, target vs reached beneficiaries, and official MIMU P-codes.
- **DHIS2 API:** Standard `dataValueSets` JSON payload formatted with Data Elements, Periods (`202608`), and OrgUnit P-codes.

---

## 👤 Author Profile & Target Organizations
Designed as an executive demonstration project for **M&E & Data Assistant** applications at:
- **UN World Food Programme (WFP)** (RAM/VAM, Cash & Voucher Operations)
- **Terre des hommes (Tdh)** (Nutrition & MCCT MEAL)
- **Sun Community Health (SCH)** (Jr. MIS / DHIS2 Officer)
- **Shwe Kyun Thar Network (SKT)** (ECHO Emergency Education & Cash)
- **Best Shelter** (Emergency Nutrition & Food Assistance)
- **Myanmar Youth Stars (MYS)** (Community Health & Livelihood Cash)
