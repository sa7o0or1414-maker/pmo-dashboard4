import os
import pandas as pd

DATA_PATH = "data/current.xlsx"

COLUMN_ALIASES = {
    "municipality": ["municipality", "city", "البلدية"],
    "entity": ["entity", "department", "الجهة"],
    "project": ["project", "project name", "المشروع"],
    "status": ["status", "الحالة"],
    "budget": ["budget", "cost", "الميزانية"],
    "progress": ["progress", "completion", "نسبة الانجاز"],
    "start_date": ["start", "start date", "تاريخ البداية"],
    "end_date": ["end", "end date", "تاريخ النهاية"],
    "actual_end_date": ["actual end", "تاريخ الانتهاء"],
}

def ensure_data_file():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_PATH):
        pd.DataFrame().to_excel(DATA_PATH, index=False)

def save_uploaded_file(file):
    with open(DATA_PATH, "wb") as f:
        f.write(file.getbuffer())

def read_raw_data():
    return pd.read_excel(DATA_PATH)

def normalize_columns(df):
    mapped = {}
    for logical, aliases in COLUMN_ALIASES.items():
        for col in df.columns:
            if col.lower().strip() in [a.lower() for a in aliases]:
                mapped[logical] = col
                break

    out = pd.DataFrame()
    for logical, col in mapped.items():
        out[logical] = df[col]

    return out

def prepare_dashboard_data():
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()

    raw = read_raw_data()
    if raw.empty:
        return raw

    df = normalize_columns(raw)

    if "progress" in df:
        df["progress"] = pd.to_numeric(df["progress"], errors="coerce").clip(0, 100)
    if "budget" in df:
        df["budget"] = pd.to_numeric(df["budget"], errors="coerce")

    for d in ["start_date", "end_date", "actual_end_date"]:
        if d in df:
            df[d] = pd.to_datetime(df[d], errors="coerce")

    return df
