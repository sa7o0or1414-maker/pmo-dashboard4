import streamlit as st

# إعداد الصفحة (مرة واحدة فقط)
st.set_page_config(
    page_title="لوحة تحكم PMO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# إخفاء الـ Navigation الافتراضي (الإنجليزي)
st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

# إنشاء حالة تسجيل الدخول
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# سايد بار عربي مخصص
with st.sidebar:
    st.markdown("## 📊 لوحة التحكم")

    if st.button("🏠 الصفحة الرئيسية"):
        st.switch_page("pages/dashboard.py")

    if st.button("⬆️ رفع البيانات"):
        if st.session_state.logged_in:
            st.switch_page("pages/upload_data.py")
        else:
            st.warning("🔒 يجب تسجيل الدخول أولًا")

    if st.button("🔐 تسجيل الدخول"):
        st.switch_page("pages/admin_login.py")

    if st.session_state.logged_in:
        if st.button("🚪 تسجيل الخروج"):
            st.session_state.logged_in = False
            st.success("تم تسجيل الخروج")

# التوجيه الافتراضي
st.switch_page("pages/dashboard.py")
