# Charles Schwab Developer Portal Setup & OAuth Authentication

## 1. Create a Developer Account

1. Go to [developer.schwab.com](https://developer.schwab.com) and sign in with your Charles Schwab brokerage account credentials.
2. Navigate to **Apps** → **Create App**.
3. Select **Individual Developer** as the app type.

---

## 2. Configure the App

Fill in the app registration form:

| Field | Value |
|---|---|
| **App Name** | Any descriptive name (e.g. "My Market Data App") |
| **Callback URL** | `https://127.0.0.1` for production; `https://127.0.0.1:8182` for local dev |
| **API Products** | Enable **Market Data Production** (required for all market data calls) |

**Callback URL rules:**
- The value configured here must **exactly match** `SCHWAB_REDIRECT_URI` in your `.env` file — including the port if present.
- Schwab does not allow `http://` — only `https://` callbacks are accepted.
- For purely programmatic access (no account trading), `https://127.0.0.1` with no port is the simplest choice.
- If you also need trading APIs, you may need to add the Account Trading Products as well.

After creating the app, Schwab shows an **App Key** (Client ID) and **App Secret**. Copy both — the secret is shown only once.

---

## 3. Environment Variables

Create a `.env` file in the project root:

```ini
SCHWAB_CLIENT_ID=AbCdEfGhIjKlMnOpQrStUvWxYz123456
SCHWAB_CLIENT_SECRET=SecretValueFromPortal
SCHWAB_REDIRECT_URI=https://127.0.0.1
SCHWAB_TOKEN_PATH=config/schwab_token.json
```

Add `.env` and `config/schwab_token.json` to `.gitignore` immediately:

```
.env
config/schwab_token.json
```

---

## 4. First-Time Token Generation

OAuth token generation requires a one-time browser interaction. Create and run `scripts/schwab_auth.py`:

```python
"""
Run once to generate config/schwab_token.json.

    python scripts/schwab_auth.py

A browser will open Schwab's login page. After authorizing, the token
is saved and all subsequent calls will refresh it automatically.
"""
import os
import schwab
from dotenv import load_dotenv

load_dotenv()

app_key    = os.environ["SCHWAB_CLIENT_ID"]
app_secret = os.environ["SCHWAB_CLIENT_SECRET"]
callback   = os.environ.get("SCHWAB_REDIRECT_URI", "https://127.0.0.1")
token_path = os.environ.get("SCHWAB_TOKEN_PATH", "config/schwab_token.json")

os.makedirs(os.path.dirname(token_path), exist_ok=True)

print(f"Opening browser for Schwab OAuth...")
print(f"Callback URL: {callback}")
print(f"Token will be saved to: {token_path}\n")

client = schwab.auth.easy_client(
    api_key=app_key,
    app_secret=app_secret,
    callback_url=callback,
    token_path=token_path,
)

print("Auth complete. Token saved.")
```

**What happens during first-time auth:**
1. `easy_client` detects no token file exists and opens your default browser to Schwab's OAuth consent page.
2. Log in with your Schwab brokerage credentials and approve the app.
3. The browser redirects to the callback URL (e.g. `https://127.0.0.1`). The page will appear blank or give a connection error — that is expected.
4. Copy the full URL from the browser address bar and paste it when prompted in the terminal.
5. schwab-py exchanges the authorization code for an access token and saves it to `token_path`.

---

## 5. Token Auto-Refresh

After initial setup, `schwab.auth.easy_client` automatically:
- Reads the token from `token_path` on initialization.
- Refreshes the access token (valid 30 minutes) using the refresh token (valid 7 days) before each request.
- Writes the updated token back to `token_path`.

**Token expiry:** If the refresh token expires (after 7 days of inactivity), re-run `scripts/schwab_auth.py` to generate a fresh token via browser login.

---

## 6. Headless / CI Environments

For server environments without a browser, use `schwab.auth.client_from_token_file` after generating the token locally:

```python
import schwab

# Token was generated on a dev machine and copied to the server
client = schwab.auth.client_from_token_file(
    token_path="config/schwab_token.json",
    api_key=os.environ["SCHWAB_CLIENT_ID"],
    app_secret=os.environ["SCHWAB_CLIENT_SECRET"],
)
```

This only works as long as the refresh token remains valid (7-day window). For unattended long-running services, schedule a token refresh or re-auth before the window expires.

---

## 7. Verifying the Setup

After running `schwab_auth.py`, verify connectivity:

```python
from schwab_client import get_client

client = get_client()
resp = client.get_quote("SPY")
resp.raise_for_status()
print(resp.json()["SPY"]["quote"]["lastPrice"])
```

A valid last price confirms authentication is working.
