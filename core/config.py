import json
import os
import streamlit as st

CONFIG_PATH = "data/config.json"

DEFAULT_CONFIG = {
    "site_title": "PMO Dashboard",
    "dashboard_title": "Project Portfolio Overview",
    "logo_path": "assets/logo.png",
    "brand": {
        "primary_color": "#7dd3fc",
        "background_color": "#0b1220",
        "panel_color": "#0f172a",
        "text_color": "#e5e7eb",
        "muted_text_color": "#94a3b8"
    },
    "layout": {
        "rtl": True,
        "kpi_font_size": 28,
        "sidebar_width": 320
    }
}


def ensure_defaults():
    os.makedirs("data", exist_ok=True)
    os.makedirs("assets", exist_ok=True)

    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def apply_branding(config: dict):
    brand = config.get("brand", {})
    layout = config.get("layout", {})

    rtl = layout.get("rtl", True)
    sidebar_width = layout.get("sidebar_width", 320)
    kpi_font_size = layout.get("kpi_font_size", 28)

    css = f"""
    <style>
        :root {{
            --primary-color: {brand.get("primary_color")};
            --background-color: {brand.get("background_color")};
            --panel-color: {brand.get("panel_color")};
            --text-color: {brand.get("text_color")};
            --muted-text-color: {brand.get("muted_text_color")};
        }}

        .stApp {{
            background-color: var(--background-color);
            color: var(--text-color);
        }}

        section[data-testid="stSidebar"] {{
            min-width: {sidebar_width}px;
        }}

        {"html, body { direction: rtl; text-align: right; }" if rtl else ""}

        .kpi-card {{
            background-color: var(--panel-color);
            border-radius: 14px;
            padding: 16px;
            border: 1px solid rgba(255,255,255,0.08);
        }}

        .kpi-label {{
            color: var(--muted-text-color);
            font-size: 13px;
        }}

        .kpi-value {{
            font-size: {kpi_font_size}px;
            font-weight: 700;
        }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

    logo_path = config.get("logo_path")
    if logo_path and os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_column_width=True)

    st.sidebar.markdown(f"### {config.get('site_title')}")
