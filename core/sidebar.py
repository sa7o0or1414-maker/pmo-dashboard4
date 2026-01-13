import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.markdown("## 📊 لوحة التحكم")

        st.page_link(
            "pages/dashboard.py",
            label="🏠 الصفحة الرئيسية"
        )

        st.page_link(
            "pages/upload_data.py",
            label="⬆️ رفع البيانات"
        )

        st.page_link(
            "pages/admin_login.py",
            label="🔐 تسجيل الدخول"
        )

        # تظهر فقط لو الأدمن مسجل دخول
        if st.session_state.get("is_admin"):
            st.page_link(
                "pages/settings.py",
                label="⚙️ الإعدادات"
            )

        st.markdown("---")
        st.markdown(
            """
            <div style="font-size:12px;opacity:0.7;text-align:center">
            PMO Dashboard<br>
            تحليل ومتابعة المشاريع
            </div>
            """,
            unsafe_allow_html=True
        )
