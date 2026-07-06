import os

from flask import Flask, jsonify
from flask_cors import CORS
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from app.cache import cache
from app.db import db
from app.routes import portfolio_bp, security_bp, trade_bp, user_bp
from app.schemas.error_schemas import ErrorResponse


def _parse_cors_origins(cors_origins):
    if isinstance(cors_origins, str) and cors_origins != '*':
        return [origin.strip() for origin in cors_origins.split(',') if origin.strip()]
    return cors_origins


def _seed_default_dev_user(app):
    if not app.config.get('SEED_DEFAULT_DEV_USER', False):
        return

    seed_username = os.environ.get('DEFAULT_DEV_USERNAME')
    seed_password = os.environ.get('DEFAULT_DEV_PASSWORD')

    if not seed_username or not seed_password:
        app.logger.warning(
            'SEED_DEFAULT_DEV_USER is enabled but DEFAULT_DEV_USERNAME/DEFAULT_DEV_PASSWORD are missing',
        )
        return

    from app.service import user_service

    if user_service.get_user_by_username(seed_username):
        return

    seed_firstname = os.environ.get('DEFAULT_DEV_FIRSTNAME', 'Dev')
    seed_lastname = os.environ.get('DEFAULT_DEV_LASTNAME', 'User')
    seed_balance_raw = os.environ.get('DEFAULT_DEV_BALANCE', '1000.0')
    try:
        seed_balance = float(seed_balance_raw)
    except (TypeError, ValueError):
        app.logger.warning(
            "Invalid DEFAULT_DEV_BALANCE value %r; falling back to 1000.0",
            seed_balance_raw,
        )
        seed_balance = 1000.0
    user_service.create_user(
        username=seed_username,
        password=seed_password,
        firstname=seed_firstname,
        lastname=seed_lastname,
        balance=seed_balance,
    )
    db.session.commit()


def _configure_cognito_validator(app):
    from app.auth.auth import CognitoTokenValidator

    region = app.config.get('COGNITO_REGION')
    user_pool_id = app.config.get('COGNITO_USER_POOL_ID')
    app_client_id = app.config.get('COGNITO_APP_CLIENT_ID')

    if not user_pool_id or not app_client_id:
        app.logger.warning("Cognito User Pool ID or App Client ID missing; skipping Cognito validator setup.")
        return

    app.config['COGNITO_VALIDATOR'] = CognitoTokenValidator(region, user_pool_id, app_client_id)


def _configure_arcjet(app):
    from arcjet import Mode, arcjet_sync, detect_bot, fixed_window, shield
    from flask import jsonify, request

    aj_key = os.environ.get("ARCJET_KEY")
    if not aj_key:
        app.logger.warning("ARCJET_KEY is not set. Arcjet protection is disabled.")
        return

    aj = arcjet_sync(
        key=aj_key,
        rules=[
            shield(mode=Mode.LIVE),
            detect_bot(
                mode=Mode.LIVE,
                allow=["CATEGORY:SEARCH_ENGINE", "CATEGORY:MONITOR"]
            ),
            fixed_window(
                mode=Mode.LIVE,
                max=100,
                window=60,
            ),
        ],
    )

    @app.before_request
    def arcjet_middleware():
        decision = aj.protect(request)
        if decision.is_denied():
            from app.schemas.error_schemas import ErrorResponse
            if decision.reason.is_rate_limit():
                return jsonify(ErrorResponse(error="Too Many Requests", code=429).model_dump()), 429
            return jsonify(ErrorResponse(error="Forbidden", code=403).model_dump()), 403


def _register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        code = getattr(e, 'code', 500)
        error_response = ErrorResponse(error=e.description or e.name, code=code)
        return jsonify(error_response.model_dump()), code

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        first_error = error.errors()[0]
        error_message = f"{first_error['loc'][0]}: {first_error['msg']}"
        error_response = ErrorResponse(error=error_message, code=422)
        return jsonify(error_response.model_dump()), 422


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    # Configure CORS after loading settings to allow restricted origins
    CORS(app, origins=_parse_cors_origins(app.config.get('CORS_ORIGINS', '*')))

    @app.route("/", methods=['GET'])
    def home():
        return jsonify({"message": "Portfolio Management API is running"})

    # register extensions
    db.init_app(app)
    cache.init_app(app)
    with app.app_context():
        if app.config.get('AUTO_CREATE_SCHEMA', False):
            db.create_all()
        _seed_default_dev_user(app)

    _configure_cognito_validator(app)
    _configure_arcjet(app)

    # register blueprints
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(portfolio_bp, url_prefix='/portfolios')
    app.register_blueprint(security_bp, url_prefix='/securities')
    app.register_blueprint(trade_bp, url_prefix='/trades')

    _register_error_handlers(app)

    @app.errorhandler(404)
    def handle_not_found(error):
        error_response = ErrorResponse(error="Resource not found", code=404)
        return jsonify(error_response.model_dump()), 404

    # Domain exception handlers
    from app.service.portfolio_service import UnsupportedPortfolioOperationError
    from app.service.trade_service import InsufficientFundsError, TradeExecutionException
    from app.service.user_service import UnsupportedUserOperationError

    @app.errorhandler(UnsupportedUserOperationError)
    def handle_user_error(e):
        msg = str(e)
        if 'Unauthorized' in msg:
            code = 403
        elif 'not found' in msg:
            code = 404
        else:
            code = 400
        error_response = ErrorResponse(error=msg, code=code)
        return jsonify(error_response.model_dump()), code

    @app.errorhandler(UnsupportedPortfolioOperationError)
    def handle_portfolio_error(e):
        msg = str(e)
        if 'Unauthorized' in msg:
            code = 403
        elif 'not found' in msg:
            code = 404
        else:
            code = 400
        error_response = ErrorResponse(error=msg, code=code)
        return jsonify(error_response.model_dump()), code

    @app.errorhandler(TradeExecutionException)
    def handle_trade_error(e):
        error_response = ErrorResponse(error=str(e), code=400)
        return jsonify(error_response.model_dump()), 400

    @app.errorhandler(InsufficientFundsError)
    def handle_insufficient_funds_error(e):
        error_response = ErrorResponse(error=str(e), code=400)
        return jsonify(error_response.model_dump()), 400

    @app.errorhandler(Exception)
    def handle_exception(e):
        db.session.rollback()
        detail = str(e) if app.debug else 'An unexpected error occurred'
        error_response = ErrorResponse(error=detail, code=500)
        return jsonify(error_response.model_dump()), 500

    return app
