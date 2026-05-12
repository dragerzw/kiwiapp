from dataclasses import dataclass
from typing import Optional
import threading
import time

import requests
from flask import current_app

from app.cache import cache

ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
ALPHA_VANTAGE_CACHE_TIMEOUT_SECONDS = 300
ALPHA_VANTAGE_MIN_INTERVAL_SECONDS = 1.05
ALPHA_VANTAGE_BURST_RETRY_DELAY_SECONDS = 1.1
ALPHA_VANTAGE_MAX_ATTEMPTS = 2
POPULAR_SECURITY_NAMES = {
    "AAPL": "Apple Inc.",
    "AMZN": "Amazon.com, Inc.",
    "GOOGL": "Alphabet Inc.",
    "JPM": "JPMorgan Chase & Co.",
    "META": "Meta Platforms, Inc.",
    "MSFT": "Microsoft Corporation",
    "NFLX": "Netflix, Inc.",
    "NVDA": "NVIDIA Corporation",
    "TSLA": "Tesla, Inc.",
    "WMT": "Walmart Inc.",
}
_alpha_vantage_request_lock = threading.Lock()
_last_alpha_vantage_request_at = 0.0


@dataclass
class SecurityQuote:
    ticker: str
    date: str
    price: float
    issuer: str

class AlphaVantageError(Exception):
    pass

def _get_api_key() -> str:
    api_key = current_app.config.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise AlphaVantageError("ALPHA_VANTAGE_API_KEY is not configured")
    return api_key


def _normalize_ticker(ticker: str) -> str:
    return (ticker or "").strip().upper()


def _extract_api_error(data: dict) -> tuple[Optional[str], bool]:
    for key in ("Error Message", "Note", "Information"):
        message = data.get(key)
        if not message:
            continue

        normalized_message = " ".join(str(message).split())
        lowered_message = normalized_message.lower()
        if (
            "rate limit" in lowered_message
            or "25 requests per day" in lowered_message
            or "1 request per second" in lowered_message
        ):
            return (
                f"Alpha Vantage rate limit reached. {normalized_message}",
                "1 request per second" in lowered_message,
            )

        if "api key" in lowered_message:
            return (f"Alpha Vantage API key issue. {normalized_message}", False)

        return (f"Alpha Vantage error. {normalized_message}", False)

    return None, False


def _wait_for_alpha_vantage_window() -> None:
    global _last_alpha_vantage_request_at

    with _alpha_vantage_request_lock:
        now = time.monotonic()
        wait_seconds = ALPHA_VANTAGE_MIN_INTERVAL_SECONDS - (now - _last_alpha_vantage_request_at)
        if wait_seconds > 0:
            time.sleep(wait_seconds)
        _last_alpha_vantage_request_at = time.monotonic()


def _request_alpha_vantage(function: str, **params) -> dict:
    for attempt in range(ALPHA_VANTAGE_MAX_ATTEMPTS):
        _wait_for_alpha_vantage_window()

        try:
            kwargs = {
                "params": {"function": function, "apikey": _get_api_key(), **params},
                "timeout": 10,
            }
            # Only bypass proxies if explicitly configured to do so
            if current_app.config.get('DISABLE_OUTBOUND_PROXIES', False):
                kwargs["proxies"] = {}

            response = requests.get(ALPHA_VANTAGE_BASE_URL, **kwargs)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            raise AlphaVantageError(f"Failed to fetch {function} data from Alpha Vantage: {e}") from e
        except ValueError as e:
            raise AlphaVantageError(f"Alpha Vantage returned invalid JSON for {function}: {e}") from e

        error_message, retryable = _extract_api_error(data)
        if not error_message:
            return data

        if retryable and attempt < ALPHA_VANTAGE_MAX_ATTEMPTS - 1:
            time.sleep(ALPHA_VANTAGE_BURST_RETRY_DELAY_SECONDS)
            continue

        raise AlphaVantageError(error_message)

    raise AlphaVantageError(f"Failed to fetch {function} data from Alpha Vantage")


def _extract_company_name(search_payload: dict, ticker: str) -> Optional[str]:
    matches = search_payload.get("bestMatches")
    if not isinstance(matches, list):
        return None

    normalized_ticker = _normalize_ticker(ticker)
    for match in matches:
        if _normalize_ticker(match.get("1. symbol")) == normalized_ticker:
            company_name = (match.get("2. name") or "").strip()
            if company_name:
                return company_name

    for match in matches:
        company_name = (match.get("2. name") or "").strip()
        if company_name:
            return company_name

    return None


def get_company_name(ticker: str) -> Optional[str]:
    normalized_ticker = _normalize_ticker(ticker)
    if not normalized_ticker:
        return None

    cache_key = f'company_name:{normalized_ticker}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    result = POPULAR_SECURITY_NAMES.get(normalized_ticker)
    if result is None:
        data = _request_alpha_vantage("SYMBOL_SEARCH", keywords=normalized_ticker)
        result = _extract_company_name(data, normalized_ticker)

    if result is not None:
        cache.set(cache_key, result, timeout=ALPHA_VANTAGE_CACHE_TIMEOUT_SECONDS)
    return result


def get_price_data(ticker: str) -> Optional[dict]:
    normalized_ticker = _normalize_ticker(ticker)
    if not normalized_ticker:
        return None

    cache_key = f'price_data:{normalized_ticker}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    data = _request_alpha_vantage("GLOBAL_QUOTE", symbol=normalized_ticker)
    
    quote = data.get("Global Quote", {})
    if not quote or "05. price" not in quote:
        return None

    try:
        price = float(quote["05. price"])
    except (TypeError, ValueError) as e:
        raise AlphaVantageError(
            f"Alpha Vantage returned an invalid price for {normalized_ticker}: {quote.get('05. price')}"
        ) from e

    result = {
        "price": price,
        "date": quote.get("07. latest trading day", "")
    }
    cache.set(cache_key, result, timeout=ALPHA_VANTAGE_CACHE_TIMEOUT_SECONDS)
    return result


def get_quote(ticker: str) -> Optional[SecurityQuote]:
    """
    Combines company search and global quote info to construct a full SecurityQuote
    """
    price_data = get_price_data(ticker)
    if not price_data:
        return None
        
    company_name = get_company_name(ticker)
    if not company_name:
        company_name = "Unknown Issuer"
        
    return SecurityQuote(
        ticker=_normalize_ticker(ticker),
        date=price_data["date"],
        price=price_data["price"],
        issuer=company_name
    )
