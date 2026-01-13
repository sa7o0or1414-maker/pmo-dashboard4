import streamlit as st
import bootstrap  # noqa: F401

from core.config import ensure_defaults, load_config, apply_branding
from core.sidebar import render_sidebar
from core.auth import require_admin
from core.data_io import save_uploaded_file, prepare_dashboard_data

st.set_page_config(layout="wide")

ensure_defaults()
cfg = load_config()
apply_branding(cfg)
render_sidebar()

require_admin()

st.title("رفع البيانات")

uploaded_file = st.file_uploader("ارفع ملف Excel", type=["xlsx"])

if uploaded_file:
    save_uploaded_file(uploaded_file)
    st.success("تم رفع الملف بنجاح. انتقلي للصفحة الرئيسية لمشاهدة الداشبورد.")
    df = prepare_dashboard_data()
    st.subheader("Preview")
    st.dataframe(df.head(50), use_container_width=True)
