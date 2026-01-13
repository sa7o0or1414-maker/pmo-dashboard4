import streamlit as st

def hide_streamlit_default_nav():
    st.markdown(
        """
        <style>
        /* إخفاء قائمة Streamlit الافتراضية (الإنجليزية) */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        /* إخفاء الهيدر العلوي */
        header {
            visibility: hidden;
            height: 0px;
        }

        /* إخفاء Menu و Footer */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )
