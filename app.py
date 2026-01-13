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

config = load_config()
apply_branding(config)
render_sidebar()

st.title("PMO Dashboard")
st.info("Use the sidebar menu to navigate.")
