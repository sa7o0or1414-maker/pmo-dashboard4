import json
import os
import streamlit as st

CONFIG_PATH = "data/config.json"

DEFAULT_CONFIG = {
    "site_title": "PMO Dashboard",
    "dashboard_title": "Project Portfolio Overview",
    "brand": {
        "primary_color": "#7dd3fc",
        "background_color": "#0b1220",
        "panel_color": "#0f172a",
        "text_color": "#e5e7eb",
        "muted_text_color": "#94a3b8"
    },
    "layout": {
        "rtl": True,
        "sidebar_width": 300,
        "kpi_font_size": 26
    }
}

def ensure_defaults():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)

def load_config():
    ensure_defaults()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def apply_branding(cfg):
    brand = cfg["brand"]
    layout = cfg["layout"]

    css = f"""
    <style>
    html, body {{
        direction: {"rtl" if layout["rtl"] else "ltr"};
    }}
    .stApp {{
        background-color: {brand["background_color"]};
        color: {brand["text_color"]};
    }}
    section[data-testid="stSidebar"] {{
        min-width: {layout["sidebar_width"]}px;
    }}
    .kpi-card {{
        background: {brand["panel_color"]};
        padding: 16px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,.08);
    }}
    .kpi-label {{
        color: {brand["muted_text_color"]};
        font-size: 13px;
    }}
    .kpi-value {{
        font-size: {layout["kpi_font_size"]}px;
        font-weight: 700;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    st.sidebar.markdown(f"### {cfg['site_title']}")
