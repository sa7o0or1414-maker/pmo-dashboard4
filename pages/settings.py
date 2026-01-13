import streamlit as st
import streamlit as st

st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="الإعدادات",
    layout="wide"
)

from core.ui import hide_streamlit_default_nav
hide_streamlit_default_nav()

from core.sidebar import render_sidebar
render_sidebar()


if not st.session_state.get("is_admin"):
    st.error("هذه الصفحة للأدمن فقط")
    st.stop()

cfg = load_config()

st.title("الإعدادات")

primary = st.color_picker("اللون الأساسي", cfg["theme"]["primary"])
bg = st.color_picker("لون الخلفية", cfg["theme"]["bg"])

if st.button("حفظ"):
    cfg["theme"]["primary"] = primary
    cfg["theme"]["bg"] = bg
    save_config(cfg)
    st.success("تم الحفظ")
