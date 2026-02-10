import re

import streamlit as st

from api import APIClient

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #070b14; color: #f8fafc; }
        .block-container { max-width: 920px; padding-top: 1.5rem; }
        h1,h2,h3,p,label,span,div { color: #f8fafc !important; }
        [data-testid="stSidebar"] { background: #0f172a; }
        .card { background: #111827; border: 1px solid #475569; border-radius: 14px; padding: 1rem 1.25rem; }
        .stTextInput input {
            background: #0f172a !important;
            color: #f8fafc !important;
            border: 1px solid #64748b !important;
        }
        .stTextInput label { color: #e2e8f0 !important; }
        .stButton button, .stForm button {
            width: 100%;
            border-radius: 10px;
            font-weight: 700;
            background: #2563eb;
            color: white;
            border: none;
        }
        .stAlert { border-radius: 10px; }
        @media (max-width: 768px){ .block-container { padding: 0.8rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_session() -> None:
    st.session_state.setdefault("token", None)


def _validate_login(email: str, password: str) -> str | None:
    if not EMAIL_REGEX.match(email.strip().lower()):
        return "Please enter a valid email address"
    if not password:
        return "Password is required"
    return None


def render_auth(client: APIClient) -> None:
    st.markdown("### Login")
    st.caption("Use the admin credentials to access VisionPilot AI.")

    with st.form("login_form"):
        email = st.text_input("Email", value="admin@visionpilot.ai")
        password = st.text_input("Password", type="password", value="admin123")
        submit = st.form_submit_button("Login")

        if submit:
            error = _validate_login(email=email, password=password)
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
