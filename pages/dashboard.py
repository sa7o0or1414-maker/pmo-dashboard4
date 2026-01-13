import streamlit as st
import pandas as pd
import numpy as np

# ==============================
# لا تكرر set_page_config هنا ❌
# ==============================

# ---------- Helpers ----------
def safe_for_display(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    for c in d.columns:
        if np.issubdtype(d[c].dtype, np.datetime64):
            d[c] = d[c].astype(str)
        elif isinstance(d[c].iloc[0], (list, dict)):
            d[c] = d[c].astype(str)
    return d


def show_readonly_table(title: str, df: pd.DataFrame):
    st.subheader(title)

    if df.empty:
        st.info("لا توجد بيانات للعرض")
        return

    d = safe_for_display(df).copy()

    # حل مشكلة الأعمدة المكررة
    seen = {}
    new_cols = []
    for c in d.columns:
        if c in seen:
            seen[c] += 1
            new_cols.append(f"{c} ({seen[c]})")
        else:
            seen[c] = 1
            new_cols.append(c)
    d.columns = new_cols

    st.data_editor(
        d,
        use_container_width=True,
        height=420,
        disabled=True,
        hide_index=True
    )


# ---------- Load Data ----------
st.title("📊 لوحة المعلومات")

if "data_df" not in st.session_state or st.session_state["data_df"] is None:
    st.warning("⚠️ الرجاء رفع ملف البيانات أولًا من صفحة (رفع البيانات)")
    st.stop()

df = st.session_state["data_df"].copy()

# ---------- Normalize Columns ----------
cols_lower = {c.lower(): c for c in df.columns}

def col(*names):
    for n in names:
        if n.lower() in cols_lower:
            return cols_lower[n.lower()]
    return None

status_col = col("حالة المشروع", "status")
municipality_col = col("البلدية", "municipality")
entity_col = col("الجهة", "entity")
value_col = col("قيمة المشروع", "value", "amount", "budget", "cost")
spend_col = col("نسبة الصرف", "spend", "spending")

# ---------- KPIs ----------
total_projects = len(df)
total_value = df[value_col].sum() if value_col else 0
avg_spend = df[spend_col].mean() if spend_col else 0

actual_delayed = df[df[status_col].astype(str).str.contains("متأخر", na=False)] if status_col else pd.DataFrame()
actual_delayed_count = len(actual_delayed)

# ---------- Cards ----------
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("عدد المشاريع", total_projects)
c2.metric("إجمالي قيمة المشاريع", f"{total_value:,.0f}")
c3.metric("متوسط نسبة الصرف", f"{avg_spend:.1f}%" if spend_col else "—")
c4.metric(
    "عدد المشاريع المتعثرة",
    actual_delayed_count,
    help="يتم الحساب من حالة المشروع"
)
c5.metric(
    "نسبة الصرف",
    f"{avg_spend:.1f}%" if spend_col else "—"
)

st.divider()

# ---------- Toggles ----------
if "show_actual" not in st.session_state:
    st.session_state.show_actual = False
if "show_pred" not in st.session_state:
    st.session_state.show_pred = False

b1, b2 = st.columns(2)

with b1:
    if st.button(f"🔴 المشاريع المتأخرة فعليًا ({actual_delayed_count})", use_container_width=True):
        st.session_state.show_actual = not st.session_state.show_actual

with b2:
    # تنبؤ بسيط ذكي (بدون كسر)
    pred_df = df.copy()
    pred_df["مستوى الخطر"] = np.where(
        pred_df.get(spend_col, 0) < 30, "🔴 عالي",
        np.where(pred_df.get(spend_col, 0) < 60, "🟠 متوسط", "🟢 منخفض")
    )
    pred_df["سبب التوقع المختصر"] = np.where(
        pred_df.get(spend_col, 0) < 30,
        "انخفاض نسبة الصرف",
        "مؤشرات مستقرة"
    )
    pred_df["سبب التوقع التفصيلي"] = np.where(
        pred_df.get(spend_col, 0) < 30,
        "نسبة الصرف أقل من الحد الآمن مقارنة بزمن المشروع",
        "لا توجد إشارات تأخير حالية"
    )

    predicted_delayed = pred_df[pred_df["مستوى الخطر"].isin(["🔴 عالي", "🟠 متوسط"])]

    if st.button(f"🟠 المشاريع المتوقع تأخرها ({len(predicted_delayed)})", use_container_width=True):
        st.session_state.show_pred = not st.session_state.show_pred

# ---------- Tables ----------
if st.session_state.show_actual:
    show_readonly_table("🔴 المشاريع المتأخرة فعليًا", actual_delayed)

if st.session_state.show_pred:
    show_readonly_table(
        "🟠 المشاريع المتوقع تأخرها (تحليل ذكي)",
        predicted_delayed
    )

st.divider()

# ---------- Charts ----------
col1, col2 = st.columns(2)

with col1:
    st.subheader("توزيع المشاريع حسب الحالة")
    if status_col:
        status_counts = df[status_col].value_counts().reset_index()
        status_counts.columns = ["الحالة", "عدد المشاريع"]
        st.bar_chart(status_counts, x="الحالة", y="عدد المشاريع", use_container_width=True)
    else:
        st.info("لا يوجد عمود حالة المشروع")

with col2:
    st.subheader("أكثر الجهات / البلديات مشاريع")
    group_col = municipality_col or entity_col
    if group_col:
        top_entities = df[group_col].value_counts().head(15).reset_index()
        top_entities.columns = ["الجهة / البلدية", "عدد المشاريع"]
        st.bar_chart(top_entities, x="الجهة / البلدية", y="عدد المشاريع", use_container_width=True)
    else:
        st.info("لا يوجد عمود جهة أو بلدية")
