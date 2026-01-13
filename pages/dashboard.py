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

# ===================== Styling =====================
st.markdown(
    """
    <style>
      html, body, [class*="css"] { direction: rtl; }
      .block-container { padding-top: 1.2rem; }
      .kpi{
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 14px;
        text-align: center;
      }
      .kpi h4{ margin:0; font-size:0.9rem; color:#cfd8dc; }
      .kpi h2{ margin:6px 0 0 0; font-size:1.6rem; color:white; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===================== Load Data =====================
st.title("لوحة المعلومات")

df = prepare_dashboard_data()
if df is None or df.empty:
    st.info("يرجى رفع ملف Excel من صفحة (رفع البيانات)")
    st.stop()

predict = importlib.import_module("core.predict")
df = predict.build_delay_outputs(df)

# ===================== Sidebar Filters =====================
st.sidebar.markdown("## تحديد النتائج")

def opt(col):
    if col not in df.columns:
        return ["الكل"]
    return ["الكل"] + sorted(df[col].dropna().astype(str).unique().tolist())

sel_status = st.sidebar.selectbox("حالة المشروع", opt("status"))
sel_muni = st.sidebar.selectbox("البلدية", opt("municipality"))
sel_entity = st.sidebar.selectbox("الجهة", opt("entity"))

fdf = df.copy()
if sel_status != "الكل" and "status" in fdf.columns:
    fdf = fdf[fdf["status"] == sel_status]
if sel_muni != "الكل" and "municipality" in fdf.columns:
    fdf = fdf[fdf["municipality"] == sel_muni]
if sel_entity != "الكل" and "entity" in fdf.columns:
    fdf = fdf[fdf["entity"] == sel_entity]

# ===================== KPI Calculations =====================
def pick_col(keywords):
    for c in fdf.columns:
        name = c.lower()
        if any(k in name for k in keywords) and pd.api.types.is_numeric_dtype(fdf[c]):
            return c
    return None

value_col = pick_col(["value","amount","budget","cost","قيمة","ميزانية","تكلفة"])
spent_col = pick_col(["spent","paid","صرف","مدفوع","مستخلص"])
remain_col = pick_col(["remaining","متبقي","باقي"])
progress_col = pick_col(["progress","انجاز","إنجاز","percent","%"])

total_projects = len(fdf)
total_value = fdf[value_col].sum() if value_col else 0
spent = fdf[spent_col].sum() if spent_col else 0
remaining = fdf[remain_col].sum() if remain_col else max(total_value - spent, 0)

avg_progress = 0
if progress_col:
    p = pd.to_numeric(fdf[progress_col], errors="coerce")
    if p.dropna().between(0,1).mean() > 0.7:
        p = p * 100
    avg_progress = p.mean()

actual_delayed = int(fdf["is_delayed_actual"].sum()) if "is_delayed_actual" in fdf.columns else 0
pred_delayed = int(fdf["is_delayed_predicted"].sum()) if "is_delayed_predicted" in fdf.columns else 0

# ===================== KPI Cards =====================
c1,c2,c3,c4 = st.columns(4)

with c1:
    st.markdown(f"<div class='kpi'><h4>عدد المشاريع</h4><h2>{total_projects}</h2></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='kpi'><h4>إجمالي قيمة المشاريع</h4><h2>{total_value/1e9:.2f} bn</h2></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='kpi'><h4>متوسط الإنجاز</h4><h2>{avg_progress:.1f}%</h2></div>", unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='kpi'><h4>التنبيهات</h4><h2>متأخر {actual_delayed} | متوقع {pred_delayed}</h2></div>", unsafe_allow_html=True)

st.markdown("---")

# ===================== Action Buttons =====================
if "view_mode" not in st.session_state:
    st.session_state.view_mode = None

b1,b2 = st.columns(2)
with b1:
    if st.button("المشاريع المتأخرة فعليًا", use_container_width=True):
        st.session_state.view_mode = "actual"
with b2:
    if st.button("المشاريع المتوقع تأخرها", use_container_width=True):
        st.session_state.view_mode = "pred"

# ===================== Results =====================
if st.session_state.view_mode == "actual":
    st.subheader("المشاريع المتأخرة فعليًا")
    df_a = fdf[fdf["is_delayed_actual"] == 1]
    if df_a.empty:
        st.info("لا توجد نتائج حسب الفلاتر الحالية")
    else:
        st.dataframe(df_a, use_container_width=True, height=420)

elif st.session_state.view_mode == "pred":
    st.subheader("المشاريع المتوقع تأخرها")
    df_p = fdf[fdf["is_delayed_predicted"] == 1]
    if df_p.empty:
        st.info("لا توجد نتائج حسب الفلاتر الحالية")
    else:
        cols = [c for c in [
            "project","entity","municipality",
            "risk_color","risk_level","delay_risk",
            "reason_short","reason_detail","action_recommendation"
        ] if c in df_p.columns]
        st.dataframe(df_p[cols] if cols else df_p, use_container_width=True, height=420)

st.markdown("---")

# ===================== Charts =====================
left,right = st.columns(2)

with left:
    st.subheader("توزيع المشاريع حسب الحالة")
    if "status" in fdf.columns:
        fig1 = px.histogram(fdf, x="status")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("لا يوجد عمود حالة")

with right:
    st.subheader("أكثر البلديات / الجهات مشاريع")
    group_col = "municipality" if "municipality" in fdf.columns else ("entity" if "entity" in fdf.columns else None)
    if group_col:
        top = (
            fdf[group_col]
            .fillna("غير محدد")
            .value_counts()
            .head(20)
            .reset_index()
        )
        top.columns = ["الاسم","العدد"]

        fig2 = px.bar(top, x="الاسم", y="العدد", text="العدد")
        fig2.update_layout(showlegend=False)
        fig2.update_xaxes(tickangle=-30)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("لا يوجد عمود بلدية أو جهة")

# ===================== Gauges =====================
g1,g2 = st.columns(2)

with g1:
    pct_delay = (actual_delayed/total_projects*100) if total_projects else 0
    fig_g1 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct_delay,
        title={"text":"مؤشر المشاريع المتعثرة"},
        gauge={"axis":{"range":[0,100]}},
        number={"suffix":"%"}
    ))
    st.plotly_chart(fig_g1, use_container_width=True)

with g2:
    pct_spent = (spent/total_value*100) if total_value else 0
    fig_g2 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct_spent,
        title={"text":"نسبة الصرف"},
        gauge={"axis":{"range":[0,100]}},
        number={"suffix":"%"}
    ))
    st.plotly_chart(fig_g2, use_container_width=True)
