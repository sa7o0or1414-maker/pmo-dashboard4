import pandas as pd

DELAY_WORDS = [
    "متأخر", "متاخر", "تأخر", "تاخر",
    "delayed", "delay", "late", "overdue",
    "متعثر", "متوقف", "حرج"
]

def _text_has_delay(row):
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
    actual_delay = []

    for _, row in out.iterrows():
        delayed = False

        # 1) تجاوز الموعد
        dtd = row.get("days_to_deadline", pd.NA)
        if pd.notna(dtd) and dtd < 0:
            delayed = True

        # 2) نص الحالة
        if _text_has_delay(row):
            delayed = True

        actual_delay.append(1 if delayed else 0)

    out["is_delayed_actual"] = actual_delay

    # ---------- التنبؤ بالتأخير ----------
    risks = []
    predicted = []

    for _, row in out.iterrows():
        score = 0.0

        dtd = row.get("days_to_deadline", pd.NA)
        prog = row.get("progress", pd.NA)

        # قرب الموعد
        if pd.notna(dtd):
            if dtd <= 14:
                score += 0.4
            elif dtd <= 30:
                score += 0.25

        # إنجاز ضعيف
        if pd.notna(prog):
            if prog < 30:
                score += 0.4
            elif prog < 60:
                score += 0.2

        # إشارات نصية
        if _text_has_delay(row):
            score += 0.3

        score = min(score, 1.0)

        risks.append(score)

        # متوقع فقط لو غير متأخر فعليًا
        if score >= 0.6 and row["is_delayed_actual"] == 0:
            predicted.append(1)
        else:
            predicted.append(0)

    out["delay_risk"] = risks
    out["is_delayed_predicted"] = predicted

    return out
