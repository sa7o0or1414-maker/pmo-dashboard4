import streamlit as st
from core.config import load_config, apply_branding
from core.auth import login, logout, is_admin

st.set_page_config(page_title="Admin Login", layout="wide")

cfg = load_config()
apply_branding(cfg)

st.title("Admin Login")

if is_admin():
    st.success("You are logged in as admin.")
    if st.button("Log out"):
        logout()
        st.rerun()
    st.stop()

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

if submitted:
    ok = login(username, password)
    if ok:
        st.success("Login successful.")
        st.rerun()
    else:
        st.error("Invalid username or password.")
