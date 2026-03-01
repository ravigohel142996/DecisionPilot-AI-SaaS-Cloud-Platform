import os

import streamlit as st


def get_api_base_url() -> str:
    secrets_url = None
    try:
        secrets_url = st.secrets.get("API_BASE_URL")
    except FileNotFoundError:
        secrets_url = None

    url = secrets_url or os.getenv("API_BASE_URL") or "http://localhost:8000"
    return str(url).rstrip("/")


REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
