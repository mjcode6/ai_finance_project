# app/topstep/client.py

import os
import requests
from dotenv import load_dotenv

# ------------------------------
# Load .env configuration
# ------------------------------
load_dotenv()
BASE_URL = os.getenv("TOPSTEP_BASE_URL")
USERNAME = os.getenv("TOPSTEP_USERNAME")
API_KEY = os.getenv("TOPSTEP_API_KEY")

if not BASE_URL or not USERNAME or not API_KEY:
    raise ValueError(
        "❌ Please set TOPSTEP_BASE_URL, TOPSTEP_USERNAME, and TOPSTEP_API_KEY in .env"
    )


class TopstepClient:
    """
    Topstep / ProjectX API client
    """

    def __init__(self, base_url=BASE_URL, username=USERNAME, api_key=API_KEY):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.api_key = api_key
        self.session_token = None
        self.login()

    def login(self):
        """
        Authenticate with Topstep API and store session token.
        """
        login_url = f"{self.base_url}/api/Auth/loginKey"  # adjust if demo endpoint differs
        payload = {"userName": self.username, "apiKey": self.api_key}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            response = requests.post(login_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Debug output
            print("Login response:", data)

            if data.get("success") and data.get("token"):
                self.session_token = data["token"]
                print("✅ Login successful. Session token acquired.")
            else:
                print("⚠️ Login failed or token not returned:", data)

        except requests.exceptions.HTTPError as http_err:
            print("HTTP Error ❌", http_err)
            print("Response:", response.text)
        except requests.exceptions.RequestException as req_err:
            print("Request Error ❌", req_err)

    def get(self, endpoint: str, params: dict = None):
        """
        Generic GET request with session token
        """
        if not self.session_token:
            print("⚠️ No session token — please login first")
            return None

        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.session_token}", "Accept": "application/json"}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ GET request failed for {url}:", e)
            return None

    def post(self, endpoint: str, body: dict = None):
        """
        Generic POST request with session token
        """
        if not self.session_token:
            print("⚠️ No session token — please login first")
            return None

        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.session_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, json=body, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ POST request failed for {url}:", e)
            return None

    # ------------------------------
    # Example utility methods
    # ------------------------------
    def get_accounts(self):
        """
        Fetch all active accounts
        """
        return self.post("/api/Account/search", body={"onlyActiveAccounts": True})

    def get_available_contracts(self, live=True):
        """
        Fetch all available futures contracts
        """
        return self.post("/api/Contract/available", body={"live": live})

    def place_order(self, account_id, contract_id, order_type, side, size):
        """
        Place an order via Topstep API
        """
        body = {
            "accountId": account_id,
            "contractId": contract_id,
            "type": order_type,
            "side": side,
            "size": size
        }
        return self.post("/api/Order/place", body=body)


# ------------------------------
# Test when run directly
# ------------------------------
if __name__ == "__main__":
    client = TopstepClient()
    accounts = client.get_accounts()
    print("Accounts:", accounts)
