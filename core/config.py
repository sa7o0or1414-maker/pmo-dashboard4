import json
import os
import streamlit as st

CONFIG_PATH = "data/config.json"

DEFAULT_CONFIG = {
    "site_title": "لوحة معلومات PMO",
    "dashboard_title": "الصفحة الرئيسية",
    "brand": {
        "background": "#0b1220",
        "panel": "#0f172a",
        "text": "#e5e7eb",
        "muted": "#94a3b8",
        "primary": "#38bdf8"
    },
    "layout": {
        "rtl": True,
        "sidebar_width": 300
    }
}

def ensure_defaults():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        return

    # upgrade old config safely
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    updated = False

    if "brand" not in cfg:
        cfg["brand"] = DEFAULT_CONFIG["brand"]
        updated = True
    else:
        for k, v in DEFAULT_CONFIG["brand"].items():
            if k not in cfg["brand"]:
                cfg["brand"][k] = v
                updated = True

    if "layout" not in cfg:
        cfg["layout"] = DEFAULT_CONFIG["layout"]
        updated = True
    else:
        for k, v in DEFAULT_CONFIG["layout"].items():
            if k not in cfg["layout"]:
                cfg["layout"][k] = v
                updated = True

    if "site_title" not in cfg:
        cfg["site_title"] = DEFAULT_CONFIG["site_title"]
        updated = True

    if "dashboard_title" not in cfg:
        cfg["dashboard_title"] = DEFAULT_CONFIG["dashboard_title"]
        updated = True

    if updated:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)

def load_config():
    ensure_defaults()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def apply_branding(cfg):
    b = cfg["brand"]
    l = cfg["layout"]

    st.markdown(f"""
    <style>
    html, body {{
        direction: rtl;
        background-color: {b['background']};
        color: {b['text']};
    }}

    .stApp {{
        background-color: {b['background']};
    }}

    section[data-testid="stSidebar"] {{
        min-width: {l['sidebar_width']}px;
        background-color: {b['panel']};
    }}

    [data-testid="stSidebarNav"] {{
        display: none;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(f"### {cfg['site_title']}")
