import streamlit as st

st.set_page_config(page_title="لوحة المعلومات", layout="wide")

from core.ui import hide_streamlit_default_nav
hide_streamlit_default_nav()

from core.sidebar import render_sidebar
from core.config import ensure_defaults, load_config, apply_branding
import pandas as pd
import plotly.express as px

ensure_defaults()
cfg = load_config()
apply_branding(cfg)
render_sidebar()

st.title("لوحة المعلومات")

st.info("سيتم عرض التحليلات هنا بعد رفع ملف البيانات")
