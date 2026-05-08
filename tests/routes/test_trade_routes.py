def test_buy_trade(client, auth_headers, monkeypatch):
    from app.service.alpha_vantage_client import SecurityQuote
    def mock_get_quote(ticker):
        return SecurityQuote(ticker="AAPL", date="2023-11-20", price=150.0, issuer="Apple Inc.")
    monkeypatch.setattr("app.service.trade_service.get_quote", mock_get_quote)
    monkeypatch.setattr("app.routes.trade_routes.get_quote", mock_get_quote)
    
    create_resp = client.post('/portfolios/', json={"name": "Trade Port 1", "description": "Desc"}, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    
    data = {"portfolio_id": pid, "ticker": "AAPL", "quantity": 2}
    response = client.post('/trades/buy', json=data, headers=auth_headers)
    assert response.status_code == 201

def test_sell_trade(client, auth_headers, monkeypatch):
    from app.service.alpha_vantage_client import SecurityQuote
    def mock_get_quote(ticker):
        return SecurityQuote(ticker="AAPL", date="2023-11-20", price=150.0, issuer="Apple Inc.")
    monkeypatch.setattr("app.service.trade_service.get_quote", mock_get_quote)
    monkeypatch.setattr("app.routes.trade_routes.get_quote", mock_get_quote)
    
    create_resp = client.post('/portfolios/', json={"name": "Trade Port 2", "description": "Desc"}, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    
    buy_data = {"portfolio_id": pid, "ticker": "AAPL", "quantity": 5}
    client.post('/trades/buy', json=buy_data, headers=auth_headers)
    
    sell_data = {"portfolio_id": pid, "ticker": "AAPL", "quantity": 2}
    response = client.post('/trades/sell', json=sell_data, headers=auth_headers)
    assert response.status_code == 200

def test_buy_trade_unauthorized(client, auth_headers, monkeypatch):
    monkeypatch.setattr('app.service.portfolio_service.has_portfolio_access', lambda pid, username, roles: False)
    data = {"portfolio_id": 999, "ticker": "AAPL", "quantity": 2}
    response = client.post('/trades/buy', json=data, headers=auth_headers)
    assert response.status_code == 403
    assert 'Unauthorized' in response.json['error']

def test_sell_trade_unauthorized(client, auth_headers, monkeypatch):
    monkeypatch.setattr('app.service.portfolio_service.has_portfolio_access', lambda pid, username, roles: False)
    data = {"portfolio_id": 999, "ticker": "AAPL", "quantity": 2}
    response = client.post('/trades/sell', json=data, headers=auth_headers)
    assert response.status_code == 403
    assert 'Unauthorized' in response.json['error']

def test_buy_trade_invalid_input(client, auth_headers):
    response = client.post('/trades/buy', json={}, headers=auth_headers)
    assert response.status_code == 422 or response.status_code == 400

def test_sell_trade_invalid_input(client, auth_headers):
    response = client.post('/trades/sell', json={}, headers=auth_headers)
    assert response.status_code == 422 or response.status_code == 400

def test_buy_trade_internal_error(monkeypatch, client, auth_headers):
    monkeypatch.setattr('app.service.trade_service.execute_purchase_order', lambda *args, **kwargs: (_ for _ in ()).throw(Exception('DB fail')))
    data = {"portfolio_id": 1, "ticker": "AAPL", "quantity": 2}
    response = client.post('/trades/buy', json=data, headers=auth_headers)
    assert response.status_code == 500
    assert 'unexpected error' in response.json['error'].lower()

def test_sell_trade_internal_error(monkeypatch, client, auth_headers):
    monkeypatch.setattr('app.service.trade_service.liquidate_investment', lambda *args, **kwargs: (_ for _ in ()).throw(Exception('DB fail')))
    data = {"portfolio_id": 1, "ticker": "AAPL", "quantity": 2}
    response = client.post('/trades/sell', json=data, headers=auth_headers)
    assert response.status_code == 500
    assert 'unexpected error' in response.json['error'].lower()
