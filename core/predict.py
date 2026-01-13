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

    # -------- مؤشرات مشتقة --------
    if "end_date" in out.columns:
        out["days_to_deadline"] = (out["end_date"] - today).dt.days
    else:
        out["days_to_deadline"] = pd.NA

    status = out["status"] if "status" in out.columns else ""
    out["status_has_delay"] = status.apply(_contains_delay).astype(int)

    # -------- متأخر فعليًا --------
    actual = pd.Series([0] * len(out), index=out.index)

    if "status" in out.columns:
        actual = actual | out["status_has_delay"].astype(bool)

    if "end_date" in out.columns:
        prog = out["progress"] if "progress" in out.columns else pd.Series([pd.NA]*len(out), index=out.index)
        not_done = prog.fillna(0) < 100
        overdue = out["days_to_deadline"].fillna(999999) < 0
        actual = actual | (overdue & not_done)

    out["is_delayed_actual"] = actual.astype(int)

    # -------- التنبؤ بالتأخير (ذكي بدون ML) --------
    risks = []
    reasons_list = []

    for _, row in out.iterrows():
        score = 0.0
        reasons = []

        # 1) حالة المشروع تشير إلى تأخير
        if row.get("status_has_delay", 0) == 1:
            score += 0.55
            reasons.append("حالة المشروع تشير إلى تأخير")

        # 2) قرب أو تجاوز الموعد النهائي
        dtd = row.get("days_to_deadline", pd.NA)
        if pd.notna(dtd):
            if dtd < 0:
                score += 0.35
                reasons.append("تجاوز الموعد النهائي")
            elif dtd <= 14:
                score += 0.25
                reasons.append("الموعد النهائي خلال أقل من 14 يوم")
            elif dtd <= 30:
                score += 0.15
                reasons.append("الموعد النهائي خلال أقل من 30 يوم")

        # 3) نسبة إنجاز منخفضة
        prog = row.get("progress", pd.NA)
        if pd.notna(prog):
            if prog < 30:
                score += 0.25
                reasons.append("نسبة الإنجاز أقل من 30٪")
            elif prog < 60:
                score += 0.12
                reasons.append("نسبة الإنجاز أقل من 60٪")

        # ضبط النتيجة
        score = max(0.0, min(1.0, score))

        if not reasons:
            reasons = ["لا توجد مؤشرات كافية حاليًا"]

        risks.append(score)
        reasons_list.append(" • ".join(reasons))

    out["delay_risk"] = risks
    out["delay_reason"] = reasons_list

    # -------- متوقع تأخره --------
    out["is_delayed_predicted"] = (out["delay_risk"] >= 0.6).astype(int)

    return out
