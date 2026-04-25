"""
prices.py

This module creates simulated current market prices and checks market data health.
Current prices are intentionally different from trade prices to simulate market movement.
"""

import random
from datetime import datetime, timedelta

import pandas as pd


BASE_MARKET_PRICES = {
    "AAPL": 187.50,
    "MSFT": 414.25,
    "SPY": 522.80,
    "TSLA": 171.40,
    "NVDA": 889.75,
}

PRICE_FEED_TEMPLATE = {
    "AAPL": {"age_minutes": 2, "availability": "available"},
    "MSFT": {"age_minutes": 4, "availability": "available"},
    "SPY": {"age_minutes": 22, "availability": "available"},
    "TSLA": {"age_minutes": 6, "availability": "available"},
    "NVDA": {"age_minutes": None, "availability": "unavailable"},
}


def generate_current_prices(instruments, seed=99):
    """
    Generate current market prices for each instrument.

    Plain English:
    Trading operations teams compare trade records and positions against
    current market prices to estimate profit and loss. This function creates
    fake current prices and a simple last-updated timestamp so the project can
    also monitor whether the pricing tool looks healthy.
    """
    random.seed(seed)
    now = datetime.now().replace(second=0, microsecond=0)
    price_rows = []

    for instrument in instruments:
        base_price = BASE_MARKET_PRICES.get(instrument)
        feed_template = PRICE_FEED_TEMPLATE.get(
            instrument,
            {"age_minutes": 5, "availability": "available"},
        )

        if base_price is None or feed_template["availability"] == "unavailable":
            current_price = None
            last_updated = None
        else:
            current_price = round(base_price + random.uniform(-2.50, 2.50), 2)
            last_updated = now - timedelta(minutes=feed_template["age_minutes"])

        price_rows.append({
            "instrument": instrument,
            "current_price": current_price,
            "last_updated": last_updated,
        })

    return pd.DataFrame(price_rows)


def build_market_data_health_report(prices_df, stale_after_minutes=15):
    """
    Check whether price data is healthy, stale, or unavailable.

    Plain English:
    A pricing tool is only useful if prices arrive on time. This report shows
    whether each instrument has a live-looking price, an old price, or no
    usable price at all.
    """
    now = datetime.now().replace(second=0, microsecond=0)
    health_rows = []

    for _, row in prices_df.iterrows():
        current_price = row["current_price"]
        last_updated = row["last_updated"]

        if pd.isna(current_price):
            market_data_status = "Unavailable"
            minutes_since_update = None
            issue = "No price was returned from the pricing tool."
            last_updated_display = "Not available"
        else:
            last_updated_timestamp = pd.to_datetime(last_updated)
            minutes_since_update = int(
                (now - last_updated_timestamp.to_pydatetime()).total_seconds() // 60
            )
            last_updated_display = last_updated_timestamp.strftime("%Y-%m-%d %H:%M")

            if minutes_since_update > stale_after_minutes:
                market_data_status = "Stale"
                issue = f"Price update is {minutes_since_update} minutes old."
            else:
                market_data_status = "Healthy"
                issue = "Price feed looks current."

        health_rows.append({
            "instrument": row["instrument"],
            "current_price": current_price,
            "last_updated": last_updated_display,
            "minutes_since_update": minutes_since_update,
            "market_data_status": market_data_status,
            "issue": issue,
        })

    return pd.DataFrame(health_rows).sort_values("instrument").reset_index(drop=True)


if __name__ == "__main__":
    # This lets you run: python prices.py
    prices = generate_current_prices(["AAPL", "MSFT", "SPY", "TSLA", "NVDA"])
    print(prices)
    print(build_market_data_health_report(prices))
