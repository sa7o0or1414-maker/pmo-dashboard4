import streamlit as st
import bootstrap  # noqa: F401

from core.ui import hide_streamlit_default_nav
hide_streamlit_default_nav()
from core.config import ensure_defaults, load_config, apply_branding
from core.sidebar import render_sidebar

st.set_page_config(layout="wide")

ensure_defaults()
cfg = load_config()
apply_branding(cfg)
render_sidebar()

st.title("لوحة معلومات PMO")
st.write("اختاري صفحة من القائمة الجانبية")
