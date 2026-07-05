import pytest
from flask import jsonify

from app.auth import require_auth


@pytest.fixture(scope="module", autouse=True)
def setup_auth_route(app):
    with app.app_context():
        # Set up dummy CognitoTokenValidator
        from app.auth.auth import CognitoTokenValidator
        app.config['COGNITO_VALIDATOR'] = CognitoTokenValidator("dummy-region", "dummy-pool", "dummy-client")
        @app.route('/test_protected')
        @require_auth
        def test_protected():
            from flask import g
            if hasattr(g, 'user') and g.user and 'username' in g.user:
                return jsonify(username=g.user['username']), 200
            return jsonify(success=True), 200

def test_missing_auth_header(client, app):
    response = client.get('/test_protected')
    assert response.status_code == 401
    assert b"Missing authentication Token" in response.data

def test_invalid_bearer(client, app):
    response = client.get('/test_protected', headers={"Authorization": "Token 123"})
    assert response.status_code == 401
    assert b"Missing authentication Token" in response.data

def test_valid_token_mocked(client, app, monkeypatch):
    monkeypatch.setattr('app.auth.auth.jwt.get_unverified_header', lambda x: {"kid": "key1"})
    monkeypatch.setattr('app.auth.auth.CognitoTokenValidator._get_jwks', lambda self: {"keys": [{"kid": "key1", "kty": "RSA", "alg": "RS256"}]})

    def mock_decode(*args, **kwargs):
        return {
            "sub": "user123",
            "username": "testuser",
            "token_use": "id",
            "aud": "dummy-client",
            "iss": "https://cognito-idp.dummy-region.amazonaws.com/dummy-pool",
        }
    monkeypatch.setattr('app.auth.auth.jwt.decode', mock_decode)

    response = client.get('/test_protected', headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert response.json["username"] == "testuser"

def test_valid_access_token_mocked(client, app, monkeypatch):
    monkeypatch.setattr('app.auth.auth.jwt.get_unverified_header', lambda x: {"kid": "key1"})
    monkeypatch.setattr('app.auth.auth.CognitoTokenValidator._get_jwks', lambda self: {"keys": [{"kid": "key1", "kty": "RSA", "alg": "RS256"}]})

    def mock_decode(*args, **kwargs):
        return {
            "sub": "user123",
            "username": "testuser",
            "token_use": "access",
            "client_id": "dummy-client",
            "iss": "https://cognito-idp.dummy-region.amazonaws.com/dummy-pool",
        }
    monkeypatch.setattr('app.auth.auth.jwt.decode', mock_decode)

    response = client.get('/test_protected', headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert response.json["username"] == "testuser"

def test_expired_token(client, app, monkeypatch):
    monkeypatch.setattr('app.auth.auth.jwt.get_unverified_header', lambda x: {"kid": "key1"})
    monkeypatch.setattr('app.auth.auth.CognitoTokenValidator._get_jwks', lambda self: {"keys": [{"kid": "key1", "kty": "RSA", "alg": "RS256"}]})

    from jose.exceptions import ExpiredSignatureError
    def mock_decode_expired(*args, **kwargs):
        raise ExpiredSignatureError("Expired")
    monkeypatch.setattr('app.auth.auth.jwt.decode', mock_decode_expired)

    response = client.get('/test_protected', headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 401
    assert b"Token validation failed" in response.data

