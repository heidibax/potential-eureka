import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

from zoneinfo import ZoneInfo
ET = ZoneInfo("America/New_York")

import sys

# Premium Picks — $15
premium_picks = [
    "AAPL",  # Apple
    "MSFT",  # Microsoft
    "GOOGL", # Alphabet
    "AMZN",  # Amazon
    "NVDA",  # NVIDIA
    "META",  # Meta Platforms
    "BRK-B", # Berkshire Hathaway
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
    "CRWD",  # CrowdStrike
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
    "CVNA",  # Carvana
]
COMPANIES = premium_picks + mid_tier + wildcards + risky_plays
POINTS = {
        "eps": {
            "beat": 10,
            "meet": 3,
            "miss": -8
        },
        "bonus": {
            "surprise_superstar": 20,
            "comeback_kid": 15,
        },
        "daily_change": {
            "big_increase": 10,
            "small_increase": 5,
            "big_decrease": -15,
            "small_decrease": -8,
            "no_change": 0  
        },
        "monthly_change": {
            "big_increase": 15,
            "small_increase": 7,
            "big_decrease": -20,
            "small_decrease": -12,
            "no_change": 0  
        }
    }
    
# Determine EPS outcome

def eps_outcome(actual, estimate):
    if actual > estimate:
        return "beat"
    elif actual < estimate:
        return "miss"
    else:
        return "meet"

def score_company_game(row):
    """
    Input: one row from results (dict)
    Output: dict with score breakdown
    """

    score = 0
    breakdown = {}

    # EPS base score
    eps_result = row["eps_result"]
    eps_score = POINTS["eps"][eps_result]
    score += eps_score
    breakdown["eps"] = eps_score

    #Price change scores
    daily_change_score = stock_market_reaction(row["ticker"])[1]
    monthly_change_score = price_change_1month(row["ticker"])[1]

    price_change_bonus = POINTS["daily_change"][daily_change_score]+ POINTS["monthly_change"][monthly_change_score]
    
    breakdown["daily percent change"] = POINTS["daily_change"][daily_change_score]
    breakdown["monthly percent change"] = POINTS["monthly_change"][monthly_change_score]

    # Bonus: Surprise Superstar
    bonus = 0
    if row["surprise_pct"] is not None and row["surprise_pct"] > 20:
        bonus += POINTS["bonus"]["surprise_superstar"]

    score += bonus
    score += price_change_bonus
    breakdown["bonus"] = bonus

    return {
        "ticker": row["ticker"],
        "game_score": score,
        "eps_result": eps_result,
        "surprise_pct": row["surprise_pct"],
        "breakdown": breakdown
    }

def points_from_percent_change(pct):
    if pct>.05:
        return "big_increase"
    elif pct>.02:
        return "small_increase"
    elif pct<= -.1:
        return "big_decrease"
    elif pct<= -.05:
        return "small_decrease"
    return "no_change"


def stock_open_prices_last2days(ticker):
    today = datetime.now(ET).date()
    df = yf.download(
        ticker, 
        start = pd.Timestamp(today - timedelta(days=10)), #buffer in case weekend/market holiday
        end = pd.Timestamp(today + timedelta(days=1)),
        interval = "1d",
        progress = False
    )

    #if df is None or df.empty():
        #raise HTTPException(status_code=400, detail = "No stock data")
    

    df = df.sort_index()
    df.index = pd.to_datetime(df.index).date

    df = df[df.index <= today]

    #if len(df) < 2:
        #raise HTTPException(status_code=400, detail = "No two days of stock data")
    
    prev_date = df.index[-2]
    curr_date = df.index[-1]

    prev_open = float(df.loc[prev_date, "Open"].iloc[0])
    curr_open = float(df.loc[curr_date, "Open"].iloc[0])

    return prev_date, prev_open, curr_date, curr_open
    
def stock_market_reaction(ticker):
    prev_date, prev_open, curr_date, curr_open = stock_open_prices_last2days(ticker)
    pct_change = (float)((curr_open-prev_open)/prev_open)
    change_in_points = points_from_percent_change(pct_change)
    return pct_change, change_in_points


#get historical price
def price_change_1month(ticker):
    today = datetime.now(ET).date()
    df = yf.download(
        ticker, 
        start = pd.Timestamp(today - timedelta(days=31)), 
        end = pd.Timestamp(today + timedelta(days=1)),
        interval = "1d",
        progress = False
    )

    #if df is None or df.empty():
        #raise HTTPException(status_code=400, detail = "No stock data")
    

    df = df.sort_index()
    df.index = pd.to_datetime(df.index).date

    df = df[df.index <= today]

    start_date = df.index[0]
    curr_date = df.index[-1]

    start_open = float(df.loc[start_date, "Open"].iloc[0])
    curr_open = float(df.loc[curr_date, "Open"].iloc[0])

    pct_change = (curr_open - start_open)/start_open

    change_in_points = points_from_percent_change(pct_change)
    return pct_change, change_in_points

results = []
for ticker in COMPANIES:
    try:
        yt = yf.Ticker(ticker)

        # --- Earnings history ---
        eh = yt.earnings_history
        if eh is None or eh.empty:
            print(f"Skipping {ticker}, no earnings data.")
            continue

        row = eh.iloc[0]  # most recent quarter

        actual_eps = (
            row.get("epsActual")
            if "epsActual" in row
            else row.get("Reported EPS", None)
        )

        est_eps = (
            row.get("epsEstimate")
            if "epsEstimate" in row
            else row.get("Earnings Estimate", None)
        )

        earnings_date = row.name.strftime("%Y-%m-%d")

        if pd.isna(actual_eps) or pd.isna(est_eps):
            print(f"Skipping {ticker}, missing EPS.")
            continue

        surprise_pct = None
        if est_eps != 0:
            surprise_pct = ((actual_eps - est_eps) / abs(est_eps)) * 100

        earnings_rows = [{
            "date": earnings_date,
            "actual_eps": actual_eps,
            "estimated_eps": est_eps,
            "surprise_pct": surprise_pct
        }]

        daily_pct_change = stock_market_reaction(ticker)[0]
        monthly_pct_change = price_change_1month(ticker)[0]

        eps_result = eps_outcome(actual_eps, est_eps)

        bonus_tags = []
        if surprise_pct is not None and surprise_pct > 20:
            bonus_tags.append("surprise_superstar")

        results.append(
            {
                "stock name": yt.info.get("shortName", "N/A"),
                "ticker": ticker,
                "earnings_date": earnings_date,
                "eps_estimate": float(est_eps),
                "eps_actual": float(actual_eps),
                "eps_result": eps_result,          # beat / miss / meet
                "surprise_pct": surprise_pct,
                "bonus_flags": bonus_tags,          # informational only
                "daily_pct_change" : daily_pct_change,
                "monthly_price_change": monthly_pct_change
            }
        )

    except Exception as e:
        print(f"Error processing {ticker}: {e}")

if not results: 
    print("No results to display.")
    sys.exit(0)

df = pd.DataFrame(results)
print(df.to_string(index=False))

# SCORING RESULTS

game_results = []

for row in results:
    game_score = score_company_game(row)
    game_results.append(game_score)

game_df = pd.DataFrame(game_results)
game_df = game_df.sort_values(by="game_score", ascending=False)

print("\n GAME SCORING (per company)")
print(game_df.to_string(index=False))