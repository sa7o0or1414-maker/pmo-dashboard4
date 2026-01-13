import streamlit as st
from core.config import ensure_defaults, load_config, apply_branding
from core.data_io import save_uploaded_file
from core.auth import require_admin
from core.sidebar import render_sidebar

st.set_page_config(layout="wide")

ensure_defaults()
cfg = load_config()
apply_branding(cfg)
render_sidebar()
require_admin()

st.title("Upload Data")

file = st.file_uploader("Upload Excel file", type=["xlsx"])
if file:
    save_uploaded_file(file)
    st.success("File uploaded successfully")
