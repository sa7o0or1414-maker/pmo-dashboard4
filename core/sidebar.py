import streamlit as st

def render_sidebar():
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("## لوحة التحكم")

    st.page_link("pages/dashboard.py", label="🏠 الصفحة الرئيسية")
    st.page_link("pages/upload_data.py", label="⬆️ رفع البيانات")
    st.page_link("pages/settings.py", label="⚙️ الإعدادات")
    st.page_link("pages/admin_login.py", label="🔐 دخول المشرف")
