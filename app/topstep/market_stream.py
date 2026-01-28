# app/topstep/market_stream.py

import os
import sys
import time
import csv
import logging
from datetime import datetime
from dotenv import load_dotenv
from signalrcore.hub_connection_builder import HubConnectionBuilder

# Fix import path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from rest_client import TopstepRESTClient

# ===== Config =====
MARKET_HUB_URL = "https://rtc.topstepx.com/hubs/market"
RECONNECT_DELAY = 5  # seconds
MARKET_FIELDS = ["LastPrice", "Bid", "Ask", "Volume"]
CSV_FILE = os.path.join(current_dir, "live_market_data.csv")

# Hardcoded active contracts
TARGET_CONTRACTS = [
    {"symbolId": "F.US.ES", "name": "E-mini S&P"},
    {"symbolId": "F.US.NQ", "name": "E-mini Nasdaq-100"},
    {"symbolId": "F.US.GC", "name": "Gold Futures"},
]

hub_connection = None
client = None

# ===== Load .env =====
load_dotenv()

# ===== CSV setup =====
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Symbol", "LastPrice", "Bid", "Ask", "Volume"])

# ===== Hub callbacks =====
def on_open():
    print("✅ Connected to TopstepX Market Hub")
    time.sleep(0.5)
    for contract in TARGET_CONTRACTS:
        payload = {"symbols": [contract["symbolId"]], "fields": MARKET_FIELDS}
        hub_connection.send("SubscribeSymbols", [payload])
        print(f"📡 Subscribed to {contract['symbolId']} ({contract['name']})")


def on_close():
    print(f"❌ Disconnected from Market Hub. Reconnecting in {RECONNECT_DELAY}s...")
    time.sleep(RECONNECT_DELAY)
    reconnect()


def on_error(error):
    print("❌ Hub Error:", error)


def on_market_data(message):
    # Example message: {'Symbol': 'F.US.ES', 'LastPrice': 4390.25, 'Bid': 4390.0, 'Ask': 4390.5, 'Volume': 10}
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    symbol = message.get("Symbol")
    last = message.get("LastPrice")
    bid = message.get("Bid")
    ask = message.get("Ask")
    volume = message.get("Volume")

    print(f"{timestamp} | {symbol} | Last:{last} Bid:{bid} Ask:{ask} Vol:{volume}")

    # Log to CSV
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, symbol, last, bid, ask, volume])


def reconnect():
    global hub_connection
    hub_connection.start()


# ===== Main streaming logic =====
def start_market_stream(token):
    global hub_connection, client

    client.session_token = token
    accounts = client.get_active_accounts()
    if not accounts:
        print("❌ No active accounts found.")
        return
    account_id = accounts[0]["id"]
    print(f"✅ Active account ID: {account_id}")

    hub_connection = (
        HubConnectionBuilder()
        .with_url(
            MARKET_HUB_URL,
            options={
                "access_token_factory": lambda: token,
                "headers": {"User-Agent": "PythonSignalRClient"},
                "keep_alive_interval": 15,
            },
        )
        .configure_logging(logging_level="INFO")
        .build()
    )

    hub_connection.on_open(on_open)
    hub_connection.on_close(on_close)
    hub_connection.on_error(on_error)
    hub_connection.on("MarketData", on_market_data)

    hub_connection.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Stopping market stream...")
        hub_connection.stop()


# ===== Run =====
if __name__ == "__main__":
    client = TopstepRESTClient()
    token = client.login()

    if token:
        print("✅ Starting stable live market stream for ES, NQ, Gold contracts...")
        start_market_stream(token)
    else:
        print("❌ Cannot start market stream without session token")
