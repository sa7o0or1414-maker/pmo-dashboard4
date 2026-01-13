import streamlit as st


def is_admin() -> bool:
    return bool(st.session_state.get("is_admin", False))


def require_admin():
    if not is_admin():
        st.warning("Admin access required. Please log in from the Admin Login page.")
        st.stop()


def login(username: str, password: str) -> bool:
    admin_user = st.secrets.get("ADMIN_USER", "")
    admin_pass = st.secrets.get("ADMIN_PASSWORD", "")

    if username == admin_user and password == admin_pass:
        st.session_state["is_admin"] = True
        return True

    return False


def logout():
    st.session_state["is_admin"] = False
