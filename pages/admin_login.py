import streamlit as st
from core.config import ensure_defaults, load_config, apply_branding
from core.auth import login, logout, is_admin
from core.sidebar import render_sidebar

st.set_page_config(layout="wide")

ensure_defaults()
cfg = load_config()
apply_branding(cfg)
render_sidebar()

st.title("Admin Login")

if is_admin():
    st.success("Logged in as admin")
    if st.button("Logout"):
        logout()
        st.rerun()
else:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(username, password):
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")
