import streamlit as st


def hide_default_streamlit_nav():
    st.markdown(
        """
        <style>
          /* Hide the default multi-page navigation */
          [data-testid="stSidebarNav"] { display: none; }

          /* Sidebar spacing */
          section[data-testid="stSidebar"] .block-container {
            padding-top: 1rem;
          }

          /* Menu buttons */
          .menu-title {
            font-size: 14px;
            letter-spacing: .5px;
            opacity: .85;
            margin: 12px 0 8px 0;
          }

          .menu-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 10px;
            margin-bottom: 10px;
          }

          .menu-hint {
            font-size: 12px;
            opacity: .75;
            margin-top: 6px;
          }

          /* Make buttons full width */
          section[data-testid="stSidebar"] button {
            width: 100%;
            border-radius: 12px !important;
            padding: 10px 12px !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            background: rgba(255,255,255,0.04) !important;
          }
          section[data-testid="stSidebar"] button:hover {
            border-color: rgba(255,255,255,0.22) !important;
            background: rgba(255,255,255,0.07) !important;
          }

          /* Divider line */
          .menu-divider {
            height: 1px;
            background: rgba(255,255,255,0.10);
            margin: 12px 0;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(active: str):
    """
    active: one of
      - "dashboard"
      - "upload"
      - "settings"
      - "login"
    """
    hide_default_streamlit_nav()

    # Top block (title already handled in apply_branding; this adds structure)
    st.sidebar.markdown('<div class="menu-card">', unsafe_allow_html=True)
    st.sidebar.caption("Navigation")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    st.sidebar.markdown('<div class="menu-title">MENU</div>', unsafe_allow_html=True)

    # Public
    if st.sidebar.button("Home", use_container_width=True, disabled=(active == "dashboard")):
        st.switch_page("pages/dashboard.py")

    st.sidebar.markdown('<div class="menu-divider"></div>', unsafe_allow_html=True)

    st.sidebar.markdown('<div class="menu-title">ADMIN</div>', unsafe_allow_html=True)

    if st.sidebar.button("Upload Data", use_container_width=True, disabled=(active == "upload")):
        st.switch_page("pages/upload_data.py")

    if st.sidebar.button("Settings", use_container_width=True, disabled=(active == "settings")):
        st.switch_page("pages/settings.py")

    if st.sidebar.button("Admin Login", use_container_width=True, disabled=(active == "login")):
        st.switch_page("pages/admin_login.py")

    st.sidebar.markdown('<div class="menu-card menu-hint">', unsafe_allow_html=True)
    st.sidebar.markdown("Tip: Home page is public. Admin pages require login.", unsafe_allow_html=True)
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
