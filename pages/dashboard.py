import streamlit as st
import pandas as pd
import plotly.express as px

# لازم يكون أول أمر Streamlit
st.set_page_config(page_title="الصفحة الرئيسية", layout="wide")

from core.ui import hide_streamlit_default_nav
from core.sidebar import render_sidebar
from core.data_io import load_latest_data

hide_streamlit_default_nav()
render_sidebar()

# -----------------------------
# Helpers
# -----------------------------
def find_col(df, keywords):
    for c in df.columns:
        name = str(c).lower()
        if any(k.lower() in name for k in keywords):
            return c
    return None

def fmt_big(n):
    try:
        n = float(n)
        if abs(n) >= 1e9:
            return f"{n/1e9:.2f} مليار"
        if abs(n) >= 1e6:
            return f"{n/1e6:.2f} مليون"
        return f"{n:,.0f}"
    except Exception:
        return "—"

def normalize_percent(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    if s.dropna().between(0, 1).mean() > 0.6:
        s = s * 100
    return s

def safe_for_display(d: pd.DataFrame, max_len: int = 400) -> pd.DataFrame:
    """
    تحويل DataFrame لنسخة آمنة للعرض بدون مشاكل Arrow:
    - إعادة ضبط الـ index
    - تحويل datetime/timedelta/period/object إلى نص
    - قص النصوص الطويلة
    """
    out = d.copy().reset_index(drop=True)

    # حوّل datetime / timedelta / period إلى نص
    for c in out.columns:
        try:
            if pd.api.types.is_datetime64_any_dtype(out[c]):
                out[c] = out[c].dt.strftime("%Y-%m-%d")
            elif pd.api.types.is_timedelta64_dtype(out[c]):
                out[c] = out[c].astype(str)
            elif pd.api.types.is_period_dtype(out[c]):
                out[c] = out[c].astype(str)
        except Exception:
            pass

    # الأعمدة غير الرقمية نحولها نص آمن
    for c in out.columns:
        if pd.api.types.is_numeric_dtype(out[c]):
            continue

        def _to_safe(x):
            if x is None:
                return ""
            try:
                if isinstance(x, float) and pd.isna(x):
                    return ""
            except Exception:
                pass

            # أي شيء معقد -> نص
            try:
                import numpy as np
                if isinstance(x, np.ndarray):
                    s = str(x.tolist())
                elif isinstance(x, (list, dict, set, tuple)):
                    s = str(x)
                else:
                    s = str(x)
            except Exception:
                s = str(x)

            if len(s) > max_len:
                s = s[:max_len] + "..."
            return s

        out[c] = out[c].map(_to_safe)

    return out

def show_readonly_table(title: str, d: pd.DataFrame):
    st.subheader(title)
    d2 = safe_for_display(d)
    # data_editor read-only (أكثر استقرارًا من dataframe مع pyarrow في حالات معينة)
    st.data_editor(
        d2,
        use_container_width=True,
        height=420,
        disabled=True,
        hide_index=True
    )

# -----------------------------
# Load data
# -----------------------------
df = load_latest_data()
if df is None or df.empty:
    st.warning("الرجاء رفع ملف البيانات أولًا من صفحة (رفع البيانات).")
    st.stop()

# -----------------------------
# Detect columns
# -----------------------------
status_col = find_col(df, ["status", "حالة"])
entity_col = find_col(df, ["entity", "جهة"])
municipality_col = find_col(df, ["municipality", "بلدية"])
project_col = find_col(df, ["project", "اسم المشروع", "مشروع", "project name"])
value_col = find_col(df, ["value", "amount", "budget", "cost", "قيمة", "ميزانية", "تكلفة"])
progress_col = find_col(df, ["progress", "إنجاز", "انجاز", "%"])
spend_ratio_col = find_col(df, ["نسبة الصرف", "spend ratio", "spending", "صرف"])

# -----------------------------
# Filters
# -----------------------------
st.markdown("## الفلاتر")
c1, c2, c3 = st.columns(3)

fdf = df.copy()

with c1:
    if entity_col:
        ent_vals = ["الكل"] + sorted(fdf[entity_col].dropna().astype(str).unique().tolist())
        ent = st.selectbox("الجهة", ent_vals)
        if ent != "الكل":
            fdf = fdf[fdf[entity_col].astype(str) == ent]
    else:
        st.selectbox("الجهة", ["غير متوفر"], disabled=True)

with c2:
    if municipality_col:
        mun_vals = ["الكل"] + sorted(fdf[municipality_col].dropna().astype(str).unique().tolist())
        mun = st.selectbox("البلدية", mun_vals)
        if mun != "الكل":
            fdf = fdf[fdf[municipality_col].astype(str) == mun]
    else:
        st.selectbox("البلدية", ["غير متوفر"], disabled=True)

with c3:
    if status_col:
        st_vals = ["الكل"] + sorted(fdf[status_col].dropna().astype(str).unique().tolist())
        stt = st.selectbox("حالة المشروع", st_vals)
        if stt != "الكل":
            fdf = fdf[fdf[status_col].astype(str) == stt]
    else:
        st.selectbox("حالة المشروع", ["غير متوفر"], disabled=True)

# -----------------------------
# KPIs
# -----------------------------
total_projects = len(fdf)
total_value = pd.to_numeric(fdf[value_col], errors="coerce").sum() if value_col else 0

avg_progress = 0
if progress_col:
    p = normalize_percent(fdf[progress_col])
    avg_progress = float(p.mean()) if p.notna().any() else 0

spend_ratio = 0
if spend_ratio_col:
    sr = normalize_percent(fdf[spend_ratio_col])
    spend_ratio = float(sr.mean()) / 100 if sr.notna().any() else 0

# Actual delayed
actual_df = pd.DataFrame()
if status_col:
    actual_mask = fdf[status_col].astype(str).str.contains("متأخر|متعثر|delayed|delay", case=False, na=False)
    actual_df = fdf[actual_mask].copy()

# Predicted delayed (risk score + reasons)
tmp = fdf.copy()
risk = pd.Series(0.0, index=tmp.index)

if progress_col:
    prog = normalize_percent(tmp[progress_col]).fillna(0)
    risk += (100 - prog) * 0.55

bad_words = ["تأخير", "متأخر", "تعثر", "معوقات", "تحديات", "مشكلة", "delay", "risk", "issue", "problem"]
text_cols = [c for c in tmp.columns if tmp[c].dtype == object]

def text_penalty(row):
    joined = " ".join([str(row[c]) for c in text_cols]) if text_cols else ""
    joined = joined.lower()
    return 25 if any(w in joined for w in bad_words) else 0

if text_cols:
    risk += tmp[text_cols].fillna("").apply(text_penalty, axis=1)

if value_col and progress_col:
    val = pd.to_numeric(tmp[value_col], errors="coerce").fillna(0)
    prog = normalize_percent(tmp[progress_col]).fillna(0)
    try:
        hi_val = (val > val.quantile(0.75)).astype(int)
    except Exception:
        hi_val = 0
    risk += (hi_val * (prog < 50).astype(int)) * 12

tmp["risk_score"] = risk.clip(0, 100)

def classify_and_reason(row):
    score = float(row.get("risk_score", 0))
    reasons = []

    if progress_col:
        p = pd.to_numeric(row.get(progress_col, None), errors="coerce")
        if pd.notna(p):
            if 0 <= p <= 1:
                p = p * 100
            if p < 30:
                reasons.append("نسبة الإنجاز منخفضة جدًا")
            elif p < 50:
                reasons.append("نسبة الإنجاز منخفضة")

    if text_cols:
        joined = " ".join([str(row.get(c, "")) for c in text_cols]).lower()
        if any(w in joined for w in bad_words):
            reasons.append("وجود إشارات نصية لمشاكل أو تأخير")

    if value_col:
        v = pd.to_numeric(row.get(value_col, None), errors="coerce")
        try:
            q75 = pd.to_numeric(tmp[value_col], errors="coerce").dropna().quantile(0.75)
            if pd.notna(v) and pd.notna(q75) and v > q75:
                reasons.append("قيمة المشروع عالية مقارنة بمتوسط المشاريع")
        except Exception:
            pass

    if score >= 70:
        level = "عالي"
    elif score >= 40:
        level = "متوسط"
    else:
        level = "منخفض"

    if not reasons:
        reasons = ["مؤشرات مخاطر عامة من البيانات"]

    short_reason = "، ".join(reasons[:2])
    long_reason = "؛ ".join(reasons)

    return pd.Series([level, short_reason, long_reason])

tmp[["مستوى الخطر", "سبب مختصر", "سبب تفصيلي"]] = tmp.apply(classify_and_reason, axis=1)
pred_df = tmp[tmp["risk_score"] >= 40].copy()

actual_count = len(actual_df)
pred_count = len(pred_df)

# KPI cards
st.markdown("## لوحة المعلومات")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("عدد المشاريع", total_projects)
k2.metric("إجمالي قيمة المشاريع", fmt_big(total_value))
k3.metric("متوسط الإنجاز", f"{avg_progress:.1f}%")
k4.metric("عدد المشاريع المتعثرة", actual_count, help=f"من أصل {total_projects} مشروع")
k5.metric("نسبة الصرف", f"{spend_ratio*100:.1f}%" if spend_ratio else "—")

st.markdown("---")

# Toggle icons
if "open_panel" not in st.session_state:
    st.session_state.open_panel = None

def toggle(panel_name):
    st.session_state.open_panel = None if st.session_state.open_panel == panel_name else panel_name

b1, b2 = st.columns(2)
with b1:
    if st.button(f"🔴 المشاريع المتأخرة فعليًا ({actual_count})", use_container_width=True):
        toggle("actual")
with b2:
    if st.button(f"🟠 المشاريع المتوقع تأخرها ({pred_count})", use_container_width=True):
        toggle("pred")

# Panels
if st.session_state.open_panel == "actual":
    if actual_df.empty:
        st.success("لا توجد مشاريع متأخرة فعليًا حسب الفلاتر الحالية")
    else:
        show_cols = [c for c in [project_col, entity_col, municipality_col, status_col, progress_col, value_col] if c]
        table_df = actual_df[show_cols] if show_cols else actual_df
        show_readonly_table("المشاريع المتأخرة فعليًا", table_df)

if st.session_state.open_panel == "pred":
    if pred_df.empty:
        st.success("لا توجد مشاريع عالية/متوسطة المخاطر حسب الفلاتر الحالية")
    else:
        cols = [c for c in [project_col, entity_col, municipality_col, status_col] if c]
        extra = ["risk_score", "مستوى الخطر", "سبب مختصر", "سبب تفصيلي"]
        cols = cols + [c for c in extra if c in pred_df.columns]
        show_readonly_table("المشاريع المتوقع تأخرها (تحليل ذكي)", pred_df[cols])

st.markdown("---")

# Charts
st.markdown("## التحليلات")
left, right = st.columns(2)

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
        fig = px.bar(status_df, x="الحالة", y="عدد المشاريع", text="عدد المشاريع")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("لا يوجد عمود لحالة المشاريع أو لا توجد بيانات بعد الفلاتر.")

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
        top_df.columns = ["الجهة/البلدية", "عدد المشاريع"]
        fig2 = px.bar(top_df, x="الجهة/البلدية", y="عدد المشاريع", text="عدد المشاريع")
        fig2.update_layout(showlegend=False)
        fig2.update_xaxes(tickangle=-30)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("لا يوجد عمود للجهة/البلدية أو لا توجد بيانات بعد الفلاتر.")

with st.expander("عرض البيانات بعد الفلاتر"):
    st.data_editor(
        safe_for_display(fdf),
        use_container_width=True,
        disabled=True,
        hide_index=True
    )
