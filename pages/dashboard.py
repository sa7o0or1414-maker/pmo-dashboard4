import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit as st

# =========================
# تحميل البيانات من Session
# =========================
df = st.session_state.get("data")

st.title("📊 لوحة المعلومات")

if df is None or df.empty:
    st.warning("⚠️ الرجاء رفع ملف البيانات أولًا من صفحة (رفع البيانات)")
    st.stop()

# =========================
# توحيد أسماء الأعمدة (مرن)
# =========================
def find_col(possible):
    for c in df.columns:
        for p in possible:
            if p.lower() in c.lower():
                return c
    return None

col_status = find_col(["حالة", "status"])
col_value  = find_col(["قيمة", "value", "amount", "budget"])
col_spend  = find_col(["صرف", "نسبة", "spend"])
col_entity = find_col(["جهة", "entity"])
col_muni   = find_col(["بلدية", "municipality"])
col_delay  = find_col(["متأخر", "delay"])

# =========================
# الفلاتر
# =========================
with st.container():
    st.subheader("🔍 الفلاتر")

    c1, c2, c3 = st.columns(3)

    with c1:
        status_filter = st.selectbox(
            "حالة المشروع",
            ["الكل"] + sorted(df[col_status].dropna().unique().tolist())
            if col_status else ["الكل"]
        )

    with c2:
        muni_filter = st.selectbox(
            "البلدية",
            ["الكل"] + sorted(df[col_muni].dropna().unique().tolist())
            if col_muni else ["الكل"]
        )

    with c3:
        entity_filter = st.selectbox(
            "الجهة",
            ["الكل"] + sorted(df[col_entity].dropna().unique().tolist())
            if col_entity else ["الكل"]
        )

# تطبيق الفلاتر
fdf = df.copy()

if col_status and status_filter != "الكل":
    fdf = fdf[fdf[col_status] == status_filter]

if col_muni and muni_filter != "الكل":
    fdf = fdf[fdf[col_muni] == muni_filter]

if col_entity and entity_filter != "الكل":
    fdf = fdf[fdf[col_entity] == entity_filter]

# =========================
# الكروت
# =========================
total_projects = len(fdf)
total_value = fdf[col_value].sum() if col_value else 0
avg_spend = fdf[col_spend].mean() if col_spend else 0

delayed_df = fdf[fdf[col_status].astype(str).str.contains("متأخر", na=False)] if col_status else pd.DataFrame()
delayed_count = len(delayed_df)

c1, c2, c3, c4 = st.columns(4)

c1.metric("عدد المشاريع", total_projects)
c2.metric("إجمالي قيمة المشاريع", f"{total_value:,.0f}")
c3.metric("متوسط نسبة الصرف", f"{avg_spend:.1f}%")
c4.metric("عدد المشاريع المتعثرة", delayed_count)

st.divider()

# =========================
# أيقونات المشاريع المتأخرة
# =========================
if "show_delayed" not in st.session_state:
    st.session_state.show_delayed = False

if st.button(f"🔴 المشاريع المتأخرة فعليًا ({delayed_count})"):
    st.session_state.show_delayed = not st.session_state.show_delayed

if st.session_state.show_delayed:
    st.subheader("📋 المشاريع المتأخرة فعليًا")
    st.dataframe(delayed_df.reset_index(drop=True), use_container_width=True)

# =========================
# توزيع المشاريع حسب الحالة
# =========================
if col_status:
    st.subheader("📊 توزيع المشاريع حسب الحالة")
    status_count = fdf[col_status].value_counts().reset_index()
    status_count.columns = ["الحالة", "عدد المشاريع"]

    fig1 = px.bar(
        status_count,
        x="الحالة",
        y="عدد المشاريع",
        text="عدد المشاريع"
    )
    st.plotly_chart(fig1, use_container_width=True)

# =========================
# أكثر الجهات / البلديات
# =========================
if col_muni:
    st.subheader("🏙️ أكثر البلديات مشاريع")
    muni_count = fdf[col_muni].value_counts().head(10).reset_index()
    muni_count.columns = ["البلدية", "عدد المشاريع"]

    fig2 = px.bar(
        muni_count,
        x="البلدية",
        y="عدد المشاريع",
        text="عدد المشاريع"
    )
    st.plotly_chart(fig2, use_container_width=True)
