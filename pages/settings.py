import streamlit as st
from core.config import (
    ensure_defaults,
    load_config,
    save_config,
    apply_branding,
)
from core.sidebar import render_sidebar
from core.auth import require_admin

st.set_page_config(layout="wide")

ensure_defaults()
cfg = load_config()

apply_branding(cfg)
render_sidebar()

require_admin()

st.title("الإعدادات")

cfg["site_title"] = st.text_input(
    "عنوان الموقع",
    value=cfg.get("site_title", "")
)

cfg["dashboard_title"] = st.text_input(
    "عنوان الصفحة الرئيسية",
    value=cfg.get("dashboard_title", "")
)

if st.button("حفظ الإعدادات"):
    save_config(cfg)
    st.success("تم حفظ الإعدادات بنجاح")
    st.rerun()
