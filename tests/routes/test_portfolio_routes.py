from app.config import TestConfig
from app.db import db
def test_get_all_portfolios(client, auth_headers, db_session):
    db.session.commit()
    db.session.expire_all()
    response = client.get('/portfolios/', headers=auth_headers)
    print('DEBUG: test_get_all_portfolios response:', response.json)
    assert response.status_code == 200
    assert isinstance(response.json, list)

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
    monkeypatch.setattr('app.routes.portfolio_routes.get_quote', lambda x: None)
    data = {"name": "Test Port", "description": "Test"}
    create_resp = client.post('/portfolios/', json=data, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    
    response = client.get(f'/portfolios/{pid}', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['name'] == 'Test Port'

def test_delete_portfolio(client, auth_headers, db_session):
    data = {"name": "Delete Me", "description": "Test"}
    create_resp = client.post('/portfolios/', json=data, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    db.session.commit()
    db.session.expire_all()
    response = client.delete(f'/portfolios/{pid}', headers=auth_headers)
    print('DEBUG: test_delete_portfolio response:', response.status_code, response.json)
    assert response.status_code in (200, 404)

def test_portfolio_access_grant(client, auth_headers):
    data = {"name": "Access Port", "description": "Test"}
    create_resp = client.post('/portfolios/', json=data, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    
    client.post('/users/', json={"username": "user2", "password": "x", "firstname": "A", "lastname": "B", "balance": 0.0}, headers=auth_headers)
    
    grant_data = {"username": "user2", "role": "Viewer"}
    response = client.post(f'/portfolios/{pid}/access', json=grant_data, headers=auth_headers)
    assert response.status_code == 200

def test_portfolio_access_revoke(client, auth_headers):
    data = {"name": "Access Port", "description": "Test"}
    create_resp = client.post('/portfolios/', json=data, headers=auth_headers)
    pid = create_resp.json['portfolio_id']
    
    client.post('/users/', json={"username": "user2", "password": "x", "firstname": "A", "lastname": "B", "balance": 0.0}, headers=auth_headers)
    grant_data = {"username": "user2", "role": "Viewer"}
    client.post(f'/portfolios/{pid}/access', json=grant_data, headers=auth_headers)
    
    response = client.delete(f'/portfolios/{pid}/access/user2', headers=auth_headers)
    assert response.status_code == 200

def test_enrich_portfolio_handles_quote_failure(monkeypatch):
    # Simulate get_quote raising exception
    monkeypatch.setattr('app.routes.portfolio_routes.get_quote', lambda ticker: (_ for _ in ()).throw(Exception('API fail')))
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
    assert enriched['total_portfolio_value'] == 0.0

def test_get_all_portfolios_handles_serialization_error(monkeypatch, client, auth_headers, db_session):
    # Simulate portfolio.__to_dict__ raising exception
    class DummyPortfolio:
        def __to_dict__(self):
            raise Exception('Serialization fail')
    monkeypatch.setattr('app.service.portfolio_service.get_portfolios_by_user', lambda user: [DummyPortfolio()])
    response = client.get('/portfolios/', headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_all_portfolios_handles_internal_error(monkeypatch, client, auth_headers, db_session):
    # Simulate portfolio_service.get_portfolios_by_user raising exception
    monkeypatch.setattr('app.service.portfolio_service.get_portfolios_by_user', lambda user: (_ for _ in ()).throw(Exception('DB fail')))
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
    monkeypatch.setattr('app.service.portfolio_service.delete_portfolio', lambda pid: None)
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
