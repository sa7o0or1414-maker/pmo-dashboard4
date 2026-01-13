import streamlit as st

def hide_streamlit_default_nav():
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] { display: none !important; }
        header { visibility: hidden; height: 0px; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )
