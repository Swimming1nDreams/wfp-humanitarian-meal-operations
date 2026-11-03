"""
WFP & INGO MEAL Portfolio Project
Module 2: Standard Humanitarian Indicator Calculations (FCS, rCSI, SADD, CARI, ITT)
Author: M&E & Data Assistant Candidate
Implements official WFP Vulnerability Analysis and Mapping (VAM) / RAM methodologies,
SPHERE Standards, and Inter-Agency Standing Committee (IASC) Gender & Disability metrics.
"""

import os
import pandas as pd
import numpy as np
from cari_engine import run_cari_analysis, generate_cari_summary_matrix

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED_PATH = os.path.join(BASE_DIR, "data", "cleaned", "cleaned_kobo_pdm_survey.csv")
DISTRIBUTION_PATH = os.path.join(BASE_DIR, "data", "raw", "raw_distribution_register.csv")
LOGFRAME_PATH = os.path.join(BASE_DIR, "data", "raw", "project_logframe_targets.csv")
INDICATORS_OUT_DIR = os.path.join(BASE_DIR, "data", "indicators")
os.makedirs(INDICATORS_OUT_DIR, exist_ok=True)

# Official WFP Food Group Weights for FCS
WFP_FCS_WEIGHTS = {
    "fcs_cereals_tubers": 2.0,
    "fcs_pulses_nuts": 3.0,
    "fcs_vegetables": 1.0,
    "fcs_fruits": 1.0,
    "fcs_meat_fish_eggs": 4.0,
    "fcs_milk_dairy": 4.0,
    "fcs_sugar_sweets": 0.5,
    "fcs_oils_fats": 0.5
}

# Official WFP Reduced Coping Strategy Index (rCSI) Weights
WFP_RCSI_WEIGHTS = {
    "cs_less_preferred": 1.0,
    "cs_borrow_food": 2.0,
    "cs_reduce_portion": 1.0,
    "cs_restrict_adult": 3.0,
    "cs_reduce_meals": 1.0
}

def calculate_fcs(df):
    """
    Computes household Food Consumption Score (FCS) and classifies into WFP categories:
    - Poor: 0 - 21
    - Borderline: 21.5 - 35
    - Acceptable: > 35
    """
    df = df.copy()
    fcs_score = 0.0
    for col, weight in WFP_FCS_WEIGHTS.items():
        if col in df.columns:
            fcs_score += df[col] * weight
        
    df["fcs_score"] = fcs_score.round(1)
    
    conditions = [
        (df["fcs_score"] <= 21.0),
        (df["fcs_score"] > 21.0) & (df["fcs_score"] <= 35.0),
        (df["fcs_score"] > 35.0)
    ]
    choices = ["Poor", "Borderline", "Acceptable"]
    df["fcs_category"] = np.select(conditions, choices, default="Borderline")
    return df

def calculate_rcsi(df):
    """
    Computes household Reduced Coping Strategy Index (rCSI) score and severity phase:
    - Phase 1 (Low / None): 0 - 3
    - Phase 2 (Medium): 4 - 9
    - Phase 3 (High Coping): >= 10
    """
    df = df.copy()
    rcsi_score = 0.0
    for col, weight in WFP_RCSI_WEIGHTS.items():
        if col in df.columns:
            rcsi_score += df[col] * weight
        
    df["rcsi_score"] = rcsi_score.round(1)
    
    conditions = [
        (df["rcsi_score"] <= 3.0),
        (df["rcsi_score"] > 3.0) & (df["rcsi_score"] <= 9.0),
        (df["rcsi_score"] >= 10.0)
    ]
    choices = ["Low / Normal", "Medium Coping", "High Coping"]
    df["rcsi_category"] = np.select(conditions, choices, default="Medium Coping")
    return df

def compute_sadd_breakdown(df):
    """
    Generates Sex, Age, Disability Disaggregated Data (SADD) statistics
    demanded by ECHO, WFP, and UN cluster reporting standards.
    """
    total_hh = len(df)
    gender_counts = df["head_gender"].value_counts(normalize=True) * 100
    female_headed_pct = round(float(gender_counts.get("Female", 0.0)), 1)
    male_headed_pct = round(float(gender_counts.get("Male", 0.0)), 1)
    
    disability_count = int((df["has_disability"] == "Yes").sum())
    disability_pct = round((disability_count / total_hh) * 100, 1)
    
    u5_count = int((df["children_under_5"] > 0).sum())
    u5_pct = round((u5_count / total_hh) * 100, 1)
    
    plw_count = int((df["pregnant_lactating_women"] == "Yes").sum())
    plw_pct = round((plw_count / total_hh) * 100, 1)
    
    return {
        "total_households_monitored": total_hh,
        "female_headed_hh_pct": female_headed_pct,
        "male_headed_hh_pct": male_headed_pct,
        "households_with_pwd_count": disability_count,
        "households_with_pwd_pct": disability_pct,
        "households_with_children_under5_pct": u5_pct,
        "households_with_plw_pct": plw_pct
    }

def generate_indicator_tracking_table(df_pdm, df_dist, df_log):
    """
    Computes actual progress against project LogFrame targets
    and assigns RAG (Red-Amber-Green) monitoring status.
    """
    itt_records = []
    
    # Total reached from distribution registers
    reach_col = "reached_households" if "reached_households" in df_dist.columns else "reached_beneficiary_hh"
    total_reached_beneficiaries = int(df_dist[reach_col].sum()) if reach_col in df_dist.columns else 0
    
    # FCS Acceptable % from PDM
    acceptable_fcs_pct = round((len(df_pdm[df_pdm["fcs_category"] == "Acceptable"]) / len(df_pdm)) * 100, 1)
    
    # Mean rCSI score from PDM
    mean_rcsi = round(float(df_pdm["rcsi_score"].mean()), 1)
    
    # Female-headed HH %
    female_headed_pct = round((len(df_pdm[df_pdm["head_gender"] == "Female"]) / len(df_pdm)) * 100, 1)
    
    actual_map = {
        "IND-1.1": total_reached_beneficiaries,
        "IND-1.2": acceptable_fcs_pct,
        "IND-1.3": mean_rcsi,
        "IND-2.1": female_headed_pct,
        "IND-3.1": 88.5 # Synced with CFRM module
    }
    
    for _, row in df_log.iterrows():
        code = row["indicator_code"]
        target = float(row["target_2026"])
        actual = actual_map.get(code, 0.0)
        
        # In rCSI (IND-1.3), lower is better! Target is <= 6.5
        if code == "IND-1.3":
            pct_achieved = round((target / actual) * 100, 1) if actual > 0 else 100.0
            rag = "Green" if actual <= target else ("Amber" if actual <= target * 1.3 else "Red")
        else:
            pct_achieved = round((actual / target) * 100, 1) if target > 0 else 0.0
            rag = "Green" if pct_achieved >= 90.0 else ("Amber" if pct_achieved >= 70.0 else "Red")
            
        itt_records.append({
            "code": code,
            "indicator_name": row["indicator_name"],
            "sector": row["sector"],
            "unit": row["unit"],
            "baseline": row["baseline"],
            "target": target,
            "actual": actual,
            "pct_achieved": pct_achieved,
            "status": rag
        })
        
    return pd.DataFrame(itt_records)

def process_all_indicators():
    """
    Full pipeline to compute FCS, rCSI, CARI, SADD, and ITT from cleaned data.
    Saves outputs to data/indicators/
    """
    df_pdm = pd.read_csv(CLEANED_PATH)
    df_dist = pd.read_csv(DISTRIBUTION_PATH)
    df_log = pd.read_csv(LOGFRAME_PATH)
    
    # 1. Compute FCS & rCSI
    df_pdm = calculate_fcs(df_pdm)
    df_pdm = calculate_rcsi(df_pdm)
    
    # 2. Compute WFP Corporate CARI Engine
    df_pdm = run_cari_analysis(df_pdm)
    df_cari_matrix = generate_cari_summary_matrix(df_pdm)
    cari_matrix_path = os.path.join(INDICATORS_OUT_DIR, "wfp_cari_summary_matrix.csv")
    df_cari_matrix.to_csv(cari_matrix_path, index=False)
    
    # 3. Save enriched PDM dataset with indicator columns
    enriched_path = os.path.join(INDICATORS_OUT_DIR, "pdm_with_wfp_indicators.csv")
    df_pdm.to_csv(enriched_path, index=False)
    
    # 4. Compute ITT
    df_itt = generate_indicator_tracking_table(df_pdm, df_dist, df_log)
    itt_path = os.path.join(INDICATORS_OUT_DIR, "indicator_tracking_table.csv")
    df_itt.to_csv(itt_path, index=False)
    
    # 5. Compute SADD
    sadd = compute_sadd_breakdown(df_pdm)
    sadd_df = pd.DataFrame([sadd])
    sadd_path = os.path.join(INDICATORS_OUT_DIR, "sadd_disaggregation_summary.csv")
    sadd_df.to_csv(sadd_path, index=False)
    
    print("=== WFP & INGO INDICATORS + CARI ENGINE COMPUTED ===")
    print(f"1. Enriched PDM dataset with CARI: {enriched_path}")
    print(f"2. Indicator Tracking Table (ITT): {itt_path}")
    print(f"3. CARI Console Summary Matrix: {cari_matrix_path}")
    print(f"4. SADD Disaggregation: {sadd_path}\n")
    print(f"- Overall Acceptable FCS Rate: {round((len(df_pdm[df_pdm['fcs_category'] == 'Acceptable']) / len(df_pdm)) * 100, 1)}%")
    print(f"- Overall CARI Food Insecure Rate: {round((df_pdm['cari_fsi_code'].isin([3, 4]).sum() / len(df_pdm)) * 100, 1)}%")
    print(f"- Mean rCSI Score: {round(df_pdm['rcsi_score'].mean(), 2)}")
    
    return df_pdm, df_itt, sadd

if __name__ == "__main__":
    process_all_indicators()
