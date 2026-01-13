import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.markdown("### لوحة التحكم")
        st.page_link("pages/dashboard.py", label="الصفحة الرئيسية", icon="🏠")
        st.page_link("pages/upload_data.py", label="رفع البيانات", icon="⬆️")
        st.page_link("pages/admin_login.py", label="تسجيل الدخول", icon="🔒")
