import os
import re
import pandas as pd

DATA_PATH = "data/current.xlsx"

ALIASES = {
    "municipality": ["municipality", "muni", "city", "بلدية", "البلدية", "municipal"],
    "entity": ["entity", "agency", "department", "جهة", "الجهة", "الإدارة", "ادارة"],
    "project": ["project", "project name", "name", "المشروع", "اسم المشروع", "عنوان المشروع"],
    "status": ["status", "state", "الحالة", "حالة", "حالة المشروع"],
    "progress": ["progress", "completion", "percent", "نسبة الانجاز", "نسبة الإنجاز", "الانجاز", "إنجاز", "%"],
    "budget": ["budget", "cost", "amount", "الميزانية", "التكلفة", "قيمة", "قيمة المشروع"],
    "start_date": ["start date", "start", "تاريخ البدء", "تاريخ البداية", "بداية"],
    "end_date": ["end date", "end", "due date", "تاريخ الانتهاء", "تاريخ النهاية", "نهاية", "موعد التسليم"],
}

def ensure_data_file():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_PATH):
        pd.DataFrame().to_excel(DATA_PATH, index=False)

def save_uploaded_file(file):
    ensure_data_file()
    with open(DATA_PATH, "wb") as f:
        f.write(file.getbuffer())

def read_raw_data():
    ensure_data_file()
    try:
        return pd.read_excel(DATA_PATH)
    except Exception:
        return pd.DataFrame()

def _norm(s):
    return re.sub(r"\s+", " ", str(s).strip().lower())

def _find_best_match(columns, candidates):
    for c in columns:
        for cand in candidates:
            if _norm(cand) in _norm(c) or _norm(c) in _norm(cand):
                return c
    return None

def normalize_columns(df):
    out = df.copy()
    for logical, aliases in ALIASES.items():
        col = _find_best_match(out.columns, aliases)
        if col:
            out[logical] = out[col]
    return out

def prepare_dashboard_data():
    raw = read_raw_data()
    if raw is None or raw.empty:
        return pd.DataFrame()

    df = raw.copy()
    df.columns = [str(c).strip() for c in df.columns]

    # ---- تحويل أي عمود رقمي تلقائيًا ----
    for col in df.columns:
        numeric_try = pd.to_numeric(df[col], errors="coerce")
        if numeric_try.notna().mean() >= 0.5:
            df[col] = numeric_try

    # ---- تحويل أي عمود تاريخ ----
    for col in df.columns:
        if any(k in col.lower() for k in ["date", "تاريخ", "deadline", "due", "end", "start"]):
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # ---- تنظيف النصوص ----
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()

    # ---- أعمدة منطقية إن وُجدت ----
    df = normalize_columns(df)

    return df
