import pandas as pd

DELAY_WORDS = [
    "متأخر", "متاخر", "تأخر", "تاخر",
    "delayed", "delay", "late", "overdue",
    "متعثر", "متوقف", "حرج"
]

def _row_has_delay_text(row):
    for v in row.values:
        if isinstance(v, str):
            t = v.lower()
            if any(w in t for w in DELAY_WORDS):
                return True
    return False

def _detect_end_date_column(df):
    for c in df.columns:
        name = c.lower()
        if any(k in name for k in ["end", "due", "deadline", "تاريخ", "موعد"]):
            if pd.api.types.is_datetime64_any_dtype(df[c]):
                return c
    return None

def build_delay_outputs(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    out = df.copy()
    today = pd.Timestamp.today().normalize()

    # ---------- تاريخ الانتهاء ----------
    end_col = _detect_end_date_column(out)
    if end_col:
        end_series = pd.to_datetime(out[end_col], errors="coerce")
        out["days_to_deadline"] = (end_series - today).dt.days
    else:
        out["days_to_deadline"] = pd.NA

    # ---------- متأخر فعليًا ----------
    actual_list = []
    for _, row in out.iterrows():
        actual = False

        dtd = row.get("days_to_deadline", pd.NA)
        if pd.notna(dtd) and dtd < 0:
            actual = True

        if _row_has_delay_text(row):
            actual = True

        actual_list.append(1 if actual else 0)

    out["is_delayed_actual"] = actual_list

    # ---------- التنبؤ ----------
    risks = []
    predicted = []
    levels = []
    colors = []
    reasons_short = []
    reasons_detail = []
    actions = []

    for _, row in out.iterrows():
        score = 0.0
        reasons = []

        dtd = row.get("days_to_deadline", pd.NA)
        if pd.notna(dtd):
            if dtd <= 14:
                score += 0.35
                reasons.append("قرب الموعد النهائي")
            elif dtd <= 30:
                score += 0.25
                reasons.append("الموعد النهائي خلال 30 يوم")

        prog = row.get("progress", pd.NA)
        if pd.notna(prog):
            if prog < 30:
                score += 0.35
                reasons.append("نسبة الإنجاز منخفضة جدًا")
            elif prog < 60:
                score += 0.20
                reasons.append("نسبة الإنجاز أقل من المطلوب")

        if _row_has_delay_text(row):
            score += 0.25
            reasons.append("وجود مؤشرات تأخير في البيانات")

        score = min(score, 1.0)
        risks.append(score)

        if score >= 0.7:
            level = "عالي"
            color = "🔴"
            action = "يتطلب تدخل عاجل من الإدارة العليا"
        elif score >= 0.4:
            level = "متوسط"
            color = "🟠"
            action = "يتطلب متابعة قريبة وتصحيح المسار"
        else:
            level = "منخفض"
            color = "🟢"
            action = "المخاطر تحت السيطرة"

        levels.append(level)
        colors.append(color)
        actions.append(action)

        if not reasons:
            reasons = ["مؤشرات الخطر محدودة حاليًا"]

        reasons_short.append(reasons[0])
        reasons_detail.append(" • ".join(reasons))

        if score >= 0.4 and row["is_delayed_actual"] == 0:
            predicted.append(1)
        else:
            predicted.append(0)

    out["delay_risk"] = risks
    out["is_delayed_predicted"] = predicted
    out["risk_level"] = levels
    out["risk_color"] = colors
    out["reason_short"] = reasons_short
    out["reason_detail"] = reasons_detail
    out["action_recommendation"] = actions

    return out
