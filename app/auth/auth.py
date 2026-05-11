from functools import wraps
from typing import Dict, Optional

import requests
from flask import current_app, jsonify, request, g
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error_message: str
    request_id: str = ''

def _get_session() -> requests.Session:
    """Create a requests session that ignores system proxy environment variables.
    This ensures the JWKS fetch goes directly to Cognito without being intercepted.
    """
    session = requests.Session()
    session.trust_env = False  # Disable proxy handling
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

    def validate_token(self, token: str) -> Dict:
        signing_key = self._get_signing_key(token)
        if not signing_key:
            raise Exception('Unable to find matching signing key')
        try:
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=['RS256'],
                audience=self.app_client_id,
                issuer=self.issuer,
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_aud': True,
                    'verify_iss': True,
                },
            )
            return claims
        except ExpiredSignatureError:
            raise Exception('Token has expired')
        except JWTClaimsError:
            raise Exception('Invalid claims in token (check audience/issuer)')
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
            g.user = {'user_id': claims.get('sub'), 'username': username, 'claims': claims}
            g.username = username
        except Exception as e:
            from app.schemas.error_schemas import ErrorResponse
            return jsonify(ErrorResponse(error="Token validation failed: " + str(e), code=401).model_dump()), 401
        return f(*args, **kwargs)
    return decorated_function
