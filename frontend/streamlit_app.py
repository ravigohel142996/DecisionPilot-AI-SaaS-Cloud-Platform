import os
from datetime import datetime
from urllib.parse import quote_plus

import requests
import streamlit as st
from requests import Response


def resolve_api_base_url() -> str:
    configured_url = (
        st.secrets.get("api_base_url")
        or os.getenv("API_BASE_URL")
        or os.getenv("BACKEND_URL")
        or "http://localhost:8000"
    )
    return configured_url.rstrip("/")


if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = resolve_api_base_url()

st.set_page_config(page_title="DecisionPilot SaaS", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
      .hero {
        padding: 1rem 1.25rem;
        border: 1px solid #D8E4FF;
        border-radius: 16px;
        background: linear-gradient(130deg, #f4f8ff 0%, #f8fcff 100%);
      }
      .hero h1 { margin-bottom: 0.2rem; }
      .hero p { color: #1d3557; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>📊 DecisionPilot AI SaaS Analytics Workspace</h1>
      <p>Secure multi-tenant analysis platform with executive reporting.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "token" not in st.session_state:
    st.session_state.token = None
if "last_summary" not in st.session_state:
    st.session_state.last_summary = ""


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {st.session_state.token}"}


def api_post(path: str, **kwargs) -> Response | None:
    try:
        return requests.post(f"{st.session_state.api_base_url}{path}", timeout=45, **kwargs)
    except requests.RequestException:
        return None


def api_get(path: str, **kwargs) -> Response | None:
    try:
        return requests.get(f"{st.session_state.api_base_url}{path}", timeout=45, **kwargs)
    except requests.RequestException:
        return None


with st.sidebar:
    st.subheader("Environment")
    st.caption(f"API: {st.session_state.api_base_url}")
    with st.expander("API configuration", expanded=False):
        manual_api_base_url = st.text_input(
            "API base URL",
            value=st.session_state.api_base_url,
            placeholder="https://your-backend.example.com",
            help="Use your deployed FastAPI URL when running this UI on Streamlit Cloud.",
        ).strip()
        if st.button("Apply API URL", use_container_width=True):
            st.session_state.api_base_url = manual_api_base_url.rstrip("/")
            st.query_params["api_base_url"] = st.session_state.api_base_url
            st.rerun()

        if st.query_params.get("api_base_url") and st.query_params.get("api_base_url") != st.session_state.api_base_url:
            st.session_state.api_base_url = st.query_params.get("api_base_url", "").rstrip("/")

        st.caption(
            "Tip: you can share a prefilled app URL with `?api_base_url=` query parameter, "
            f"for example `?api_base_url={quote_plus('https://api.example.com')}`."
        )

    if "localhost" in st.session_state.api_base_url or "127.0.0.1" in st.session_state.api_base_url:
        st.warning("API URL is set to localhost. This will not work on Streamlit Cloud deployments.")

    health = api_get("/health")
    if health and health.ok:
        st.success("Backend reachable")
    else:
        st.error("Backend unreachable. Update API base URL in API configuration.")

    if st.button("Sign out", use_container_width=True):
        st.session_state.token = None
        st.session_state.last_summary = ""
        st.rerun()


tab_auth, tab_workspace = st.tabs(["Authentication", "Workspace"])

with tab_auth:
    left, right = st.columns(2)

    with left:
        st.subheader("Register workspace")
        with st.form("register"):
            company = st.text_input("Company name", placeholder="Acme Inc")
            name = st.text_input("Full name", placeholder="Jane Doe")
            email = st.text_input("Work email", placeholder="jane@acme.com")
            password = st.text_input("Password", type="password")
            register_submit = st.form_submit_button("Create account", use_container_width=True)

        if register_submit:
            response = api_post(
                "/auth/register",
                json={"company_name": company, "email": email, "password": password, "full_name": name},
            )
            if response and response.ok:
                st.session_state.token = response.json()["access_token"]
                st.success("Registration successful. You're now signed in.")
            else:
                st.error(response.text if response is not None else "Request failed. Check API URL and backend status.")

    with right:
        st.subheader("Sign in")
        with st.form("login"):
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            login_submit = st.form_submit_button("Sign in", use_container_width=True)

        if login_submit:
            response = api_post("/auth/login", json={"email": login_email, "password": login_password})
            if response and response.ok:
                st.session_state.token = response.json()["access_token"]
                st.success("Logged in successfully.")
            else:
                st.error(response.text if response is not None else "Request failed. Check API URL and backend status.")

with tab_workspace:
    if not st.session_state.token:
        st.warning("Please authenticate first in the Authentication tab.")
    else:
        profile = api_get("/auth/me", headers=auth_headers())
        if not profile or not profile.ok:
            st.error("Session invalid or expired. Please sign in again.")
            st.stop()

        user = profile.json()
        c1, c2, c3 = st.columns(3)
        c1.metric("Workspace", user["company_name"])
        c2.metric("Plan", user["subscription_tier"].upper())
        c3.metric("Status", user["subscription_status"].capitalize())

        st.divider()
        st.subheader("Upload CSV and auto-analyze")
        uploaded = st.file_uploader("Select dataset", type=["csv"])
        if uploaded and st.button("Run analysis", type="primary"):
            response = api_post(
                "/analysis/upload",
                files={"file": (uploaded.name, uploaded.getvalue(), "text/csv")},
                headers=auth_headers(),
            )
            if response and response.ok:
                payload = response.json()
                st.session_state.last_summary = payload["summary"]
                st.success(f"Analysis complete for upload #{payload['upload_id']}.")
            else:
                st.error(response.text if response is not None else "Request failed. Check API URL and backend status.")

        if st.session_state.last_summary:
            st.markdown("**Latest analysis summary**")
            st.code(st.session_state.last_summary)

        st.divider()
        st.subheader("Recent uploads")
        uploads_resp = api_get("/analysis/uploads", headers=auth_headers())
        if uploads_resp and uploads_resp.ok:
            items = uploads_resp.json().get("items", [])
            if not items:
                st.info("No uploads yet.")
            else:
                for row in items:
                    row_cols = st.columns([4, 2, 2])
                    row_cols[0].markdown(f"**{row['filename']}**")
                    created = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
                    row_cols[1].caption(created.strftime("%Y-%m-%d %H:%M"))
                    report = api_get(f"/analysis/report/{row['id']}", headers=auth_headers())
                    if report and report.ok:
                        row_cols[2].download_button(
                            "PDF",
                            data=report.content,
                            file_name=f"executive-report-{row['id']}.pdf",
                            mime="application/pdf",
                            key=f"dl-{row['id']}",
                            use_container_width=True,
                        )
                    else:
                        row_cols[2].button("Unavailable", disabled=True, key=f"na-{row['id']}")
        else:
            st.error("Failed to load uploads.")
