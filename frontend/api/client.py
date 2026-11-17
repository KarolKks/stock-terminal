import requests
from typing import Optional


class ApiError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ApiClient:

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    def _auth_headers(self) -> dict:
        if not self.access_token:
            return {}
        return {"Authorization": f"Bearer {self.access_token}"}

    @staticmethod
    def _handle_response(resp: requests.Response):
        if resp.status_code == 204:
            return None
        try:
            data = resp.json()
        except Exception:
            data = None

        if not resp.ok:
            detail = ""
            if isinstance(data, dict):
                detail = data.get("detail", "")
            if not detail:
                detail = resp.text or f"HTTP Error {resp.status_code}"
            raise ApiError(detail, status_code=resp.status_code)
        return data

    def register(
        self,
        username: str,
        email: str,
        first_name: str,
        password: str,
        last_name: str = "",
    ) -> dict:
        payload = {
            "username": username,
            "email": email,
            "first_name": first_name,
            "last_name": last_name or None,
            "password": password,
        }
        resp = requests.post(f"{self.base_url}/auth/register", json=payload, timeout=10)
        return self._handle_response(resp)

    def login(self, username: str, password: str) -> dict:
        payload = {"username": username, "password": password}
        resp = requests.post(f"{self.base_url}/auth/login", json=payload, timeout=10)
        data = self._handle_response(resp)
        self.access_token = data.get("access_token")
        self.refresh_token = data.get("refresh_token")
        return data

    def logout(self) -> dict:
        payload = {"refresh_token": self.refresh_token or ""}
        try:
            resp = requests.post(f"{self.base_url}/auth/logout", json=payload, timeout=10)
            data = self._handle_response(resp)
        except Exception:
            data = {"message": "Logged out"}
        finally:
            self.access_token = None
            self.refresh_token = None
        return data

    def refresh_access_token(self) -> dict:
        payload = {"refresh_token": self.refresh_token}
        resp = requests.post(f"{self.base_url}/auth/refresh", json=payload, timeout=10)
        data = self._handle_response(resp)
        self.access_token = data.get("access_token")
        self.refresh_token = data.get("refresh_token", self.refresh_token)
        return data

    def get_me(self) -> dict:
        resp = requests.get(
            f"{self.base_url}/auth/me",
            headers=self._auth_headers(),
            timeout=10,
        )
        return self._handle_response(resp)

    def get_watchlists(self) -> list[dict]:
        resp = requests.get(
            f"{self.base_url}/watchlists/categories",
            headers=self._auth_headers(),
            timeout=15,
        )
        return self._handle_response(resp)

    def create_category(self, name: str) -> dict:
        payload = {"name": name.strip()}
        resp = requests.post(
            f"{self.base_url}/watchlists/categories",
            json=payload,
            headers=self._auth_headers(),
            timeout=15,
        )
        return self._handle_response(resp)

    def rename_category(self, category_id: int, name: str) -> dict:
        payload = {"name": name.strip()}
        resp = requests.patch(
            f"{self.base_url}/watchlists/categories/{category_id}",
            json=payload,
            headers=self._auth_headers(),
            timeout=15,
        )
        return self._handle_response(resp)

    def delete_category(self, category_id: int) -> None:
        resp = requests.delete(
            f"{self.base_url}/watchlists/categories/{category_id}",
            headers=self._auth_headers(),
            timeout=15,
        )
        return self._handle_response(resp)

    def add_ticker(self, category_id: int, ticker: str) -> dict:
        payload = {"ticker": ticker.strip().upper()}
        resp = requests.post(
            f"{self.base_url}/watchlists/categories/{category_id}/items",
            json=payload,
            headers=self._auth_headers(),
            timeout=25,
        )
        return self._handle_response(resp)

    def remove_ticker(self, category_id: int, ticker: str) -> None:
        clean_ticker = ticker.strip().upper()
        resp = requests.delete(
            f"{self.base_url}/watchlists/categories/{category_id}/items/{clean_ticker}",
            headers=self._auth_headers(),
            timeout=15,
        )
        return self._handle_response(resp)

    def get_candles(
        self,
        ticker: str,
        interval: str = "1d",
        period: str = "6mo",
    ) -> dict:
        clean_ticker = ticker.strip().upper()
        params = {"interval": interval, "period": period}
        resp = requests.get(
            f"{self.base_url}/market/candles/{clean_ticker}",
            params=params,
            headers=self._auth_headers(),
            timeout=30,
        )
        return self._handle_response(resp)
