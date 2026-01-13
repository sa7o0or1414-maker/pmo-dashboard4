import streamlit as st
from core.config import ensure_defaults, load_config, apply_branding
from core.sidebar import render_sidebar
from core.data_io import prepare_dashboard_data

st.set_page_config(layout="wide")

ensure_defaults()
cfg = load_config()
apply_branding(cfg)
render_sidebar()

st.title(cfg["dashboard_title"])

df = prepare_dashboard_data()
if df.empty:
    st.info("No data uploaded yet.")
else:
    st.dataframe(df, use_container_width=True)
