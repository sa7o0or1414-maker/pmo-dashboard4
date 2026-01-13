import streamlit as st

from core.config import ensure_defaults, load_config, save_config
from core.auth import verify_password, hash_password

st.set_page_config(layout="wide")

ensure_defaults()
cfg = load_config()

st.title("تسجيل دخول الأدمن")

# session defaults
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "admin_user" not in st.session_state:
    st.session_state.admin_user = None

admin_cfg = cfg.get("admin", {})
default_user = admin_cfg.get("username", "admin")
stored_hash = admin_cfg.get("password_hash", "")

with st.form("admin_login_form", clear_on_submit=False):
    username = st.text_input("اسم المستخدم", value=default_user)
    password = st.text_input("كلمة المرور", type="password")
    submitted = st.form_submit_button("دخول")

if submitted:
    # First-time fallback: allow admin/admin ONCE if no password hash is set
    if not stored_hash:
        if username == default_user and password == "admin":
            st.session_state.is_admin = True
            st.session_state.admin_user = username
            st.warning("تم الدخول. من فضلك غيّري كلمة المرور من صفحة الإعدادات.")
        else:
            st.error("بيانات الدخول غير صحيحة.")
    else:
        if username == default_user and verify_password(password, stored_hash):
            st.session_state.is_admin = True
            st.session_state.admin_user = username
            st.success("تم تسجيل الدخول.")
        else:
            st.error("بيانات الدخول غير صحيحة.")

if st.session_state.is_admin:
    st.markdown("---")
    st.info("يمكنك الآن الدخول إلى صفحة الإعدادات.")

    if st.button("تسجيل خروج", use_container_width=True):
        st.session_state.is_admin = False
        st.session_state.admin_user = None
        st.success("تم تسجيل الخروج.")

st.markdown("---")
st.caption("ملاحظة: أول مرة إذا ما تم ضبط كلمة مرور من الإعدادات، استخدمي admin / admin.")
