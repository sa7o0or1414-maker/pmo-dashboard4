import streamlit as st

st.set_page_config(
    page_title="رفع البيانات",
    layout="wide"
)

from core.ui import hide_streamlit_default_nav
from core.sidebar import render_sidebar
from core.data_io import save_uploaded_file

hide_streamlit_default_nav()
render_sidebar()

st.markdown("## ⬆️ رفع ملف البيانات")

st.info(
    "يرجى رفع ملف Excel واحد فقط. "
    "سيتم تحديث لوحة المعلومات تلقائيًا بعد الرفع."
)

uploaded_file = st.file_uploader(
    "اختر ملف Excel",
    type=["xlsx"]
)

if uploaded_file:
    save_uploaded_file(uploaded_file)
    st.success("✅ تم رفع الملف بنجاح")
    st.info("انتقلي الآن إلى الصفحة الرئيسية لمشاهدة التحديثات")
