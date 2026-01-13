import streamlit as st
from core.config import ensure_defaults, load_config, apply_branding
from core.data_io import ensure_data_file
from core.sidebar import render_sidebar

st.set_page_config(
    page_title="PMO Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_defaults()
ensure_data_file()

cfg = load_config()
apply_branding(cfg)

render_sidebar(active="dashboard")

st.title("PMO Dashboard")
st.caption("Use the sidebar menu to open the dashboard.")
st.info("Open Home from the sidebar.")
