import streamlit as st
from core.config import ensure_defaults, load_config, apply_branding
from core.data_io import ensure_data_file

st.set_page_config(
    page_title="PMO Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_defaults()
ensure_data_file()

cfg = load_config()
apply_branding(cfg)

st.sidebar.success("Select a page from the sidebar.")
st.title("PMO Dashboard")
st.caption("Go to the Dashboard page from the sidebar navigation.")
