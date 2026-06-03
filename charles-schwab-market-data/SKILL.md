---
name: charles-schwab-market-data
description: This skill should be used when the user asks to "use the Charles Schwab API", "fetch Schwab quotes", "get price history from Schwab", "query an options chain", "set up Schwab Market Data", "get market hours from Schwab", "search Schwab instruments", "get top movers", "connect to Schwab", or "integrate with Charles Schwab". Provides complete guidance for authenticating and calling the Schwab Market Data Production API using the schwab-py library.
version: 0.1.0
---

# Charles Schwab Market Data

## Overview

The Charles Schwab Market Data Production API provides real-time and historical equity, options, and market data. Access it via [schwab-py](https://github.com/alexgolec/schwab-py), an unofficial Python wrapper that handles OAuth 2.0 token management, request signing, and response parsing.

**Prerequisites:**
- A Charles Schwab brokerage account
- An app registered at [developer.schwab.com](https://developer.schwab.com) with the **Market Data Production** API product enabled
- App Key and App Secret from the developer portal
- Python 3.10+ with `schwab-py` installed

---

## Installation

```bash
pip install schwab-py python-dotenv
```

---

## Environment Setup

Store credentials in a `.env` file (never commit this file):

```ini
SCHWAB_CLIENT_ID=your_app_key_here
SCHWAB_CLIENT_SECRET=your_app_secret_here
SCHWAB_REDIRECT_URI=https://127.0.0.1
SCHWAB_TOKEN_PATH=config/schwab_token.json
```

`SCHWAB_REDIRECT_URI` must exactly match the callback URL configured in your developer portal app. Use `https://127.0.0.1` for production apps; use `https://127.0.0.1:8182` only when the developer portal app is explicitly configured with that port.

For detailed developer portal setup and first-time token generation, see `references/auth-setup.md`.

---

## Client Initialization

Create a reusable client module (`schwab_client.py`):

```python
import os
import schwab
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client():
    global _client
    if _client is not None:
        return _client
    app_key    = os.environ["SCHWAB_CLIENT_ID"]
    app_secret = os.environ["SCHWAB_CLIENT_SECRET"]
    token_path = os.environ.get("SCHWAB_TOKEN_PATH", "config/schwab_token.json")
    callback   = os.environ.get("SCHWAB_REDIRECT_URI", "https://127.0.0.1")
    _client = schwab.auth.easy_client(
        api_key=app_key,
        app_secret=app_secret,
        callback_url=callback,
        token_path=token_path,
    )
    return _client
```

`easy_client` automatically refreshes the token from `token_path` on each call. No manual token management is needed after initial setup.

---

## Available Endpoints

| Category | Method | Purpose |
|---|---|---|
| **Quotes** | `get_quote(symbol)` | Single symbol real-time quote |
| **Quotes** | `get_quotes([symbols])` | Batch quotes (up to 500 symbols) |
| **Price History** | `get_price_history(symbol, ...)` | OHLCV candles with configurable range |
| **Options Chain** | `get_option_chain(symbol, ...)` | Full call/put chain with greeks and IV |
| **Instruments** | `get_instruments(symbol, projection)` | Symbol search and fundamentals |
| **Movers** | `get_movers(index)` | Top movers for a given index |
| **Market Hours** | `get_market_hours([markets], date)` | Open/close times per market type |

All methods return an `httpx.Response`. Always call `.raise_for_status()` before `.json()`.

---

## Core Patterns

### Quotes

```python
from schwab_client import get_client

client = get_client()

# Single quote
resp = client.get_quote("AAPL")
resp.raise_for_status()
data = resp.json()
last = data["AAPL"]["quote"]["lastPrice"]

# Batch quotes
resp = client.get_quotes(["SPY", "QQQ", "AAPL"])
resp.raise_for_status()
quotes = resp.json()
```

### Price History

```python
import datetime
from schwab.client import Client

end   = datetime.datetime.now()
start = end - datetime.timedelta(days=365)

resp = client.get_price_history(
    "SPY",
    period_type=Client.PriceHistory.PeriodType.YEAR,
    frequency_type=Client.PriceHistory.FrequencyType.DAILY,
    frequency=Client.PriceHistory.Frequency.DAILY,
    start_datetime=start,
    end_datetime=end,
    need_extended_hours_data=False,
)
resp.raise_for_status()
candles = resp.json()["candles"]
# Each candle: {"open", "high", "low", "close", "volume", "datetime"} (datetime in ms)
```

### Options Chain

```python
resp = client.get_option_chain("SPY")
resp.raise_for_status()
data = resp.json()

spot      = data["underlying"]["last"]
call_map  = data["callExpDateMap"]   # {"YYYY-MM-DD:DTE": {"strike": [contract, ...]}}
put_map   = data["putExpDateMap"]

# IV is returned as a percentage (e.g. 25.5 → 0.255). Value -1 means unavailable.
```

---

## Data Normalization

Apply these transformations consistently when consuming API responses:

| Field | Raw format | Normalized |
|---|---|---|
| `datetime` in candles | Integer milliseconds since epoch | `pd.to_datetime(val, unit="ms")` |
| `volatility` / IV | Percentage (e.g. `25.5` = 25.5%) | Divide by 100; treat `-1` as `NaN` |
| Missing numeric fields | `-1` or `None` | Replace with `float("nan")` |
| Options expiry key | `"YYYY-MM-DD:DTE"` | Split on `:` to get date and DTE |

---

## Error Handling

```python
import httpx

try:
    resp = client.get_quote("AAPL")
    resp.raise_for_status()
    data = resp.json()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        # Token expired and could not be refreshed — re-run auth setup
        pass
    elif e.response.status_code == 429:
        # Rate limited — back off and retry
        pass
    raise
```

Rate limits for Market Data Production: 120 requests/minute per app. Batch endpoints (`get_quotes`) count as a single request regardless of symbol count.

---

## Additional Resources

### Reference Files

- **`references/auth-setup.md`** — Developer portal walkthrough, OAuth flow, first-time token generation, callback URL configuration
- **`references/market-data-api.md`** — Full parameter reference for all 6 endpoint methods with response schemas and enum constants

### Example Files

- **`examples/schwab_client.py`** — Production-ready client factory with env validation
- **`examples/market_data.py`** — Working examples for all endpoint categories with pandas normalization
