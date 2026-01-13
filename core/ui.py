import streamlit as st

def hide_streamlit_default_nav():
    st.markdown(
        """
        <style>
          /* Hide Streamlit default multipage navigation */
          [data-testid="stSidebarNav"] { display: none !important; }

          /* Optional: hide default header/footer */
          #MainMenu {visibility: hidden;}
          footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )
