import streamlit as st
from core.config import load_config, save_config, apply_branding
from core.auth import require_admin
from core.sidebar import render_sidebar

st.set_page_config(layout="wide")

cfg = load_config()
apply_branding(cfg)
render_sidebar()
require_admin()

st.title("Settings")

cfg["site_title"] = st.text_input("Site title", cfg["site_title"])
cfg["dashboard_title"] = st.text_input("Dashboard title", cfg["dashboard_title"])

if st.button("Save"):
    save_config(cfg)
    st.success("Saved")
    st.rerun()
