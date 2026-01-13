# =====================================================
# Dashboard Page | الصفحة الرئيسية
# =====================================================
import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------
# Helper functions
# -----------------------------------------------------
def smart_col(df, keywords):
    """إيجاد أول عمود يحتوي على كلمة من الكلمات"""
    for c in df.columns:
        for k in keywords:
            if k.lower() in str(c).lower():
                return c
    return None


def format_number(x):
    try:
        return f"{x:,.0f}"
    except:
        return x


# -----------------------------------------------------
# Load data from session (uploaded data)
# -----------------------------------------------------
if "data" not in st.session_state or st.session_state["data"] is None:
    st.warning("⚠️ الرجاء رفع ملف البيانات أولًا من صفحة رفع البيانات")
    st.stop()

df = st.session_state["data"].copy()

# -----------------------------------------------------
# Sidebar filters
# -----------------------------------------------------
st.sidebar.markdown("## 🔍 تحديث النتائج")

entity_col = smart_col(df, ["entity", "جهة"])
municipality_col = smart_col(df, ["municipality", "بلدية"])
status_col = smart_col(df, ["status", "حالة"])

fdf = df.copy()

if entity_col:
    ent = st.sidebar.selectbox("الجهة", ["الكل"] + sorted(fdf[entity_col].dropna().unique().tolist()))
    if ent != "الكل":
        fdf = fdf[fdf[entity_col] == ent]

if municipality_col:
    mun = st.sidebar.selectbox("البلدية", ["الكل"] + sorted(fdf[municipality_col].dropna().unique().tolist()))
    if mun != "الكل":
        fdf = fdf[fdf[municipality_col] == mun]

if status_col:
    stt = st.sidebar.selectbox("حالة المشروع", ["الكل"] + sorted(fdf[status_col].dropna().unique().tolist()))
    if stt != "الكل":
        fdf = fdf[fdf[status_col] == stt]

# -----------------------------------------------------
# KPI Cards
# -----------------------------------------------------
st.markdown("## 📊 لوحة المعلومات")

value_col = smart_col(fdf, ["value", "budget", "cost", "قيمة", "تكلفة"])
spent_col = smart_col(fdf, ["spent", "صرف", "منصرف"])
progress_col = smart_col(fdf, ["progress", "نسبة", "إنجاز"])

total_projects = len(fdf)

total_value = fdf[value_col].sum() if value_col else 0
total_spent = fdf[spent_col].sum() if spent_col else 0

spend_ratio = (total_spent / total_value * 100) if total_value else 0

delayed_actual = (
    fdf[status_col].astype(str).str.contains("متأخر", na=False).sum()
    if status_col else 0
)

delayed_expected = (
    fdf[status_col].astype(str).str.contains("متوقع", na=False).sum()
    if status_col else 0
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("عدد المشاريع", total_projects)
c2.metric("إجمالي قيمة المشاريع", format_number(total_value))
c3.metric("نسبة الصرف", f"{spend_ratio:.2f}%")
c4.metric("المشاريع المتعثرة", f"{delayed_actual}", help=f"من أصل {total_projects} مشروع")

st.divider()

# -----------------------------------------------------
# Toggle Sections (Delayed Projects)
# -----------------------------------------------------
if "show_actual" not in st.session_state:
    st.session_state.show_actual = False

if "show_expected" not in st.session_state:
    st.session_state.show_expected = False

b1, b2 = st.columns(2)

if b1.button(f"🔴 المشاريع المتأخرة فعليًا ({delayed_actual})"):
    st.session_state.show_actual = not st.session_state.show_actual

if b2.button(f"🟠 المشاريع المتوقع تأخرها ({delayed_expected})"):
    st.session_state.show_expected = not st.session_state.show_expected

if st.session_state.show_actual and status_col:
    st.subheader("📍 المشاريع المتأخرة فعليًا")
    st.dataframe(
        fdf[fdf[status_col].astype(str).str.contains("متأخر", na=False)],
        use_container_width=True
    )

if st.session_state.show_expected and status_col:
    st.subheader("📍 المشاريع المتوقع تأخرها")
    st.dataframe(
        fdf[fdf[status_col].astype(str).str.contains("متوقع", na=False)],
        use_container_width=True
    )

st.divider()

# -----------------------------------------------------
# Charts
# -----------------------------------------------------
st.markdown("## 📈 التحليلات")

left, right = st.columns(2)

# توزيع المشاريع حسب الحالة
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

        fig1 = px.bar(
            status_df,
            x="الحالة",
            y="عدد المشاريع",
            text="عدد المشاريع"
        )
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("لا تتوفر بيانات حالة المشاريع")

# أكثر الجهات / البلديات
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
        top_df.columns = ["الجهة / البلدية", "عدد المشاريع"]

        fig2 = px.bar(
            top_df,
            x="الجهة / البلدية",
            y="عدد المشاريع",
            text="عدد المشاريع"
        )
        fig2.update_layout(showlegend=False)
        fig2.update_xaxes(tickangle=-30)

        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("لا تتوفر بيانات الجهات / البلديات")

# -----------------------------------------------------
# Raw data preview
# -----------------------------------------------------
with st.expander("📄 عرض البيانات بعد الفلاتر"):
    st.dataframe(fdf, use_container_width=True)
