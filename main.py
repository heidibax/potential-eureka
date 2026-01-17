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
        "revenue": {
            "beat": 7,
            "miss": -5
        },
        "guidance": {
            "raised": 8,
            "maintained": 2,
            "lowered": -6
        },
        "bonus": {
            "perfect_quarter_multiplier": 2,
            "surprise_superstar": 20,
            "comeback_kid": 15,
            "disaster": -25
        }
    }
    
# SCORING LOGIC FOR EARNINGS SEASON 

# Date Estimator
def get_company_season(latest_earnings_date):
    today = datetime.now().date()
    earnings_date = datetime.strptime(latest_earnings_date, "%Y-%m-%d").date()

    if earnings_date <= today:
        return "earnings_season"

    return "portfolio_season"


# Scoring Functions
def score_eps(actual, estimate):
    if actual > estimate:
        return POINTS["eps"]["beat"], "beat"
    elif actual < estimate:
        return POINTS["eps"]["miss"], "miss"
    else:
        return POINTS["eps"]["meet"], "meet"

def score_revenue(actual, estimate):
    if estimate is None or actual is None:
        return 0, "unknown"
    if actual > estimate:
        return POINTS["revenue"]["beat"], "beat"
    else:
        return POINTS["revenue"]["miss"], "miss"

def infer_guidance(current_estimate, previous_estimate):
    if current_estimate is None or previous_estimate is None:
        return 0, "unknown"

    if current_estimate > previous_estimate:
        return POINTS["guidance"]["raised"], "raised"
    elif current_estimate < previous_estimate:
        return POINTS["guidance"]["lowered"], "lowered"
    else:
        return POINTS["guidance"]["maintained"], "maintained"

def score_bonuses(eps_result, rev_result, guidance_result,
                  eps_surprise_pct, eps_history):

    bonus = 0
    tags = []

    # Perfect Quarter
    if eps_result == "beat" and rev_result == "beat" and guidance_result == "raised":
        tags.append("perfect_quarter")

    # Surprise Superstar (computed surprise)
    if eps_surprise_pct is not None and eps_surprise_pct > 20:
        bonus += POINTS["bonus"]["surprise_superstar"]
        tags.append("surprise_superstar")

    # Comeback Kid (requires 3+ quarters of EPS history)
    if len(eps_history) >= 3:
        if eps_history[1] == "miss" and eps_history[2] == "miss" and eps_result == "beat":
            bonus += POINTS["bonus"]["comeback_kid"]
            tags.append("comeback_kid")

    # Disaster Quarter
    if eps_result == "miss" and rev_result == "miss" and guidance_result == "lowered":
        bonus += POINTS["bonus"]["disaster"]
        tags.append("disaster")

    return bonus, tags

def score_company_yf(
    ticker,
    earnings_rows,        # list of dicts from yfinance
    analyst_estimates     # list of forward EPS estimates
):
    latest = earnings_rows[0]
    season = get_company_season(latest["date"])

    if season == "portfolio_season":
        return {
            "ticker": ticker,
            "season": "portfolio_season",
            "score": 0,
            "details": "Awaiting earnings"
        }

    # EPS
    eps_score, eps_result = score_eps(
        latest["actual_eps"],
        latest["estimated_eps"]
    )

    # Guidance (proxy)
    guidance_score, guidance_result = infer_guidance(
        analyst_estimates[0] if len(analyst_estimates) > 0 else None,
        analyst_estimates[1] if len(analyst_estimates) > 1 else None
    )

    # EPS history for bonuses
    eps_history = [
        "beat" if r["actual_eps"] > r["estimated_eps"] else "miss"
        for r in earnings_rows[:3]
        if r["actual_eps"] is not None and r["estimated_eps"] is not None
    ]

    bonus_score, bonus_tags = score_bonuses(
        eps_result,
        guidance_result,
        latest.get("surprise_pct"),
        eps_history
    )

    total = eps_score + guidance_score + bonus_score

    if "perfect_quarter" in bonus_tags:
        total *= POINTS["bonus"]["perfect_quarter_multiplier"]

    return {
        "ticker": ticker,
        "season": "earnings_season",
        "score": total,
        "breakdown": {
            "eps": eps_score,
            "bonus": bonus_score,
            "tags": bonus_tags
        }
    }

def eps_outcome(actual, estimate):
    if actual > estimate:
        return "beat"
    elif actual < estimate:
        return "miss"
    else:
        return "meet"


def points_from_reaction_move(pct):
    if pct>.05:
        return 10
    elif pct>.02:
        return 5
    elif pct<= -.1:
        return -15
    elif pct<= -.05:
        return -8
    return 0

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
    change_in_points = points_from_reaction_move(pct_change)
    #print(f"{t}: {prev_date} open {prev_open} -> {curr_date} open {curr_open}, pct change {pct_change:.2%}, points change {change_in_points}")
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

    return pct_change

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
        monthly_pct_change = price_change_1month(ticker)

        eps_result = eps_outcome(actual_eps, est_eps)

        bonus_tags = []
        if surprise_pct is not None and surprise_pct > 20:
            bonus_tags.append("surprise_superstar")

        results.append(
            {
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


