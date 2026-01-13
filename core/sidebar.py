import streamlit as st

def render_sidebar():
    st.sidebar.markdown(
        """
        <div style="padding: 8px 6px;">
          <div style="font-size:18px;font-weight:700;">لوحة معلومات PMO</div>
          <div style="opacity:.7;font-size:12px;margin-top:4px;">القائمة</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")
    st.sidebar.page_link("pages/dashboard.py", label="الصفحة الرئيسية")
    st.sidebar.page_link("pages/upload_data.py", label="رفع البيانات")
    st.sidebar.page_link("pages/settings.py", label="الإعدادات")
    st.sidebar.page_link("pages/admin_login.py", label="دخول المشرف")
