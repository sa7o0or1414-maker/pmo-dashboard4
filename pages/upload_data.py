import streamlit as st
import pandas as pd

st.set_page_config(page_title="رفع البيانات", layout="wide")

# إخفاء السايدبار الافتراضي
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] > div:first-child {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("📤 رفع ملف البيانات")

uploaded_file = st.file_uploader(
    "ارفع ملف المشاريع (Excel)",
    type=["xlsx", "xls"]
)

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        # تنظيف عام
        df.columns = df.columns.astype(str).str.strip()

        st.session_state["data"] = df
        st.success("✅ تم رفع الملف بنجاح وسيتم استخدامه في لوحة التحكم")

        st.dataframe(df.head(), use_container_width=True)

    except Exception as e:
        st.error(f"❌ خطأ في قراءة الملف: {e}")
