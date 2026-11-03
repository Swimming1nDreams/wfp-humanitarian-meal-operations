"""
WFP & Humanitarian Partner MEAL Portfolio Project
Module 5: Cluster Interoperability (UN OCHA 4Ws & DHIS2 API Formats)
Author: M&E & Data Assistant Candidate
Implements:
1. UN OCHA 4Ws (Who does What, Where, When) standardized reporting matrix with MIMU P-codes.
2. DHIS2 DataValueSets JSON payload generation for HMIS / donor integration (Sun Community Health / Global Fund).
"""

import os
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# MIMU P-Code Dictionary
MIMU_MAPPING = {
    "Mandalay": {
        "admin1_pcode": "MMR004",
        "admin1_name": "Mandalay Region",
        "admin3_pcode": "MMR004001",
        "district": "Mandalay District",
        "cluster": "Food Security & MCCT",
        "donor": "WFP / LIFT"
    },
    "Dawei": {
        "admin1_pcode": "MMR007",
        "admin1_name": "Tanintharyi Region",
        "admin3_pcode": "MMR007001",
        "district": "Dawei District",
        "cluster": "Education & Emergency Cash",
        "donor": "ECHO / UNICEF"
    },
    "Lashio": {
        "admin1_pcode": "MMR014",
        "admin1_name": "Shan State (North)",
        "admin3_pcode": "MMR014001",
        "district": "Lashio District",
        "cluster": "Emergency Food Security (FSAC)",
        "donor": "WFP Emergency"
    },
    "Bogale": {
        "admin1_pcode": "MMR017",
        "admin1_name": "Ayeyarwady Region",
        "admin3_pcode": "MMR017006",
        "district": "Pyapon District",
        "cluster": "Community Health & Cash",
        "donor": "Global Fund / 3MDG"
    }
}

def generate_ocha_4ws_matrix(df_pdm, df_dist):
    """
    Synthesizes distribution register and PDM SADD metrics into standard
    UN OCHA 4Ws (Who, What, Where, When) cluster matrix format.
    """
    rows_4ws = []
    
    # Group distribution by township and modality
    for (t_name, modality), group in df_dist.groupby(["township", "modality"]):
        info = MIMU_MAPPING.get(t_name, {})
        partner = group["implementing_partner"].iloc[0]
        
        # PDM sample for this township to derive SADD ratios
        pdm_t = df_pdm[df_pdm["township"] == t_name]
        total_sample = len(pdm_t) if len(pdm_t) > 0 else 1
        
        female_ratio = (pdm_t["head_gender"] == "Female").sum() / total_sample
        u5_ratio = (pdm_t["children_under_5"] > 0).sum() / total_sample
        pwd_ratio = (pdm_t["has_disability"] == "Yes").sum() / total_sample
        
        planned_hh = int(group["planned_households"].sum())
        reached_hh = int(group["reached_households"].sum())
        
        # Estimate individuals (assuming avg HH size 4.8)
        avg_hh_size = 4.8
        total_ind = int(reached_hh * avg_hh_size)
        female_ind = int(total_ind * 0.52)
        male_ind = total_ind - female_ind
        u5_ind = int(reached_hh * 0.65)
        pwd_ind = int(total_ind * 0.08)
        
        rows_4ws.append({
            "Reporting Organization": "UN World Food Programme (WFP) & Partners",
            "Implementing Partner (Who)": partner,
            "Cluster / Sector": info.get("cluster", "Food Security"),
            "Activity Description (What)": f"Unconditional {modality} to crisis-affected households",
            "Modality": modality,
            "State / Region": info.get("admin1_name", ""),
            "Admin 1 P-Code": info.get("admin1_pcode", ""),
            "Township (Where)": t_name,
            "Admin 3 P-Code": info.get("admin3_pcode", ""),
            "Reporting Month (When)": "August - October 2026",
            "Planned HHs": planned_hh,
            "Reached HHs": reached_hh,
            "Total Individuals Reached": total_ind,
            "Female Individuals": female_ind,
            "Male Individuals": male_ind,
            "Children Under 5": u5_ind,
            "Persons with Disabilities (PwD)": pwd_ind,
            "Total Cash Disbursed (MMK)": int(group["actual_disbursed_cash_mmk"].sum()),
            "Total Food Distributed (KG)": int(group["actual_food_kg"].sum()),
            "Donor / Funding Source": info.get("donor", "WFP Core")
        })
        
    df_4ws = pd.DataFrame(rows_4ws)
    return df_4ws

def generate_dhis2_payload(df_pdm, period="202608"):
    """
    Constructs a DHIS2 DataValueSets JSON export payload.
    Compatible with DHIS2 Web API `/api/dataValueSets`.
    """
    data_values = []
    
    # DHIS2 Data Elements mapping
    DE_MAPPING = {
        "FCS_ACCEPTABLE": "fcs_acc_de_01",
        "FCS_POOR": "fcs_poor_de_02",
        "PLW_REACHED": "plw_count_de_03",
        "PWD_REACHED": "pwd_count_de_04"
    }
    
    for t_name, info in MIMU_MAPPING.items():
        sub = df_pdm[df_pdm["township"] == t_name]
        if len(sub) == 0:
            continue
            
        org_unit_id = info["admin3_pcode"]
        
        # 1. FCS Acceptable count
        acc_count = (sub["fcs_category"] == "Acceptable").sum() if "fcs_category" in sub.columns else 0
        data_values.append({
            "dataElement": DE_MAPPING["FCS_ACCEPTABLE"],
            "period": period,
            "orgUnit": org_unit_id,
            "value": str(acc_count),
            "comment": f"WFP PDM Survey {t_name} FCS Acceptable HHs"
        })
        
        # 2. FCS Poor count
        poor_count = (sub["fcs_category"] == "Poor").sum() if "fcs_category" in sub.columns else 0
        data_values.append({
            "dataElement": DE_MAPPING["FCS_POOR"],
            "period": period,
            "orgUnit": org_unit_id,
            "value": str(poor_count),
            "comment": f"WFP PDM Survey {t_name} FCS Poor HHs"
        })
        
        # 3. PLW count
        plw_count = (sub["pregnant_lactating_women"] == "Yes").sum()
        data_values.append({
            "dataElement": DE_MAPPING["PLW_REACHED"],
            "period": period,
            "orgUnit": org_unit_id,
            "value": str(plw_count),
            "comment": f"Nutrition Cash PLW Beneficiaries in {t_name}"
        })
        
    payload = {
        "dataSet": "WFP_MEAL_MONTHLY_REPORT",
        "completeDate": "2026-10-31",
        "period": period,
        "orgUnit": "MMR_COUNTRY_LEVEL",
        "dataValues": data_values
    }
    return payload

if __name__ == "__main__":
    from dqa_cleaning_pipeline import run_dqa_pipeline
    from wfp_indicators import calculate_fcs
    
    df_clean, _, _ = run_dqa_pipeline()
    df_ind = calculate_fcs(df_clean)
    df_dist = pd.read_csv(os.path.join(BASE_DIR, "data", "raw", "raw_distribution_register.csv"))
    
    df_4ws = generate_ocha_4ws_matrix(df_ind, df_dist)
    dhis2_json = generate_dhis2_payload(df_ind)
    
    df_4ws.to_csv(os.path.join(REPORTS_DIR, "ocha_4ws_humanitarian_matrix.csv"), index=False)
    with open(os.path.join(REPORTS_DIR, "dhis2_datavaluesets_export.json"), "w") as f:
        json.dump(dhis2_json, f, indent=2)
        
    print("[OK] UN OCHA 4Ws Matrix generated!")
    print("[OK] DHIS2 JSON payload generated!")
