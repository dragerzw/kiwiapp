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


class CognitoTokenValidationError(Exception):
    pass


def _safe_header_diagnostics(token: str) -> Dict:
    try:
        header = jwt.get_unverified_header(token)
    except JWTError:
        header = {}

    return {
        'kid': header.get('kid'),
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
            raise CognitoTokenValidationError('Unable to find matching signing key')
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
            raise CognitoTokenValidationError('Token has expired')
        except JWTClaimsError as e:
            raise CognitoTokenValidationError(f'Invalid claims in token (check audience/issuer): {str(e)}')
        except JWTError as e:
            raise CognitoTokenValidationError(f'Token validation failed: {str(e)}')


def get_token_from_header():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header:
        return None
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    return parts[1]


def _extract_username_from_claims(claims: Dict) -> str:
    return (claims.get('cognito:username') or claims.get('username') or '').strip()


def _maybe_provision_user_from_claims(username: str, claims: Dict) -> None:
    if not current_app.config.get('ENABLE_AUTH_JIT_PROVISIONING', False):
        return

    from app.service import user_service
    from app.db import db

    try:
        user = user_service.get_user_by_username(username)
        if user is None:
            current_app.logger.info('Provisioning new user for Cognito username: %s', username)
            user_service.create_user(
                username=username,
                password=secrets.token_urlsafe(24),
                firstname=claims.get('given_name') or claims.get('name') or 'User',
                lastname=claims.get('family_name') or '',
                balance=1000.0,
            )
            db.session.commit()
    except IntegrityError:
        db.session.rollback()
        current_app.logger.info('User %s already exists, skipping JIT provisioning', username)


def _auth_error_response(message: str, code: int):
    from app.schemas.error_schemas import ErrorResponse
    return jsonify(ErrorResponse(error=message, code=code).model_dump()), code


def _log_auth_validation_failure(token: str, error: Exception) -> None:
    if current_app.config.get('ENABLE_DEBUG_AUTH_DIAGNOSTICS', False):
        current_app.logger.warning(
            'Auth validation failed: %s | diagnostics=%s',
            str(error),
            _safe_header_diagnostics(token),
        )
    else:
        current_app.logger.warning('Auth validation failed: %s', str(error))

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return _auth_error_response("Missing authentication Token", 401)
        validator = current_app.config.get('COGNITO_VALIDATOR')
        if not validator:
            return _auth_error_response("Missing cognito token validator in the app configuration.", 500)
        try:
            claims = validator.validate_token(token)
            username = _extract_username_from_claims(claims)
            if not username:
                raise CognitoTokenValidationError('Token missing username claim')

            _maybe_provision_user_from_claims(username, claims)

            g.user = {'user_id': claims.get('sub'), 'username': username, 'claims': claims}
            g.username = username
        except CognitoTokenValidationError as e:
            _log_auth_validation_failure(token, e)
            return _auth_error_response("Token validation failed: " + str(e), 401)
        except Exception as e:
            current_app.logger.warning('Unexpected auth failure: %s', str(e))
            return _auth_error_response("Token validation failed: " + str(e), 401)
        return f(*args, **kwargs)
    return decorated_function
