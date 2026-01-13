import pandas as pd
import numpy as np


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Builds features for analytics + prediction.
    Works even if some columns are missing.
    Expected normalized columns (from prepare_dashboard_data):
    municipality, entity, project, status, budget, progress,
    start_date, end_date, actual_end_date, risk, notes
    """
    out = df.copy()

    # Ensure basic text cols exist
    for col in ["municipality", "entity", "project", "status"]:
        if col not in out.columns:
            out[col] = ""

        out[col] = out[col].astype(str)

    # Numeric
    if "progress" not in out.columns:
        out["progress"] = np.nan
    out["progress"] = pd.to_numeric(out["progress"], errors="coerce").clip(0, 100)

    if "budget" not in out.columns:
        out["budget"] = np.nan
    out["budget"] = pd.to_numeric(out["budget"], errors="coerce")

    # Dates
    for col in ["start_date", "end_date", "actual_end_date"]:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col], errors="coerce")
        else:
            out[col] = pd.NaT

    # Days to deadline
    today = pd.Timestamp.today().normalize()
    out["days_to_deadline"] = (out["end_date"] - today).dt.days

    # Actual delay label (rule-based from status or dates)
    # If status contains 'delay'/'delayed'/'متأخر' -> delayed
    status_text = out["status"].str.lower()
    out["is_delayed_actual"] = (
        status_text.str.contains("delayed", na=False)
        | status_text.str.contains("delay", na=False)
        | status_text.str.contains("متأخر", na=False)
    ).astype(int)

    # If actual_end_date exists and is after end_date => delayed
    mask_dates = out["actual_end_date"].notna() & out["end_date"].notna()
    out.loc[mask_dates, "is_delayed_actual"] = (
        (out.loc[mask_dates, "actual_end_date"] > out.loc[mask_dates, "end_date"])
    ).astype(int)

    return out


def reason_rules(row: pd.Series) -> list:
    """
    Human-friendly reason hints (doesn't require SHAP).
    """
    reasons = []

    # progress low
    try:
        p = float(row.get("progress", np.nan))
        if pd.notna(p) and p < 30:
            reasons.append("Low progress")
        elif pd.notna(p) and p < 60:
            reasons.append("Medium progress")
    except Exception:
        pass

    # deadline near
    try:
        d = row.get("days_to_deadline", np.nan)
        if pd.notna(d) and d < 0:
            reasons.append("Past deadline")
        elif pd.notna(d) and d <= 30:
            reasons.append("Deadline is near")
    except Exception:
        pass

    # status contains stop/blocked
    stx = str(row.get("status", "")).lower()
    if "blocked" in stx or "stopped" in stx or "متوقف" in stx:
        reasons.append("Blocked/stopped status")

    if not reasons:
        reasons.append("Need more signals (dates/risks/notes)")

    return reasons
