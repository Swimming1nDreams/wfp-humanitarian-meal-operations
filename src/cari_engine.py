"""
WFP & Humanitarian Partner MEAL Portfolio Project
Module 3: WFP CARI (Consolidated Approach for Reporting Indicators) Engine
Author: M&E & Data Assistant Candidate
Methodology: Official WFP Corporate Guidance for CARI (RAM / VAM).
Synthesizes household food security across two domains:
  1. Current Food Consumption: Food Consumption Score (FCS)
  2. Coping Capacity:
     - Economic Vulnerability: Food Expenditure Share (FES)
     - Asset Depletion: Livelihood Coping Strategies (LCS-FS)
Produces the 4-point Food Security Index (FSI) & Official CARI Console Matrix.
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDICATORS_DIR = os.path.join(BASE_DIR, "data", "indicators")
os.makedirs(INDICATORS_DIR, exist_ok=True)

def classify_fcs_cari_domain(fcs_score):
    """
    CARI 4-point coding for Current Consumption (FCS):
    - Score > 35 (Acceptable) -> 1 (Food Secure)
    - Score 21.5 - 35 (Borderline) -> 3 (Moderately Insecure)
    - Score <= 21 (Poor) -> 4 (Severely Insecure)
    (Note: In CARI standard 4-point scale, Borderline represents Moderate Insecurity Code 3).
    """
    if fcs_score > 35.0:
        return 1
    elif fcs_score > 21.0:
        return 3
    else:
        return 4

def classify_fes_cari_domain(fes_pct):
    """
    CARI 4-point coding for Economic Vulnerability (Food Expenditure Share):
    - < 50% -> 1 (Food Secure)
    - 50% - 64.9% -> 2 (Marginally Secure)
    - 65% - 74.9% -> 3 (Moderately Insecure)
    - >= 75% -> 4 (Severely Insecure)
    """
    if fes_pct < 50.0:
        return 1
    elif fes_pct < 65.0:
        return 2
    elif fes_pct < 75.0:
        return 3
    else:
        return 4

def classify_lcs_cari_domain(lcs_category):
    """
    CARI 4-point coding for Asset Depletion (Livelihood Coping Strategies):
    - None -> 1 (Food Secure)
    - Stress -> 2 (Marginally Secure)
    - Crisis -> 3 (Moderately Insecure)
    - Emergency -> 4 (Severely Insecure)
    """
    mapping = {
        "None": 1,
        "Stress": 2,
        "Crisis": 3,
        "Emergency": 4
    }
    return mapping.get(str(lcs_category).title(), 1)

def run_cari_analysis(df):
    """
    Executes full WFP CARI 4-point algorithm on DataFrame:
    Requires: 'fcs_score', 'food_expenditure_share_pct', 'lcs_highest_category'
    Returns enriched DataFrame with CARI codes, overall Food Security Index (FSI),
    and the corporate CARI Summary Console Matrix.
    """
    df = df.copy()

    # 1. Domain 1: Current Consumption Code (1, 3, or 4)
    df["cari_current_consumption"] = df["fcs_score"].apply(classify_fcs_cari_domain)
    
    # 2. Domain 2: Coping Capacity Codes
    # 2A: Food Expenditure Share
    df["cari_fes_code"] = df["food_expenditure_share_pct"].apply(classify_fes_cari_domain)
    # 2B: Livelihood Coping Strategies
    df["cari_lcs_code"] = df["lcs_highest_category"].apply(classify_lcs_cari_domain)
    
    # Combine Coping Capacity (average of FES and LCS, rounded)
    df["cari_coping_capacity"] = np.round((df["cari_fes_code"] + df["cari_lcs_code"]) / 2.0).astype(int)
    
    # 3. Overall Food Security Index (FSI)
    # CARI composite score = (Current Consumption + Coping Capacity) / 2
    df["cari_raw_score"] = (df["cari_current_consumption"] + df["cari_coping_capacity"]) / 2.0
    # WFP standard round-half-up classification:
    # 1.0 - 1.49 -> 1 (Food Secure)
    # 1.5 - 2.49 -> 2 (Marginally Secure)
    # 2.5 - 3.49 -> 3 (Moderately Insecure)
    # 3.5 - 4.00 -> 4 (Severely Insecure)
    conditions = [
        (df["cari_raw_score"] < 1.5),
        (df["cari_raw_score"] >= 1.5) & (df["cari_raw_score"] < 2.5),
        (df["cari_raw_score"] >= 2.5) & (df["cari_raw_score"] < 3.5),
        (df["cari_raw_score"] >= 3.5)
    ]
    fsi_codes = [1, 2, 3, 4]
    fsi_labels = [
        "1 - Food Secure",
        "2 - Marginally Secure",
        "3 - Moderately Insecure",
        "4 - Severely Insecure"
    ]
    df["cari_fsi_code"] = np.select(conditions, fsi_codes, default=2)
    df["cari_fsi_label"] = np.select(conditions, fsi_labels, default="2 - Marginally Secure")
    
    # Binary Food Insecure Flag (Codes 3 and 4)
    df["is_food_insecure"] = df["cari_fsi_code"].isin([3, 4])
    
    return df

def generate_cari_summary_matrix(df):
    """
    Builds the official WFP CARI Console table cross-tabulating Current Consumption
    and Coping Capacity with population percentages.
    """
    total = len(df)
    
    summary = {
        "Food Security Category": [
            "Food Secure (Phase 1)",
            "Marginally Secure (Phase 2)",
            "Moderately Insecure (Phase 3)",
            "Severely Insecure (Phase 4)",
            "OVERALL FOOD INSECURE (Phase 3+4)"
        ],
        "Households": [
            (df["cari_fsi_code"] == 1).sum(),
            (df["cari_fsi_code"] == 2).sum(),
            (df["cari_fsi_code"] == 3).sum(),
            (df["cari_fsi_code"] == 4).sum(),
            (df["cari_fsi_code"].isin([3, 4])).sum()
        ],
        "Percentage (%)": [
            round(((df["cari_fsi_code"] == 1).sum() / total) * 100, 1),
            round(((df["cari_fsi_code"] == 2).sum() / total) * 100, 1),
            round(((df["cari_fsi_code"] == 3).sum() / total) * 100, 1),
            round(((df["cari_fsi_code"] == 4).sum() / total) * 100, 1),
            round(((df["cari_fsi_code"].isin([3, 4])).sum() / total) * 100, 1)
        ]
    }
    return pd.DataFrame(summary)

if __name__ == "__main__":
    pdm_path = os.path.join(INDICATORS_DIR, "pdm_with_wfp_indicators.csv")
    if os.path.exists(pdm_path):
        df = pd.read_csv(pdm_path)
        df_cari = run_cari_analysis(df)
        matrix = generate_cari_summary_matrix(df_cari)
        print("=== WFP CARI CONSOLE SUMMARY MATRIX ===")
        print(matrix.to_string(index=False))
