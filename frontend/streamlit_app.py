import requests
import streamlit as st

API_BASE_URL = st.secrets.get("api_base_url", "http://localhost:8000")

st.set_page_config(page_title="DecisionPilot SaaS", page_icon="📊", layout="wide")
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
            if response.ok:
                st.session_state.token = response.json()["access_token"]
                st.success("Logged in.")
            else:
                st.error(response.text)

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
