"""
WFP & Humanitarian Partner MEAL Portfolio Project
Module 4: Enumerator Forensics & Fraud Detection Engine (Zero-Dependency Pure Python)
Author: M&E & Data Assistant Candidate
Methodology:
- Benford's Law First-Digit Analysis (detects fabricated numeric reporting)
- Survey Duration Speed-Run Detection (identifies hurried / fake interviews)
- GPS Teleportation & Velocity Checks (Haversine distance vs elapsed time)
- Automated Enumerator Integrity Scorecard (Trust Score 0-100%)
"""

import os
import math
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Benford's Theoretical Probabilities for Digits 1-9
# P(d) = log10(1 + 1/d)
BENFORD_THEORETICAL = {
    d: math.log10(1.0 + 1.0 / d) for d in range(1, 10)
}

# Chi-square Critical Values for df = 8 (Digits 1-9 -> 8 degrees of freedom)
CHI2_CRITICAL_05 = 15.51  # p = 0.05
CHI2_CRITICAL_01 = 20.09  # p = 0.01
CHI2_CRITICAL_001 = 26.12 # p = 0.001

def haversine_distance_km(lat1, lon1, lat2, lon2):
    """
    Computes great-circle distance between two GPS coordinates in kilometers.
    """
    try:
        R = 6371.0 # Earth radius in km
        phi1, phi2 = math.radians(float(lat1)), math.radians(float(lat2))
        delta_phi = math.radians(float(lat2) - float(lat1))
        delta_lambda = math.radians(float(lon2) - float(lon1))
        
        a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c
    except:
        return 0.0

def extract_first_digit(num):
    """Extracts first significant digit (1-9) from number, ignoring leading zeros."""
    try:
        s = str(abs(float(num))).lstrip("0").replace(".", "")
        if len(s) > 0 and s[0].isdigit() and s[0] != "0":
            return int(s[0])
    except:
        pass
    return None

def calculate_chi_square_benford(observed, expected):
    """
    Computes Chi-Square statistic sum((O - E)^2 / E)
    and estimates p-value category.
    """
    chi2 = 0.0
    for o, e in zip(observed, expected):
        if e > 0:
            chi2 += ((o - e) ** 2) / e
            
    if chi2 > CHI2_CRITICAL_001:
        p_est = "< 0.001 (Highly Significant Anomaly)"
    elif chi2 > CHI2_CRITICAL_01:
        p_est = "< 0.01 (Significant Anomaly)"
    elif chi2 > CHI2_CRITICAL_05:
        p_est = "< 0.05 (Borderline)"
    else:
        p_est = ">= 0.05 (Conforms to Benford)"
        
    return round(chi2, 2), p_est

def analyze_benford_law(df, numeric_col="expenditure_food_mmk"):
    """
    Tests distribution of first digits against Benford's Law.
    Returns observed vs expected counts and Chi-square statistic.
    """
    if numeric_col not in df.columns:
        return None, None, None
        
    digits = df[numeric_col].apply(extract_first_digit).dropna().astype(int)
    n = len(digits)
    if n < 15:
        return None, None, "Insufficient Sample (<15)"
        
    counts = digits.value_counts().to_dict()
    observed = [counts.get(d, 0) for d in range(1, 10)]
    expected = [BENFORD_THEORETICAL[d] * n for d in range(1, 10)]
    
    chi2, p_val_str = calculate_chi_square_benford(observed, expected)
    
    df_benford = pd.DataFrame({
        "Digit": list(range(1, 10)),
        "Observed_Count": observed,
        "Observed_Pct": [round((c / n) * 100, 1) for c in observed],
        "Theoretical_Benford_Pct": [round(BENFORD_THEORETICAL[d] * 100, 1) for d in range(1, 10)],
    })
    return df_benford, chi2, p_val_str

def audit_interview_durations(df, min_threshold_min=7.0):
    """
    Flags interviews completed in unrealistically short times (< min_threshold_min)
    or extreme Z-score outliers.
    """
    df = df.copy()
    if "duration_minutes" not in df.columns:
        df["duration_minutes"] = 30.0
        
    durations = df["duration_minutes"].astype(float)
    median_dur = durations.median()
    std_dur = durations.std()
    
    z_scores = (durations - median_dur) / (std_dur if std_dur > 0 else 1.0)
    
    is_speeder = (durations < min_threshold_min) | (z_scores < -2.2)
    df["is_speed_anomaly"] = is_speeder
    df["duration_z_score"] = z_scores.round(2)
    return df

def audit_gps_velocity(df, max_speed_kmh=50.0):
    """
    Sorts interviews by enumerator and start time.
    Flags impossible travel speeds (> max_speed_kmh between consecutive surveys).
    """
    df = df.copy()
    if "start_time" not in df.columns or "latitude" not in df.columns:
        df["gps_travel_speed_kmh"] = 0.0
        df["is_gps_teleport_anomaly"] = False
        return df
        
    df["start_dt"] = pd.to_datetime(df["start_time"], errors="coerce")
    df = df.sort_values(by=["enumerator_id", "start_dt"]).reset_index(drop=True)
    
    teleport_flags = [False] * len(df)
    speeds = [0.0] * len(df)
    
    for i in range(1, len(df)):
        prev_row = df.iloc[i - 1]
        curr_row = df.iloc[i]
        
        # Check if same enumerator and both timestamps valid
        if prev_row["enumerator_id"] == curr_row["enumerator_id"] and pd.notna(prev_row["start_dt"]) and pd.notna(curr_row["start_dt"]):
            time_diff_hours = (curr_row["start_dt"] - prev_row["start_dt"]).total_seconds() / 3600.0
            if 0 < time_diff_hours <= 1.0: # Within 1 hour
                dist_km = haversine_distance_km(
                    prev_row["latitude"], prev_row["longitude"],
                    curr_row["latitude"], curr_row["longitude"]
                )
                speed = dist_km / time_diff_hours
                speeds[i] = round(speed, 1)
                if speed > max_speed_kmh:
                    teleport_flags[i] = True
                    
    df["gps_travel_speed_kmh"] = speeds
    df["is_gps_teleport_anomaly"] = teleport_flags
    df = df.drop(columns=["start_dt"])
    return df

def generate_enumerator_scorecard(df):
    """
    Aggregates all forensics checks into an Enumerator Integrity & Trust Score (0-100%).
    Outputs a ranked scorecard for MEAL Managers.
    """
    scorecard = []
    
    for enum_id, group in df.groupby("enumerator_id"):
        n_surveys = len(group)
        speed_anomalies = int(group["is_speed_anomaly"].sum()) if "is_speed_anomaly" in group.columns else 0
        gps_anomalies = int(group["is_gps_teleport_anomaly"].sum()) if "is_gps_teleport_anomaly" in group.columns else 0
        
        # Benford check on enumerator level
        _, chi2, p_val_str = analyze_benford_law(group, "expenditure_food_mmk")
        benford_flag = True if (chi2 is not None and chi2 > CHI2_CRITICAL_01) else False
        
        # Calculate Trust Score (starts at 100, penalize per anomaly)
        speed_penalty = (speed_anomalies / n_surveys) * 35.0
        gps_penalty = (gps_anomalies / n_surveys) * 35.0
        benford_penalty = 20.0 if benford_flag else 0.0
        
        trust_score = round(max(0.0, 100.0 - (speed_penalty + gps_penalty + benford_penalty)), 1)
        
        if trust_score >= 85.0:
            status = "Verified"
            action = "Quality Approved"
        elif trust_score >= 65.0:
            status = "Audit Needed"
            action = "Spot Check & Supervision"
        else:
            status = "High Risk"
            action = "Immediate Retraining / Reject"
            
        scorecard.append({
            "Enumerator ID": enum_id,
            "Total Submissions": n_surveys,
            "Avg Duration (min)": round(group["duration_minutes"].mean(), 1) if "duration_minutes" in group.columns else 0.0,
            "Speeding Outliers": speed_anomalies,
            "GPS Teleport Flags": gps_anomalies,
            "Benford Anomaly": "Flagged" if benford_flag else "Normal",
            "Trust Score (%)": trust_score,
            "Audit Status": status,
            "Recommended Action": action
        })
        
    df_score = pd.DataFrame(scorecard).sort_values(by="Trust Score (%)", ascending=True)
    return df_score

if __name__ == "__main__":
    from dqa_cleaning_pipeline import run_dqa_pipeline
    df_clean, _, _ = run_dqa_pipeline()
    df_audited = audit_interview_durations(df_clean)
    df_audited = audit_gps_velocity(df_audited)
    scorecard = generate_enumerator_scorecard(df_audited)
    print("=== ENUMERATOR INTEGRITY & FORENSICS SCORECARD ===")
    print(scorecard.to_string(index=False))
