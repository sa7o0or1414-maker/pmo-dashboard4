import os
import pandas as pd

DATA_PATH = "data/current.xlsx"
SHEET_NAME = "Data"

REQUIRED_COLUMNS = [
    "municipality",   # Municipality
    "entity",         # Entity/Department
    "project",        # Project name
    "status",         # Status (e.g., On Track, Delayed, Completed)
    "budget",         # Budget (number)
    "progress",       # Progress (0-100)
]

OPTIONAL_COLUMNS = [
    "start_date",       # YYYY-MM-DD
    "end_date",         # YYYY-MM-DD
    "actual_end_date",  # YYYY-MM-DD
    "risk",             # optional text/category
    "notes",            # optional text
]


def ensure_data_file():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=REQUIRED_COLUMNS + OPTIONAL_COLUMNS)
        df.to_excel(DATA_PATH, index=False, sheet_name=SHEET_NAME)


def read_data(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=SHEET_NAME)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def validate_columns(df: pd.DataFrame):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    return missing


def save_uploaded_file(uploaded_file):
    os.makedirs("data", exist_ok=True)
    with open(DATA_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())
