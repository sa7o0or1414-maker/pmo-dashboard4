import streamlit as st


def hide_default_streamlit_nav():
    st.markdown(
        """
        <style>
          [data-testid="stSidebarNav"] { display: none; }

          section[data-testid="stSidebar"] .block-container {
            padding-top: 1rem;
          }

          .menu-title {
            font-size: 13px;
            opacity: .7;
            margin: 14px 0 6px 0;
            letter-spacing: .4px;
          }

          .menu-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 12px;
            margin-bottom: 10px;
          }

          section[data-testid="stSidebar"] a {
            width: 100%;
            display: block;
            text-decoration: none;
            border-radius: 12px;
            padding: 10px 12px;
            border: 1px solid rgba(255,255,255,0.10);
            background: rgba(255,255,255,0.04);
            margin-bottom: 8px;
            color: inherit;
          }

          section[data-testid="stSidebar"] a:hover {
            border-color: rgba(255,255,255,0.25);
            background: rgba(255,255,255,0.07);
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    hide_default_streamlit_nav()

    st.sidebar.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.sidebar.caption("Navigation")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    st.sidebar.markdown('<div class="menu-title">MENU</div>', unsafe_allow_html=True)

    st.page_link("pages/dashboard.py", label="Home")

    st.sidebar.markdown('<div class="menu-title">ADMIN</div>', unsafe_allow_html=True)

    st.page_link("pages/upload_data.py", label="Upload Data")
    st.page_link("pages/settings.py", label="Settings")
    st.page_link("pages/admin_login.py", label="Admin Login")

    st.sidebar.markdown(
        '<div class="menu-card"><small>Home page is public. Admin pages require login.</small></div>',
        unsafe_allow_html=True,
    )
