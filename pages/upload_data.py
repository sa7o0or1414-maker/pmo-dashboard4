import streamlit as st

st.set_page_config(page_title="رفع البيانات", layout="wide")
from core.sidebar import render_sidebar
render_sidebar()

from core.ui import hide_streamlit_default_nav
hide_streamlit_default_nav()

from core.sidebar import render_sidebar
render_sidebar()

st.title("رفع البيانات")
st.file_uploader("ارفع ملف Excel", type=["xlsx"])
