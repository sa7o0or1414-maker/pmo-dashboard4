import pandas as pd
import streamlit as st
from pathlib import Path

DATA_PATH = Path("data")
DATA_FILE = DATA_PATH / "dashboard_data.xlsx"

def save_uploaded_file(uploaded_file):
    DATA_PATH.mkdir(exist_ok=True)
    with open(DATA_FILE, "wb") as f:
        f.write(uploaded_file.getbuffer())

def load_data():
    if not DATA_FILE.exists():
        return None
    try:
        return pd.read_excel(DATA_FILE)
    except Exception:
        return None

def prepare_dashboard_data():
    # نضمن التحديث الفوري
    st.cache_data.clear()
    return load_data()
