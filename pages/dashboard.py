import streamlit as st
import pandas as pd
import plotly.express as px

from core.config import load_config, apply_branding
from core.data_io import prepare_dashboard_data
from core.ml import train_delay_model, predict_delay_risk
from core.features import build_features, reason_rules
from core.sidebar import render_sidebar


st.set_page_config(page_title="Dashboard", layout="wide")

cfg = load_config()
apply_branding(cfg)

st.title(cfg.get("dashboard_title", "Dashboard"))

df = prepare_dashboard_data()

if df.empty:
    st.info("No data found. Ask admin to upload an Excel file.")
    st.stop()

# Filters
with st.sidebar:
    st.subheader("Filters")

    municipality_list = sorted([x for x in df.get("municipality", pd.Series()).dropna().unique().tolist()])
    entity_list = sorted([x for x in df.get("entity", pd.Series()).dropna().unique().tolist()])
    status_list = sorted([x for x in df.get("status", pd.Series()).dropna().unique().tolist()])

    selected_municipality = st.multiselect("Municipality", municipality_list, default=[])
    selected_entity = st.multiselect("Entity", entity_list, default=[])
    selected_status = st.multiselect("Status", status_list, default=[])

filtered = df.copy()
if "municipality" in filtered.columns and selected_municipality:
    filtered = filtered[filtered["municipality"].isin(selected_municipality)]
if "entity" in filtered.columns and selected_entity:
    filtered = filtered[filtered["entity"].isin(selected_entity)]
if "status" in filtered.columns and selected_status:
    filtered = filtered[filtered["status"].isin(selected_status)]

# KPIs
f = build_features(filtered)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="kpi-card"><div class="kpi-label">Projects</div>'
                f'<div class="kpi-value">{len(filtered):,}</div></div>', unsafe_allow_html=True)
with col2:
    delayed_actual = int(f["is_delayed_actual"].sum())
    st.markdown('<div class="kpi-card"><div class="kpi-label">Delayed (Actual)</div>'
                f'<div class="kpi-value">{delayed_actual:,}</div></div>', unsafe_allow_html=True)
with col3:
    avg_progress = f["progress"].mean()
    st.markdown('<div class="kpi-card"><div class="kpi-label">Avg Progress</div>'
                f'<div class="kpi-value">{(avg_progress if pd.notna(avg_progress) else 0):.1f}%</div></div>',
                unsafe_allow_html=True)
with col4:
    total_budget = pd.to_numeric(filtered.get("budget", pd.Series()), errors="coerce").sum()
    st.markdown('<div class="kpi-card"><div class="kpi-label">Total Budget</div>'
                f'<div class="kpi-value">{(total_budget if pd.notna(total_budget) else 0):,.0f}</div></div>',
                unsafe_allow_html=True)

st.divider()

# Charts
c1, c2 = st.columns(2)

with c1:
    if "status" in filtered.columns and len(filtered["status"].unique()) > 0:
        fig = px.histogram(filtered, x="status", title="Projects by Status")
        st.plotly_chart(fig, use_container_width=True)

with c2:
    if "municipality" in filtered.columns and len(filtered["municipality"].unique()) > 0:
        top = filtered["municipality"].value_counts().head(10).reset_index()
        top.columns = ["municipality", "count"]
        fig = px.bar(top, x="municipality", y="count", title="Top Municipalities")
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# Prediction section
st.subheader("Delay prediction (risk)")

pipe, auc = train_delay_model(filtered)
if pipe is None:
    st.info("Not enough labeled data to train prediction model (need >= 30 rows and both delayed/non-delayed samples).")
else:
    pred = predict_delay_risk(pipe, filtered)

    if auc is not None:
        st.caption(f"Model validation AUC: {auc:.3f}")

    high_risk = pred[pred["risk_bucket"] == "High"].copy()
    st.write("High risk projects")
    if high_risk.empty:
        st.success("No high risk projects found in current filters.")
    else:
        # add reasons
        bf = build_features(high_risk)
        reasons = []
        for _, row in bf.iterrows():
            reasons.append(", ".join(reason_rules(row)))
        high_risk["risk_reasons"] = reasons

        cols_show = [c for c in ["project", "municipality", "entity", "status", "progress", "budget", "delay_risk", "risk_reasons"] if c in high_risk.columns]
        st.dataframe(high_risk[cols_show].sort_values("delay_risk", ascending=False), use_container_width=True)

st.divider()

# Actual delayed list
st.subheader("Delayed projects (actual)")
actual_delayed = filtered[f["is_delayed_actual"] == 1].copy()
if actual_delayed.empty:
    st.success("No actual delayed projects found in current filters.")
else:
    cols_show = [c for c in ["project", "municipality", "entity", "status", "progress", "budget", "end_date", "actual_end_date"] if c in actual_delayed.columns]
    st.dataframe(actual_delayed[cols_show], use_container_width=True)
