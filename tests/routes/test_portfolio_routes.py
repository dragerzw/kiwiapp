from app.config import TestConfig
from app.db import db
from app.service.portfolio_service import PortfolioOperationError


def raise_runtime_error(message):
    raise RuntimeError(message)


def test_get_all_portfolios(client, auth_headers, db_session):
    db.session.commit()
    db.session.expire_all()
    response = client.get('/portfolios/', headers=auth_headers)
    print('DEBUG: test_get_all_portfolios response:', response.json)
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert all('total_portfolio_value' in portfolio for portfolio in response.json)
    assert all('access_role' in portfolio for portfolio in response.json)
    assert all(isinstance(portfolio['total_portfolio_value'], (int, float)) for portfolio in response.json)

def test_get_all_portfolios_skips_quotes_by_default(client, auth_headers, monkeypatch):
    def fail_if_called(_ticker):
        raise AssertionError('Alpha Vantage should not be called for portfolio list requests by default')

    monkeypatch.setattr('app.routes.portfolio_routes.get_price_data', fail_if_called)
    response = client.get('/portfolios/', headers=auth_headers)
    assert response.status_code == 200

def test_get_all_portfolios_can_include_quotes(client, auth_headers, monkeypatch):
    monkeypatch.setattr(
        'app.routes.portfolio_routes.get_price_data',
        lambda _ticker: {'price': 150.0, 'date': '2023-11-20'},
    )
    response = client.get('/portfolios/?include_quotes=true', headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert all('total_portfolio_value' in portfolio for portfolio in response.json)

def test_get_all_portfolios_shows_estimated_balance_from_transactions(client, auth_headers, monkeypatch):
    def mock_get_price_data(_ticker):
        return {"price": 150.0, "date": "2023-11-20"}

    monkeypatch.setattr("app.service.trade_service.get_price_data", mock_get_price_data)
    monkeypatch.setattr("app.routes.trade_routes.get_price_data", mock_get_price_data)

    create_resp = client.post('/portfolios/', json={"name": "Growth Fund", "description": ""}, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    client.post('/trades/buy', json={"portfolio_id": pid, "ticker": "AAPL", "quantity": 2}, headers=auth_headers)

    response = client.get('/portfolios/', headers=auth_headers)
    assert response.status_code == 200
    created_portfolio = next(portfolio for portfolio in response.json if portfolio['id'] == pid)
    assert created_portfolio['total_portfolio_value'] == 300.0

def test_create_portfolio(client, auth_headers):
    data = {"name": "Test Port", "description": "Test"}
    response = client.post('/portfolios/', json=data, headers=auth_headers)
    assert response.status_code == 201
    assert 'portfolio_id' in response.json

def test_create_portfolio_wrong_user(client, auth_headers):
    data = {"name": "Test Port", "description": "Test", "username": "other_user"}
    response = client.post('/portfolios/', json=data, headers=auth_headers)
    assert response.status_code == 422

def test_get_portfolio(client, auth_headers, monkeypatch):
    monkeypatch.setattr('app.routes.portfolio_routes.get_price_data', lambda x: None)
    data = {"name": "Test Port", "description": "Test"}
    create_resp = client.post('/portfolios/', json=data, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    
    response = client.get(f'/portfolios/{pid}', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['name'] == 'Test Port'
    assert response.json['access_role'] == 'Owner'

def test_delete_portfolio(client, auth_headers, db_session):
    data = {"name": "Delete Me", "description": "Test"}
    create_resp = client.post('/portfolios/', json=data, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    db.session.commit()
    db.session.expire_all()
    response = client.delete(f'/portfolios/{pid}', headers=auth_headers)
    print('DEBUG: test_delete_portfolio response:', response.status_code, response.json)
    assert response.status_code == 200

def test_delete_portfolio_with_holdings_returns_400(client, auth_headers, monkeypatch):
    def mock_get_price_data(_ticker):
        return {"price": 150.0, "date": "2023-11-20"}

    monkeypatch.setattr("app.service.trade_service.get_price_data", mock_get_price_data)
    monkeypatch.setattr("app.routes.trade_routes.get_price_data", mock_get_price_data)

    create_resp = client.post('/portfolios/', json={"name": "Cannot Delete", "description": "Has holdings"}, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    client.post('/trades/buy', json={"portfolio_id": pid, "ticker": "AAPL", "quantity": 1}, headers=auth_headers)

    response = client.delete(f'/portfolios/{pid}', headers=auth_headers)
    assert response.status_code == 400
    assert 'cannot be deleted while it still contains holdings' in response.json['error']

def test_portfolio_access_grant(client, auth_headers):
    data = {"name": "Access Port", "description": "Test"}
    create_resp = client.post('/portfolios/', json=data, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    
    grant_data = {"username": "user2", "role": "Viewer"}
    response = client.post(f'/portfolios/{pid}/access', json=grant_data, headers=auth_headers)
    assert response.status_code == 200

def test_portfolio_access_revoke(client, auth_headers):
    data = {"name": "Access Port", "description": "Test"}
    create_resp = client.post('/portfolios/', json=data, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    grant_data = {"username": "user2", "role": "Viewer"}
    client.post(f'/portfolios/{pid}/access', json=grant_data, headers=auth_headers)
    
    response = client.delete(f'/portfolios/{pid}/access/user2', headers=auth_headers)
    assert response.status_code == 200

def test_enrich_portfolio_handles_quote_failure(monkeypatch):
    # Simulate get_price_data raising exception
    monkeypatch.setattr('app.routes.portfolio_routes.get_price_data', lambda ticker: raise_runtime_error('API fail'))
    from app.routes.portfolio_routes import _enrich_portfolio
    portfolio_dict = {
        'investments': [
            {'ticker': 'AAPL', 'quantity': 10},
            {'ticker': 'GOOGL', 'quantity': 5}
        ]
    }
    enriched = _enrich_portfolio(portfolio_dict)
    for inv in enriched['investments']:
        assert inv['current_price'] is None
        assert inv['total_value'] is None
    assert enriched['total_portfolio_value'] >= 0.0

def test_enrich_portfolio_exposes_alpha_vantage_errors(monkeypatch):
    from app.service.alpha_vantage_client import AlphaVantageError
    monkeypatch.setattr(
        'app.routes.portfolio_routes.get_price_data',
        lambda ticker: (_ for _ in ()).throw(AlphaVantageError('Alpha Vantage rate limit reached. Slow down.')),
    )
    from app.routes.portfolio_routes import _enrich_portfolio
    portfolio_dict = {
        'investments': [
            {'ticker': 'AAPL', 'quantity': 10},
        ]
    }
    enriched = _enrich_portfolio(portfolio_dict)
    assert enriched['quote_error'] == 'Alpha Vantage rate limit reached. Slow down.'
    assert enriched['investments'][0]['current_price'] is None
    assert enriched['investments'][0]['total_value'] is None

def test_get_all_portfolios_handles_serialization_error(monkeypatch, client, auth_headers, db_session):
    # Simulate portfolio.__to_dict__ raising exception
    class DummyPortfolio:
        def __to_dict__(self):
            raise RuntimeError('Serialization fail')
    monkeypatch.setattr('app.service.portfolio_service.get_portfolios_by_user', lambda user: [DummyPortfolio()])
    response = client.get('/portfolios/', headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_all_portfolios_handles_internal_error(monkeypatch, client, auth_headers, db_session):
    # Simulate portfolio_service.get_portfolios_by_user raising exception
    monkeypatch.setattr('app.service.portfolio_service.get_portfolios_by_user', lambda user: raise_runtime_error('DB fail'))
    response = client.get('/portfolios/', headers=auth_headers)
    assert response.status_code == 500
    assert response.json['code'] == 500
    assert 'Internal server error' in response.json['error']

def test_get_portfolios_by_user_unauthorized(client, auth_headers):
    response = client.get('/portfolios/user/other_user', headers=auth_headers)
    assert response.status_code == 403
    assert 'Unauthorized' in response.json['error']

def test_get_portfolios_by_user_not_found(client, auth_headers):
    response = client.get('/portfolios/user/nonexistent', headers=auth_headers)
    assert response.status_code == 404
    assert 'not found' in response.json['error']

def test_create_portfolio_user_not_found(client, auth_headers, monkeypatch):
    monkeypatch.setattr('app.service.user_service.get_user_by_username', lambda username: None)
    data = {"name": "Test Port", "description": "Test"}
    response = client.post('/portfolios/', json=data, headers=auth_headers)
    assert response.status_code == 403
    assert 'not found' in response.json['error']

def test_create_portfolio_invalid_input(client, auth_headers, monkeypatch):
    monkeypatch.setattr('app.service.portfolio_service.create_portfolio', lambda name, description, user: None)
    data = {"name": "Test Port", "description": "Test"}
    response = client.post('/portfolios/', json=data, headers=auth_headers)
    assert response.status_code == 400
    assert 'Invalid portfolio input' in response.json['error']

def test_get_portfolio_not_found(client, auth_headers):
    response = client.get('/portfolios/99999', headers=auth_headers)
    assert response.status_code == 404
    assert 'not found' in response.json['error']

def test_get_portfolio_unauthorized(client, auth_headers, monkeypatch):
    monkeypatch.setattr('app.service.portfolio_service.has_portfolio_access', lambda pid, username, roles: False)
    data = {"name": "Test Port", "description": "Test"}
    create_resp = client.post('/portfolios/', json=data, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    response = client.get(f'/portfolios/{pid}', headers=auth_headers)
    assert response.status_code == 403
    assert 'Unauthorized' in response.json['error']

def test_grant_access_unauthorized(client, auth_headers, monkeypatch):
    monkeypatch.setattr('app.service.portfolio_service.has_portfolio_access', lambda pid, username, roles: False)
    data = {"name": "Access Port", "description": "Test"}
    create_resp = client.post('/portfolios/', json=data, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    grant_data = {"username": "user2", "role": "Viewer"}
    response = client.post(f'/portfolios/{pid}/access', json=grant_data, headers=auth_headers)
    assert response.status_code == 403
    assert 'Owner' in response.json['error']

def test_grant_access_invalid(client, auth_headers, monkeypatch):
    monkeypatch.setattr('app.service.portfolio_service.has_portfolio_access', lambda pid, username, roles: True)
    monkeypatch.setattr('app.service.portfolio_service.grant_portfolio_access', lambda pid, username, role: None)
    data = {"name": "Access Port", "description": "Test"}
    create_resp = client.post('/portfolios/', json=data, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    grant_data = {"username": "user2", "role": "Viewer"}
    response = client.post(f'/portfolios/{pid}/access', json=grant_data, headers=auth_headers)
    assert response.status_code == 400
    assert 'Invalid portfolio access grant' in response.json['error']

def test_delete_portfolio_unauthorized(client, auth_headers, monkeypatch):
    monkeypatch.setattr('app.service.portfolio_service.has_portfolio_access', lambda pid, username, roles: False)
    data = {"name": "Delete Me", "description": "Test"}
    create_resp = client.post('/portfolios/', json=data, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    response = client.delete(f'/portfolios/{pid}', headers=auth_headers)
    assert response.status_code == 403
    assert 'Owner' in response.json['error']

def test_delete_portfolio_not_found(client, auth_headers, monkeypatch):
    monkeypatch.setattr('app.service.portfolio_service.has_portfolio_access', lambda pid, username, roles: True)
    monkeypatch.setattr(
        'app.service.portfolio_service.delete_portfolio',
        lambda pid: (_ for _ in ()).throw(PortfolioOperationError(f'Portfolio {pid} not found')),
    )
    response = client.delete('/portfolios/99999', headers=auth_headers)
    assert response.status_code == 404
    assert 'not found' in response.json['error']

def test_revoke_access_unauthorized(client, auth_headers, monkeypatch):
    monkeypatch.setattr('app.service.portfolio_service.has_portfolio_access', lambda pid, username, roles: False)
    data = {"name": "Access Port", "description": "Test"}
    create_resp = client.post('/portfolios/', json=data, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    response = client.delete(f'/portfolios/{pid}/access/user2', headers=auth_headers)
    assert response.status_code == 403
    assert 'Owner' in response.json['error']

# --- New tests targeting previously uncovered branches ---

def test_get_portfolio_transactions_success(client, auth_headers, db_session):
    """Covers GET /portfolios/<id>/transactions success path."""
    db.session.commit()
    db.session.expire_all()
    data = {"name": "Txn Port", "description": "Test"}
    create_resp = client.post('/portfolios/', json=data, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    response = client.get(f'/portfolios/{pid}/transactions', headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_portfolio_transactions_unauthorized(client, auth_headers, monkeypatch):
    """Covers GET /portfolios/<id>/transactions unauthorized 403."""
    monkeypatch.setattr('app.service.portfolio_service.has_portfolio_access', lambda pid, username, roles: False)
    response = client.get('/portfolios/1/transactions', headers=auth_headers)
    assert response.status_code == 403
    assert 'Unauthorized' in response.json['error']

def test_get_portfolios_by_user_success(client, auth_headers, monkeypatch):
    """Covers GET /portfolios/user/<username> success path."""
    monkeypatch.setattr('app.routes.portfolio_routes.get_price_data', lambda x: None)
    response = client.get('/portfolios/user/admin', headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert all('total_portfolio_value' in portfolio for portfolio in response.json)
    assert all('access_role' in portfolio for portfolio in response.json)

def test_get_portfolio_internal_error(monkeypatch, client, auth_headers):
    """Covers the except path in get_portfolio."""
    monkeypatch.setattr('app.service.portfolio_service.get_portfolio_by_id', lambda pid: raise_runtime_error('DB fail'))
    response = client.get('/portfolios/1', headers=auth_headers)
    assert response.status_code == 500
    assert 'Internal server error' in response.json['error']

def test_grant_access_invalid_role_422(client, auth_headers):
    """Confirms Pydantic ValidationError returns 422 (not 500) for bad role in grant_access."""
    data = {"name": "RoleTest Port", "description": "Test"}
    create_resp = client.post('/portfolios/', json=data, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    response = client.post(f'/portfolios/{pid}/access', json={"username": "user2", "role": "SuperAdmin"}, headers=auth_headers)
    assert response.status_code == 422

def test_grant_access_extra_field_422(client, auth_headers):
    """Confirms extra fields in grant_access body return 422 due to extra='forbid'."""
    data = {"name": "ExtraTest Port", "description": "Test"}
    create_resp = client.post('/portfolios/', json=data, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    response = client.post(f'/portfolios/{pid}/access', json={"username": "user2", "role": "Viewer", "extra": "bad"}, headers=auth_headers)
    assert response.status_code == 422
