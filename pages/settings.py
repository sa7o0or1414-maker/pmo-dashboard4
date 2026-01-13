import os
import streamlit as st

from core.config import ensure_defaults, load_config, save_config, restore_backup, reset_to_defaults, ASSETS_DIR
from core.auth import hash_password

st.set_page_config(layout="wide")

ensure_defaults()
cfg = load_config()

st.title("الإعدادات")

# ===================== Admin Guard =====================
if not st.session_state.get("is_admin", False):
    st.error("هذه الصفحة للأدمن فقط. الرجاء تسجيل الدخول من صفحة (Admin Login).")
    st.stop()

# ===================== Helpers =====================
def _save_and_rerun(new_cfg):
    save_config(new_cfg, make_backup=True)
    st.success("تم حفظ الإعدادات.")
    st.rerun()

# ===================== Tabs =====================
tab1, tab2, tab3 = st.tabs(["الهوية والألوان", "اللوقو", "الأدمن والحفظ"])

# --------------------- Tab 1: Theme ---------------------
with tab1:
    st.subheader("الألوان")

    theme = cfg.get("theme", {})
    col1, col2, col3 = st.columns(3)

    with col1:
        primary = st.color_picker("Primary", value=theme.get("primary", "#0f8f87"))
        secondary = st.color_picker("Secondary", value=theme.get("secondary", "#0b5c56"))
    with col2:
        accent = st.color_picker("Accent", value=theme.get("accent", "#d18b00"))
        bg = st.color_picker("Background", value=theme.get("bg", "#0e1117"))
    with col3:
        text = st.color_picker("Text", value=theme.get("text", "#ffffff"))

    st.markdown("---")
    st.subheader("Palette")

    palette = list(theme.get("palette", [])) if isinstance(theme.get("palette", []), list) else []
    if "palette_edit" not in st.session_state:
        st.session_state.palette_edit = palette[:] if palette else [primary, secondary, accent]

    pcols = st.columns(5)
    for i in range(len(st.session_state.palette_edit)):
        with pcols[i % 5]:
            st.session_state.palette_edit[i] = st.color_picker(
                f"Color {i+1}",
                value=st.session_state.palette_edit[i],
                key=f"pal_{i}",
            )

    add_col, del_col = st.columns(2)
    with add_col:
        if st.button("إضافة لون", use_container_width=True):
            st.session_state.palette_edit.append("#ffffff")
            st.rerun()
    with del_col:
        if st.button("حذف آخر لون", use_container_width=True) and len(st.session_state.palette_edit) > 1:
            st.session_state.palette_edit.pop()
            st.rerun()

    st.markdown("---")
    st.subheader("عنوان الموقع")
    site_title = st.text_input("عنوان لوحة المعلومات", value=cfg.get("site", {}).get("title", "لوحة معلومات المشاريع"))

    if st.button("حفظ تغييرات الألوان والهوية", use_container_width=True):
        new_cfg = load_config()
        new_cfg["theme"] = {
            "primary": primary,
            "secondary": secondary,
            "accent": accent,
            "bg": bg,
            "text": text,
            "palette": st.session_state.palette_edit,
        }
        new_cfg["site"] = {"title": site_title}
        _save_and_rerun(new_cfg)

# --------------------- Tab 2: Logo ---------------------
with tab2:
    st.subheader("اللوقو")

    logo = cfg.get("logo", {})
    enabled = st.toggle("تفعيل اللوقو", value=bool(logo.get("enabled", True)))

    loc = st.selectbox(
        "موقع اللوقو",
        options=["header", "sidebar", "both"],
        index=["header", "sidebar", "both"].index(logo.get("location", "sidebar")) if logo.get("location", "sidebar") in ["header","sidebar","both"] else 1,
    )

    align = st.selectbox(
        "محاذاة اللوقو",
        options=["left", "center", "right"],
        index=["left","center","right"].index(logo.get("align", "center")) if logo.get("align","center") in ["left","center","right"] else 1,
    )

    width = st.slider("مقاس اللوقو (عرض px)", min_value=60, max_value=320, value=int(logo.get("width", 140)))
    margin_top = st.slider("مسافة أعلى", 0, 40, int(logo.get("margin_top", 8)))
    margin_bottom = st.slider("مسافة أسفل", 0, 40, int(logo.get("margin_bottom", 10)))
    padding = st.slider("Padding داخلي", 0, 30, int(logo.get("padding", 6)))

    st.markdown("---")
    st.subheader("رفع اللوقو")
    uploaded = st.file_uploader("ارفع صورة (PNG/JPG)", type=["png", "jpg", "jpeg"])

    saved_path = logo.get("path", "assets/logo.png")

    if uploaded is not None:
        os.makedirs(ASSETS_DIR, exist_ok=True)
        # keep as png if possible
        ext = os.path.splitext(uploaded.name)[1].lower()
        fname = "logo.png" if ext == ".png" else f"logo{ext}"
        out_path = os.path.join(ASSETS_DIR, fname)
        with open(out_path, "wb") as f:
            f.write(uploaded.getbuffer())
        saved_path = f"assets/{fname}"
        st.success("تم رفع اللوقو بنجاح.")

    # Preview
    abs_preview = os.path.join(os.path.dirname(os.path.dirname(__file__)), saved_path)
    if enabled and os.path.exists(abs_preview):
        st.image(abs_preview, width=width)

    st.markdown("---")
    if st.button("حفظ إعدادات اللوقو", use_container_width=True):
        new_cfg = load_config()
        new_cfg["logo"] = {
            "enabled": enabled,
            "path": saved_path,
            "location": loc,
            "width": width,
            "align": align,
            "margin_top": margin_top,
            "margin_bottom": margin_bottom,
            "padding": padding,
        }
        _save_and_rerun(new_cfg)

# --------------------- Tab 3: Admin + Save/Restore ---------------------
with tab3:
    st.subheader("الأدمن")

    admin_cfg = cfg.get("admin", {})
    st.text_input("اسم مستخدم الأدمن", value=admin_cfg.get("username", "admin"), disabled=True)

    st.markdown("تغيير كلمة المرور")
    new_pw = st.text_input("كلمة المرور الجديدة", type="password")
    new_pw2 = st.text_input("تأكيد كلمة المرور", type="password")

    if st.button("حفظ كلمة المرور", use_container_width=True):
        if not new_pw or len(new_pw) < 6:
            st.error("كلمة المرور يجب أن تكون 6 أحرف على الأقل.")
        elif new_pw != new_pw2:
            st.error("كلمتا المرور غير متطابقتين.")
        else:
            new_cfg = load_config()
            new_cfg["admin"]["password_hash"] = hash_password(new_pw)
            save_config(new_cfg, make_backup=True)
            st.success("تم حفظ كلمة المرور.")
            st.rerun()

    st.markdown("---")
    st.subheader("الحفظ والاسترجاع")

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("حفظ (Backup تلقائي)", use_container_width=True):
            # save current config again to ensure backup created
            save_config(load_config(), make_backup=True)
            st.success("تم إنشاء نسخة احتياطية.")

    with c2:
        if st.button("استرجاع آخر نسخة", use_container_width=True):
            ok = restore_backup()
            if ok:
                st.success("تم الاسترجاع.")
                st.rerun()
            else:
                st.error("لا توجد نسخة احتياطية للاسترجاع.")

    with c3:
        if st.button("إرجاع للوضع الافتراضي", use_container_width=True):
            reset_to_defaults()
            st.success("تمت إعادة الضبط للإعدادات الافتراضية.")
            st.rerun()
