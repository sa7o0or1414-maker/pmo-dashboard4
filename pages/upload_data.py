import streamlit as st
import bootstrap  # noqa: F401
from core.config import ensure_defaults, load_config, apply_branding
from core.sidebar import render_sidebar
from core.auth import require_admin

st.set_page_config(layout="wide")

ensure_defaults()
cfg = load_config()
apply_branding(cfg)
render_sidebar()

require_admin()

st.title("رفع البيانات")
st.file_uploader("ارفع ملف Excel", type=["xlsx"])
