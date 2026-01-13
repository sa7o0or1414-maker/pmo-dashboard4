import streamlit as st

# مهم جدًا: مرة واحدة فقط
st.set_page_config(
    page_title="لوحة تحكم PMO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# توجيه للداش بورد
st.switch_page("pages/dashboard.py")
