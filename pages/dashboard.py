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

# ✅ import predict safely (no circular import)
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

# =====================================================
# ✅ KPI + Gauges + Status chart (مثل Power BI)
# =====================================================
st.markdown("## المؤشرات الرئيسية")

total_projects = len(fdf)
delayed_actual = int(fdf["is_delayed_actual"].sum()) if "is_delayed_actual" in fdf.columns else 0
delayed_pct = (delayed_actual / total_projects * 100) if total_projects else 0
predicted_delayed = int(fdf["is_delayed_predicted"].sum()) if "is_delayed_predicted" in fdf.columns else 0

numeric_cols = [c for c in fdf.columns if pd.api.types.is_numeric_dtype(fdf[c])]

# اختيار عمود "قيمة" ذكي + "صرف" + "متبقي"
def pick_money_col(keys):
    for c in numeric_cols:
        name = c.lower()
        if any(k in name for k in keys):
            return c
    return None

value_col = pick_money_col(["value", "amount", "budget", "cost", "قيمة", "ميزانية", "تكلفة"]) or (numeric_cols[0] if numeric_cols else None)
spent_col = pick_money_col(["spent", "paid", "صرف", "مدفوع", "دفعات", "مستخلص"])
remain_col = pick_money_col(["remaining", "متبقي", "باقي"])

total_value = float(fdf[value_col].sum()) if value_col else 0.0
spent = float(fdf[spent_col].sum()) if spent_col else 0.0
remaining = float(fdf[remain_col].sum()) if remain_col else max(total_value - spent, 0.0)

spend_pct = (spent / total_value * 100) if total_value else 0.0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("عدد المشاريع", f"{total_projects:,}")
k2.metric("المشاريع المتعثرة", f"{delayed_actual:,}")
k3.metric("قيمة المشاريع", f"{total_value/1e9:.2f} bn" if total_value else "—")
k4.metric("المستخلصات", f"{spent/1e9:.2f} bn" if spent else "—")
k5.metric("الأعمال المتبقية", f"{remaining/1e9:.2f} bn" if remaining else "—")

st.markdown("---")

g1, g2 = st.columns(2)

with g1:
    fig_delay = go.Figure(go.Indicator(
        mode="gauge+number",
        value=delayed_pct,
        title={"text": "مؤشر المشاريع المتعثرة"},
        gauge={"axis": {"range": [0, 100]}},
        number={"suffix": "%"}
    ))
    st.plotly_chart(fig_delay, use_container_width=True)

with g2:
    fig_spend = go.Figure(go.Indicator(
        mode="gauge+number",
        value=spend_pct,
        title={"text": "نسبة الصرف"},
        gauge={"axis": {"range": [0, 100]}},
        number={"suffix": "%"}
    ))
    st.plotly_chart(fig_spend, use_container_width=True)

# ===================== Status Distribution =====================
st.markdown("---")
st.subheader("عدد المشاريع حسب حالة المشروع")

if "status" in fdf.columns:
    status_count = (
        fdf["status"].value_counts().reset_index()
        .rename(columns={"index": "الحالة", "status": "العدد"})
    )
    fig_status = px.bar(status_count, x="الحالة", y="العدد", text="العدد")
    fig_status.update_layout(showlegend=False)
    st.plotly_chart(fig_status, use_container_width=True)
else:
    st.info("لا يوجد عمود status في الملف لعرض توزيع الحالات.")

# =====================================================
# ✅ التحليل الذكي (أزرار)
# =====================================================
st.markdown("---")
st.markdown("### التحليل الذكي للمشاريع")

if "view_mode" not in st.session_state:
    st.session_state.view_mode = None

b1, b2 = st.columns(2)
with b1:
    if st.button("المشاريع المتأخرة فعليًا", use_container_width=True):
        st.session_state.view_mode = "actual"
with b2:
    if st.button("المشاريع المتوقع تأخرها", use_container_width=True):
        st.session_state.view_mode = "pred"

st.markdown("---")

if st.session_state.view_mode == "actual":
    st.subheader("المشاريع المتأخرة فعليًا")
    df_actual = fdf[fdf["is_delayed_actual"] == 1] if "is_delayed_actual" in fdf.columns else fdf.iloc[0:0]
    if df_actual.empty:
        st.info("لا توجد مشاريع متأخرة فعليًا حسب البيانات الحالية")
    else:
        st.dataframe(df_actual, use_container_width=True, height=450)

elif st.session_state.view_mode == "pred":
    st.subheader("المشاريع المتوقع تأخرها (تحليل تنبؤي)")
    df_pred = fdf[fdf["is_delayed_predicted"] == 1] if "is_delayed_predicted" in fdf.columns else fdf.iloc[0:0]
    if df_pred.empty:
        st.info("لا توجد مشاريع عالية الخطورة حاليًا")
    else:
        show_cols = [c for c in [
            "project","entity","municipality",
            "risk_color","risk_level","delay_risk",
            "reason_short","reason_detail","action_recommendation"
        ] if c in df_pred.columns]
        st.dataframe(df_pred[show_cols] if show_cols else df_pred, use_container_width=True, height=450)
