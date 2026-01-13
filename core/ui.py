import streamlit as st

def hide_streamlit_default_nav():
    # يخفي قائمة صفحات Streamlit الافتراضية
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True,
    )
