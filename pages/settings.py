import streamlit as st
from core.config import load_config, save_config, apply_branding
from core.auth import require_admin

st.set_page_config(page_title="Settings", layout="wide")

cfg = load_config()
apply_branding(cfg)

require_admin()

st.title("Settings")

st.subheader("Titles")
cfg["site_title"] = st.text_input("Site title", value=cfg.get("site_title", "PMO Dashboard"))
cfg["dashboard_title"] = st.text_input("Dashboard title", value=cfg.get("dashboard_title", "Dashboard"))

st.subheader("Brand colors")
brand = cfg.get("brand", {})
brand["primary_color"] = st.color_picker("Primary color", value=brand.get("primary_color", "#7dd3fc"))
brand["background_color"] = st.color_picker("Background color", value=brand.get("background_color", "#0b1220"))
brand["panel_color"] = st.color_picker("Panel color", value=brand.get("panel_color", "#0f172a"))
brand["text_color"] = st.color_picker("Text color", value=brand.get("text_color", "#e5e7eb"))
brand["muted_text_color"] = st.color_picker("Muted text color", value=brand.get("muted_text_color", "#94a3b8"))
cfg["brand"] = brand

st.subheader("Layout")
layout = cfg.get("layout", {})
layout["rtl"] = st.checkbox("Right-to-left layout", value=layout.get("rtl", True))
layout["sidebar_width"] = st.slider("Sidebar width", 240, 460, int(layout.get("sidebar_width", 320)), 10)
layout["kpi_font_size"] = st.slider("KPI font size", 18, 44, int(layout.get("kpi_font_size", 28)), 1)
cfg["layout"] = layout

st.subheader("Logo")
cfg["logo_path"] = st.text_input("Logo path", value=cfg.get("logo_path", "assets/logo.png"))
st.caption("Upload your logo file to assets/ and set its path here.")

if st.button("Save settings"):
    save_config(cfg)
    st.success("Settings saved. Refreshing...")
    st.rerun()
