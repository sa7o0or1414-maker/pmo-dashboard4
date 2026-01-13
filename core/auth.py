import streamlit as st

def is_admin():
    return st.session_state.get("is_admin", False)

def require_admin():
    if not is_admin():
        st.warning("الدخول مخصص للمشرف فقط")
        st.stop()

def login(username, password):
    try:
        admin_user = st.secrets["ADMIN_USER"]
        admin_pass = st.secrets["ADMIN_PASSWORD"]
    except Exception:
        st.error("Secrets غير مضافة في Streamlit Cloud (ADMIN_USER / ADMIN_PASSWORD)")
        st.stop()

    if username == admin_user and password == admin_pass:
        st.session_state["is_admin"] = True
        return True
    return False

def logout():
    st.session_state["is_admin"] = False
