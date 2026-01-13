import streamlit as st
import plotly.express as px
import pandas as pd
import bootstrap  # noqa: F401

from core.config import ensure_defaults, load_config, apply_branding
from core.sidebar import render_sidebar
from core.data_io import prepare_dashboard_data
from core.predict import build_delay_outputs

st.set_page_config(layout="wide")

ensure_defaults()
cfg = load_config()
apply_branding(cfg)
render_sidebar()

st.title("الصفحة الرئيسية")

# ===================== Load Data =====================
df = prepare_dashboard_data()
if df is None or df.empty:
    st.info("لا توجد بيانات. ارفعي ملف Excel من صفحة (رفع البيانات).")
    st.stop()

df = build_delay_outputs(df)

# ===================== Filters =====================
st.sidebar.markdown("---")
st.sidebar.markdown("### الفلاتر")

def _options(col):
    if col not in df.columns:
        return ["الكل"]
    vals = sorted([v for v in df[col].dropna().unique() if str(v).strip()])
    return ["الكل"] + vals

muni = st.sidebar.selectbox("البلدية", _options("municipality"))
entity = st.sidebar.selectbox("الجهة", _options("entity"))
status = st.sidebar.selectbox("حالة المشروع", _options("status"))

fdf = df.copy()
if muni != "الكل" and "municipality" in fdf.columns:
    fdf = fdf[fdf["municipality"] == muni]
if entity != "الكل" and "entity" in fdf.columns:
    fdf = fdf[fdf["entity"] == entity]
if status != "الكل" and "status" in fdf.columns:
    fdf = fdf[fdf["status"] == status]

# ===================== AUTO KPI CARDS =====================
numeric_cols = [
    c for c in fdf.columns
    if pd.api.types.is_numeric_dtype(fdf[c])
    and c not in ["delay_risk", "days_to_deadline"]
]

if numeric_cols:
    st.markdown("### مؤشرات رقمية من الملف")
    cols = st.columns(min(4, len(numeric_cols)))
    for i, col in enumerate(numeric_cols[:4]):
        with cols[i]:
            st.metric(
                label=col,
                value=f"{fdf[col].sum(skipna=True):,.0f}",
                delta=f"متوسط {fdf[col].mean(skipna=True):,.1f}"
            )

st.markdown("---")

# ===================== Risk Buttons =====================
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "overview"

b1, b2, b3 = st.columns(3)
with b1:
    if st.button("المشاريع المتأخرة فعليًا", use_container_width=True):
        st.session_state.view_mode = "actual"
with b2:
    if st.button("المشاريع المتوقع تأخرها", use_container_width=True):
        st.session_state.view_mode = "pred"
with b3:
    if st.button("ملخص", use_container_width=True):
        st.session_state.view_mode = "overview"

# ===================== Tables =====================
def show_table(title, tdf, extra_cols=None):
    if tdf.empty:
        st.info("لا توجد نتائج")
        return

    cols = list(tdf.columns)
    if extra_cols:
        cols = [c for c in cols if c not in extra_cols] + extra_cols

    sort_col = "delay_risk" if "delay_risk" in tdf.columns else cols[0]
    st.subheader(title)
    st.dataframe(
        tdf.sort_values(by=sort_col, ascending=False)[cols],
        use_container_width=True
    )

if st.session_state.view_mode == "actual":
    show_table("المشاريع المتأخرة فعليًا", fdf[fdf["is_delayed_actual"] == 1])

elif st.session_state.view_mode == "pred":
    show_table(
        "المشاريع المتوقع تأخرها",
        fdf[fdf["is_delayed_predicted"] == 1],
        extra_cols=[
            "risk_color",
            "risk_level",
            "delay_risk",
            "reason_short",
            "reason_detail",
            "action_recommendation",
        ],
    )

# ===================== Analysis =====================
st.markdown("---")
st.subheader("تحليل شامل")

if "status" in fdf.columns:
    st.plotly_chart(
        px.histogram(fdf, x="status", title="توزيع المشاريع حسب الحالة"),
        use_container_width=True
    )

st.dataframe(fdf.head(200), use_container_width=True)
