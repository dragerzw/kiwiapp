from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
from typing import Generator

import pytest
from app import create_app
from app.config import TestConfig
from app.db import db
from sqlalchemy.orm import sessionmaker
from app.models import User
from sqlalchemy.orm import Session


@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    # Inject test session into config
    TestConfig.TEST_SESSION = db.session
    app = create_app(TestConfig)
    ctx = app.app_context()
    ctx.push()
    db.create_all()
    yield app
    db.drop_all()
    ctx.pop()


@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def auth_headers(monkeypatch):
    """Provides valid authorization headers for tests."""
    monkeypatch.setattr('app.auth.auth.jwt.get_unverified_header', lambda x: {"kid": "key1"})
    monkeypatch.setattr('app.auth.auth.CognitoTokenValidator._get_jwks', lambda self: {"keys": [{"kid": "key1", "kty": "RSA", "alg": "RS256"}]})
    monkeypatch.setattr('jose.backends.rsa_backend.RSAKey._process_jwk', lambda self, jwk_dict: "dummy_rsa_key")
    
    def mock_decode(*args, **kwargs):
        return {"sub": "admin", "username": "admin"}
    monkeypatch.setattr('app.auth.auth.jwt.decode', mock_decode)

    return {"Authorization": "Bearer validtoken"}


@pytest.fixture(scope='function', autouse=True)
def db_session(app) -> Generator[Session]:
    """A database session scoped to a single test function."""
    # Use a single in-memory SQLite connection for app and tests
    connection = db.engine.connect()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db.session.bind = connection
    with app.app_context():
        db.create_all()
        _populate_database(db.session)
        try:
            yield db.session
            db.session.rollback()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        finally:
            db.session.remove()
            db.drop_all()
            connection.close()


def _populate_database(session):
    def get_or_create_user(username, password, firstname, lastname, balance):
        user = session.query(User).filter_by(username=username).one_or_none()
        if user:
            return user
        user = User(username=username, password=password, firstname=firstname, lastname=lastname, balance=balance)
        session.add(user)
        session.commit()
        return user

    admin_user = get_or_create_user('admin', 'admin', 'Admin', 'User', 1000.00)
    user2 = get_or_create_user('user2', 'pwd', 'User', 'Two', 500.00)
    user3 = get_or_create_user('other_user', 'pwd', 'Other', 'User', 300.00)
    # Optionally, add portfolios for admin and user2
    from app.models import Portfolio, PortfolioAccess
    port1 = Portfolio(name='Test Port', description='Test', user=admin_user, owner=admin_user.username)
    port2 = Portfolio(name='Access Port', description='Access', user=admin_user, owner=admin_user.username)
    port3 = Portfolio(name='Delete Me', description='Delete', user=admin_user, owner=admin_user.username)
    session.add(port1)
    session.add(port2)
    session.add(port3)
    session.commit()
    # Grant access
    access_admin1 = PortfolioAccess(username='admin', portfolio_id=port1.id, role='Owner')
    access_admin2 = PortfolioAccess(username='admin', portfolio_id=port2.id, role='Owner')
    access_admin3 = PortfolioAccess(username='admin', portfolio_id=port3.id, role='Owner')
    access_user2 = PortfolioAccess(username='user2', portfolio_id=port2.id, role='Viewer')
    session.add(access_admin1)
    session.add(access_admin2)
    session.add(access_admin3)
    session.add(access_user2)
    session.commit()
