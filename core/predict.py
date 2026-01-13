
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from core.data_io import prepare_dashboard_data
from core.predict import build_delay_outputs


st.set_page_config(layout="wide")

ensure_defaults()
cfg = load_config()
apply_branding(cfg)
render_sidebar()

st.title("لوحة معلومات المشاريع")

# ===================== Load Data =====================
df = prepare_dashboard_data()
if df.empty:
    st.warning("يرجى رفع ملف البيانات")
    st.stop()

df = build_delay_outputs(df)

# ===================== Filters =====================
def opt(col):
    if col not in df.columns:
        return ["الكل"]
    return ["الكل"] + sorted(df[col].dropna().unique().tolist())

f1, f2, f3, f4 = st.columns(4)

with f1:
    sel_entity = st.selectbox("الجهة", opt("entity"))
with f2:
    sel_muni = st.selectbox("البلدية", opt("municipality"))
with f3:
    sel_status = st.selectbox("حالة المشروع", opt("status"))
with f4:
    sel_type = st.selectbox("تصنيف المشروع", opt("project_type") if "project_type" in df.columns else ["الكل"])

fdf = df.copy()
if sel_entity != "الكل": fdf = fdf[fdf["entity"] == sel_entity]
if sel_muni != "الكل": fdf = fdf[fdf["municipality"] == sel_muni]
if sel_status != "الكل": fdf = fdf[fdf["status"] == sel_status]
if sel_type != "الكل" and "project_type" in fdf.columns:
    fdf = fdf[fdf["project_type"] == sel_type]

# ===================== KPI CARDS =====================
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.metric("عدد المشاريع", len(fdf))

with c2:
    st.metric("المشاريع المتعثرة", fdf["is_delayed_actual"].sum())

num_cols = [c for c in fdf.columns if pd.api.types.is_numeric_dtype(fdf[c])]

with c3:
    if num_cols:
        st.metric("قيمة المشاريع", f"{fdf[num_cols[0]].sum():,.0f}")

with c4:
    if len(num_cols) > 1:
        st.metric("المستخلصات", f"{fdf[num_cols[1]].sum():,.0f}")

with c5:
    if len(num_cols) > 2:
        st.metric("الأعمال المتبقية", f"{fdf[num_cols[2]].sum():,.0f}")

st.markdown("---")

# ===================== Main Layout =====================
left, mid, right = st.columns([3,4,2])

# -------- Table --------
with left:
    st.subheader("اسم المشروع")
    show_cols = [c for c in ["project", "entity", "municipality", "status", "progress", "risk_level"] if c in fdf.columns]
    st.dataframe(fdf[show_cols], height=420, use_container_width=True)

# -------- Stacked Bar --------
with mid:
    if "municipality" in fdf.columns and "status" in fdf.columns:
        fig = px.histogram(
            fdf,
            y="municipality",
            color="status",
            title="عدد المشاريع بالأمانات والبلديات",
            barmode="stack"
        )
        st.plotly_chart(fig, use_container_width=True)

# -------- Gauges --------
with right:
    delayed_pct = (fdf["is_delayed_actual"].mean() * 100) if len(fdf) else 0
    fig1 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=delayed_pct,
        title={"text": "مؤشر المشاريع المتعثرة"},
        gauge={"axis": {"range": [0, 100]}}
    ))
    st.plotly_chart(fig1, use_container_width=True)

    if num_cols:
        spend_pct = (fdf[num_cols[1]].sum() / fdf[num_cols[0]].sum()) * 100 if len(num_cols) > 1 else 0
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=spend_pct,
            title={"text": "نسبة الصرف"},
            gauge={"axis": {"range": [0, 100]}}
        ))
        st.plotly_chart(fig2, use_container_width=True)

# ===================== Status Distribution =====================
st.markdown("---")
st.subheader("عدد المشاريع حسب حالة المشروع")

if "status" in fdf.columns:
    fig = px.histogram(fdf, x="status", color="status")
    st.plotly_chart(fig, use_container_width=True)
