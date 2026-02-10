import re

import streamlit as st

from api import APIClient

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #0b1220; color: #e2e8f0; }
        .block-container { max-width: 900px; padding-top: 1.5rem; }
        h1,h2,h3,p,label,span,div { color: #e2e8f0 !important; }
        .card { background: #111827; border: 1px solid #334155; border-radius: 14px; padding: 1rem 1.25rem; }
        .stTextInput input { background: #1f2937 !important; color: #e2e8f0 !important; }
        .stButton button { width: 100%; border-radius: 10px; font-weight: 700; }
        @media (max-width: 768px){ .block-container { padding: 0.8rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_session() -> None:
    st.session_state.setdefault("token", None)
    st.session_state.setdefault("view", "login")


def _validate_form(email: str, password: str, full_name: str = "") -> str | None:
    if full_name is not None and full_name != "" and len(full_name.strip()) < 2:
        return "Full name must be at least 2 characters"
    if not EMAIL_REGEX.match(email.strip().lower()):
        return "Please enter a valid email address"
    if len(password) < 8:
        return "Password must be at least 8 characters"
    return None


def render_auth(client: APIClient) -> None:
    tabs = st.tabs(["Login", "Register"])

    with tabs[0]:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="you@company.com")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                error = _validate_form(email=email, password=password)
                if error:
                    st.error(error)
                else:
                    with st.spinner("Signing in..."):
                        ok, data = client.login(email=email.strip().lower(), password=password)
                    if ok:
                        st.session_state.token = data["access_token"]
                        st.success("Login successful")
                        st.rerun()
                    st.error(data["detail"])

    with tabs[1]:
        with st.form("register_form"):
            full_name = st.text_input("Full name", placeholder="Alex Morgan")
            email = st.text_input("Work email", placeholder="alex@visionpilot.ai")
            password = st.text_input("Password", type="password", help="At least 8 characters")
            submit = st.form_submit_button("Create account")

            if submit:
                error = _validate_form(email=email, password=password, full_name=full_name)
                if error:
                    st.error(error)
                else:
                    with st.spinner("Creating account..."):
                        ok, data = client.register(
                            full_name=full_name.strip(),
                            email=email.strip().lower(),
                            password=password,
                        )
                    if ok:
                        st.success("Signup successful. Please login.")
                    else:
                        st.error(data["detail"])
