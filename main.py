import yfinance as yf
import pandas as pd

# Premium Picks — $15
premium_picks = [
    "AAPL",  # Apple
    "MSFT",  # Microsoft
    "GOOGL", # Alphabet
    "AMZN",  # Amazon
    "NVDA",  # NVIDIA
    "META",  # Meta Platforms
    "BRK.B", # Berkshire Hathaway
    "JPM",   # JPMorgan Chase
    "XOM",   # Exxon Mobil
    "JNJ",   # Johnson & Johnson
    "V",     # Visa
    "PG"     # Procter & Gamble
]

# Mid-Tier — $10
mid_tier = [
    "ABNB",  # Airbnb
    "SHOP",  # Shopify
    "NFLX",  # Netflix
    "TSLA",  # Tesla
    "AMD",   # Advanced Micro Devices
    "CRM",   # Salesforce
    "UBER",  # Uber
    "ADBE",  # Adobe
    "INTC",  # Intel
    "QCOM",  # Qualcomm
    "SPOT",  # Spotify
    "SBUX"   # Starbucks
]

# Wildcards — $5
wildcards = [
    "PLTR",  # Palantir
    "SNAP",  # Snap
    "COIN",  # Coinbase
    "RBLX",  # Roblox
    "ROKU",  # Roku
    "ZM",    # Zoom
    "SQ",    # Block
    "TWLO",  # Twilio
    "PINS",  # Pinterest
    "DKNG",  # DraftKings
    "ETSY",  # Etsy
    "U"      # Unity Software
]

# Risky Plays — $3
risky_plays = [
    "BA",    # Boeing
    "PTON",  # Peloton
    "GME",   # GameStop
    "AMC",   # AMC Entertainment
    "PYPL",  # PayPal
    "LYFT",  # Lyft
    "BYND",  # Beyond Meat
    "HOOD",  # Robinhood
    "LCID",  # Lucid
    "RIVN",  # Rivian
    "WBD",   # Warner Bros Discovery
    "PARA"   # Paramount Global
]

