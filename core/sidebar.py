import os
import streamlit as st
from core.config import load_config

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def render_sidebar():
    cfg = load_config()

    with st.sidebar:
        logo = cfg.get("logo", {})
        if logo.get("enabled"):
            path = os.path.join(BASE_DIR, logo.get("path",""))
            if os.path.exists(path):
                st.image(path, width=logo.get("width",140))

        st.markdown("## القائمة")
        st.page_link("pages/dashboard.py", label="الصفحة الرئيسية")
        st.page_link("pages/upload_data.py", label="رفع البيانات")
        st.page_link("pages/admin_login.py", label="دخول الأدمن")

        if st.session_state.get("is_admin"):
            st.page_link("pages/settings.py", label="الإعدادات")
