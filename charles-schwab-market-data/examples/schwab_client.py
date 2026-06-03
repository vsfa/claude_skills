"""
Production-ready Schwab client factory.

Reads credentials from environment variables (or a .env file).
Returns a singleton client that auto-refreshes its OAuth token.

Prerequisites:
  1. Run schwab_auth.py once to generate the token file.
  2. Set SCHWAB_CLIENT_ID, SCHWAB_CLIENT_SECRET in .env.
"""
import os
import schwab
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_client():
    global _client
    if _client is not None:
        return _client

    app_key = os.environ.get("SCHWAB_CLIENT_ID", "")
    app_secret = os.environ.get("SCHWAB_CLIENT_SECRET", "")
    if not app_key or not app_secret:
        raise RuntimeError(
            "Schwab credentials not configured. "
            "Set SCHWAB_CLIENT_ID and SCHWAB_CLIENT_SECRET in .env or environment."
        )

    token_path = os.environ.get("SCHWAB_TOKEN_PATH", "config/schwab_token.json")
    callback_url = os.environ.get("SCHWAB_REDIRECT_URI", "https://127.0.0.1")

    _client = schwab.auth.easy_client(
        api_key=app_key,
        app_secret=app_secret,
        callback_url=callback_url,
        token_path=token_path,
    )
    return _client
