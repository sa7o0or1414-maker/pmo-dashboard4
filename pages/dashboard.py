import streamlit as st
import plotly.express as px
from core.config import load_config, apply_branding
from core.data_io import prepare_dashboard_data
from core.ml import train_delay_model, predict_delay
from core.sidebar import render_sidebar

st.set_page_config(layout="wide")

cfg = load_config()
apply_branding(cfg)
render_sidebar()

st.title(cfg["dashboard_title"])

df = prepare_dashboard_data()
if df.empty:
    st.info("No data available")
    st.stop()

pipe, auc = train_delay_model(df)
if pipe:
    df = predict_delay(pipe, df)
    st.caption(f"Model AUC: {auc:.2f}")

st.dataframe(df, use_container_width=True)
