import streamlit as st

def is_admin():
    return st.session_state.get("is_admin", False)

def require_admin():
    if not is_admin():
        st.warning("Admin access required")
        st.stop()

def login(user, password):
    if user == st.secrets["ADMIN_USER"] and password == st.secrets["ADMIN_PASSWORD"]:
        st.session_state["is_admin"] = True
        return True
    return False

def logout():
    st.session_state["is_admin"] = False
