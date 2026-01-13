from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "dashboard_data.xlsx"

def save_uploaded_excel(uploaded_file) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "wb") as f:
        f.write(uploaded_file.getbuffer())
    # نخلي الصفحة الرئيسية تقرأ آخر نسخة فورًا
    st.cache_data.clear()

@st.cache_data(show_spinner=False)
def load_latest_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        return pd.DataFrame()
    try:
        return pd.read_excel(DATA_FILE)
    except Exception:
        return pd.DataFrame()
