import streamlit as st
import pandas as pd
import plotly.express as px

# ======================================================
# Page Config (مرة واحدة فقط)
# ======================================================
st.set_page_config(
    page_title="لوحة المعلومات",
    layout="wide"
)

# ======================================================
# تحميل البيانات (من صفحة رفع البيانات)
# ======================================================
from core.data_io import prepare_dashboard_data

df = prepare_dashboard_data()
if df is None or df.empty:
    st.info("يرجى رفع ملف البيانات من صفحة (رفع البيانات)")
    st.stop()

# ======================================================
# Helpers ذكية (بدون أسماء أعمدة ثابتة)
# ======================================================
def pick_col(df, keywords, numeric_only=True):
    for c in df.columns:
        name = str(c).lower()
        if any(k in name for k in keywords):
            if not numeric_only or pd.api.types.is_numeric_dtype(df[c]):
                return c
    return None

def detect_delay_column(df):
    keys = ["متأخر", "تأخير", "delay", "delayed"]
    for c in df.columns:
        if any(k in str(c).lower() for k in keys):
            return c
    return None

def count_delayed(series):
    if series is None:
        return 0
    try:
        if series.dtype == object:
            return series.astype(str).str.lower().isin(
                ["نعم","yes","true","متأخر","delayed","1"]
            ).sum()
        return (pd.to_numeric(series, errors="coerce") > 0).sum()
    except Exception:
        return 0

# ======================================================
# فلاتر
# ======================================================
st.markdown("### الفلاتر")

def opt(col):
    if col not in df.columns:
        return ["الكل"]
    return ["الكل"] + sorted(df[col].dropna().astype(str).unique().tolist())

f1,f2,f3 = st.columns(3)

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

# ======================================================
# حساب المؤشرات
# ======================================================
total_projects = len(fdf)

value_col = pick_col(fdf, ["value","amount","budget","cost","قيمة","ميزانية","تكلفة"])
spent_col = pick_col(fdf, ["spent","paid","صرف","مدفوع","مستخلص"])
progress_col = pick_col(fdf, ["progress","انجاز","إنجاز","percent","%"])

total_value = fdf[value_col].sum() if value_col else 0
spent = fdf[spent_col].sum() if spent_col else 0

avg_progress = 0
if progress_col:
    p = pd.to_numeric(fdf[progress_col], errors="coerce")
    if p.dropna().between(0,1).mean() > 0.7:
        p = p * 100
    avg_progress = p.mean()

delay_col = detect_delay_column(fdf)
actual_delayed = count_delayed(fdf[delay_col]) if delay_col else 0

delay_ratio = (actual_delayed / total_projects) if total_projects else 0
spend_ratio = (spent / total_value) if total_value else 0

# ======================================================
# كروت المؤشرات (مثل Power BI)
# ======================================================
st.markdown("## نظرة عامة")

c1,c2,c3,c4,c5 = st.columns(5)

c1.metric("عدد المشاريع", total_projects)
c2.metric("إجمالي قيمة المشاريع", f"{total_value/1e9:.2f} مليار" if total_value else "—")
c3.metric("متوسط الإنجاز", f"{avg_progress:.1f}%")
c4.metric("عدد المشاريع المتعثرة", actual_delayed)
c5.metric("نسبة الصرف", f"{spend_ratio*100:.1f}%" if total_value else "—")

st.markdown("---")

# ======================================================
# Toggle (فتح / إغلاق)
# ======================================================
if "view_mode" not in st.session_state:
    st.session_state.view_mode = None

def toggle(mode):
    st.session_state.view_mode = None if st.session_state.view_mode == mode else mode

b1,b2 = st.columns(2)

with b1:
    if st.button("📌 المشاريع المتأخرة فعليًا", use_container_width=True):
        toggle("actual")

with b2:
    if st.button("🧠 المشاريع المتوقع تأخرها", use_container_width=True):
        toggle("pred")

# ======================================================
# النتائج
# ======================================================
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
    st.info("سيتم تفعيل التنبؤ الذكي لاحقًا (الأساس جاهز)")

st.markdown("---")

# ======================================================
# الرسوم التحليلية
# ======================================================
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
            .head(15)
            .reset_index()
        )
        top.columns = ["الاسم","العدد"]
        fig2 = px.bar(top, x="الاسم", y="العدد", text="العدد")
        fig2.update_layout(showlegend=False)
        fig2.update_xaxes(tickangle=-30)
        st.plotly_chart(fig2, use_container_width=True)
