import os

import streamlit as st


def get_api_base_url() -> str:
    url = st.secrets.get("API_BASE_URL") or os.getenv("API_BASE_URL") or "http://localhost:8000"
    return str(url).rstrip("/")


REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
