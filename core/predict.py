import pandas as pd

AR_DELAY_WORDS = ["متأخر", "متاخر", "تأخر", "تاخر"]
EN_DELAY_WORDS = ["delayed", "delay", "late", "overdue"]

def _contains_delay(text: str) -> bool:
    t = str(text).lower()
    return any(w in t for w in AR_DELAY_WORDS) or any(w in t for w in EN_DELAY_WORDS)

def build_delay_outputs(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    out = df.copy()
    today = pd.Timestamp.today().normalize()

    # derived signals
    if "end_date" in out.columns:
        out["days_to_deadline"] = (out["end_date"] - today).dt.days
    else:
        out["days_to_deadline"] = pd.NA

    status = out["status"] if "status" in out.columns else ""
    out["status_has_delay"] = status.apply(_contains_delay).astype(int)

    # actual delayed logic
    actual = pd.Series([0] * len(out), index=out.index)
    if "status" in out.columns:
        actual = actual | out["status_has_delay"].astype(bool)
    if "end_date" in out.columns:
        # overdue and not completed
        prog = out["progress"] if "progress" in out.columns else pd.Series([pd.NA]*len(out), index=out.index)
        not_done = prog.fillna(0) < 100
        overdue = out["days_to_deadline"].fillna(999999) < 0
        actual = actual | (overdue & not_done)
    out["is_delayed_actual"] = actual.astype(int)

    # predicted delay risk (rule-based)
    reasons_list = []
    risks = []

    for _, row in out.iterrows():
        score = 0.0
        reasons = []

        # 1) status hint
        if "status_has_delay" in out.columns and row.get("status_has_delay", 0) == 1:
            score += 0.55
            reasons.append("Status indicates delay")

        # 2) deadline proximity/overdue
        dtd = row.get("days_to_deadline", pd.NA)
        if pd.notna(dtd):
            if dtd < 0:
                score += 0.35
                reasons.append("Past deadline")
            elif dtd <= 14:
                score += 0.25
                reasons.append("Deadline within 14 days")
            elif dtd <= 30:
                score += 0.15
                reasons.append("Deadline within 30 days")

        # 3) low progress
        prog = row.get("progress", pd.NA)
        if pd.notna(prog):
            if prog < 30:
                score += 0.25
                reasons.append("Low progress (<30%)")
            elif prog < 60:
                score += 0.12
                reasons.append("Moderate progress (<60%)")

        # clamp
        score = max(0.0, min(1.0, score))
        if not reasons:
            reasons = ["Insufficient indicators"]

        risks.append(score)
        reasons_list.append(" / ".join(reasons))

    out["delay_risk"] = risks
    out["delay_reason"] = reasons_list

    # predicted delayed flag
    out["is_delayed_predicted"] = (out["delay_risk"] >= 0.6).astype(int)

    return out
