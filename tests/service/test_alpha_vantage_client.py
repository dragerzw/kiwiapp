import pytest

from app.service.alpha_vantage_client import AlphaVantageError, get_company_name, get_price_data, get_quote


def test_get_company_name(monkeypatch, app):
    with app.app_context():
        from app.cache import cache
        cache.clear()
        assert get_company_name("AAPL") == "Apple Inc."

def test_get_price_data(monkeypatch, app):
    with app.app_context():
        from app.cache import cache
        cache.clear()
        import requests
        class MockResponse:
            def json(self):
                return {"Global Quote": {"05. price": "150.00", "07. latest trading day": "2023-11-20"}}
            def raise_for_status(self):
                pass
        def mock_get(*args, **kwargs):
            return MockResponse()
        monkeypatch.setattr(requests, "get", mock_get)
        data = get_price_data("AAPL")
        assert data["price"] == 150.0
        assert data["date"] == "2023-11-20"

def test_get_company_name_looks_up_nonpopular_ticker(monkeypatch, app):
    with app.app_context():
        from app.cache import cache
        cache.clear()
        import requests

        class MockResponse:
            def json(self):
                return {
                    "bestMatches": [
                        {
                            "1. symbol": "IBM",
                            "2. name": "International Business Machines Corporation",
                        }
                    ]
                }

            def raise_for_status(self):
                pass

        monkeypatch.setattr(requests, "get", lambda *args, **kwargs: MockResponse())
        assert get_company_name("IBM") == "International Business Machines Corporation"

def test_get_price_data_rate_limit(monkeypatch, app):
    with app.app_context():
        from app.cache import cache
        cache.clear()
        import requests
        class MockResponse:
            def json(self):
                return {
                    "Information": (
                        "Thank you for using Alpha Vantage! Please consider spreading out your free "
                        "API requests more sparingly (1 request per second)."
                    )
                }
            def raise_for_status(self):
                pass
        def mock_get(*args, **kwargs):
            return MockResponse()
        monkeypatch.setattr(requests, "get", mock_get)
        with pytest.raises(AlphaVantageError, match="rate limit"):
            get_price_data("AAPL")

def test_get_price_data_retries_after_burst_rate_limit(monkeypatch, app):
    with app.app_context():
        from app.cache import cache
        cache.clear()
        import requests

        responses = iter([
            {
                "Information": (
                    "Thank you for using Alpha Vantage! Please consider spreading out your free "
                    "API requests more sparingly (1 request per second)."
                )
            },
            {"Global Quote": {"05. price": "150.00", "07. latest trading day": "2023-11-20"}},
        ])
        sleep_calls = []

        class MockResponse:
            def __init__(self, payload):
                self.payload = payload

            def json(self):
                return self.payload

            def raise_for_status(self):
                pass

        def mock_get(*args, **kwargs):
            return MockResponse(next(responses))

        monkeypatch.setattr(requests, "get", mock_get)
        monkeypatch.setattr("app.service.alpha_vantage_client.time.sleep", lambda seconds: sleep_calls.append(seconds))

        data = get_price_data("AAPL")
        assert data["price"] == 150.0
        assert any(seconds >= 1 for seconds in sleep_calls)

def test_get_quote(monkeypatch, app):
    with app.app_context():
        from app.cache import cache
        cache.clear()
        import requests
        class MockResponse:
            def json(self):
                return {"Global Quote": {"05. price": "150.00", "07. latest trading day": "2023-11-20"}, "bestMatches": [{"2. name": "Apple Inc."}]}
            def raise_for_status(self):
                pass

        def mock_get(url, *args, **kwargs):
            return MockResponse()
        monkeypatch.setattr(requests, "get", mock_get)

        quote = get_quote("AAPL")
        assert quote.ticker == "AAPL"
        assert quote.price == 150.0
        assert quote.issuer == "Apple Inc."
        assert quote.date == "2023-11-20"

def test_get_quote_invalid(monkeypatch, app):
    with app.app_context():
        import requests

        from app.cache import cache
        cache.clear()
        class MockResponse:
            def json(self):
                return {"Global Quote": {}}
            def raise_for_status(self):
                pass

        def mock_get(url, *args, **kwargs):
            return MockResponse()
        monkeypatch.setattr(requests, "get", mock_get)

        assert get_quote("AAPL") is None
