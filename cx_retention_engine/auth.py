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
        <div class='hero-card' style='padding:2rem 2.15rem;border-radius:28px'>
          <div style='display:inline-flex;padding:0.45rem 0.8rem;border-radius:999px;background:rgba(12,92,114,0.08);color:#0c5c72;font-size:0.74rem;font-weight:800;letter-spacing:0.08em;text-transform:uppercase'>Customer Success Platform</div>
          <div style='margin-top:1rem;color:#162033;font-size:3.2rem;line-height:1;font-weight:900;letter-spacing:-0.04em;max-width:980px'>CX Retention Engine</div>
          <div style='margin-top:1rem;max-width:820px;color:#5c687d;font-size:1.05rem;line-height:1.65'>A modular customer success operations workspace for retention risk, renewals, portfolio ownership, and executive visibility.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.force_login_view:
        st.session_state["retention_auth_mode"] = "Login"
        st.session_state.force_login_view = False

    mode = st.radio("Access", ["Login", "Sign Up"], horizontal=True, key="retention_auth_mode")

    if st.session_state.signup_success:
        st.success(st.session_state.signup_success)
        st.session_state.signup_success = None

    if mode == "Login":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Try Demo")
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
            st.markdown("### Premium Login")
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
            st.markdown("### Create Premium Workspace")
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
    st.stop()
