import streamlit as st
import pandas as pd
import plotly.express as px

# 1) لازم أول سطر Streamlit
st.set_page_config(page_title="الصفحة الرئيسية", layout="wide")

from core.ui import hide_streamlit_default_nav
from core.sidebar import render_sidebar
from core.data_io import load_latest_data

# 2) اخفاء قائمة ستريملت الافتراضية (app/dashboard...)
hide_streamlit_default_nav()
# 3) سايدبارنا العربي
render_sidebar()

# -----------------------------
# Helpers
# -----------------------------
def find_col(df, keywords):
    for c in df.columns:
        name = str(c).lower()
        if any(k.lower() in name for k in keywords):
            return c
    return None

def fmt_big(n):
    try:
        n = float(n)
        if abs(n) >= 1e9:
            return f"{n/1e9:.2f} مليار"
        if abs(n) >= 1e6:
            return f"{n/1e6:.2f} مليون"
        return f"{n:,.0f}"
    except Exception:
        return "—"

# -----------------------------
# Load latest saved data
# -----------------------------
df = load_latest_data()

if df is None or df.empty:
    st.warning("الرجاء رفع ملف البيانات أولًا من صفحة (رفع البيانات).")
    st.stop()

# -----------------------------
# Detect columns
# -----------------------------
status_col = find_col(df, ["status", "حالة"])
entity_col = find_col(df, ["entity", "جهة"])
municipality_col = find_col(df, ["municipality", "بلدية"])
value_col = find_col(df, ["value", "amount", "budget", "cost", "قيمة", "ميزانية", "تكلفة"])
progress_col = find_col(df, ["progress", "إنجاز", "انجاز", "%"])
spend_ratio_col = find_col(df, ["نسبة الصرف", "spend ratio", "spending"])

# -----------------------------
# Filters (على الصفحة نفسها مثل الصورة)
# -----------------------------
st.markdown("## الفلاتر")
c1, c2, c3 = st.columns(3)

fdf = df.copy()

with c1:
    if entity_col:
        ent_vals = ["الكل"] + sorted(fdf[entity_col].dropna().astype(str).unique().tolist())
        ent = st.selectbox("الجهة", ent_vals)
        if ent != "الكل":
            fdf = fdf[fdf[entity_col].astype(str) == ent]
    else:
        st.selectbox("الجهة", ["غير متوفر"], disabled=True)

with c2:
    if municipality_col:
        mun_vals = ["الكل"] + sorted(fdf[municipality_col].dropna().astype(str).unique().tolist())
        mun = st.selectbox("البلدية", mun_vals)
        if mun != "الكل":
            fdf = fdf[fdf[municipality_col].astype(str) == mun]
    else:
        st.selectbox("البلدية", ["غير متوفر"], disabled=True)

with c3:
    if status_col:
        st_vals = ["الكل"] + sorted(fdf[status_col].dropna().astype(str).unique().tolist())
        stt = st.selectbox("حالة المشروع", st_vals)
        if stt != "الكل":
            fdf = fdf[fdf[status_col].astype(str) == stt]
    else:
        st.selectbox("حالة المشروع", ["غير متوفر"], disabled=True)

# -----------------------------
# KPIs
# -----------------------------
total_projects = len(fdf)
total_value = pd.to_numeric(fdf[value_col], errors="coerce").sum() if value_col else 0

avg_progress = 0
if progress_col:
    p = pd.to_numeric(fdf[progress_col], errors="coerce")
    if p.dropna().between(0, 1).mean() > 0.6:
        p = p * 100
    avg_progress = float(p.mean()) if p.notna().any() else 0

# نسبة الصرف من عمود نسبة الصرف إن وجد
spend_ratio = 0
if spend_ratio_col:
    sr = pd.to_numeric(fdf[spend_ratio_col], errors="coerce")
    if sr.dropna().between(0, 1).mean() > 0.6:
        sr = sr * 100
    spend_ratio = float(sr.mean()) / 100 if sr.notna().any() else 0

# عدد المتعثرة من حالة المشاريع (لو تحتوي متعثر/متأخر)
troubled = 0
if status_col:
    troubled = fdf[status_col].astype(str).str.contains("متعثر|متأخر", case=False, na=False).sum()

st.markdown("## لوحة المعلومات")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("عدد المشاريع", total_projects)
k2.metric("إجمالي قيمة المشاريع", fmt_big(total_value))
k3.metric("متوسط الإنجاز", f"{avg_progress:.1f}%")
k4.metric("عدد المشاريع المتعثرة", troubled)
k5.metric("نسبة الصرف", f"{spend_ratio*100:.1f}%" if spend_ratio else "—")

st.markdown("---")

# -----------------------------
# Charts (مثل أول)
# -----------------------------
st.markdown("## التحليلات")
left, right = st.columns(2)

with left:
    st.subheader("توزيع المشاريع حسب الحالة")
    if status_col and not fdf.empty:
        status_df = (
            fdf[status_col]
            .fillna("غير محدد")
            .astype(str)
            .value_counts()
            .reset_index()
        )
        status_df.columns = ["الحالة", "عدد المشاريع"]
        fig = px.bar(status_df, x="الحالة", y="عدد المشاريع", text="عدد المشاريع")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا يوجد عمود لحالة المشاريع أو لا توجد بيانات بعد الفلاتر.")

with right:
    st.subheader("أكثر الجهات / البلديات مشاريع")
    group_col = municipality_col or entity_col
    if group_col and not fdf.empty:
        top_df = (
            fdf[group_col]
            .fillna("غير محدد")
            .astype(str)
            .value_counts()
            .head(15)
            .reset_index()
        )
        top_df.columns = ["الجهة/البلدية", "عدد المشاريع"]
        fig2 = px.bar(top_df, x="الجهة/البلدية", y="عدد المشاريع", text="عدد المشاريع")
        fig2.update_layout(showlegend=False)
        fig2.update_xaxes(tickangle=-30)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("لا يوجد عمود للجهة/البلدية أو لا توجد بيانات بعد الفلاتر.")

with st.expander("عرض البيانات بعد الفلاتر"):
    st.dataframe(fdf, use_container_width=True)
