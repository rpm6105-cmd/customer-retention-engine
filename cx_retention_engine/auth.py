from __future__ import annotations

import streamlit as st

from cx_retention_engine.data_loader import create_user, email_domain, get_user_by_credentials


def init_auth_state() -> None:
    defaults = {
        "logged_in": False,
        "user_type": None,
        "user_name": "",
        "user_email": "",
        "user_role": "",
        "signup_success": None,
        "force_login_view": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_login_shell() -> None:
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] { display:none !important; }
        [data-testid="collapsedControl"] { display:none !important; }
        </style>
        <div class='auth-shell'>
        <div class='auth-hero'>
          <div class='auth-kicker'>Customer Success Platform</div>
          <div class='auth-title'>CX Retention Engine</div>
          <div class='auth-sub'>A modular customer success operations workspace for retention risk, renewals, portfolio ownership, and executive visibility.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.force_login_view:
        st.session_state["retention_auth_mode"] = "Login"
        st.session_state.force_login_view = False

    st.markdown("<div class='auth-toggle-shell'>", unsafe_allow_html=True)
    mode = st.radio("Access", ["Login", "Sign Up"], horizontal=True, key="retention_auth_mode")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.signup_success:
        st.success(st.session_state.signup_success)
        st.session_state.signup_success = None

    if mode == "Login":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                """
                <div class='auth-card auth-card-demo'>
                  <div class='auth-card-kicker'>Explore The Product</div>
                  <div class='auth-card-title'>Try Demo</div>
                  <div class='auth-card-copy'>
                    Use the sample workspace to explore dashboards, tasks, renewals, and portfolio monitoring without uploading your own master dataset.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            demo_user = st.text_input("Username", key="demo_user")
            demo_password = st.text_input("Password", type="password", key="demo_password")
            if st.button("Login Demo"):
                if demo_user.strip().lower() == "freeuser" and demo_password.strip() == "123456":
                    st.session_state.logged_in = True
                    st.session_state.user_type = "demo"
                    st.session_state.user_name = "Freeuser"
                    st.session_state.user_email = "demo@local"
                    st.session_state.user_role = "demo"
                    st.rerun()
                st.error("Invalid demo credentials")
        with col2:
            st.markdown(
                """
                <div class='auth-card auth-card-premium'>
                  <div class='auth-card-kicker'>Premium Workspace</div>
                  <div class='auth-card-title'>Use My Account</div>
                  <div class='auth-card-copy'>
                    Sign in to manage the live company master dataset, assign CSM ownership, review renewal exposure, and run the full retention workspace.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            email = st.text_input("Email", key="premium_email")
            password = st.text_input("Password", type="password", key="premium_password")
            if st.button("Login Premium"):
                user = get_user_by_credentials(email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_type = "premium"
                    st.session_state.user_name = user[0]
                    st.session_state.user_email = user[2]
                    st.session_state.user_role = user[5]
                    st.rerun()
                st.error("Invalid credentials")
    else:
        _, mid, _ = st.columns([1, 1.15, 1])
        with mid:
            st.markdown(
                """
                <div class='auth-card auth-card-premium'>
                  <div class='auth-card-kicker'>Premium Onboarding</div>
                  <div class='auth-card-title'>Create your retention workspace</div>
                  <div class='auth-card-copy'>
                    Set up an admin or CSM account for your company domain and start running the Customer Success operations workspace from one shared platform.
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            name = st.text_input("Name", key="signup_name")
            company = st.text_input("Company", key="signup_company")
            email = st.text_input("Email", key="signup_email")
            place = st.text_input("Place", key="signup_place")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
            if st.button("Create Account"):
                if not name.strip() or not email.strip() or not password.strip():
                    st.error("Name, Email, and Password are required")
                elif "@" not in email.strip():
                    st.error("Please enter a valid company email")
                elif password.strip() != confirm.strip():
                    st.error("Passwords do not match")
                else:
                    ok, role, message = create_user(name, company, email, place, password)
                    if ok:
                        st.session_state.force_login_view = True
                        st.session_state.signup_success = (
                            "Account created successfully. "
                            + ("You are set as Admin for your company domain. " if role == "admin" else "")
                            + "Please login with Premium."
                        )
                        st.rerun()
                    st.error(message)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()
