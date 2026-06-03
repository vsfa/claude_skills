# Charles Schwab Market Data API Reference

All methods are on the `schwab.client.Client` object. Every method returns an `httpx.Response`. Always call `.raise_for_status()` before `.json()`.

---

## Quotes

### `get_quote(symbol)`

Fetch a real-time quote for a single symbol.

```python
resp = client.get_quote("AAPL")
resp.raise_for_status()
data = resp.json()
```

**Response structure:**
```json
{
  "AAPL": {
    "quote": {
      "lastPrice": 189.30,
      "bidPrice": 189.28,
      "askPrice": 189.32,
      "bidSize": 3,
      "askSize": 2,
      "totalVolume": 45321000,
      "52WeekHigh": 199.62,
      "52WeekLow": 124.17,
      "regularMarketLastPrice": 189.30,
      "postMarketChange": 0.12,
      "postMarketChangePercent": 0.063,
      "postMarketPrice": 189.42
    },
    "fundamental": { ... },
    "reference": { ... }
  }
}
```

Key fields: `lastPrice`, `bidPrice`, `askPrice`, `totalVolume`. Extended hours fields: `postMarketPrice`, `preMarketPrice`.

---

### `get_quotes(symbols)`

Fetch quotes for multiple symbols in a single request (up to 500 symbols).

```python
resp = client.get_quotes(["SPY", "QQQ", "IWM", "DIA"])
resp.raise_for_status()
data = resp.json()
# data is a dict keyed by symbol, same structure as get_quote per symbol
spy_last = data["SPY"]["quote"]["lastPrice"]
```

---

## Price History

### `get_price_history(symbol, ...)`

Fetch OHLCV candle data with configurable granularity and date range.

```python
import datetime
from schwab.client import Client

resp = client.get_price_history(
    symbol,
    period_type=Client.PriceHistory.PeriodType.YEAR,
    frequency_type=Client.PriceHistory.FrequencyType.DAILY,
    frequency=Client.PriceHistory.Frequency.DAILY,
    start_datetime=datetime.datetime(2024, 1, 1),
    end_datetime=datetime.datetime.now(),
    need_extended_hours_data=False,
)
resp.raise_for_status()
data = resp.json()
```

**Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `symbol` | str | Ticker symbol |
| `period_type` | `PeriodType` enum | Time period unit |
| `period` | int | Number of period_type units (only used when not specifying start/end) |
| `frequency_type` | `FrequencyType` enum | Candle frequency unit |
| `frequency` | `Frequency` enum | Number of frequency_type units per candle |
| `start_datetime` | datetime | Start of range (use with end_datetime) |
| `end_datetime` | datetime | End of range |
| `need_extended_hours_data` | bool | Include pre/post market candles |

**PeriodType enums:**
```python
Client.PriceHistory.PeriodType.DAY
Client.PriceHistory.PeriodType.MONTH
Client.PriceHistory.PeriodType.YEAR
Client.PriceHistory.PeriodType.YEAR_TO_DATE
```

**FrequencyType enums:**
```python
Client.PriceHistory.FrequencyType.MINUTE
Client.PriceHistory.FrequencyType.DAILY
Client.PriceHistory.FrequencyType.WEEKLY
Client.PriceHistory.FrequencyType.MONTHLY
```

**Frequency enums** (valid values depend on FrequencyType):
```python
# MINUTE: 1, 5, 10, 15, 30
Client.PriceHistory.Frequency.EVERY_MINUTE
Client.PriceHistory.Frequency.EVERY_FIVE_MINUTES
Client.PriceHistory.Frequency.EVERY_TEN_MINUTES
Client.PriceHistory.Frequency.EVERY_FIFTEEN_MINUTES
Client.PriceHistory.Frequency.EVERY_THIRTY_MINUTES

# DAILY/WEEKLY/MONTHLY:
Client.PriceHistory.Frequency.DAILY
Client.PriceHistory.Frequency.WEEKLY
Client.PriceHistory.Frequency.MONTHLY
```

**Response structure:**
```json
{
  "symbol": "SPY",
  "empty": false,
  "candles": [
    {
      "open": 450.12,
      "high": 452.30,
      "low": 449.88,
      "close": 451.75,
      "volume": 78234000,
      "datetime": 1704067200000
    }
  ]
}
```

`datetime` is milliseconds since Unix epoch. Convert with `pd.to_datetime(val, unit="ms")`.

**Check for empty data before parsing:**
```python
if data.get("empty") or not data.get("candles"):
    raise ValueError(f"No price history for {symbol}")
```

---

## Options Chain

### `get_option_chain(symbol, ...)`

Fetch a full options chain with calls and puts.

```python
resp = client.get_option_chain(
    symbol,
    contract_type=Client.Options.ContractType.ALL,  # ALL, CALL, or PUT
    strike_count=20,          # number of strikes above/below ATM
    include_underlying_quote=True,
    strategy=Client.Options.Strategy.SINGLE,
    from_date=datetime.date.today(),
    to_date=datetime.date.today() + datetime.timedelta(days=45),
)
resp.raise_for_status()
data = resp.json()
```

**Key parameters:**

| Parameter | Type | Description |
|---|---|---|
| `contract_type` | `ContractType` enum | Filter to CALL, PUT, or ALL |
| `strike_count` | int | Strikes above and below ATM to include |
| `include_underlying_quote` | bool | Include spot price in response |
| `strategy` | `Strategy` enum | Chain strategy type (SINGLE, ANALYTICAL, etc.) |
| `from_date` | date | Earliest expiration date |
| `to_date` | date | Latest expiration date |
| `strike` | float | Filter to a specific strike |

**Response structure:**
```json
{
  "symbol": "SPY",
  "status": "SUCCESS",
  "underlying": {
    "last": 451.75,
    "bid": 451.73,
    "ask": 451.77,
    "change": 1.25,
    "percentChange": 0.28
  },
  "callExpDateMap": {
    "2024-01-19:5": {
      "450.0": [
        {
          "putCall": "CALL",
          "symbol": "SPY_011924C450",
          "bid": 2.15,
          "ask": 2.18,
          "last": 2.16,
          "mark": 2.165,
          "bidSize": 10,
          "askSize": 15,
          "openInterest": 12450,
          "volatility": 14.25,
          "delta": 0.52,
          "gamma": 0.08,
          "theta": -0.15,
          "vega": 0.12,
          "rho": 0.04,
          "strikePrice": 450.0,
          "expirationDate": "2024-01-19",
          "daysToExpiration": 5,
          "inTheMoney": false
        }
      ]
    }
  },
  "putExpDateMap": { ... }
}
```

**Expiry map key format:** `"YYYY-MM-DD:DTE"` where DTE is days to expiration. Parse with:
```python
for key in call_map:
    date_str, dte_str = key.split(":")
    dte = int(dte_str)
```

**IV normalization:** `volatility` is a percentage (e.g. `14.25` means 14.25% IV). Convert to decimal; treat `-1` as unavailable:
```python
raw = contract.get("volatility", -1)
iv = raw / 100.0 if raw > 0 else float("nan")
```

---

## Instruments

### `get_instruments(symbol, projection)`

Search for instruments or retrieve fundamentals.

```python
from schwab.client import Client

# Search by symbol (exact or partial)
resp = client.get_instruments("AAPL", Client.Instrument.Projection.SYMBOL_SEARCH)

# Get full fundamental data
resp = client.get_instruments("AAPL", Client.Instrument.Projection.FUNDAMENTAL)

resp.raise_for_status()
data = resp.json()
```

**Projection enums:**
```python
Client.Instrument.Projection.SYMBOL_SEARCH      # partial/exact symbol match
Client.Instrument.Projection.SYMBOL_REGEX       # regex symbol match
Client.Instrument.Projection.DESC_SEARCH        # search by company name
Client.Instrument.Projection.DESC_REGEX         # regex on description
Client.Instrument.Projection.FUNDAMENTAL        # full fundamental data
```

**Response structure (FUNDAMENTAL):**
```json
[
  {
    "cusip": "037833100",
    "symbol": "AAPL",
    "description": "Apple Inc",
    "exchange": "NASDAQ",
    "assetType": "EQUITY",
    "fundamental": {
      "high52": 199.62,
      "low52": 124.17,
      "dividendYield": 0.55,
      "peRatio": 28.5,
      "marketCap": 2940000000000,
      "eps": 6.64,
      "beta": 1.29
    }
  }
]
```

---

## Movers

### `get_movers(index)`

Fetch the top moving symbols for a given index.

```python
from schwab.client import Client

resp = client.get_movers(
    index=Client.Movers.Index.SPX,
    sort_order=Client.Movers.SortOrder.PERCENT_CHANGE_UP,
    frequency=0,   # 0=all, or number of top movers to return
)
resp.raise_for_status()
data = resp.json()
```

**Index enums:**
```python
Client.Movers.Index.SPX      # S&P 500  ($SPX.X)
Client.Movers.Index.DJI      # Dow Jones ($DJI)
Client.Movers.Index.COMPX    # NASDAQ Composite ($COMPX)
Client.Movers.Index.RUT      # Russell 2000
```

**SortOrder enums:**
```python
Client.Movers.SortOrder.PERCENT_CHANGE_UP
Client.Movers.SortOrder.PERCENT_CHANGE_DOWN
Client.Movers.SortOrder.VOLUME
```

**Response structure:**
```json
{
  "screeners": [
    {
      "symbol": "NVDA",
      "description": "NVIDIA Corporation",
      "lastPrice": 495.50,
      "netChange": 12.30,
      "netPercentChange": 2.55,
      "marketShare": 0.0,
      "totalVolume": 38421000,
      "trades": 284230
    }
  ]
}
```

---

## Market Hours

### `get_market_hours(markets, date)`

Fetch open/close times for one or more market types on a given date.

```python
from schwab.client import Client
import datetime

resp = client.get_market_hours(
    markets=[
        Client.MarketHours.Market.EQUITY,
        Client.MarketHours.Market.OPTION,
    ],
    date=datetime.date.today(),
)
resp.raise_for_status()
data = resp.json()
```

**Market enums:**
```python
Client.MarketHours.Market.EQUITY
Client.MarketHours.Market.OPTION
Client.MarketHours.Market.BOND
Client.MarketHours.Market.FUTURE
Client.MarketHours.Market.FOREX
```

**Response structure:**
```json
{
  "equity": {
    "EQ": {
      "date": "2024-01-15",
      "marketType": "EQUITY",
      "exchange": "NULL",
      "category": "NULL",
      "isOpen": true,
      "sessionHours": {
        "preMarket": [{"start": "2024-01-15T07:00:00-05:00", "end": "2024-01-15T09:30:00-05:00"}],
        "regularMarket": [{"start": "2024-01-15T09:30:00-05:00", "end": "2024-01-15T16:00:00-05:00"}],
        "postMarket": [{"start": "2024-01-15T16:00:00-05:00", "end": "2024-01-15T20:00:00-05:00"}]
      }
    }
  },
  "option": { ... }
}
```

Check `isOpen` to determine if the market is open on the requested date (handles holidays automatically).

---

## Rate Limits

| Limit | Value |
|---|---|
| Requests per minute | 120 per app |
| Symbols per `get_quotes` call | Up to 500 |
| Streaming connections | 1 per app |

Batch endpoints (`get_quotes`) count as **1 request** regardless of symbol count — always prefer batch over looped single-symbol calls.

On HTTP 429, implement exponential backoff before retrying.
