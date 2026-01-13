import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# أدوات مساعدة
# --------------------------------------------------
def find_col(df, keywords):
    for c in df.columns:
        for k in keywords:
            if k.lower() in str(c).lower():
                return c
    return None


def fmt(x):
    try:
        return f"{x:,.0f}"
    except:
        return x


# --------------------------------------------------
# تحميل البيانات من الرفع
# --------------------------------------------------
if "data" not in st.session_state or st.session_state["data"] is None:
    st.warning("⚠️ الرجاء رفع ملف البيانات أولًا")
    st.stop()

df = st.session_state["data"].copy()

# --------------------------------------------------
# تحديد الأعمدة الذكية
# --------------------------------------------------
status_col = find_col(df, ["status", "حالة"])
entity_col = find_col(df, ["entity", "جهة"])
municipality_col = find_col(df, ["municipality", "بلدية"])
value_col = find_col(df, ["value", "budget", "cost", "قيمة"])
spent_col = find_col(df, ["spent", "صرف"])

# --------------------------------------------------
# الفلاتر (سايدبار)
# --------------------------------------------------
st.sidebar.markdown("## 🔍 تحديث النتائج")

fdf = df.copy()

if entity_col:
    e = st.sidebar.selectbox("الجهة", ["الكل"] + sorted(fdf[entity_col].dropna().unique()))
    if e != "الكل":
        fdf = fdf[fdf[entity_col] == e]

if municipality_col:
    m = st.sidebar.selectbox("البلدية", ["الكل"] + sorted(fdf[municipality_col].dropna().unique()))
    if m != "الكل":
        fdf = fdf[fdf[municipality_col] == m]

if status_col:
    s = st.sidebar.selectbox("حالة المشروع", ["الكل"] + sorted(fdf[status_col].dropna().unique()))
    if s != "الكل":
        fdf = fdf[fdf[status_col] == s]

# --------------------------------------------------
# الكروت العلوية
# --------------------------------------------------
st.markdown("## 📊 لوحة المعلومات")

total_projects = len(fdf)
total_value = fdf[value_col].sum() if value_col else 0
total_spent = fdf[spent_col].sum() if spent_col else 0
spend_ratio = (total_spent / total_value * 100) if total_value else 0

delayed_actual = (
    fdf[status_col].astype(str).str.contains("متأخر", na=False).sum()
    if status_col else 0
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("عدد المشاريع", total_projects)
c2.metric("إجمالي قيمة المشاريع", fmt(total_value))
c3.metric("نسبة الصرف", f"{spend_ratio:.2f}%")
c4.metric("عدد المشاريع المتعثرة", f"{delayed_actual}", help=f"من أصل {total_projects} مشروع")

st.divider()

# --------------------------------------------------
# الرسوم التحليلية
# --------------------------------------------------
st.markdown("## 📈 التحليلات")

left, right = st.columns(2)

# ========= توزيع المشاريع حسب الحالة =========
with left:
    st.subheader("توزيع المشاريع حسب الحالة")

    if status_col:
        status_df = (
            fdf
            .groupby(status_col)
            .size()
            .reset_index(name="عدد المشاريع")
        )

        fig1 = px.bar(
            status_df,
            x=status_col,
            y="عدد المشاريع",
            text="عدد المشاريع"
        )
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("لا يوجد عمود لحالة المشروع")

# ========= أكثر الجهات / البلديات مشاريع =========
with right:
    st.subheader("أكثر الجهات / البلديات مشاريع")

    group_col = municipality_col or entity_col

    if group_col:
        top_df = (
            fdf
            .groupby(group_col)
            .size()
            .reset_index(name="عدد المشاريع")
            .sort_values("عدد المشاريع", ascending=False)
            .head(15)
        )

        fig2 = px.bar(
            top_df,
            x=group_col,
            y="عدد المشاريع",
            text="عدد المشاريع"
        )
        fig2.update_layout(showlegend=False)
        fig2.update_xaxes(tickangle=-30)

        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("لا يوجد عمود جهة / بلدية")

# --------------------------------------------------
# عرض البيانات
# --------------------------------------------------
with st.expander("📄 عرض البيانات بعد الفلاتر"):
    st.dataframe(fdf, use_container_width=True)
