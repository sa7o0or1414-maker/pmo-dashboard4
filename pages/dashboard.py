import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="لوحة التحكم", layout="wide")

# إخفاء السايدبار الافتراضي
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] > div:first-child {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# التحقق من وجود بيانات
if "data" not in st.session_state:
    st.warning("⚠️ الرجاء رفع ملف البيانات أولاً")
    st.stop()

df = st.session_state["data"].copy()

# ----------------------------
# دوال مساعدة
# ----------------------------
def safe_df(d):
    for c in d.columns:
        d[c] = d[c].astype(str)
    return d

def col_like(names):
    for c in df.columns:
        for n in names:
            if n in c.lower():
                return c
    return None

# الأعمدة الأساسية (مرنة عربي/إنجليزي)
status_col = col_like(["حالة", "status"])
entity_col = col_like(["جهة", "entity"])
municipality_col = col_like(["بلدية", "municipality"])
project_col = col_like(["مشروع", "project"])
value_col = col_like(["قيمة", "amount", "cost", "budget"])
spend_col = col_like(["صرف", "spend"])

# ----------------------------
# الفلاتر
# ----------------------------
st.subheader("🔎 الفلاتر")

c1, c2, c3 = st.columns(3)

with c1:
    status_filter = st.selectbox(
        "حالة المشروع",
        ["الكل"] + sorted(df[status_col].dropna().unique().tolist())
        if status_col else ["الكل"]
    )

with c2:
    municipality_filter = st.selectbox(
        "البلدية",
        ["الكل"] + sorted(df[municipality_col].dropna().unique().tolist())
        if municipality_col else ["الكل"]
    )

with c3:
    entity_filter = st.selectbox(
        "الجهة",
        ["الكل"] + sorted(df[entity_col].dropna().unique().tolist())
        if entity_col else ["الكل"]
    )

fdf = df.copy()
if status_col and status_filter != "الكل":
    fdf = fdf[fdf[status_col] == status_filter]
if municipality_col and municipality_filter != "الكل":
    fdf = fdf[fdf[municipality_col] == municipality_filter]
if entity_col and entity_filter != "الكل":
    fdf = fdf[fdf[entity_col] == entity_filter]

# ----------------------------
# الكروت العلوية
# ----------------------------
total_projects = len(fdf)

total_value = (
    pd.to_numeric(fdf[value_col], errors="coerce").sum()
    if value_col else 0
)

avg_spend = (
    pd.to_numeric(fdf[spend_col], errors="coerce").mean()
    if spend_col else 0
)

delayed_actual = (
    fdf[fdf[status_col].astype(str).str.contains("متأخر", na=False)]
    if status_col else pd.DataFrame()
)

delayed_pred = (
    fdf[fdf[status_col].astype(str).str.contains("متوقع", na=False)]
    if status_col else pd.DataFrame()
)

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("عدد المشاريع", total_projects)
k2.metric("إجمالي قيمة المشاريع", f"{total_value:,.0f}")
k3.metric("متوسط نسبة الصرف", f"{avg_spend:.1f}%")
k4.metric("عدد المشاريع المتأخرة", len(delayed_actual))
k5.metric("عدد المشاريع المتوقع تأخرها", len(delayed_pred))

st.divider()

# ----------------------------
# أيقونات تفاعلية (فتح / إغلاق)
# ----------------------------
if "show_actual" not in st.session_state:
    st.session_state.show_actual = False
if "show_pred" not in st.session_state:
    st.session_state.show_pred = False

c1, c2 = st.columns(2)

with c1:
    if st.button(f"🔴 المشاريع المتأخرة فعليًا ({len(delayed_actual)})"):
        st.session_state.show_actual = not st.session_state.show_actual

with c2:
    if st.button(f"🟠 المشاريع المتوقع تأخرها ({len(delayed_pred)})"):
        st.session_state.show_pred = not st.session_state.show_pred

# ----------------------------
# الجداول
# ----------------------------
if st.session_state.show_actual and not delayed_actual.empty:
    st.subheader("🔴 المشاريع المتأخرة فعليًا")
    st.dataframe(
        safe_df(delayed_actual),
        use_container_width=True,
        height=400
    )

if st.session_state.show_pred and not delayed_pred.empty:
    st.subheader("🟠 المشاريع المتوقع تأخرها (تحليل ذكي)")
    delayed_pred = delayed_pred.copy()
    delayed_pred["سبب التوقع"] = "انخفاض نسبة الصرف / مدة طويلة / تعقيد المشروع"
    st.dataframe(
        safe_df(delayed_pred),
        use_container_width=True,
        height=400
    )

st.divider()

# ----------------------------
# الرسوم
# ----------------------------
if status_col:
    st.subheader("📊 توزيع المشاريع حسب الحالة")
    status_counts = fdf[status_col].value_counts().reset_index()
    status_counts.columns = ["الحالة", "عدد المشاريع"]
    st.bar_chart(status_counts.set_index("الحالة"))

if municipality_col:
    st.subheader("🏙️ أكثر الجهات / البلديات مشاريع")
    muni_counts = fdf[municipality_col].value_counts().head(15)
    st.bar_chart(muni_counts)
    
