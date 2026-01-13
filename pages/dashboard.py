import streamlit as st
import plotly.express as px
import bootstrap  # noqa: F401

from core.config import ensure_defaults, load_config, apply_branding
from core.sidebar import render_sidebar
from core.data_io import prepare_dashboard_data
from core.predict import build_delay_outputs

st.set_page_config(layout="wide")

ensure_defaults()
cfg = load_config()
apply_branding(cfg)
render_sidebar()

st.title("الصفحة الرئيسية")

df = prepare_dashboard_data()
if df is None or df.empty:
    st.info("ما فيه بيانات. ارفعي ملف Excel من صفحة (رفع البيانات).")
    st.stop()

df = build_delay_outputs(df)

# --- Filters in sidebar (Arabic) ---
st.sidebar.markdown("---")
st.sidebar.markdown("### الفلاتر")

def _options(col):
    if col not in df.columns:
        return ["الكل"]
    vals = sorted([v for v in df[col].dropna().unique().tolist() if str(v).strip() != ""])
    return ["الكل"] + vals

muni = st.sidebar.selectbox("البلدية", _options("municipality"))
entity = st.sidebar.selectbox("الجهة", _options("entity"))
status = st.sidebar.selectbox("حالة المشروع", _options("status"))

fdf = df.copy()
if muni != "الكل" and "municipality" in fdf.columns:
    fdf = fdf[fdf["municipality"] == muni]
if entity != "الكل" and "entity" in fdf.columns:
    fdf = fdf[fdf["entity"] == entity]
if status != "الكل" and "status" in fdf.columns:
    fdf = fdf[fdf["status"] == status]

# --- KPIs ---
total_projects = len(fdf)
total_budget = fdf["budget"].sum() if "budget" in fdf.columns else None
avg_progress = fdf["progress"].mean() if "progress" in fdf.columns else None
actual_delayed = int(fdf["is_delayed_actual"].sum()) if "is_delayed_actual" in fdf.columns else 0
pred_delayed = int(fdf["is_delayed_predicted"].sum()) if "is_delayed_predicted" in fdf.columns else 0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("عدد المشاريع", f"{total_projects:,}")
with c2:
    st.metric("إجمالي قيمة المشاريع", f"{int(total_budget):,}" if total_budget is not None else "—")
with c3:
    st.metric("متوسط الإنجاز", f"{avg_progress:.1f}%" if avg_progress is not None else "—")
with c4:
    st.metric("التنبيهات", f"متأخر: {actual_delayed} | متوقع: {pred_delayed}")

st.markdown("---")

# --- Buttons like Power BI cards (drilldown) ---
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "overview"

b1, b2, b3 = st.columns(3)
with b1:
    if st.button(f"عرض المشاريع المتأخرة فعليًا ({actual_delayed})", use_container_width=True):
        st.session_state.view_mode = "actual"
with b2:
    if st.button(f"عرض المشاريع المتوقع تأخرها ({pred_delayed})", use_container_width=True):
        st.session_state.view_mode = "pred"
with b3:
    if st.button("عرض الملخص", use_container_width=True):
        st.session_state.view_mode = "overview"

# --- Charts ---
left, right = st.columns(2)

with left:
    if "status" in fdf.columns:
        fig1 = px.histogram(fdf, x="status", title="توزيع المشاريع حسب الحالة")
        fig1.update_layout(xaxis_title="حالة المشروع", yaxis_title="العدد")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("لا يوجد عمود حالة واضح في الملف لعرض توزيع الحالات.")

with right:
    # top delayed by municipality or entity
    if "municipality" in fdf.columns:
        tmp = fdf.groupby("municipality")["is_delayed_actual"].sum().sort_values(ascending=False).head(15).reset_index()
        fig2 = px.bar(tmp, x="municipality", y="is_delayed_actual", title="أكثر البلديات تأخرًا (فعليًا)")
        fig2.update_layout(xaxis_title="البلدية", yaxis_title="عدد المشاريع المتأخرة")
        st.plotly_chart(fig2, use_container_width=True)
    elif "entity" in fdf.columns:
        tmp = fdf.groupby("entity")["is_delayed_actual"].sum().sort_values(ascending=False).head(15).reset_index()
        fig2 = px.bar(tmp, x="entity", y="is_delayed_actual", title="أكثر الجهات تأخرًا (فعليًا)")
        fig2.update_layout(xaxis_title="الجهة", yaxis_title="عدد المشاريع المتأخرة")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("لا يوجد عمود بلدية/جهة واضح لعرض الأكثر تأخرًا.")

st.markdown("---")

# --- Drilldown tables ---
cols_base = [c for c in ["municipality", "entity", "project", "status", "progress", "end_date"] if c in fdf.columns]

def show_table(title, tdf, extra_cols=None):
    st.subheader(title)
    show_cols = cols_base.copy()
    if extra_cols:
        for c in extra_cols:
            if c in tdf.columns and c not in show_cols:
                show_cols.append(c)

    if "project" not in show_cols and "project" in tdf.columns:
        show_cols = ["project"] + show_cols

    st.dataframe(
        tdf[show_cols].sort_values(by=("delay_risk" if "delay_risk" in tdf.columns else show_cols[0]), ascending=False),
        use_container_width=True
    )

if st.session_state.view_mode == "actual":
    actual_df = fdf[fdf["is_delayed_actual"] == 1].copy()
    show_table("المشاريع المتأخرة فعليًا", actual_df)
elif st.session_state.view_mode == "pred":
    pred_df = fdf[fdf["is_delayed_predicted"] == 1].copy()
    # show reasons
    show_table("المشاريع المتوقع تأخرها (مع سبب التوقع)", pred_df, extra_cols=["delay_risk", "delay_reason"])
else:
    st.subheader("ملخص سريع")
    st.write("استخدمي الأزرار أعلاه لعرض المتأخر فعليًا أو المتوقع تأخره مع الأسباب.")
    st.caption("ملاحظة: التنبؤ هنا يعتمد على مؤشرات ذكية (الموعد النهائي، نسبة الإنجاز، نص الحالة) بدون نماذج خارجية لضمان الاستقرار على Streamlit Cloud.")
