import streamlit as st

st.set_page_config(
    page_title="تسجيل دخول الأدمن",
    layout="wide"
)

from core.ui import hide_streamlit_default_nav
hide_streamlit_default_nav()

from core.sidebar import render_sidebar
render_sidebar()

cfg = load_config()

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

st.title("دخول الأدمن")

u = st.text_input("اسم المستخدم")
p = st.text_input("كلمة المرور", type="password")

if st.button("دخول"):
    admin = cfg["admin"]
    if u == admin["username"] and (
        admin["password_hash"] == "" or verify_password(p, admin["password_hash"])
    ):
        st.session_state.is_admin = True
        st.success("تم الدخول بنجاح")
    else:
        st.error("بيانات غير صحيحة")
