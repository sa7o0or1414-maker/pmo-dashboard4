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

        st.markdown("---")
        st.markdown(
            """
            <div style="font-size:12px;opacity:0.7">
            PMO Dashboard<br>
            تحليل ومتابعة المشاريع
            </div>
            """,
            unsafe_allow_html=True
        )
