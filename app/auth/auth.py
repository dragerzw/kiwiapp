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
            response = requests.get(self.jwks_url)
            response.raise_for_status()
            self._jwks = response.json()
        return self._jwks

    def _get_signing_key(self, token: str) -> Optional[Dict]:
        try:
            # Decode header without verification to get the key ID (kid)
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

        # Get the signing key
        signing_key = self._get_signing_key(token)
        if not signing_key:
            raise Exception('Unable to find matching signing key')

        try:
            # Decode and validate the token
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=['RS256'],
                audience=self.app_client_id,  # Validates the token was issued for this app
                issuer=self.issuer,  # Validates the token came from this user pool
                options={
                    'verify_signature': True,
                    'verify_exp': True,  # Verify expiration
                    'verify_aud': True,  # Verify audience
                    'verify_iss': True,  # Verify issuer
                }
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

def requires_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return jsonify(
                ErrorResponse(error_message='Missing authentication Token', request_id='').model_dump()
            ), 401
        # Retrieve the validator instance from the Flask app config
        validator = current_app.config.get('COGNITO_VALIDATOR')  # TODO: Add cognito validator to the app config
        if not validator:
            return jsonify(
                ErrorResponse(
                    error_message='Missing cognito token validator in the app configuration.', request_id=''
                ).model_dump()
            ), 500
        try:
            # Validate token and store claims in Flask's global request context
            claims = validator.validate_token(token)
            g.user = {'user_id': claims.get('sub'), 'username': claims.get('username'), 'claims': claims}
        except Exception as e:
            return jsonify(
                ErrorResponse(error_message='Token validation failed', request_id='').model_dump()
            ), 401
        return f(*args, **kwargs)
    return decorated_function