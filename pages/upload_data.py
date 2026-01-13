import streamlit as st
import pandas as pd

st.title("⬆️ رفع البيانات")

file = st.file_uploader("ارفع ملف Excel", type=["xlsx", "xls"])

if file:
    df = pd.read_excel(file)
    st.session_state["data"] = df
    st.success("✅ تم رفع البيانات بنجاح")
    st.dataframe(df.head(), use_container_width=True)
