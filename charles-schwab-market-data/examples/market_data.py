"""
Working examples for all Charles Schwab Market Data Production API endpoints.

Requires: schwab-py, pandas, python-dotenv
Run schwab_auth.py first to generate config/schwab_token.json.
"""
import datetime
import pandas as pd
from schwab.client import Client
from schwab_client import get_client

client = get_client()


# ---------------------------------------------------------------------------
# Quotes
# ---------------------------------------------------------------------------

def single_quote(symbol: str) -> dict:
    resp = client.get_quote(symbol)
    resp.raise_for_status()
    data = resp.json()
    q = data[symbol]["quote"]
    return {
        "last": q["lastPrice"],
        "bid": q["bidPrice"],
        "ask": q["askPrice"],
        "volume": q["totalVolume"],
    }


def batch_quotes(symbols: list[str]) -> dict[str, float]:
    """Return last price for each symbol in the list."""
    resp = client.get_quotes(symbols)
    resp.raise_for_status()
    data = resp.json()
    return {sym: data[sym]["quote"]["lastPrice"] for sym in symbols if sym in data}


# ---------------------------------------------------------------------------
# Price History
# ---------------------------------------------------------------------------

def daily_ohlcv(symbol: str, days: int = 365) -> pd.DataFrame:
    """Fetch daily OHLCV candles as a DataFrame indexed by date."""
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=days)

    resp = client.get_price_history(
        symbol,
        period_type=Client.PriceHistory.PeriodType.YEAR,
        frequency_type=Client.PriceHistory.FrequencyType.DAILY,
        frequency=Client.PriceHistory.Frequency.DAILY,
        start_datetime=start,
        end_datetime=end,
        need_extended_hours_data=False,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("empty") or not data.get("candles"):
        raise ValueError(f"No price history available for {symbol!r}")

    df = pd.DataFrame(data["candles"])
    df.index = pd.to_datetime(df["datetime"], unit="ms")
    df.index.name = None
    return (
        df[["open", "high", "low", "close", "volume"]]
        .rename(columns={"open": "Open", "high": "High", "low": "Low",
                          "close": "Close", "volume": "Volume"})
        .dropna()
    )


def intraday_ohlcv(symbol: str, frequency_minutes: int = 5) -> pd.DataFrame:
    """Fetch intraday candles for the last 10 days."""
    freq_map = {
        1: Client.PriceHistory.Frequency.EVERY_MINUTE,
        5: Client.PriceHistory.Frequency.EVERY_FIVE_MINUTES,
        10: Client.PriceHistory.Frequency.EVERY_TEN_MINUTES,
        15: Client.PriceHistory.Frequency.EVERY_FIFTEEN_MINUTES,
        30: Client.PriceHistory.Frequency.EVERY_THIRTY_MINUTES,
    }
    if frequency_minutes not in freq_map:
        raise ValueError(f"frequency_minutes must be one of {list(freq_map)}")

    resp = client.get_price_history(
        symbol,
        period_type=Client.PriceHistory.PeriodType.DAY,
        period=10,
        frequency_type=Client.PriceHistory.FrequencyType.MINUTE,
        frequency=freq_map[frequency_minutes],
        need_extended_hours_data=False,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("empty") or not data.get("candles"):
        raise ValueError(f"No intraday data for {symbol!r}")

    df = pd.DataFrame(data["candles"])
    df.index = pd.to_datetime(df["datetime"], unit="ms")
    df.index.name = None
    return (
        df[["open", "high", "low", "close", "volume"]]
        .rename(columns={"open": "Open", "high": "High", "low": "Low",
                          "close": "Close", "volume": "Volume"})
    )


# ---------------------------------------------------------------------------
# Options Chain
# ---------------------------------------------------------------------------

def options_chain(
    symbol: str,
    dte_max: int = 45,
    strike_count: int = 20,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Return (calls_df, puts_df) DataFrames for the nearest expiry within dte_max days.
    Columns: strike, bid, ask, openInterest, impliedVolatility, delta, gamma, theta, vega
    """
    resp = client.get_option_chain(
        symbol,
        contract_type=Client.Options.ContractType.ALL,
        strike_count=strike_count,
        include_underlying_quote=True,
        from_date=datetime.date.today(),
        to_date=datetime.date.today() + datetime.timedelta(days=dte_max),
    )
    resp.raise_for_status()
    data = resp.json()

    call_map = data.get("callExpDateMap", {})
    put_map = data.get("putExpDateMap", {})

    if not call_map:
        raise ValueError(f"No options data for {symbol!r}")

    def nearest(exp_map: dict) -> dict:
        key = min(exp_map, key=lambda k: int(k.split(":")[1]))
        return {key: exp_map[key]}

    def parse(exp_map: dict) -> pd.DataFrame:
        rows = []
        for strikes in exp_map.values():
            for strike_str, contracts in strikes.items():
                c = contracts[0]
                raw_vol = c.get("volatility", -1)
                try:
                    iv = float(raw_vol) / 100.0 if float(raw_vol) > 0 else float("nan")
                except (TypeError, ValueError):
                    iv = float("nan")
                rows.append({
                    "strike": float(strike_str),
                    "bid": float(c.get("bid") or 0.0),
                    "ask": float(c.get("ask") or 0.0),
                    "openInterest": int(c.get("openInterest") or 0),
                    "impliedVolatility": iv,
                    "delta": c.get("delta"),
                    "gamma": c.get("gamma"),
                    "theta": c.get("theta"),
                    "vega": c.get("vega"),
                })
        return pd.DataFrame(rows) if rows else pd.DataFrame(
            columns=["strike", "bid", "ask", "openInterest",
                     "impliedVolatility", "delta", "gamma", "theta", "vega"]
        )

    calls = parse(nearest(call_map)).reset_index(drop=True)
    puts  = parse(nearest(put_map)).reset_index(drop=True)
    return calls, puts


def atm_iv(symbol: str) -> float:
    """Return the at-the-money implied volatility (as a decimal) for the nearest expiry."""
    resp = client.get_option_chain(symbol, include_underlying_quote=True)
    resp.raise_for_status()
    data = resp.json()

    spot = data.get("underlying", {}).get("last")
    if spot is None or spot != spot:
        raise ValueError(f"Could not retrieve spot price for {symbol!r}")

    call_map = data.get("callExpDateMap", {})
    if not call_map:
        raise ValueError(f"No options data for {symbol!r}")

    nearest_key = min(call_map, key=lambda k: int(k.split(":")[1]))
    rows = []
    for strike_str, contracts in call_map[nearest_key].items():
        c = contracts[0]
        raw = c.get("volatility", -1)
        try:
            iv = float(raw) / 100.0 if float(raw) > 0 else float("nan")
        except (TypeError, ValueError):
            iv = float("nan")
        rows.append({"strike": float(strike_str), "iv": iv,
                     "dist": abs(float(strike_str) - spot)})

    df = pd.DataFrame(rows).dropna(subset=["iv"])
    if df.empty:
        raise ValueError(f"No valid IV in options chain for {symbol!r}")
    return float(df.sort_values("dist").iloc[0]["iv"])


# ---------------------------------------------------------------------------
# Instruments
# ---------------------------------------------------------------------------

def search_symbol(query: str) -> list[dict]:
    resp = client.get_instruments(query, Client.Instrument.Projection.SYMBOL_SEARCH)
    resp.raise_for_status()
    return resp.json()


def get_fundamentals(symbol: str) -> dict:
    resp = client.get_instruments(symbol, Client.Instrument.Projection.FUNDAMENTAL)
    resp.raise_for_status()
    results = resp.json()
    if not results:
        raise ValueError(f"No fundamental data for {symbol!r}")
    return results[0].get("fundamental", {})


# ---------------------------------------------------------------------------
# Movers
# ---------------------------------------------------------------------------

def top_movers(index: str = "SPX", direction: str = "up", n: int = 10) -> list[dict]:
    index_map = {
        "SPX": Client.Movers.Index.SPX,
        "DJI": Client.Movers.Index.DJI,
        "COMPX": Client.Movers.Index.COMPX,
        "RUT": Client.Movers.Index.RUT,
    }
    sort_map = {
        "up": Client.Movers.SortOrder.PERCENT_CHANGE_UP,
        "down": Client.Movers.SortOrder.PERCENT_CHANGE_DOWN,
        "volume": Client.Movers.SortOrder.VOLUME,
    }
    resp = client.get_movers(
        index=index_map[index],
        sort_order=sort_map[direction],
        frequency=n,
    )
    resp.raise_for_status()
    return resp.json().get("screeners", [])


# ---------------------------------------------------------------------------
# Market Hours
# ---------------------------------------------------------------------------

def is_market_open(date: datetime.date = None) -> bool:
    """Return True if the equity market is open on the given date (default: today)."""
    resp = client.get_market_hours(
        markets=[Client.MarketHours.Market.EQUITY],
        date=date or datetime.date.today(),
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("equity", {}).get("EQ", {}).get("isOpen", False)


def market_session_times(date: datetime.date = None) -> dict:
    """Return pre-market, regular, and post-market open/close times."""
    resp = client.get_market_hours(
        markets=[Client.MarketHours.Market.EQUITY],
        date=date or datetime.date.today(),
    )
    resp.raise_for_status()
    data = resp.json()
    sessions = data.get("equity", {}).get("EQ", {}).get("sessionHours", {})
    return {
        "pre_market":     sessions.get("preMarket", [{}])[0],
        "regular_market": sessions.get("regularMarket", [{}])[0],
        "post_market":    sessions.get("postMarket", [{}])[0],
    }


# ---------------------------------------------------------------------------
# Quick smoke test — run this file directly to verify connectivity
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Testing Schwab Market Data API connectivity...\n")

    price = single_quote("SPY")
    print(f"SPY last price: ${price['last']:.2f}")

    prices = batch_quotes(["QQQ", "IWM"])
    for sym, p in prices.items():
        print(f"{sym}: ${p:.2f}")

    df = daily_ohlcv("SPY", days=5)
    print(f"\nSPY last 5 days:\n{df.tail()}\n")

    open_today = is_market_open()
    print(f"Market open today: {open_today}")

    movers = top_movers("SPX", direction="up", n=3)
    print(f"\nTop 3 SPX movers up:")
    for m in movers:
        print(f"  {m['symbol']}: +{m['netPercentChange']:.2f}%")
