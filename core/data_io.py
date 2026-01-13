import os
import re
import pandas as pd

DATA_PATH = "data/current.xlsx"

# Aliases to detect columns in Arabic/English without strict naming
ALIASES = {
    "municipality": ["municipality", "muni", "city", "بلدية", "البلدية", "municipal"],
    "entity": ["entity", "agency", "department", "جهة", "الجهة", "الإدارة", "ادارة"],
    "project": ["project", "project name", "name", "المشروع", "اسم المشروع", "عنوان المشروع"],
    "status": ["status", "state", "الحالة", "حالة", "حالة المشروع"],
    "progress": ["progress", "completion", "percent", "نسبة الانجاز", "نسبة الإنجاز", "الانجاز", "إنجاز", "%"],
    "budget": ["budget", "cost", "amount", "الميزانية", "التكلفة", "قيمة", "قيمة المشروع"],
    "start_date": ["start date", "start", "تاريخ البدء", "تاريخ البداية", "بداية", "تاريخ بدء"],
    "end_date": ["end date", "end", "due date", "تاريخ الانتهاء", "تاريخ النهاية", "نهاية", "موعد الانتهاء", "موعد التسليم"],
}

def ensure_data_file():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_PATH):
        pd.DataFrame().to_excel(DATA_PATH, index=False)

def save_uploaded_file(file):
    os.makedirs("data", exist_ok=True)
    with open(DATA_PATH, "wb") as f:
        f.write(file.getbuffer())

def read_raw_data():
    ensure_data_file()
    try:
        return pd.read_excel(DATA_PATH)
    except Exception:
        return pd.DataFrame()

def _norm(s: str) -> str:
    s = str(s).strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s

def _find_best_match(columns, candidates):
    # exact/contains matching (robust for Arabic/English)
    norm_cols = {c: _norm(c) for c in columns}
    cand_norm = [_norm(x) for x in candidates]

    # 1) exact
    for c, nc in norm_cols.items():
        if nc in cand_norm:
            return c

    # 2) contains
    for c, nc in norm_cols.items():
        for cand in cand_norm:
            if cand and (cand in nc or nc in cand):
                return c

    return None

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    out = pd.DataFrame()
    for logical, candidates in ALIASES.items():
        col = _find_best_match(df.columns, candidates)
        if col is not None:
            out[logical] = df[col]

    return out

def prepare_dashboard_data() -> pd.DataFrame:
    raw = read_raw_data()
    if raw.empty:
        return raw

    df = normalize_columns(raw)

    # if critical columns missing, still return what we can
    if df.empty:
        return df

    # types
    if "progress" in df.columns:
        df["progress"] = pd.to_numeric(df["progress"], errors="coerce")
        # if progress was 0-1, convert to 0-100
        if df["progress"].dropna().between(0, 1).mean() > 0.8:
            df["progress"] = df["progress"] * 100
        df["progress"] = df["progress"].clip(0, 100)

    if "budget" in df.columns:
        df["budget"] = pd.to_numeric(df["budget"], errors="coerce")

    for d in ["start_date", "end_date"]:
        if d in df.columns:
            df[d] = pd.to_datetime(df[d], errors="coerce")

    # clean strings
    for c in ["municipality", "entity", "project", "status"]:
        if c in df.columns:
            df[c] = df[c].astype(str).fillna("").str.strip()

    return df
