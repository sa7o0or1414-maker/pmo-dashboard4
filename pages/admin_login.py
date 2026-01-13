import streamlit as st
from core.config import load_config, apply_branding
from core.auth import login, logout, is_admin
from core.sidebar import render_sidebar

st.set_page_config(layout="wide")

cfg = load_config()
apply_branding(cfg)
render_sidebar()

st.title("Admin Login")

if is_admin():
    st.success("Logged in")
    if st.button("Logout"):
        logout()
        st.rerun()
else:
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(user, pwd):
            st.success("Success")
            st.rerun()
        else:
            st.error("Invalid credentials")
