# app/topstep/market_data.py

import time
import pandas as pd
from client import TopstepClient

class MarketData:
    """
    Fetch live futures market data via TopstepClient
    and generate features for ML model.
    """

    def __init__(self, tickers, client: TopstepClient):
        """
        tickers: list of futures symbols, e.g., ["NQ=F", "ES=F"]
        client: an instance of TopstepClient
        """
        self.tickers = tickers
        self.client = client
        # Store price history for each ticker
        self.data = {ticker: pd.DataFrame() for ticker in tickers}

    def fetch_price(self, ticker):
        """
        Fetch the latest price for a ticker.
        Update this endpoint according to Topstep docs for futures.
        """
        endpoint = f"/api/MarketData/latest/{ticker}"  # Placeholder
        price_data = self.client.get(endpoint)
        if price_data:
            return {
                "symbol": ticker,
                "price": price_data.get("lastPrice"),
                "timestamp": price_data.get("timestamp")
            }
        return None

    def update_data(self):
        """
        Update internal DataFrames with latest price for each ticker.
        """
        for ticker in self.tickers:
            price_point = self.fetch_price(ticker)
            if price_point:
                df = self.data[ticker]
                self.data[ticker] = pd.concat([df, pd.DataFrame([price_point])], ignore_index=True)
                print(f"📈 Updated {ticker}: {price_point['price']} at {price_point['timestamp']}")

    def generate_features(self, ticker):
        """
        Convert price history into ML features.
        Example: returns, moving averages.
        """
        df = self.data[ticker]
        if df.empty:
            return None

        # Simple example features
        df["returns"] = df["price"].pct_change()
        df["ma5"] = df["price"].rolling(5).mean()
        df["ma10"] = df["price"].rolling(10).mean()

        # Return latest feature row
        latest_features = df.iloc[-1][["price", "returns", "ma5", "ma10"]].to_dict()
        return latest_features

    def get_live_features(self):
        """
        Fetch latest prices for all tickers and return features for ML.
        """
        self.update_data()
        features = {}
        for ticker in self.tickers:
            feat = self.generate_features(ticker)
            if feat:
                features[ticker] = feat
        return features


# --------------------------
# Example usage
# --------------------------
if __name__ == "__main__":
    tickers = ["NQ=F", "ES=F"]  # Example futures tickers
    client = TopstepClient()
    market = MarketData(tickers, client)

    # Continuous live fetching
    while True:
        features = market.get_live_features()
        print("Live features:", features)
        time.sleep(5)  # fetch every 5 seconds
