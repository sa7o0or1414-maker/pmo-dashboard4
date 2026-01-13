import os
import pandas as pd

DATA_PATH = "data/current.xlsx"
SHEET_NAME = None  # read first sheet automatically


# Logical fields the dashboard needs
LOGICAL_FIELDS = {
    "municipality": ["municipality", "city", "municipal", "البلدية", "مدينة"],
    "entity": ["entity", "department", "owner", "الجهة", "الإدارة"],
    "project": ["project", "project_name", "initiative", "المشروع"],
    "status": ["status", "state", "الحالة", "وضع المشروع"],
    "budget": ["budget", "cost", "amount", "الميزانية", "التكلفة"],
    "progress": ["progress", "completion", "percent", "نسبة الانجاز", "الانجاز"],
    "start_date": ["start_date", "start", "تاريخ البداية"],
    "end_date": ["end_date", "end", "تاريخ النهاية"],
    "actual_end_date": ["actual_end_date", "actual_end", "تاريخ الانتهاء الفعلي"],
    "risk": ["risk", "risks", "المخاطر"],
    "notes": ["notes", "comments", "remarks", "ملاحظات"],
}


def ensure_data_file():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame()
        df.to_excel(DATA_PATH, index=False)


def read_data(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=SHEET_NAME)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def save_uploaded_file(uploaded_file):
    os.makedirs("data", exist_ok=True)
    with open(DATA_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())


def map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Maps any column names in Excel to logical dashboard fields.
    """
    mapped = {}
    lower_cols = {c.lower(): c for c in df.columns}

    for logical_name, aliases in LOGICAL_FIELDS.items():
        for alias in aliases:
            alias_lower = alias.lower()
            if alias_lower in lower_cols:
                mapped[logical_name] = lower_cols[alias_lower]
                break

    normalized_df = pd.DataFrame()

    for logical_name, original_col in mapped.items():
        normalized_df[logical_name] = df[original_col]

    return normalized_df


def prepare_dashboard_data():
    """
    Main function used by dashboard
    """
    df_raw = read_data()
    df = map_columns(df_raw)

    # Type normalization
    if "progress" in df.columns:
        df["progress"] = pd.to_numeric(df["progress"], errors="coerce").clip(0, 100)

    if "budget" in df.columns:
        df["budget"] = pd.to_numeric(df["budget"], errors="coerce")

    for col in ["start_date", "end_date", "actual_end_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df
