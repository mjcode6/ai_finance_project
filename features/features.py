# features/features.py
# Day 2: Feature Extraction (project-folder safe)

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# --- 1️⃣ Set project-folder paths ---
# Everything stays inside ai_finance_project folder
RAW_FOLDER = "../data/raw"
PROCESSED_FOLDER = "../data/processed"

raw_csv_path = os.path.join(RAW_FOLDER, "all_market_data.csv")
processed_csv_path = os.path.join(PROCESSED_FOLDER, "market_features.csv")

# --- 2️⃣ Ensure folders exist ---
os.makedirs(RAW_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# --- 3️⃣ Load raw CSV with multi-level columns ---
if not os.path.exists(raw_csv_path):
    raise FileNotFoundError(f"{raw_csv_path} not found. Run Day 1 script to fetch data first.")

data = pd.read_csv(raw_csv_path, header=[0,1], index_col=0, parse_dates=True)
print("Raw data loaded ✅")
print(f"Tickers in CSV: {data['Close'].columns.tolist()}")

# --- 4️⃣ Extract tickers dynamically from 'Close' column ---
tickers = data['Close'].columns.tolist()

# --- 5️⃣ Create feature DataFrame ---
features = pd.DataFrame(index=data.index)

for ticker in tickers:
    close = data['Close'][ticker]

    # Daily returns
    features[f'{ticker}_daily_return'] = close.pct_change(fill_method=None)
    
    # 14-day rolling volatility
    features[f'{ticker}_volatility_14d'] = close.pct_change(fill_method=None).rolling(window=14).std()
    
    # 14-day momentum
    features[f'{ticker}_momentum_14d'] = close - close.shift(14)

# --- 6️⃣ Handle NaNs ---
features = features.dropna()  # drop initial rows with incomplete rolling window

# --- 7️⃣ Save features CSV ---
features.to_csv(processed_csv_path)
print(f"Features saved to {os.path.abspath(processed_csv_path)} ✅")

# --- 8️⃣ Optional: visualize a sample feature ---
plt.figure(figsize=(12,6))
plt.plot(features['BTC-USD_daily_return'], label='BTC-USD Daily Return')
plt.title('BTC-USD Daily Return')
plt.xlabel('Date')
plt.ylabel('Return')
plt.legend()
plt.show()
