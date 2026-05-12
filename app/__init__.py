import os

from flask import Flask, jsonify
from flask_cors import CORS
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from app.db import db
from app.cache import cache
from app.routes import portfolio_bp, security_bp, trade_bp, user_bp
from app.schemas.error_schemas import ErrorResponse


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Configure CORS after loading settings to allow restricted origins
    cors_origins = app.config.get('CORS_ORIGINS', '*')
    CORS(app, origins=cors_origins)

    @app.route("/")
    def home():
        return jsonify({"message": "Portfolio Management API is running"})

    # register extensions
    db.init_app(app)
    cache.init_app(app)
    with app.app_context():
        if app.config.get('AUTO_CREATE_SCHEMA', False):
            db.create_all()

        if app.config.get('SEED_DEFAULT_DEV_USER', False):
            seed_username = os.environ.get('DEFAULT_DEV_USERNAME')
            seed_password = os.environ.get('DEFAULT_DEV_PASSWORD')

            if not seed_username or not seed_password:
                app.logger.warning(
                    'SEED_DEFAULT_DEV_USER is enabled but DEFAULT_DEV_USERNAME/DEFAULT_DEV_PASSWORD are missing',
                )
            else:
                from app.service import user_service

                if not user_service.get_user_by_username(seed_username):
                    seed_firstname = os.environ.get('DEFAULT_DEV_FIRSTNAME', 'Dev')
                    seed_lastname = os.environ.get('DEFAULT_DEV_LASTNAME', 'User')
                    seed_balance = float(os.environ.get('DEFAULT_DEV_BALANCE', '1000.0'))
                    user_service.create_user(
                        username=seed_username,
                        password=seed_password,
                        firstname=seed_firstname,
                        lastname=seed_lastname,
                        balance=seed_balance,
                    )
                    db.session.commit()

    # Cognito validator setup
    from app.auth.auth import CognitoTokenValidator
    region = app.config.get('COGNITO_REGION')
    user_pool_id = app.config.get('COGNITO_USER_POOL_ID')
    app_client_id = app.config.get('COGNITO_APP_CLIENT_ID')
    app.config['COGNITO_VALIDATOR'] = CognitoTokenValidator(region, user_pool_id, app_client_id)

    # register blueprints
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(portfolio_bp, url_prefix='/portfolios')
    app.register_blueprint(security_bp, url_prefix='/securities')
    app.register_blueprint(trade_bp, url_prefix='/trades')

    # Register error handlers
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

    @app.errorhandler(404)
    def handle_not_found(error):
        error_response = ErrorResponse(error="Resource not found", code=404)
        return jsonify(error_response.model_dump()), 404

    # Domain exception handlers
    from app.service.user_service import UnsupportedUserOperationError
    from app.service.portfolio_service import UnsupportedPortfolioOperationError
    from app.service.trade_service import TradeExecutionException, InsufficientFundsError

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
