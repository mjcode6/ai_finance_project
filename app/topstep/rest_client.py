# app/topstep/rest_client.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("TOPSTEP_BASE_URL", "https://api.topstepx.com")
USERNAME = os.getenv("TOPSTEP_USERNAME")
API_KEY = os.getenv("TOPSTEP_API_KEY")


class TopstepRESTClient:
    def __init__(self):
        self.session_token = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def login(self):
        """Login and get session token"""
        url = f"{BASE_URL}/api/Auth/loginKey"
        payload = {"userName": USERNAME, "apiKey": API_KEY}

        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            self.session_token = data.get("token")
            if self.session_token:
                print("✅ Login successful. Session token acquired.")
                return self.session_token
            else:
                print("❌ Login failed: No token received")
                return None
        except requests.HTTPError as e:
            print("HTTP Error ❌", e)
        except Exception as e:
            print("Login request failed ❌", e)
        return None

    def get_active_accounts(self):
        """Return a list of active accounts"""
        url = f"{BASE_URL}/api/Account/search"
        payload = {"onlyActiveAccounts": True}
        headers = {**self.headers, "Authorization": f"Bearer {self.session_token}"}

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("accounts", [])
        except Exception as e:
            print("❌ Failed to fetch accounts:", e)
            return []
