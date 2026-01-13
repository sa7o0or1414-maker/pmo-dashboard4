import streamlit as st

# =========================================
# Page Config (أول أمر)
# =========================================
st.set_page_config(
    page_title="تسجيل دخول الأدمن",
    layout="wide"
)

from core.ui import hide_streamlit_default_nav
from core.sidebar import render_sidebar

hide_streamlit_default_nav()
render_sidebar()

# =========================================
# Admin Login Logic
# =========================================
st.markdown("## 🔐 تسجيل دخول الأدمن")

# بيانات دخول مؤقتة (لاحقًا نربطها بإعدادات)
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if st.session_state.is_admin:
    st.success("✅ تم تسجيل الدخول كمسؤول")
    st.info("يمكنك الآن الدخول إلى صفحة الإعدادات من القائمة الجانبية")
    st.stop()

with st.form("login_form"):
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    submit = st.form_submit_button("تسجيل الدخول")

if submit:
    if username == ADMIN_USER and password == ADMIN_PASS:
        st.session_state.is_admin = True
        st.success("تم تسجيل الدخول بنجاح")
        st.experimental_rerun()
    else:
        st.error("بيانات الدخول غير صحيحة")
