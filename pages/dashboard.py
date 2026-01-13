import streamlit as st
from core.config import ensure_defaults, load_config, apply_branding
from core.sidebar import render_sidebar

st.set_page_config(layout="wide")

# ensure config exists
ensure_defaults()
cfg = load_config()

# apply UI
apply_branding(cfg)
render_sidebar()

st.title("الصفحة الرئيسية")

st.info("مرحبًا بك في لوحة معلومات PMO")

st.write("سيتم هنا عرض المؤشرات والتحليلات لاحقًا.")
