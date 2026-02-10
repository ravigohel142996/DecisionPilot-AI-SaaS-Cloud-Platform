import streamlit as st

from api import APIClient
from auth_ui import init_session, inject_styles, render_auth

st.set_page_config(page_title="VisionPilot AI", page_icon="🧭", layout="wide")

inject_styles()
init_session()
client = APIClient()

st.title("VisionPilot AI - 3D Decision Intelligence Platform")

with st.sidebar:
    st.caption(f"API: {client.base_url}")
    ok, _ = client.health()
    if ok:
        st.success("Backend online")
    else:
        st.warning("Server offline")

    if st.session_state.token and st.button("Logout", use_container_width=True):
        st.session_state.token = None
        st.rerun()

if not st.session_state.token:
    render_auth(client)
else:
    with st.spinner("Loading dashboard..."):
        ok, data = client.me(st.session_state.token)
    if not ok:
        st.session_state.token = None
        st.error(data["detail"])
        st.stop()

    st.success(f"Welcome, {data['full_name']}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Status", "Active")
    col2.metric("Email", data["email"])
    col3.metric("User ID", data["id"])

    st.markdown("### Decision Dashboard")
    st.info("Auth is configured. Connect your analytics modules here.")

    with st.expander("Session token"):
        st.code(st.session_state.token[:80] + "...", language="text")
