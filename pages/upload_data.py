import streamlit as st
from core.config import load_config, apply_branding
from core.auth import require_admin
from core.data_io import save_uploaded_file, read_data
from core.sidebar import render_sidebar

st.set_page_config(page_title="Upload Data", layout="wide")

cfg = load_config()
apply_branding(cfg)
render_sidebar(active="upload")

require_admin()

st.title("Upload Data")

uploaded = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded is not None:
    save_uploaded_file(uploaded)
    st.success("File uploaded successfully.")
    try:
        df_preview = read_data()
        st.write("Preview (first 20 rows)")
        st.dataframe(df_preview.head(20), use_container_width=True)
    except Exception as e:
        st.error(f"Could not read file: {e}")
