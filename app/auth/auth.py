from functools import wraps
from typing import Dict, Optional
import secrets

import requests
from flask import current_app, jsonify, request, g
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error_message: str
    request_id: str = ''


def _safe_claim_diagnostics(token: str) -> Dict:
    try:
        claims = jwt.get_unverified_claims(token)
    except JWTError:
        claims = {}

    try:
        header = jwt.get_unverified_header(token)
    except JWTError:
        header = {}

    return {
        'kid': header.get('kid'),
        'iss_present': 'iss' in claims,
        'aud_present': 'aud' in claims,
        'client_id_present': 'client_id' in claims,
        'token_use': claims.get('token_use'),
        'sub_present': 'sub' in claims,
    }

def _get_session() -> requests.Session:
    """Create a requests session for JWKS fetching.
    By default, requests will honor system/environment proxy settings. Proxy
    handling is only disabled when the application explicitly enables the
    DISABLE_OUTBOUND_PROXIES configuration flag.
    """
    session = requests.Session()
    if current_app.config.get('DISABLE_OUTBOUND_PROXIES', False):
        session.trust_env = False  # Disable proxy handling only when configured
    return session

class CognitoTokenValidator:
    def __init__(self, region: str, user_pool_id: str, app_client_id: str):
        self.region = region
        self.user_pool_id = user_pool_id
        self.app_client_id = app_client_id
        self.issuer = f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}'
        self.jwks_url = f'{self.issuer}/.well-known/jwks.json'
        self._jwks = None

    def _get_jwks(self) -> Dict:
        if self._jwks is None:
            session = _get_session()
            response = session.get(self.jwks_url)
            response.raise_for_status()
            self._jwks = response.json()
        return self._jwks

    def _get_signing_key(self, token: str) -> Optional[Dict]:
        try:
            header = jwt.get_unverified_header(token)
            kid = header.get('kid')
            if not kid:
                return None
            jwks = self._get_jwks()
            for key in jwks.get('keys', []):
                if key.get('kid') == kid:
                    return key
            return None
        except JWTError:
            return None

    def _has_expected_audience(self, audience_claim) -> bool:
        if isinstance(audience_claim, list):
            return self.app_client_id in audience_claim
        return audience_claim == self.app_client_id

    def _validate_verified_claims(self, claims: Dict) -> Dict:
        if claims.get('iss') != self.issuer:
            raise JWTClaimsError('Invalid issuer')

        token_use = claims.get('token_use')
        if token_use == 'access':
            if claims.get('client_id') != self.app_client_id:
                raise JWTClaimsError('Invalid access token client_id')
            return claims

        if self._has_expected_audience(claims.get('aud')):
            return claims

        if claims.get('client_id') == self.app_client_id:
            return claims

        raise JWTClaimsError('Invalid token audience/client_id')

    def validate_token(self, token: str) -> Dict:
        signing_key = self._get_signing_key(token)
        if not signing_key:
            raise Exception('Unable to find matching signing key')
        try:
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=['RS256'],
                issuer=self.issuer,
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_aud': False,
                    'verify_iss': True,
                    'verify_at_hash': False,
                },
            )
            return self._validate_verified_claims(claims)
        except ExpiredSignatureError:
            raise Exception('Token has expired')
        except JWTClaimsError as e:
            raise Exception(f'Invalid claims in token (check audience/issuer): {str(e)}')
        except JWTError as e:
            raise Exception(f'Token validation failed: {str(e)}')


def get_token_from_header():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header:
        return None
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    return parts[1]

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            from app.schemas.error_schemas import ErrorResponse
            return jsonify(ErrorResponse(error="Missing authentication Token", code=401).model_dump()), 401
        validator = current_app.config.get('COGNITO_VALIDATOR')
        if not validator:
            from app.schemas.error_schemas import ErrorResponse
            return jsonify(ErrorResponse(error="Missing cognito token validator in the app configuration.", code=500).model_dump()), 500
        try:
            claims = validator.validate_token(token)
            username = claims.get('cognito:username') or claims.get('username')

            if current_app.config.get('ENABLE_AUTH_JIT_PROVISIONING', False):
                from app.service import user_service
                from app.db import db

                user = user_service.get_user_by_username(username)
                if user is None:
                    current_app.logger.info('Provisioning new user for Cognito username: %s', username)
                    user_service.create_user(
                        username=username,
                        password=secrets.token_urlsafe(24),
                        firstname=claims.get('given_name') or claims.get('name') or 'User',
                        lastname=claims.get('family_name') or '',
                        balance=0.0,
                    )
                    db.session.commit()

            g.user = {'user_id': claims.get('sub'), 'username': username, 'claims': claims}
            g.username = username
        except Exception as e:
            if current_app.config.get('ENABLE_DEBUG_AUTH_DIAGNOSTICS', False):
                current_app.logger.warning(
                    'Auth validation failed: %s | diagnostics=%s',
                    str(e),
                    _safe_claim_diagnostics(token),
                )
            else:
                current_app.logger.warning('Auth validation failed: %s', str(e))
            from app.schemas.error_schemas import ErrorResponse
            return jsonify(ErrorResponse(error="Token validation failed: " + str(e), code=401).model_dump()), 401
        return f(*args, **kwargs)
    return decorated_function
