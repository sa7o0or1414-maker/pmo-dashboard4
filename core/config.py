import json
import os
from typing import Any, Dict

import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
BACKUP_PATH = os.path.join(DATA_DIR, "config_backup.json")


def _default_config() -> Dict[str, Any]:
    # Defaults work even if user hasn't configured anything yet
    return {
        "site": {
            "title": "لوحة معلومات المشاريع",
        },
        "theme": {
            "primary": "#0f8f87",
            "secondary": "#0b5c56",
            "accent": "#d18b00",
            "bg": "#0e1117",
            "text": "#ffffff",
            "palette": ["#0f8f87", "#0b5c56", "#d18b00", "#b11212", "#5a67d8"],
        },
        "logo": {
            "enabled": True,
            "path": "assets/logo.png",
            "location": "sidebar",  # header | sidebar | both
            "width": 140,
            "align": "center",  # left | center | right
            "margin_top": 8,
            "margin_bottom": 10,
            "padding": 6,
        },
        "admin": {
            # First-time: you will set it from Settings page after login (or set manually).
            # If empty, login will accept "admin/admin" ONCE and then force you to set a new password in settings.
            "username": "admin",
            "password_hash": "",
        },
    }


def ensure_defaults() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        save_config(_default_config(), make_backup=False)


def load_config() -> Dict[str, Any]:
    ensure_defaults()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = _default_config()
        save_config(cfg, make_backup=False)

    # merge missing keys with defaults
    merged = _default_config()
    merged = _deep_merge(merged, cfg)
    return merged


def save_config(cfg: Dict[str, Any], make_backup: bool = True) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if make_backup and os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                current = f.read()
            with open(BACKUP_PATH, "w", encoding="utf-8") as f:
                f.write(current)
        except Exception:
            pass

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def restore_backup() -> bool:
    if not os.path.exists(BACKUP_PATH):
        return False
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(BACKUP_PATH, "r", encoding="utf-8") as f:
        data = f.read()
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(data)
    return True


def reset_to_defaults() -> None:
    save_config(_default_config(), make_backup=True)


def apply_branding(cfg: Dict[str, Any]) -> None:
    theme = cfg.get("theme", {})
    primary = theme.get("primary", "#0f8f87")
    secondary = theme.get("secondary", "#0b5c56")
    accent = theme.get("accent", "#d18b00")
    bg = theme.get("bg", "#0e1117")
    text = theme.get("text", "#ffffff")

    # Apply CSS site-wide
    st.markdown(
        f"""
        <style>
          html, body, [class*="css"] {{
            direction: rtl;
          }}
          .stApp {{
            background: {bg};
            color: {text};
          }}
          /* Buttons */
          .stButton>button {{
            background-color: {primary};
            color: {text};
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.12);
            font-weight: 700;
          }}
          .stButton>button:hover {{
            filter: brightness(1.05);
            border: 1px solid rgba(255,255,255,0.18);
          }}
          /* Selectbox / inputs borders */
          div[data-baseweb="select"] > div {{
            border-radius: 12px !important;
            border-color: rgba(255,255,255,0.14) !important;
          }}
          input, textarea {{
            border-radius: 12px !important;
          }}
          /* Accent links */
          a {{
            color: {accent} !important;
          }}
          /* Subtle separators */
          hr {{
            border-color: rgba(255,255,255,0.10);
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(a.get(k), dict):
            a[k] = _deep_merge(a[k], v)
        else:
            a[k] = v
    return a
