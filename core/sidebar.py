import streamlit as st

def render_sidebar():
    st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    section[data-testid="stSidebar"] a {
        display: block;
        padding: 10px;
        border-radius: 12px;
        margin-bottom: 8px;
        background: rgba(255,255,255,.04);
        border: 1px solid rgba(255,255,255,.1);
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("### Menu")

    st.page_link("pages/dashboard.py", label="Home")
    st.sidebar.markdown("#### Admin")
    st.page_link("pages/upload_data.py", label="Upload Data")
    st.page_link("pages/settings.py", label="Settings")
    st.page_link("pages/admin_login.py", label="Admin Login")
