import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 1️⃣ Load tickers dynamically
# You can update tickers.csv with any instrument
try:
    tickers_df = pd.read_csv("../tickers.csv")  # CSV should have one column: Symbol
    tickers = tickers_df['Symbol'].tolist()
except FileNotFoundError:
    print("tickers.csv not found, using default tickers")
    tickers = ["SPY", "NQ=F", "BTC-USD", "EURUSD=X"]  # default fallback

# 2️⃣ Download last 10 years of daily data for all tickers
print(f"Fetching data for {len(tickers)} tickers...")
data = yf.download(tickers, period="10y", interval="1d")

import os

# Get folder where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define raw folder inside project
raw_folder = os.path.join(script_dir, "../data/raw")
os.makedirs(raw_folder, exist_ok=True)

# Save CSV in correct place
csv_path = os.path.join(raw_folder, "all_market_data.csv")
data.to_csv(csv_path)
print(f"Data saved to {csv_path} ✅")



# 4️⃣ Show first 5 rows
print("First 5 rows of market data:\n")
print(data.head())

# 5️⃣ Plot closing prices for all tickers
plt.figure(figsize=(12,6))
for ticker in tickers:
    plt.plot(data['Close'][ticker], label=ticker)

plt.title("Closing Prices – Last 6 Months")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.show()

