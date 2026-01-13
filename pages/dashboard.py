import streamlit as st
import pandas as pd
import plotly.express as px
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

      .risk-card{
        border-radius: 18px;
        padding: 18px;
        text-align: center;
        color: white;
      }
      .risk-high{ background: linear-gradient(135deg,#7a0b0b,#b11212); }
      .risk-mid{ background: linear-gradient(135deg,#8a5b00,#d18b00); }
      .risk-low{ background: linear-gradient(135deg,#0b5c56,#0f8f87); }

      .risk-title{ font-size: 0.95rem; opacity: 0.9; }
      .risk-number{ font-size: 2.2rem; font-weight: 800; margin-top: 6px; }
      .risk-sub{ font-size: 0.8rem; opacity: 0.85; margin-top: 4px; }
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

# ===================== Helper: detect delayed column =====================
def detect_delay_column(df):
    keywords = ["متأخر", "تأخير", "delayed", "delay"]
    for c in df.columns:
        name = str(c).lower()
        if any(k in name for k in keywords):
            return c
    return None

def count_delayed(series):
    # نصوص
    text_vals = ["نعم", "yes", "متأخر", "delayed", "true"]
    try:
        if series.dtype == object:
            return series.astype(str).str.lower().isin(
                [v.lower() for v in text_vals]
            ).sum()
        # أرقام
        return (pd.to_numeric(series, errors="coerce") > 0).sum()
    except Exception:
        return 0

delay_col = detect_delay_column(fdf)
actual_delayed = count_delayed(fdf[delay_col]) if delay_col else 0

# ===================== KPI Calculations =====================
def pick_col(keywords):
    for c in fdf.columns:
        if pd.api.types.is_numeric_dtype(fdf[c]):
            name = c.lower()
            if any(k in name for k in keywords):
                return c
    return None

value_col = pick_col(["value","amount","budget","cost","قيمة","ميزانية","تكلفة"])
spent_col = pick_col(["spent","paid","صرف","مدفوع","مستخلص"])
progress_col = pick_col(["progress","انجاز","إنجاز","percent","%"])

total_projects = len(fdf)
total_value = fdf[value_col].sum() if value_col else 0
spent = fdf[spent_col].sum() if spent_col else 0

avg_progress = 0
if progress_col:
    p = pd.to_numeric(fdf[progress_col], errors="coerce")
    if p.dropna().between(0,1).mean() > 0.7:
        p = p * 100
    avg_progress = p.mean()

delay_ratio = (actual_delayed / total_projects) if total_projects else 0
spend_ratio = (spent / total_value) if total_value else 0

delay_class = "risk-high" if delay_ratio >= 0.25 else "risk-mid" if delay_ratio >= 0.10 else "risk-low"
spend_class = "risk-high" if spend_ratio < 0.40 else "risk-mid" if spend_ratio < 0.70 else "risk-low"

# ===================== KPI Cards =====================
c1,c2,c3,c4,c5 = st.columns(5)

with c1:
    st.markdown(f"<div class='kpi'><h4>عدد المشاريع</h4><h2>{total_projects}</h2></div>", unsafe_allow_html=True)

with c2:
    st.markdown(f"<div class='kpi'><h4>إجمالي قيمة المشاريع</h4><h2>{total_value/1e9:.2f} bn</h2></div>", unsafe_allow_html=True)

with c3:
    st.markdown(f"<div class='kpi'><h4>متوسط الإنجاز</h4><h2>{avg_progress:.1f}%</h2></div>", unsafe_allow_html=True)

with c4:
    st.markdown(
        f"""
        <div class="risk-card {delay_class}">
            <div class="risk-title">عدد المشاريع المتعثرة</div>
            <div class="risk-number">{actual_delayed}</div>
            <div class="risk-sub">من أصل {total_projects} مشروع</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c5:
    st.markdown(
        f"""
        <div class="risk-card {spend_class}">
            <div class="risk-title">نسبة الصرف</div>
            <div class="risk-number">{spend_ratio*100:.1f}%</div>
            <div class="risk-sub">من إجمالي {total_value/1e9:.2f} bn</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# ===================== Toggle Buttons =====================
if "view_mode" not in st.session_state:
    st.session_state.view_mode = None

def toggle(mode):
    st.session_state.view_mode = None if st.session_state.view_mode == mode else mode

b1, b2 = st.columns(2)
with b1:
    if st.button("📌 المشاريع المتأخرة فعليًا", use_container_width=True):
        toggle("actual")

with b2:
    if st.button("🧠 المشاريع المتوقع تأخرها", use_container_width=True):
        toggle("pred")

# ===================== Results =====================
if st.session_state.view_mode == "actual":
    st.subheader("المشاريع المتأخرة فعليًا")
    if delay_col:
        st.dataframe(
            fdf[fdf[delay_col].notna()],
            use_container_width=True,
            height=420
        )
    else:
        st.info("لا يوجد عمود يدل على التأخير في الملف")

elif st.session_state.view_mode == "pred":
    st.subheader("المشاريع المتوقع تأخرها")
    st.info("يعتمد هذا القسم على التحليل الذكي والتنبؤ (يُستكمل لاحقًا)")

st.markdown("---")

# ===================== Charts =====================
left,right = st.columns(2)

with left:
    st.subheader("توزيع المشاريع حسب الحالة")
    if "status" in fdf.columns:
        fig1 = px.histogram(fdf, x="status")
        st.plotly_chart(fig1, use_container_width=True)

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
