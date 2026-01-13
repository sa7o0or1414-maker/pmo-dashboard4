import json, os
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")

def ensure_defaults():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        save_config(default_config())

def default_config():
    return {
        "site": {"title": "لوحة معلومات المشاريع"},
        "theme": {
            "primary": "#0f8f87",
            "bg": "#0e1117",
            "text": "#ffffff"
        },
        "logo": {
            "enabled": True,
            "path": "assets/logo.png",
            "location": "sidebar",
            "width": 140
        },
        "admin": {
            "username": "admin",
            "password_hash": ""
        }
    }

def load_config():
    ensure_defaults()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def apply_branding(cfg):
    theme = cfg.get("theme", {})
    st.markdown(
        f"""
        <style>
        body {{
            background-color: {theme.get("bg","#0e1117")};
            color: {theme.get("text","#ffffff")};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
