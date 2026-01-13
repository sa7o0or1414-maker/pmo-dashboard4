import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import importlib

from core.data_io import prepare_dashboard_data
from core.sidebar import render_sidebar
from core.config import ensure_defaults, load_config, apply_branding

# ===================== Page Config =====================
st.set_page_config(layout="wide")

ensure_defaults()
cfg = load_config()
apply_branding(cfg)
render_sidebar()

st.title("لوحة معلومات المشاريع")

# ===================== Load Data =====================
df = prepare_dashboard_data()
if df is None or df.empty:
    st.info("يرجى رفع ملف Excel من صفحة (رفع البيانات)")
    st.stop()

# ✅ تحميل التنبؤ بدون Circular Import
predict = importlib.import_module("core.predict")
df = predict.build_delay_outputs(df)

# ===================== Filters =====================
st.markdown("### الفلاتر")

def opt(col):
    if col not in df.columns:
        return ["الكل"]
    return ["الكل"] + sorted(df[col].dropna().unique().tolist())

f1, f2, f3 = st.columns(3)
with f1:
    sel_entity = st.selectbox("الجهة", opt("entity"))
with f2:
    sel_muni = st.selectbox("البلدية", opt("municipality"))
with f3:
    sel_status = st.selectbox("حالة المشروع", opt("status"))

fdf = df.copy()
if sel_entity != "الكل" and "entity" in fdf.columns:
    fdf = fdf[fdf["entity"] == sel_entity]
if sel_muni != "الكل" and "municipality" in fdf.columns:
    fdf = fdf[fdf["municipality"] == sel_muni]
if sel_status != "الكل" and "status" in fdf.columns:
    fdf = fdf[fdf["status"] == sel_status]

# ===================== KPI CARDS =====================
st.markdown("### ملخص عام")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("عدد المشاريع", len(fdf))

with c2:
    st.metric("المشاريع المتأخرة فعليًا", int(fdf["is_delayed_actual"].sum()))

num_cols = [c for c in fdf.columns if pd.api.types.is_numeric_dtype(fdf[c])]

with c3:
    st.metric(
        "قيمة المشاريع",
        f"{fdf[num_cols[0]].sum():,.0f}" if num_cols else "—"
    )

with c4:
    st.metric("المشاريع المتوقع تأخرها", int(fdf["is_delayed_predicted"].sum()))

st.markdown("---")

# =====================================================
# 🧠 التحليل الذكي (أزرار تفاعلية)
# =====================================================
st.markdown("### التحليل الذكي للمشاريع")

if "view_mode" not in st.session_state:
    st.session_state.view_mode = None

b1, b2 = st.columns(2)

with b1:
    if st.button("🟥 المشاريع المتأخرة فعليًا", use_container_width=True):
        st.session_state.view_mode = "actual"

with b2:
    if st.button("🟧 المشاريع المتوقع تأخرها", use_container_width=True):
        st.session_state.view_mode = "pred"

# ===================== Results =====================
st.markdown("---")

if st.session_state.view_mode == "actual":
    st.subheader("المشاريع المتأخرة فعليًا")

    df_actual = fdf[fdf["is_delayed_actual"] == 1]

    if df_actual.empty:
        st.info("لا توجد مشاريع متأخرة فعليًا حسب البيانات الحالية")
    else:
        st.dataframe(
            df_actual,
            use_container_width=True,
            height=450
        )

elif st.session_state.view_mode == "pred":
    st.subheader("المشاريع المتوقع تأخرها (تحليل تنبؤي ذكي)")

    df_pred = fdf[fdf["is_delayed_predicted"] == 1]

    if df_pred.empty:
        st.info("لا توجد مشاريع عالية الخطورة حاليًا")
    else:
        show_cols = [
            c for c in [
                "project",
                "entity",
                "municipality",
                "risk_color",
                "risk_level",
                "delay_risk",
                "reason_short",
                "reason_detail",
                "action_recommendation",
            ]
            if c in df_pred.columns
        ]

        st.dataframe(
            df_pred[show_cols],
            use_container_width=True,
            height=450
        )

# ===================== Charts =====================
st.markdown("---")
st.subheader("تحليل الحالات")

if "status" in fdf.columns:
    fig = px.histogram(
        fdf,
        x="status",
        color="status",
        title="عدد المشاريع حسب حالة المشروع"
    )
    st.plotly_chart(fig, use_container_width=True)

# Gauge: نسبة التعثر
delayed_pct = (fdf["is_delayed_actual"].mean() * 100) if len(fdf) else 0
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=delayed_pct,
    title={"text": "مؤشر المشاريع المتعثرة"},
    gauge={"axis": {"range": [0, 100]}}
))
st.plotly_chart(fig, use_container_width=True)
