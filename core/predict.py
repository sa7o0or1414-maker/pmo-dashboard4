import pandas as pd

# كلمات مفتاحية عامة (عربي + إنجليزي)
DELAY_WORDS = [
    "متأخر", "متاخر", "تأخر", "تاخر",
    "delayed", "delay", "late", "overdue",
    "متعثر", "متوقف", "حرج", "خطر"
]

RISK_KEYWORDS = {
    "schedule": ["موعد", "تاريخ", "deadline", "due", "schedule"],
    "progress": ["إنجاز", "تقدم", "progress", "completion"],
    "resource": ["مورد", "موارد", "resource", "contractor", "vendor"],
    "financial": ["ميزانية", "تكلفة", "budget", "cost", "مالي"],
}

# أوزان حسب نوع المشروع (حتى لو الاسم مختلف)
PROJECT_TYPE_WEIGHTS = {
    "إنشائي": 1.3,
    "بنية تحتية": 1.3,
    "تقني": 1.1,
    "تقنية": 1.1,
    "رقمي": 1.1,
    "تشغيلي": 1.0,
    "خدمي": 0.9,
}

def _text_contains_any(text, keywords):
    t = str(text).lower()
    return any(k.lower() in t for k in keywords)

def _detect_project_weight(row):
    # يبحث في كل الأعمدة النصية عن نوع المشروع
    weight = 1.0
    for val in row.values:
        if isinstance(val, str):
            for k, w in PROJECT_TYPE_WEIGHTS.items():
                if k.lower() in val.lower():
                    weight = max(weight, w)
    return weight

def build_delay_outputs(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df

    out = df.copy()
    today = pd.Timestamp.today().normalize()

    # -------- تحليل عام لكل الأعمدة --------
    text_risk_hits = []
    for idx, row in out.iterrows():
        hit = False
        for val in row.values:
            if isinstance(val, str) and _text_contains_any(val, DELAY_WORDS):
                hit = True
                break
        text_risk_hits.append(1 if hit else 0)

    out["text_risk_signal"] = text_risk_hits

    # -------- مواعيد --------
    if "end_date" in out.columns:
        out["days_to_deadline"] = (out["end_date"] - today).dt.days
    else:
        out["days_to_deadline"] = pd.NA

    # -------- متأخر فعليًا --------
    actual = pd.Series([0] * len(out), index=out.index)

    if "days_to_deadline" in out.columns:
        overdue = out["days_to_deadline"].fillna(999999) < 0
        actual = actual | overdue

    actual = actual | (out["text_risk_signal"] == 1)
    out["is_delayed_actual"] = actual.astype(int)

    # -------- التنبؤ + الأسباب --------
    risks = []
    risk_levels = []
    colors = []
    short_reasons = []
    detailed_reasons = []
    actions = []

    for _, row in out.iterrows():
        score = 0.0
        reasons = []

        # وزن حسب نوع المشروع
        project_weight = _detect_project_weight(row)

        # 1) إشارات نصية
        if row.get("text_risk_signal", 0) == 1:
            score += 0.35
            reasons.append("وجود إشارات تأخير في بيانات المشروع")

        # 2) الموعد النهائي
        dtd = row.get("days_to_deadline", pd.NA)
        if pd.notna(dtd):
            if dtd < 0:
                score += 0.35
                reasons.append("تجاوز الموعد النهائي")
            elif dtd <= 14:
                score += 0.25
                reasons.append("قرب الموعد النهائي (أقل من 14 يوم)")
            elif dtd <= 30:
                score += 0.15
                reasons.append("الموعد النهائي خلال 30 يوم")

        # 3) نسبة الإنجاز
        prog = row.get("progress", pd.NA)
        if pd.notna(prog):
            if prog < 30:
                score += 0.30
                reasons.append("نسبة الإنجاز منخفضة جدًا (<30٪)")
            elif prog < 60:
                score += 0.15
                reasons.append("نسبة الإنجاز أقل من المتوقع (<60٪)")

        # تطبيق الوزن
        score *= project_weight
        score = max(0.0, min(1.0, score))

        # مستوى المخاطر
        if score >= 0.75:
            level = "عالي"
            color = "🔴"
            action = "يتطلب تدخل عاجل من الإدارة العليا"
        elif score >= 0.45:
            level = "متوسط"
            color = "🟠"
            action = "يتطلب متابعة وتصحيح المسار"
        else:
            level = "منخفض"
            color = "🟢"
            action = "المخاطر تحت السيطرة مع متابعة دورية"

        if not reasons:
            reasons = ["لا توجد مؤشرات خطورة واضحة حاليًا"]

        risks.append(score)
        risk_levels.append(level)
        colors.append(color)
        short_reasons.append(reasons[0])
        detailed_reasons.append(" • ".join(reasons))
        actions.append(action)

    out["delay_risk"] = risks
    out["risk_level"] = risk_levels
    out["risk_color"] = colors
    out["reason_short"] = short_reasons
    out["reason_detail"] = detailed_reasons
    out["action_recommendation"] = actions

    out["is_delayed_predicted"] = (out["delay_risk"] >= 0.6).astype(int)

    return out
