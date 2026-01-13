import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import importlib

from core.data_io import prepare_dashboard_data
from core.sidebar import render_sidebar
from core.config import ensure_defaults, load_config, apply_branding

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

# ✅ import ديناميكي (يكسر الـ Circular Import نهائيًا)
predict = importlib.import_module("core.predict")
df = predict.build_delay_outputs(df)

# ===================== Filters =====================
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
    st.metric(
        "المشاريع المتوقع تأخرها",
        int(fdf["is_delayed_predicted"].sum())
    )

st.markdown("---")

# ===================== Tables =====================
b1, b2 = st.columns(2)

with b1:
    st.subheader("المشاريع المتأخرة فعليًا")
    st.dataframe(
        fdf[fdf["is_delayed_actual"] == 1],
        use_container_width=True,
        height=400
    )

with b2:
    st.subheader("المشاريع المتوقع تأخرها")
    show_cols = [
        c for c in [
            "project",
            "entity",
            "municipality",
            "risk_color",
            "risk_level",
            "delay_risk",
            "reason_short",
            "action_recommendation",
        ]
        if c in fdf.columns
    ]
    st.dataframe(
        fdf[fdf["is_delayed_predicted"] == 1][show_cols],
        use_container_width=True,
        height=400
    )

# ===================== Charts =====================
st.markdown("---")

if "status" in fdf.columns:
    fig = px.histogram(
        fdf,
        x="status",
        color="status",
        title="عدد المشاريع حسب حالة المشروع"
    )
    st.plotly_chart(fig, use_container_width=True)

delayed_pct = (fdf["is_delayed_actual"].mean() * 100) if len(fdf) else 0
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=delayed_pct,
    title={"text": "مؤشر المشاريع المتعثرة"},
    gauge={"axis": {"range": [0, 100]}}
))
st.plotly_chart(fig, use_container_width=True)
