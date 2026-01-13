import streamlit as st
from core.config import ensure_defaults, load_config, apply_branding
from core.sidebar import render_sidebar
from core.auth import login, logout, is_admin

st.set_page_config(layout="wide")

ensure_defaults()
cfg = load_config()

apply_branding(cfg)
render_sidebar()

st.title("دخول المشرف")

if is_admin():
    st.success("تم تسجيل الدخول كمشرف")
    if st.button("تسجيل الخروج"):
        logout()
        st.rerun()
else:
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")

    if st.button("دخول"):
        if login(username, password):
            st.success("تم تسجيل الدخول بنجاح")
            st.rerun()
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
