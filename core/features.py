import pandas as pd
import numpy as np

def build_features(df):
    out = df.copy()

    out["progress"] = pd.to_numeric(out.get("progress"), errors="coerce").clip(0, 100)
    out["budget"] = pd.to_numeric(out.get("budget"), errors="coerce")

    today = pd.Timestamp.today().normalize()
    out["days_to_deadline"] = (out.get("end_date") - today).dt.days

    status = out.get("status", "").astype(str).str.lower()
    out["is_delayed_actual"] = (
        status.str.contains("delay") |
        status.str.contains("متأخر")
    ).astype(int)

    return out

def reason_rules(row):
    reasons = []
    if pd.notna(row.get("progress")) and row["progress"] < 30:
        reasons.append("Low progress")
    if pd.notna(row.get("days_to_deadline")) and row["days_to_deadline"] < 0:
        reasons.append("Past deadline")
    if not reasons:
        reasons.append("Insufficient indicators")
    return reasons
