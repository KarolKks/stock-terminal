import requests
from typing import Optional


class ApiClient:

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

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
        resp.raise_for_status()
        return resp.json()

    def login(self, username: str, password: str) -> dict:
        payload = {"username": username, "password": password}
        resp = requests.post(f"{self.base_url}/auth/login", json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        self.access_token = data.get("access_token")
        self.refresh_token = data.get("refresh_token")
        return data

    def logout(self) -> dict:
        payload = {"refresh_token": self.refresh_token}
        resp = requests.post(f"{self.base_url}/auth/logout", json=payload, timeout=10)
        resp.raise_for_status()
        self.access_token = None
        self.refresh_token = None
        return resp.json()

    def refresh_access_token(self) -> dict:
        payload = {"refresh_token": self.refresh_token}
        resp = requests.post(f"{self.base_url}/auth/refresh", json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        self.access_token = data.get("access_token")
        self.refresh_token = data.get("refresh_token", self.refresh_token)
        return data

    def get_me(self) -> dict:
        headers = {"Authorization": f"Bearer {self.access_token}"}
        resp = requests.get(f"{self.base_url}/auth/me", headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
