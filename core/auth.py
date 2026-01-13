import streamlit as st

def is_admin():
    return st.session_state.get("is_admin", False)

def require_admin():
    if not is_admin():
        st.warning("الدخول مخصص للمشرف فقط")
        st.stop()

def login(username, password):
    if (
        username == st.secrets["ADMIN_USER"]
        and password == st.secrets["ADMIN_PASSWORD"]
    ):
        st.session_state["is_admin"] = True
        return True
    return False

def logout():
    st.session_state["is_admin"] = False
