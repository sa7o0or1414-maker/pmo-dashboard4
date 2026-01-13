import numpy as np
import plotly.graph_objects as go

st.markdown("## المؤشرات الرئيسية")

# ===================== حساب المؤشرات =====================

total_projects = len(fdf)

delayed_actual = int(fdf["is_delayed_actual"].sum())
delayed_pct = (delayed_actual / total_projects * 100) if total_projects else 0

predicted_delayed = int(fdf["is_delayed_predicted"].sum())

numeric_cols = [c for c in fdf.columns if pd.api.types.is_numeric_dtype(fdf[c])]

total_value = fdf[numeric_cols].sum().sum() if numeric_cols else 0

# محاولات ذكية لاستخراج الصرف والمتبقي
spent = 0
remaining = 0

for c in numeric_cols:
    cname = c.lower()
    if "صرف" in cname or "paid" in cname or "spent" in cname:
        spent += fdf[c].sum()
    if "متبقي" in cname or "remaining" in cname:
        remaining += fdf[c].sum()

spend_pct = (spent / total_value * 100) if total_value else 0

# ===================== كروت الأرقام =====================

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("عدد المشاريع", f"{total_projects:,}")
k2.metric("المشاريع المتعثرة", f"{delayed_actual:,}")
k3.metric("قيمة المشاريع", f"{total_value/1e9:.2f} bn" if total_value else "—")
k4.metric("المستخلصات", f"{spent/1e9:.2f} bn" if spent else "—")
k5.metric("الأعمال المتبقية", f"{remaining/1e9:.2f} bn" if remaining else "—")

st.markdown("---")

# ===================== عدادات Gauge =====================

g1, g2 = st.columns(2)

with g1:
    fig_delay = go.Figure(go.Indicator(
        mode="gauge+number",
        value=delayed_pct,
        title={"text": "مؤشر المشاريع المتعثرة"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#0b5c56"},
            "steps": [
                {"range": [0, 30], "color": "#dff3f1"},
                {"range": [30, 60], "color": "#a6d8d2"},
                {"range": [60, 100], "color": "#5fa9a3"},
            ],
        },
        number={"suffix": "%"}
    ))
    st.plotly_chart(fig_delay, use_container_width=True)

with g2:
    fig_spend = go.Figure(go.Indicator(
        mode="gauge+number",
        value=spend_pct,
        title={"text": "نسبة الصرف"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#0b5c56"},
        },
        number={"suffix": "%"}
    ))
    st.plotly_chart(fig_spend, use_container_width=True)

st.markdown("---")

# ===================== عدد المشاريع حسب الحالة =====================

if "status" in fdf.columns:
    st.subheader("عدد المشاريع حسب حالة المشروع")

    status_count = (
        fdf["status"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "الحالة", "status": "العدد"})
    )

    fig_status = px.bar(
        status_count,
        x="الحالة",
        y="العدد",
        color="الحالة",
        text="العدد"
    )

    fig_status.update_layout(showlegend=False)
    st.plotly_chart(fig_status, use_container_width=True)
