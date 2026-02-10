from typing import Any, Dict, Optional, Tuple

import requests

from config import REQUEST_TIMEOUT_SECONDS, get_api_base_url


class APIClient:
    def __init__(self):
        self.base_url = get_api_base_url()

    def _request(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        token: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            response = requests.request(
                method=method,
                url=f"{self.base_url}{path}",
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.Timeout:
            return False, {"detail": "Request timed out. Please try again."}
        except requests.RequestException:
            return False, {"detail": "Cannot connect to backend. Check API_BASE_URL and server health."}

        try:
            data = response.json()
        except ValueError:
            data = {"detail": response.text or "Unexpected server response"}

        if response.status_code == 404:
            return False, {"detail": "Backend route is unavailable. Verify backend deployment and API_BASE_URL."}

        if not response.ok:
            return False, {"detail": data.get("detail", "Request failed")}
        return True, data

    def health(self):
        return self._request("GET", "/health")

    def login(self, email: str, password: str):
        return self._request("POST", "/auth/login", {"email": email, "password": password})

    def me(self, token: str):
        return self._request("GET", "/auth/me", token=token)
