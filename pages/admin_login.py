import streamlit as st
from core.config import ensure_defaults, load_config, apply_branding
from core.sidebar import render_sidebar
from core.auth import login, logout, is_admin

st.set_page_config(layout="wide")

ensure_defaults()
cfg = load_config()
apply_branding(cfg)
render_sidebar()

st.title("🔐 دخول المشرف")

if is_admin():
    st.success("تم تسجيل الدخول")
    if st.button("تسجيل الخروج"):
        logout()
        st.rerun()
else:
    user = st.text_input("اسم المستخدم")
    pwd = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if login(user, pwd):
            st.success("تم الدخول")
            st.rerun()
        else:
            st.error("بيانات غير صحيحة")
