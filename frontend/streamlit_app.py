codex/build-saas-version-of-decisionpilot-ai-ogjk9v
from datetime import datetime

=======
codex/build-saas-version-of-decisionpilot-ai-oqeah7
from datetime import datetime

=======
main
 main
import requests
import streamlit as st

API_BASE_URL = st.secrets.get("api_base_url", "http://localhost:8000")

st.set_page_config(page_title="DecisionPilot SaaS", page_icon="📊", layout="wide")
 codex/build-saas-version-of-decisionpilot-ai-ogjk9v
=======
codex/build-saas-version-of-decisionpilot-ai-oqeah7
 main

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
      .metric-card {
        border: 1px solid #EAECF0;
        border-radius: 12px;
        padding: 0.6rem 0.8rem;
      }
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
 codex/build-saas-version-of-decisionpilot-ai-ogjk9v
=======
if "api_error" not in st.session_state:
    st.session_state.api_error = ""

 main
def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {st.session_state.token}"}


def api_post(path: str, **kwargs):
    return requests.post(f"{API_BASE_URL}{path}", timeout=45, **kwargs)


def api_get(path: str, **kwargs):
    return requests.get(f"{API_BASE_URL}{path}", timeout=45, **kwargs)


with st.sidebar:
    st.subheader("Environment")
    st.caption(f"API: {API_BASE_URL}")
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
            if response.ok:
                st.session_state.token = response.json()["access_token"]
                st.success("Registration successful. You're now signed in.")
            else:
                st.error(response.text)

    with right:
        st.subheader("Sign in")
        with st.form("login"):
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            login_submit = st.form_submit_button("Sign in", use_container_width=True)

        if login_submit:
            response = api_post("/auth/login", json={"email": login_email, "password": login_password})
 codex/build-saas-version-of-decisionpilot-ai-ogjk9v
=======
=======
st.title("📊 DecisionPilot AI - SaaS Analytics Workspace")

if "token" not in st.session_state:
    st.session_state.token = None
if "last_upload_id" not in st.session_state:
    st.session_state.last_upload_id = None


def get_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {st.session_state.token}"}


tab_auth, tab_upload = st.tabs(["Authentication", "CSV Analysis"])

with tab_auth:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Register Workspace")
        with st.form("register"):
            company = st.text_input("Company name")
            name = st.text_input("Full name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            register_submit = st.form_submit_button("Create account")

        if register_submit:
            response = requests.post(
                f"{API_BASE_URL}/auth/register",
                json={"company_name": company, "email": email, "password": password, "full_name": name},
                timeout=30,
            )
            if response.ok:
                st.session_state.token = response.json()["access_token"]
                st.success("Registration successful.")
            else:
                st.error(response.text)

    with c2:
        st.subheader("Sign in")
        with st.form("login"):
            login_email = st.text_input("Login email")
            login_password = st.text_input("Login password", type="password")
            login_submit = st.form_submit_button("Sign in")

        if login_submit:
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json={"email": login_email, "password": login_password},
                timeout=30,
            )
main
 main
            if response.ok:
                st.session_state.token = response.json()["access_token"]
                st.success("Logged in.")
            else:
                st.error(response.text)

 codex/build-saas-version-of-decisionpilot-ai-ogjk9v
=======
codex/build-saas-version-of-decisionpilot-ai-oqeah7
 main
with tab_workspace:
    if not st.session_state.token:
        st.warning("Please authenticate first in the Authentication tab.")
    else:
        profile = api_get("/auth/me", headers=auth_headers())
        if not profile.ok:
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
            if response.ok:
                payload = response.json()
                st.session_state.last_summary = payload["summary"]
                st.success(f"Analysis complete for upload #{payload['upload_id']}.")
            else:
                st.error(response.text)

        if st.session_state.last_summary:
            st.markdown("**Latest analysis summary**")
            st.code(st.session_state.last_summary)

        st.divider()
        st.subheader("Recent uploads")
        uploads_resp = api_get("/analysis/uploads", headers=auth_headers())
        if uploads_resp.ok:
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
                    if report.ok:
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
 codex/build-saas-version-of-decisionpilot-ai-ogjk9v
=======
=======
    if st.session_state.token:
        me = requests.get(f"{API_BASE_URL}/auth/me", headers=get_headers(), timeout=30)
        if me.ok:
            payload = me.json()
            st.info(
                f"Workspace: {payload['company_name']} | Plan: {payload['subscription_tier']} ({payload['subscription_status']})"
            )

with tab_upload:
    if not st.session_state.token:
        st.warning("Please authenticate first.")
    else:
        st.subheader("Upload CSV for automated analysis")
        file = st.file_uploader("Select a CSV file", type=["csv"])
        if file and st.button("Analyze file", type="primary"):
            response = requests.post(
                f"{API_BASE_URL}/analysis/upload",
                files={"file": (file.name, file.getvalue(), "text/csv")},
                headers=get_headers(),
                timeout=60,
            )
            if response.ok:
                payload = response.json()
                st.session_state.last_upload_id = payload["upload_id"]
                st.success(f"Analysis complete for upload #{payload['upload_id']}")
                st.code(payload["summary"])
            else:
                st.error(response.text)

        if st.session_state.last_upload_id:
            report_url = f"{API_BASE_URL}/analysis/report/{st.session_state.last_upload_id}"
            st.markdown(f"[Download Executive PDF Report]({report_url})")
main
 main