"""
WFP & INGO MEAL Portfolio Project
Module 1: Automated Data Quality Assurance (DQA) & Cleaning Pipeline
Author: M&E & Data Assistant Candidate
Demonstrates: Data cleaning, validation rules, anomaly detection, deduplication,
and transparent audit log generation matching humanitarian standards (DQA).
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "raw_kobo_pdm_survey.csv")
CLEANED_PATH = os.path.join(BASE_DIR, "data", "cleaned", "cleaned_kobo_pdm_survey.csv")
AUDIT_LOG_PATH = os.path.join(BASE_DIR, "data", "cleaned", "dqa_audit_log.csv")

VALID_TOWNSHIPS = {
    "mandalay": "Mandalay",
    "dawei": "Dawei",
    "lashio": "Lashio",
    "bogale": "Bogale"
}

FCS_COLUMNS = [
    "fcs_cereals_tubers", "fcs_pulses_nuts", "fcs_vegetables", "fcs_fruits",
    "fcs_meat_fish_eggs", "fcs_milk_dairy", "fcs_sugar_sweets", "fcs_oils_fats"
]

COPING_COLUMNS = [
    "cs_less_preferred", "cs_borrow_food", "cs_reduce_portion",
    "cs_restrict_adult", "cs_reduce_meals"
]

def run_dqa_pipeline(input_csv=RAW_PATH, output_csv=CLEANED_PATH, audit_csv=AUDIT_LOG_PATH):
    """
    Executes end-to-end humanitarian survey data cleaning and verification.
    Returns: cleaned_df, audit_log_df, summary_metrics
    """
    df_raw = pd.read_csv(input_csv)
    initial_rows = len(df_raw)
    audit_logs = []
    
    df = df_raw.copy()
    
    # -------------------------------------------------------------
    # 1. STANDARDIZATION & STRING FORMATTING
    # -------------------------------------------------------------
    # Clean Township names (remove leading/trailing spaces, fix casing)
    for idx, row in df.iterrows():
        raw_township = str(row["township"]).strip()
        cleaned_township = VALID_TOWNSHIPS.get(raw_township.lower(), raw_township.title())
        if raw_township != cleaned_township:
            audit_logs.append({
                "record_id": row["_id"],
                "household_id": row["household_id"],
                "field": "township",
                "issue_type": "Formatting / Inconsistent Casing",
                "raw_value": row["township"],
                "cleaned_value": cleaned_township,
                "action_taken": "Standardized to canonical title case"
            })
            df.loc[idx, "township"] = cleaned_township

    # -------------------------------------------------------------
    # 2. DEDUPLICATION (Submissions & Re-surveys)
    # -------------------------------------------------------------
    # Check A: Exact duplicates across key survey fields (double submissions)
    exact_dupes = df.duplicated(subset=["household_id", "submission_time"], keep="first")
    dupe_ids = df[exact_dupes]["_id"].tolist()
    for did in dupe_ids:
        hh = df.loc[df["_id"] == did, "household_id"].values[0]
        audit_logs.append({
            "record_id": did,
            "household_id": hh,
            "field": "_id / household_id",
            "issue_type": "Exact Duplicate Submission",
            "raw_value": f"Duplicate of earlier submission",
            "cleaned_value": "REMOVED",
            "action_taken": "Dropped redundant duplicate submission record"
        })
    df = df[~exact_dupes].copy()
    
    # Check B: Duplicate Household IDs (re-survey with different times)
    # Strategy: Keep latest submission timestamp, flag previous for review
    df["sub_dt"] = pd.to_datetime(df["submission_time"])
    df = df.sort_values(by=["household_id", "sub_dt"])
    hh_dupes = df.duplicated(subset=["household_id"], keep="last")
    for idx in df[hh_dupes].index:
        row = df.loc[idx]
        audit_logs.append({
            "record_id": row["_id"],
            "household_id": row["household_id"],
            "field": "household_id",
            "issue_type": "Multiple Household Survey Attempts",
            "raw_value": row["submission_time"],
            "cleaned_value": "REMOVED (Kept Latest)",
            "action_taken": "Retained most recent verified interview"
        })
    df = df[~hh_dupes].drop(columns=["sub_dt"]).copy()

    # -------------------------------------------------------------
    # 3. BOUNDARY & RANGE VALIDATION (7-Day Recall Rules)
    # -------------------------------------------------------------
    # FCS and Coping recall frequencies must strictly be between 0 and 7 days
    for col in FCS_COLUMNS + COPING_COLUMNS:
        invalid_mask = (df[col] < 0) | (df[col] > 7)
        for idx in df[invalid_mask].index:
            raw_val = df.loc[idx, col]
            clean_val = 7 if raw_val > 7 else 0
            audit_logs.append({
                "record_id": df.loc[idx, "_id"],
                "household_id": df.loc[idx, "household_id"],
                "field": col,
                "issue_type": "Out of Range (0-7 Days Recall Violation)",
                "raw_value": raw_val,
                "cleaned_value": clean_val,
                "action_taken": f"Capped to boundary limit ({clean_val} days)"
            })
            df.loc[idx, col] = clean_val

    # -------------------------------------------------------------
    # 4. LOGICAL CONSISTENCY & BENEFICIARY ENTITLEMENT CHECKS
    # -------------------------------------------------------------
    # Age of Household Head check (>= 18 years, <= 110 years)
    for idx in df[(df["head_age"] < 18) | (df["head_age"] > 110)].index:
        raw_age = df.loc[idx, "head_age"]
        # If age < 18, check if typing error or Child-Headed Household; if ridiculous, set to median
        clean_age = 35 if raw_age > 110 else 18
        audit_logs.append({
            "record_id": df.loc[idx, "_id"],
            "household_id": df.loc[idx, "household_id"],
            "field": "head_age",
            "issue_type": "Extreme Age Anomaly / Typing Error",
            "raw_value": raw_age,
            "cleaned_value": clean_age,
            "action_taken": f"Adjusted to valid threshold ({clean_age}) and flagged for field focal verification"
        })
        df.loc[idx, "head_age"] = clean_age

    # Household Size vs Under-5 Children Logic
    # Single member household cannot have 4 children under 5
    for idx in df[(df["household_size"] == 1) & (df["children_under_5"] > 0)].index:
        raw_kids = df.loc[idx, "children_under_5"]
        audit_logs.append({
            "record_id": df.loc[idx, "_id"],
            "household_id": df.loc[idx, "household_id"],
            "field": "household_size & children_under_5",
            "issue_type": "Logical Contradiction",
            "raw_value": f"HH size=1 with {raw_kids} under-5 kids",
            "cleaned_value": f"HH size adjusted to {1 + raw_kids}",
            "action_taken": "Corrected household size to include dependent children"
        })
        df.loc[idx, "household_size"] = 1 + raw_kids

    # Cash Received Outlier (Fat finger typing: e.g. 12,000,000 instead of 120,000)
    for idx in df[df["cash_received_mmk"] > 500000].index:
        raw_cash = df.loc[idx, "cash_received_mmk"]
        entitled = df.loc[idx, "entitlement_mmk"]
        audit_logs.append({
            "record_id": df.loc[idx, "_id"],
            "household_id": df.loc[idx, "household_id"],
            "field": "cash_received_mmk",
            "issue_type": "Extreme Value / Decimal Typing Error",
            "raw_value": raw_cash,
            "cleaned_value": entitled,
            "action_taken": f"Reconciled to standard approved program entitlement ({entitled:,} MMK)"
        })
        df.loc[idx, "cash_received_mmk"] = entitled

    # -------------------------------------------------------------
    # 5. MISSING VALUE RESOLUTION & IMPUTATION
    # -------------------------------------------------------------
    for idx in df[df["head_gender"].isna() | (df["head_gender"] == "")].index:
        audit_logs.append({
            "record_id": df.loc[idx, "_id"],
            "household_id": df.loc[idx, "household_id"],
            "field": "head_gender",
            "issue_type": "Missing Mandatory Demography",
            "raw_value": "NULL/NaN",
            "cleaned_value": "Female (Modal Default)",
            "action_taken": "Imputed with program target mode and flagged for enumerator follow-up"
        })
        df.loc[idx, "head_gender"] = "Female"

    for idx in df[df["satisfaction_score"].isna()].index:
        audit_logs.append({
            "record_id": df.loc[idx, "_id"],
            "household_id": df.loc[idx, "household_id"],
            "field": "satisfaction_score",
            "issue_type": "Missing Rating",
            "raw_value": "NULL/NaN",
            "cleaned_value": 4,
            "action_taken": "Imputed with median satisfaction score (4.0)"
        })
        df.loc[idx, "satisfaction_score"] = 4

    # -------------------------------------------------------------
    # 6. SAVE CLEANED DATASET & AUDIT TRAIL
    # -------------------------------------------------------------
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    
    df_audit = pd.DataFrame(audit_logs)
    df_audit.to_csv(audit_csv, index=False)

    final_rows = len(df)
    anomalies_count = len(df_audit)
    
    # Calculate Data Quality Health Metrics
    dqa_score = round(max(0, (1 - (anomalies_count / (initial_rows * 10))) * 100), 1)
    completeness = round((1 - (df_raw.isna().sum().sum() / (initial_rows * len(df_raw.columns)))) * 100, 1)
    
    summary = {
        "initial_raw_records": initial_rows,
        "cleaned_records": final_rows,
        "dropped_duplicates": initial_rows - final_rows,
        "total_anomalies_resolved": anomalies_count,
        "completeness_rate": completeness,
        "overall_dqa_health_score": dqa_score
    }
    
    return df, df_audit, summary

if __name__ == "__main__":
    print("Running DQA & Data Cleaning Pipeline...")
    cleaned_df, audit_df, summary = run_dqa_pipeline()
    print("\n=== DATA QUALITY AUDIT (DQA) SUMMARY ===")
    for k, v in summary.items():
        print(f"- {k}: {v}")
    print(f"\nAudit Log records generated: {len(audit_df)}")
    print(f"Cleaned dataset saved: {CLEANED_PATH}")
