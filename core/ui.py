import streamlit as st

def hide_streamlit_default_nav():
    st.markdown(
        """
        <style>
        /* Hide Streamlit multipage default navigation */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        /* Hide Streamlit menu & footer */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )
