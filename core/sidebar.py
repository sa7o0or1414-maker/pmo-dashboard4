import os
import streamlit as st
from core.config import load_config

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def _logo_block(cfg, where: str):
    logo = cfg.get("logo", {})
    if not logo.get("enabled", True):
        return
    location = logo.get("location", "sidebar")
    if location not in ["header", "sidebar", "both"]:
        location = "sidebar"

    if location != where and location != "both":
        return

    rel_path = logo.get("path", "assets/logo.png")
    abs_path = os.path.join(BASE_DIR, rel_path)

    if not os.path.exists(abs_path):
        return

    width = int(logo.get("width", 140))
    align = logo.get("align", "center")
    margin_top = int(logo.get("margin_top", 8))
    margin_bottom = int(logo.get("margin_bottom", 10))
    padding = int(logo.get("padding", 6))

    justify = {"left": "flex-start", "center": "center", "right": "flex-end"}.get(align, "center")

    st.markdown(
        f"""
        <div style="display:flex;justify-content:{justify};margin-top:{margin_top}px;margin-bottom:{margin_bottom}px;padding:{padding}px;">
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.image(abs_path, width=width)

def render_sidebar():
    cfg = load_config()

    # Header logo (top of page area)
    _logo_block(cfg, "header")

    with st.sidebar:
        # Sidebar logo
        _logo_block(cfg, "sidebar")

        st.markdown("## القائمة")
        st.page_link("pages/dashboard.py", label="الصفحة الرئيسية")
        st.page_link("pages/upload_data.py", label="رفع البيانات")
        st.page_link("pages/admin_login.py", label="دخول الأدمن")
        st.page_link("pages/settings.py", label="الإعدادات")
