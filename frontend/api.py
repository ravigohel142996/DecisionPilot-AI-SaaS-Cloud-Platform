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
    ) -> Tuple[bool, Dict[str, Any]]:
        try:
            response = requests.request(
                method=method,
                url=f"{self.base_url}{path}",
                json=payload,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.Timeout:
            return False, {"detail": "Request timed out."}
        except requests.RequestException:
            return False, {"detail": "Backend unavailable."}

        try:
            data = response.json()
        except ValueError:
            return False, {"detail": "Unexpected backend response."}

        if not response.ok:
            return False, {"detail": "Dashboard data is temporarily unavailable."}
        return True, data

    def health(self):
        return self._request("GET", "/health")

    def dashboard(self):
        return self._request("GET", "/dashboard")

    def data(self):
        return self._request("GET", "/data")

    def predict(self, revenue: float, cost: float, growth_rate: float):
        return self._request(
            "POST",
            "/predict",
            {"revenue": revenue, "cost": cost, "growth_rate": growth_rate},
        )
