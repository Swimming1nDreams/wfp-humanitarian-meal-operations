"""
WFP & Humanitarian Partner MEAL Portfolio Project
Enterprise Simulated Data Generator (UN/WFP Standard)
Generates:
1. KoboToolbox PDM Survey (450+ records) with CARI indicators, GPS, timestamps, SADD, and intentional DQA anomalies.
2. Distribution Monitoring Registers (Cash & Food rations).
3. AAP/CFRM Feedback & Safeguarding Tickets (including PSEA).
4. Results Framework / LogFrame Indicator Tracking Data (ITT).
5. Official MIMU P-Codes & Cluster Metadata.
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Set deterministic seed for reproducible demonstration
random.seed(42)
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# Myanmar Hubs & MIMU P-Codes
TOWNSHIPS = {
    "Mandalay": {
        "admin1_pcode": "MMR004",
        "admin1_name": "Mandalay Region",
        "admin3_pcode": "MMR004001",
        "partner": "Terre des hommes (Tdh)",
        "modality": "Maternal & Child Cash Transfer (MCCT)",
        "base_entitlement_mmk": 120000,
        "base_ration_kg": 0,
        "lat_center": 21.9750,
        "lon_center": 96.0836,
        "villages": ["Chanayethazan-East", "Mahaaungmyay-Ward 4", "Pyigyidagun-Ward 7", "Amarapura-Shwekyetyet"]
    },
    "Dawei": {
        "admin1_pcode": "MMR007",
        "admin1_name": "Tanintharyi Region",
        "admin3_pcode": "MMR007001",
        "partner": "Shwe Kyun Thar Network (SKT)",
        "modality": "Education & Emergency Cash Assistance",
        "base_entitlement_mmk": 150000,
        "base_ration_kg": 25,
        "lat_center": 14.0828,
        "lon_center": 98.1940,
        "villages": ["Zahar Village", "Maungmagan Coastal", "Kyaukmezein", "Launglon North"]
    },
    "Lashio": {
        "admin1_pcode": "MMR014",
        "admin1_name": "Shan State (North)",
        "admin3_pcode": "MMR014001",
        "partner": "Best Shelter",
        "modality": "Emergency Food Basket & Nutrition",
        "base_entitlement_mmk": 80000,
        "base_ration_kg": 50,
        "lat_center": 22.9357,
        "lon_center": 97.7492,
        "villages": ["Mansan IDP Site", "Ward 12 Camp", "Namhu Rural", "Hsenwi Outskirts"]
    },
    "Bogale": {
        "admin1_pcode": "MMR017",
        "admin1_name": "Ayeyarwady Region",
        "admin3_pcode": "MMR017006",
        "partner": "Myanmar Youth Stars (MYS)",
        "modality": "Community Health & Livelihood Cash",
        "base_entitlement_mmk": 100000,
        "base_ration_kg": 0,
        "lat_center": 16.2951,
        "lon_center": 95.4014,
        "villages": ["Setsan Village", "Kyetphamweshay", "Htawpaing", "Kyunnyogyi"]
    }
}

ENUMERATORS = [f"ENUM-{i:03d}" for i in range(1, 13)]

def generate_pdm_data(n_records=450):
    records = []
    base_start_date = datetime(2026, 8, 1)
    
    # Track previous submission time and location for enumerators to generate realistic / anomalous speeds
    enum_last_state = {}

    for i in range(1, n_records + 1):
        township_name = random.choice(list(TOWNSHIPS.keys()))
        t_info = TOWNSHIPS[township_name]
        village = random.choice(t_info["villages"])
        enumerator = random.choice(ENUMERATORS)
        
        # Interview start and submission timing
        day_offset = random.randint(0, 75)
        interview_hour = random.randint(8, 16)
        interview_minute = random.randint(0, 45)
        start_time = base_start_date + timedelta(days=day_offset, hours=interview_hour, minutes=interview_minute)
        
        # Duration simulation (Normal: 25-45 mins. Suspicious speeder: 4-6 mins)
        is_speeder_enum = (enumerator in ["ENUM-004", "ENUM-009"]) and random.random() < 0.40
        if is_speeder_enum:
            duration_minutes = round(random.uniform(3.5, 6.8), 1)
        else:
            duration_minutes = round(np.random.normal(32.0, 7.5), 1)
            duration_minutes = max(12.0, duration_minutes)
            
        end_time = start_time + timedelta(minutes=duration_minutes)
        submission_time = end_time + timedelta(minutes=random.randint(1, 15))
        
        # GPS Simulation (with slight Gaussian scatter around village centers)
        lat = t_info["lat_center"] + np.random.normal(0, 0.025)
        lon = t_info["lon_center"] + np.random.normal(0, 0.025)
        gps_accuracy = round(random.uniform(3.2, 14.5), 1)
        
        # Intentional GPS Teleportation anomaly for ENUM-009 (fabrication check)
        if enumerator == "ENUM-009" and random.random() < 0.25:
            # Sudden jump 80km away within 15 minutes!
            lat += 0.75
            lon += 0.75

        # Household Demographics & SADD
        hh_id = f"HH-{township_name[:3].upper()}-{i:04d}"
        hh_gender = random.choices(["Female", "Male"], weights=[0.62, 0.38])[0]
        hh_age = random.randint(19, 78)
        hh_size = random.randint(2, 9)
        has_disability = random.choices(["Yes", "No"], weights=[0.14, 0.86])[0]
        disability_count = random.choice([1, 2]) if has_disability == "Yes" else 0
        child_under5 = random.choices([0, 1, 2, 3], weights=[0.30, 0.45, 0.20, 0.05])[0]
        pregnant_lactating = "Yes" if (hh_gender == "Female" and hh_age < 46 and random.random() < 0.35) else "No"
        
        # Vulnerability factor
        vuln_factor = 0.75 if (has_disability == "Yes" or hh_gender == "Female" or township_name == "Lashio") else 1.05
        
        # Assistance Details
        entitlement_mmk = t_info["base_entitlement_mmk"]
        cash_received = entitlement_mmk if random.random() > 0.06 else int(entitlement_mmk * random.choice([0.5, 0.75, 1.0]))
        food_kg_received = t_info["base_ration_kg"] if random.random() > 0.05 else int(t_info["base_ration_kg"] * 0.8)
        satisfaction_score = random.choices([1, 2, 3, 4, 5], weights=[0.03, 0.07, 0.15, 0.45, 0.30])[0]
        
        # 1. Food Consumption Score (FCS) 7-day recall (0 to 7)
        fcs_staple = min(7, max(1, int(np.random.normal(6.5 * vuln_factor, 1.0))))
        fcs_pulse = min(7, max(0, int(np.random.normal(3.8 * vuln_factor, 1.6))))
        fcs_veg = min(7, max(0, int(np.random.normal(5.2 * vuln_factor, 1.4))))
        fcs_fruit = min(7, max(0, int(np.random.normal(2.5 * vuln_factor, 1.5))))
        fcs_meat = min(7, max(0, int(np.random.normal(3.0 * vuln_factor, 1.7))))
        fcs_dairy = min(7, max(0, int(np.random.normal(1.8 * vuln_factor, 1.4))))
        fcs_sugar = min(7, max(0, int(np.random.normal(4.5 * vuln_factor, 1.8))))
        fcs_oil = min(7, max(0, int(np.random.normal(5.8 * vuln_factor, 1.2))))
        
        # 2. Reduced Coping Strategies (rCSI) 7-day recall (0 to 7)
        cs_less_preferred = min(7, max(0, int(np.random.normal(2.5 / vuln_factor, 1.8))))
        cs_borrow_food = min(7, max(0, int(np.random.normal(1.4 / vuln_factor, 1.5))))
        cs_reduce_portion = min(7, max(0, int(np.random.normal(1.8 / vuln_factor, 1.6))))
        cs_restrict_adult = min(7, max(0, int(np.random.normal(1.1 / vuln_factor, 1.4))))
        cs_reduce_meals = min(7, max(0, int(np.random.normal(0.9 / vuln_factor, 1.2))))

        # 3. WFP CARI: Economic Vulnerability - Food Expenditure Share (FES)
        # 30-day expenditures in MMK
        # If fabricated by ENUM-004, use unnatural round numbers (Benford's Law anomaly)
        if enumerator == "ENUM-004" and random.random() < 0.60:
            exp_food = random.choice([150000, 200000, 250000, 300000, 350000, 400000])
            exp_nonfood = random.choice([50000, 100000, 150000, 200000])
        else:
            base_income = random.randint(220000, 680000)
            food_share_ratio = np.random.beta(5 * (1.2 / vuln_factor), 4) # Skewed towards 55-75% for vulnerable
            food_share_ratio = min(0.92, max(0.25, food_share_ratio))
            exp_food = int(base_income * food_share_ratio + random.randint(-4500, 4500))
            exp_nonfood = int(base_income * (1.0 - food_share_ratio) + random.randint(-4500, 4500))
            exp_food = max(25000, exp_food)
            exp_nonfood = max(10000, exp_nonfood)
            
        exp_total = exp_food + exp_nonfood
        food_expenditure_share = round((exp_food / exp_total) * 100.0, 1)

        # 4. WFP CARI: Asset Depletion - Livelihood Coping Strategies (LCS-FS)
        # Categories: Stress, Crisis, Emergency
        # Stress: sold household assets, spent savings, borrowed food on credit
        # Crisis: sold productive assets, reduced non-food health/education exp, took children out of school
        # Emergency: sold last female breeding animal, sold land/house, begged / high risk
        p_stress = 0.55 if vuln_factor < 1.0 else 0.28
        p_crisis = 0.35 if vuln_factor < 1.0 else 0.12
        p_emerg = 0.18 if vuln_factor < 1.0 else 0.04

        lcs_sold_assets = "Yes" if random.random() < p_stress else "No"
        lcs_spent_savings = "Yes" if random.random() < p_stress else "No"
        lcs_credit_food = "Yes" if random.random() < p_stress else "No"

        lcs_sold_productive = "Yes" if random.random() < p_crisis else "No"
        lcs_reduced_health = "Yes" if random.random() < p_crisis else "No"
        lcs_child_school = "Yes" if random.random() < (p_crisis * 0.7) else "No"

        lcs_sold_land = "Yes" if random.random() < (p_emerg * 0.4) else "No"
        lcs_begged = "Yes" if random.random() < p_emerg else "No"

        # Determine highest severity strategy
        if lcs_sold_land == "Yes" or lcs_begged == "Yes":
            lcs_highest_category = "Emergency"
        elif lcs_sold_productive == "Yes" or lcs_reduced_health == "Yes" or lcs_child_school == "Yes":
            lcs_highest_category = "Crisis"
        elif lcs_sold_assets == "Yes" or lcs_spent_savings == "Yes" or lcs_credit_food == "Yes":
            lcs_highest_category = "Stress"
        else:
            lcs_highest_category = "None"

        # Accountability & Feedback (AAP)
        cfrm_aware = random.choices(["Yes", "No"], weights=[0.78, 0.22])[0]
        used_feedback_channel = "Yes" if (cfrm_aware == "Yes" and satisfaction_score <= 3 and random.random() < 0.6) else "No"

        rec = {
            "_id": 100000 + i,
            "submission_time": submission_time.strftime("%Y-%m-%d %H:%M:%S"),
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_minutes": duration_minutes,
            "enumerator_id": enumerator,
            "township": township_name,
            "admin1_pcode": t_info["admin1_pcode"],
            "admin1_name": t_info["admin1_name"],
            "admin3_pcode": t_info["admin3_pcode"],
            "implementing_partner": t_info["partner"],
            "village_tract": village,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "gps_accuracy_m": gps_accuracy,
            "household_id": hh_id,
            "head_gender": hh_gender,
            "head_age": hh_age,
            "household_size": hh_size,
            "children_under_5": child_under5,
            "pregnant_lactating_women": pregnant_lactating,
            "has_disability": has_disability,
            "disability_count": disability_count,
            "assistance_modality": t_info["modality"],
            "entitlement_mmk": entitlement_mmk,
            "cash_received_mmk": cash_received,
            "food_kg_received": food_kg_received,
            "satisfaction_score": satisfaction_score,
            # FCS Items
            "fcs_cereals_tubers": fcs_staple,
            "fcs_pulses_nuts": fcs_pulse,
            "fcs_vegetables": fcs_veg,
            "fcs_fruits": fcs_fruit,
            "fcs_meat_fish_eggs": fcs_meat,
            "fcs_milk_dairy": fcs_dairy,
            "fcs_sugar_sweets": fcs_sugar,
            "fcs_oils_fats": fcs_oil,
            # rCSI Items
            "cs_less_preferred": cs_less_preferred,
            "cs_borrow_food": cs_borrow_food,
            "cs_reduce_portion": cs_reduce_portion,
            "cs_restrict_adult": cs_restrict_adult,
            "cs_reduce_meals": cs_reduce_meals,
            # Expenditures & FES
            "expenditure_food_mmk": exp_food,
            "expenditure_nonfood_mmk": exp_nonfood,
            "expenditure_total_mmk": exp_total,
            "food_expenditure_share_pct": food_expenditure_share,
            # LCS-FS Indicators
            "lcs_sold_assets": lcs_sold_assets,
            "lcs_spent_savings": lcs_spent_savings,
            "lcs_credit_food": lcs_credit_food,
            "lcs_sold_productive": lcs_sold_productive,
            "lcs_reduced_health": lcs_reduced_health,
            "lcs_child_school": lcs_child_school,
            "lcs_sold_land": lcs_sold_land,
            "lcs_begged": lcs_begged,
            "lcs_highest_category": lcs_highest_category,
            # CFRM AAP
            "cfrm_aware": cfrm_aware,
            "used_feedback_channel": used_feedback_channel
        }
        records.append(rec)
        
    df = pd.DataFrame(records)
    
    # === INTENTIONAL DIRTY DATA INJECTION FOR DQA ENGINE DEMO ===
    # 1. Duplicates: Clone 10 rows completely (simulating double submission on Kobo)
    dupe_rows = df.sample(n=10, random_state=101).copy()
    dupe_rows["_id"] = dupe_rows["_id"] + 800000
    df = pd.concat([df, dupe_rows], ignore_index=True)
    
    # 2. Duplicate Household IDs with different submission timestamps (re-survey error)
    for idx in [15, 42, 88, 120, 210]:
        df.loc[idx, "household_id"] = df.loc[idx - 1, "household_id"]
        
    # 3. Out-of-range FCS (> 7 days or negative)
    df.loc[12, "fcs_cereals_tubers"] = 10  # Invalid > 7
    df.loc[34, "fcs_meat_fish_eggs"] = 9   # Invalid > 7
    df.loc[65, "fcs_vegetables"] = -2      # Invalid < 0
    df.loc[99, "cs_reduce_portion"] = 12   # Invalid > 7
    
    # 4. Inconsistent logic / extreme outlier
    df.loc[18, "head_age"] = 6             # Child head of HH age 6
    df.loc[55, "head_age"] = 195           # Typing mistake: 195 instead of 19 or 95
    df.loc[82, "cash_received_mmk"] = 12000000  # 12 million instead of 120,000 (typing fat finger)
    df.loc[115, "household_size"] = 1
    df.loc[115, "children_under_5"] = 4    # Impossible: size 1 with 4 children
    
    # 5. Missing values in mandatory columns
    df.loc[25, "head_gender"] = np.nan
    df.loc[60, "head_gender"] = None
    df.loc[105, "satisfaction_score"] = np.nan
    df.loc[140, "village_tract"] = ""
    
    # 6. Text casing / whitespace dirty formatting in township
    df.loc[7, "township"] = "mandalay "
    df.loc[22, "township"] = "DAWEI"
    df.loc[45, "township"] = " Lashio"
    df.loc[90, "township"] = "bogale"

    return df

def generate_distribution_register(n_records=30):
    records = []
    base_date = datetime(2026, 8, 5)
    
    for i in range(1, n_records + 1):
        t_name = random.choice(list(TOWNSHIPS.keys()))
        t_info = TOWNSHIPS[t_name]
        dist_date = base_date + timedelta(days=i * 2)
        planned_hh = random.randint(150, 450)
        reached_hh = int(planned_hh * random.uniform(0.92, 1.04))
        planned_cash = planned_hh * t_info["base_entitlement_mmk"]
        actual_cash = reached_hh * t_info["base_entitlement_mmk"]
        planned_food = planned_hh * t_info["base_ration_kg"]
        actual_food = reached_hh * t_info["base_ration_kg"]
        
        records.append({
            "distribution_id": f"DIST-{2026}-{i:03d}",
            "distribution_date": dist_date.strftime("%Y-%m-%d"),
            "township": t_name,
            "admin3_pcode": t_info["admin3_pcode"],
            "implementing_partner": t_info["partner"],
            "modality": t_info["modality"],
            "planned_households": planned_hh,
            "reached_households": reached_hh,
            "planned_cash_mmk": planned_cash,
            "actual_disbursed_cash_mmk": actual_cash,
            "planned_food_kg": planned_food,
            "actual_food_kg": actual_food,
            "distribution_site": random.choice(t_info["villages"]),
            "monitoring_officer": random.choice(["U Kyaw Kyaw", "Daw Su Su", "U Tin Tun", "Daw Aye Aye"])
        })
    return pd.DataFrame(records)

def generate_cfrm_tickets(n_records=90):
    records = []
    base_date = datetime(2026, 8, 10)
    
    categories = [
        ("Category 1: Request for Information", 0.40, "Low", 5),
        ("Category 2: Request for Assistance / Inclusions", 0.30, "Medium", 7),
        ("Category 3: Minor Dissatisfaction / Quality / Delay", 0.18, "Medium", 7),
        ("Category 4: Fraud / Diversion / Misconduct", 0.08, "High", 3),
        ("Category 5: PSEA / Serious Safeguarding Violation", 0.04, "Critical", 1)  # Strict 24h escalation
    ]
    
    channels = ["Hotline Toll-Free", "Help Desk at Site", "Suggestion Box", "Community Focal Point", "Post-Monitoring Interview"]
    statuses = ["Resolved", "Investigating", "Escalated to PSEA Focal", "Pending Review"]
    
    for i in range(1, n_records + 1):
        t_name = random.choice(list(TOWNSHIPS.keys()))
        t_info = TOWNSHIPS[t_name]
        cat_choice = random.choices(categories, weights=[c[1] for c in categories])[0]
        cat_name, _, severity, sla_days = cat_choice
        
        open_date = base_date + timedelta(days=random.randint(0, 70), hours=random.randint(8, 17))
        channel = random.choice(channels)
        gender = random.choices(["Female", "Male", "Anonymous"], weights=[0.55, 0.35, 0.10])[0]
        
        # If Category 5 (PSEA), strict handling
        if "Category 5" in cat_name:
            status = random.choice(["Escalated to PSEA Focal", "Investigating", "Resolved"])
            days_to_resolve = random.randint(1, 3)
        else:
            status = random.choices(statuses[:3] + ["Resolved"], weights=[0.60, 0.15, 0.05, 0.20])[0]
            days_to_resolve = random.randint(1, sla_days + 4)
            
        closed_date = (open_date + timedelta(days=days_to_resolve)).strftime("%Y-%m-%d") if status == "Resolved" else None
        sla_met = "Yes" if (status == "Resolved" and days_to_resolve <= sla_days) else ("No" if status == "Resolved" else "Pending")
        
        records.append({
            "ticket_id": f"CFRM-2026-{i:04d}",
            "intake_date": open_date.strftime("%Y-%m-%d"),
            "township": t_name,
            "admin3_pcode": t_info["admin3_pcode"],
            "implementing_partner": t_info["partner"],
            "intake_channel": channel,
            "beneficiary_gender": gender,
            "category": cat_name,
            "severity_level": severity,
            "target_sla_days": sla_days,
            "status": status,
            "days_to_resolve": days_to_resolve if status == "Resolved" else None,
            "closed_date": closed_date,
            "sla_compliance": sla_met
        })
    return pd.DataFrame(records)

def generate_logframe_indicators():
    data = [
        {
            "indicator_id": "IND-FS-01",
            "cluster_sector": "Food Security (FSAC)",
            "indicator_statement": "% of assisted households with Acceptable Food Consumption Score (FCS > 35)",
            "baseline_val": 42.0,
            "target_val": 70.0,
            "unit": "%",
            "calculation_module": "wfp_indicators.py",
            "donor": "WFP / ECHO"
        },
        {
            "indicator_id": "IND-FS-02",
            "cluster_sector": "Food Security (FSAC)",
            "indicator_statement": "% of assisted households classified as Food Secure or Marginally Secure by CARI Console",
            "baseline_val": 35.0,
            "target_val": 65.0,
            "unit": "%",
            "calculation_module": "cari_engine.py",
            "donor": "WFP Executive Board"
        },
        {
            "indicator_id": "IND-FS-03",
            "cluster_sector": "Food Security (FSAC)",
            "indicator_statement": "Mean reduced Coping Strategy Index (rCSI) among beneficiary households",
            "baseline_val": 14.8,
            "target_val": 6.5,
            "unit": "Score (Lower is better)",
            "calculation_module": "wfp_indicators.py",
            "donor": "USAID / BHA"
        },
        {
            "indicator_id": "IND-NUT-01",
            "cluster_sector": "Nutrition (MCCT)",
            "indicator_statement": "Total pregnant and lactating women (PLW) reached with nutrition-sensitive cash",
            "baseline_val": 0,
            "target_val": 250,
            "unit": "Individuals",
            "calculation_module": "dqa_cleaning_pipeline.py",
            "donor": "Tdh / LIFT"
        },
        {
            "indicator_id": "IND-AAP-01",
            "cluster_sector": "Cross-Cutting AAP",
            "indicator_statement": "% of received CFRM community feedback tickets resolved within defined SLA timeframe",
            "baseline_val": 50.0,
            "target_val": 85.0,
            "unit": "%",
            "calculation_module": "cfrm_tracker.py",
            "donor": "IASC Standard"
        },
        {
            "indicator_id": "IND-AAP-02",
            "cluster_sector": "Cross-Cutting AAP / PSEA",
            "indicator_statement": "% of PSEA Category 5 complaints escalated to Country Director / PSEA focal within 24 hours",
            "baseline_val": 100.0,
            "target_val": 100.0,
            "unit": "%",
            "calculation_module": "cfrm_tracker.py",
            "donor": "UN Core Humanitarian Standard"
        }
    ]
    return pd.DataFrame(data)

if __name__ == "__main__":
    print("Generating UN/WFP MEAL simulated datasets...")
    df_pdm = generate_pdm_data(450)
    df_dist = generate_distribution_register(30)
    df_cfrm = generate_cfrm_tickets(90)
    df_logframe = generate_logframe_indicators()
    
    df_pdm.to_csv(os.path.join(RAW_DATA_DIR, "raw_kobo_pdm_survey.csv"), index=False)
    df_dist.to_csv(os.path.join(RAW_DATA_DIR, "raw_distribution_register.csv"), index=False)
    df_cfrm.to_csv(os.path.join(RAW_DATA_DIR, "raw_cfrm_tickets.csv"), index=False)
    df_logframe.to_csv(os.path.join(RAW_DATA_DIR, "project_logframe_indicators.csv"), index=False)
    
    print(f"[OK] Raw PDM Survey generated: {len(df_pdm)} records (including simulated dirty errors & CARI fields)")
    print(f"[OK] Distribution Register generated: {len(df_dist)} distributions")
    print(f"[OK] CFRM Tickets generated: {len(df_cfrm)} tickets")
    print(f"[OK] LogFrame Indicators generated: {len(df_logframe)} key indicators")
