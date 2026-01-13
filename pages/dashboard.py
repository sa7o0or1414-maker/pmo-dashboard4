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

# ===================== Styling (Elegant + RTL) =====================
st.markdown(
    """
    <style>
      html, body, [class*="css"]  { direction: rtl; }
      .block-container { padding-top: 1.2rem; }
      .kpi-wrap{
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 14px 16px;
        margin-bottom: 10px;
      }
      .kpi-title{
        font-size: 0.85rem;
        color: rgba(255,255,255,0.75);
        margin-bottom: 6px;
      }
      .kpi-value{
        font-size: 1.55rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.2;
      }
      .kpi-sub{
        font-size: 0.8rem;
        color: rgba(255,255,255,0.55);
        margin-top: 4px;
      }
      .section-title{
        font-size: 1.05rem;
        font-weight: 700;
        margin: 10px 0 6px 0;
      }
      .soft-divider{
        height: 1px;
        background: rgba(255,255,255,0.08);
        margin: 14px 0;
      }
      .btn-row .stButton>button{
        border-radius: 12px;
        padding: 0.65rem 0.8rem;
        font-weight: 700;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ===================== Helpers =====================
def _safe_num(series: pd.Series) -> float:
    try:
        return float(pd.to_numeric(series, errors="coerce").fillna(0).sum())
    except Exception:
        return 0.0

def _pick_col_by_keywords(df: pd.DataFrame, keywords):
    cols = []
    for c in df.columns:
        name = str(c).lower()
        if any(k in name for k in keywords):
            cols.append(c)
    # prefer numeric columns
    for c in cols:
        if pd.api.types.is_numeric_dtype(df[c]):
            return c
    return cols[0] if cols else None

def _format_bn(x: float):
    if x is None or pd.isna(x):
        return "—"
    if abs(x) >= 1e9:
        return f"{x/1e9:,.2f}bn"
    if abs(x) >= 1e6:
        return f"{x/1e6:,.2f}m"
    return f"{x:,.0f}"

def _kpi(title, value, sub=""):
    st.markdown(
        f"""
        <div class="kpi-wrap">
          <div class="kpi-title">{title}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ===================== Load Data =====================
st.title("لوحة المعلومات")

df = prepare_dashboard_data()
if df is None or df.empty:
    st.info("لا توجد بيانات حالياً. ارفعي ملف Excel من صفحة (رفع البيانات).")
    st.stop()

# apply prediction (safe import)
predict = importlib.import_module("core.predict")
df = predict.build_delay_outputs(df)

# ===================== Sidebar Filters =====================
st.sidebar.markdown("## تحديد النتائج")

def opt(col):
    if col not in df.columns:
        return ["الكل"]
    vals = [v for v in df[col].dropna().unique().tolist() if str(v).strip()]
    return ["الكل"] + sorted(vals)

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

# ===================== KPI Computations =====================
total_projects = len(fdf)

value_col = _pick_col_by_keywords(
    fdf,
    ["value", "amount", "budget", "cost", "contract", "قيمة", "ميزانية", "تكلفة", "عقد"],
)
spent_col = _pick_col_by_keywords(
    fdf,
    ["spent", "paid", "disb", "صرف", "مدفوع", "مستخلص", "دفعات"],
)
remain_col = _pick_col_by_keywords(
    fdf,
    ["remaining", "متبقي", "باقي", "اعمال متبقية", "الأعمال المتبقية"],
)
progress_col = _pick_col_by_keywords(
    fdf,
    ["progress", "percent", "completion", "انجاز", "إنجاز", "%"],
)

total_value = _safe_num(fdf[value_col]) if value_col else 0.0
spent = _safe_num(fdf[spent_col]) if spent_col else 0.0
remaining = _safe_num(fdf[remain_col]) if remain_col else max(total_value - spent, 0.0)

avg_progress = 0.0
if progress_col:
    try:
        pr = pd.to_numeric(fdf[progress_col], errors="coerce")
        # if values look like 0..1 convert to %
        if pr.dropna().between(0, 1).mean() > 0.7:
            pr = pr * 100
        avg_progress = float(pr.mean(skipna=True)) if pr.notna().any() else 0.0
    except Exception:
        avg_progress = 0.0

actual_delayed = int(fdf["is_delayed_actual"].sum()) if "is_delayed_actual" in fdf.columns else 0
pred_delayed = int(fdf["is_delayed_predicted"].sum()) if "is_delayed_predicted" in fdf.columns else 0

# ===================== Top KPI Row (like your screenshot) =====================
k1, k2, k3, k4 = st.columns(4)

with k1:
    _kpi("عدد المشاريع", f"{total_projects:,}")

with k2:
    _kpi("إجمالي قيمة العقود", _format_bn(total_value))

with k3:
    _kpi("متوسط الإنجاز", f"{avg_progress:.1f}%")

with k4:
    _kpi("التنبيهات", f"متأخر: {actual_delayed} | متوقع: {pred_delayed}")

st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)

# ===================== Action Buttons (open results below) =====================
st.markdown('<div class="section-title">التفاصيل</div>', unsafe_allow_html=True)

if "view_mode" not in st.session_state:
    st.session_state.view_mode = None

btn1, btn2 = st.columns(2)
with btn1:
    if st.button("المشاريع المتأخرة فعليًا", use_container_width=True):
        st.session_state.view_mode = "actual"
with btn2:
    if st.button("المشاريع المتوقع تأخرها", use_container_width=True):
        st.session_state.view_mode = "pred"

# Results appear directly below buttons
if st.session_state.view_mode == "actual":
    st.subheader(f"المشاريع المتأخرة فعليًا ({actual_delayed})")
    df_actual = fdf[fdf["is_delayed_actual"] == 1] if "is_delayed_actual" in fdf.columns else fdf.iloc[0:0]
    if df_actual.empty:
        st.info("لا توجد نتائج حسب الفلاتر الحالية.")
    else:
        st.dataframe(df_actual, use_container_width=True, height=420)

elif st.session_state.view_mode == "pred":
    st.subheader(f"المشاريع المتوقع تأخرها ({pred_delayed})")
    df_pred = fdf[fdf["is_delayed_predicted"] == 1] if "is_delayed_predicted" in fdf.columns else fdf.iloc[0:0]
    if df_pred.empty:
        st.info("لا توجد نتائج حسب الفلاتر الحالية.")
    else:
        preferred = [
            "project", "entity", "municipality", "status",
            "risk_color", "risk_level", "delay_risk",
            "reason_short", "reason_detail", "action_recommendation",
        ]
        show_cols = [c for c in preferred if c in df_pred.columns]
        st.dataframe(df_pred[show_cols] if show_cols else df_pred, use_container_width=True, height=420)

st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)

# ===================== Charts Row (similar to your screenshot) =====================
left, right = st.columns(2)

with left:
    st.markdown('<div class="section-title">توزيع المشاريع حسب الحالة</div>', unsafe_allow_html=True)
    if "status" in fdf.columns and not fdf["status"].dropna().empty:
        fig_status = px.histogram(
            fdf,
            x="status",
            title="",
        )
        fig_status.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.info("لا يوجد عمود حالة (status) لعرض الرسم.")

with right:
    st.markdown('<div class="section-title">أكثر البلديات/الجهات مشاريع</div>', unsafe_allow_html=True)
    group_col = "municipality" if "municipality" in fdf.columns else ("entity" if "entity" in fdf.columns else None)
    if group_col:
       top = (
    fdf[group_col]
    .fillna("غير محدد")
    .value_counts()
    .head(20)
    .reset_index()
)

top.columns = ["الاسم", "العدد"]

fig_top = px.bar(
    top,
    x="الاسم",
    y="العدد",
    text="العدد"
)

fig_top.update_layout(showlegend=False)

        fig_top.update_layout(margin=dict(l=10, r=10, t=10, b=10))
        fig_top.update_xaxes(tickangle=-30)
        st.plotly_chart(fig_top, use_container_width=True)
    else:
        st.info("لا يوجد عمود بلدية/جهة لعرض الرسم.")

# ===================== Gauge mini row (optional clean like image) =====================
g1, g2 = st.columns(2)
with g1:
    delayed_pct = (actual_delayed / total_projects * 100) if total_projects else 0
    fig_g1 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=delayed_pct,
        title={"text": "مؤشر المشاريع المتعثرة"},
        gauge={"axis": {"range": [0, 100]}},
        number={"suffix": "%"},
    ))
    fig_g1.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_g1, use_container_width=True)

with g2:
    spend_pct = (spent / total_value * 100) if total_value else 0
    fig_g2 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=spend_pct,
        title={"text": "نسبة الصرف"},
        gauge={"axis": {"range": [0, 100]}},
        number={"suffix": "%"},
    ))
    fig_g2.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_g2, use_container_width=True)
