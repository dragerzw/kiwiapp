
from flask import Blueprint, jsonify, request, g, current_app
import logging

logger = logging.getLogger(__name__)

import app.service.portfolio_service as portfolio_service
import app.service.transaction_service as transaction_service
import app.service.user_service as user_service
from app.db import db
from app.schemas.request_schemas import PortfolioCreateSchema, AccessGrantSchema
from app.schemas.error_schemas import ErrorResponse
from app.service.alpha_vantage_client import AlphaVantageError, get_price_data
from app.auth.auth import require_auth

portfolio_bp = Blueprint('portfolio', __name__)
INTERNAL_SERVER_ERROR_MESSAGE = 'Internal server error'


def _should_include_quotes() -> bool:
    include_quotes = request.args.get('include_quotes', '').strip().lower()
    return include_quotes in {'1', 'true', 'yes', 'on'}


def _serialize_portfolio(portfolio, include_quotes: bool = False) -> dict:
    portfolio_dict = portfolio.__to_dict__()
    portfolio_dict['access_role'] = portfolio_service.get_portfolio_role(portfolio, g.username)
    if include_quotes:
        portfolio_dict = _enrich_portfolio(portfolio_dict)
    return portfolio_dict


def _get_admin_status_from_claims(claims: dict) -> bool:
    """Determine if user is admin from Cognito claims.
    
    Handles multiple variations:
    - cognito:groups or groups claim keys
    - String or list values
    - Multiple admin group name variations
    """
    groups = claims.get('cognito:groups', []) or claims.get('groups', [])
    if isinstance(groups, str):
        groups = [groups]
    admin_group_names = {'Admins', 'Admin', 'Administrators', 'Administrator'}
    return any(g in admin_group_names for g in groups)


def _enrich_portfolio(portfolio_dict: dict) -> dict:
    total_value = 0.0
    quote_error = None
    for inv in portfolio_dict.get('investments', []):
        fallback_price = inv.get('estimated_price')
        fallback_total_value = inv.get('estimated_total_value')
        try:
            price_data = get_price_data(inv['ticker'])
        except AlphaVantageError as exc:
            logger.warning('Unable to load live quote for %s: %s', inv.get('ticker'), exc)
            quote_error = quote_error or str(exc)
            price_data = None
        except Exception:
            logger.exception('Unexpected quote lookup failure for %s', inv.get('ticker'))
            quote_error = quote_error or 'Live quotes are currently unavailable.'
            price_data = None
        if price_data:
            inv['current_price'] = price_data['price']
            inv['total_value'] = price_data['price'] * inv['quantity']
        else:
            inv['current_price'] = fallback_price
            inv['total_value'] = fallback_total_value

        if isinstance(inv.get('total_value'), (int, float)):
            total_value += inv['total_value']
    
    portfolio_dict['total_portfolio_value'] = total_value
    if quote_error:
        portfolio_dict['quote_error'] = quote_error
    return portfolio_dict

@portfolio_bp.route('/', methods=['GET'])
@require_auth
def get_all_portfolios():
    try:
        claims = g.user.get('claims', {})
        is_admin = _get_admin_status_from_claims(claims)

        include_quotes = _should_include_quotes()
        
        if is_admin:
            portfolios = portfolio_service.get_all_portfolios()
        else:
            user = user_service.get_user_by_username(g.username)
            if user is None:
                error_response = ErrorResponse(error=f'User {g.username} not found', code=403)
                return jsonify(error_response.model_dump()), 403
            portfolios = portfolio_service.get_portfolios_by_user(user)
        result = []
        for p in portfolios:
            try:
                result.append(_serialize_portfolio(p, include_quotes=include_quotes))
            except Exception as ex:
                logger.error('Failed to serialize portfolio: %s', ex)
        return jsonify(result), 200
    except Exception as e:
        logger.exception('Error in get_all_portfolios: %s', e)
        error_response = ErrorResponse(error=INTERNAL_SERVER_ERROR_MESSAGE, code=500)
        return jsonify(error_response.model_dump()), 500


@portfolio_bp.route('/user/<username>', methods=['GET'])
@require_auth
def get_portfolios_by_user(username):
    try:
        user = user_service.get_user_by_username(username)
        if user is None:
            error_response = ErrorResponse(error=f'User {username} not found', code=404)
            return jsonify(error_response.model_dump()), 404
        if g.username != username:
            error_response = ErrorResponse(error='Unauthorized to view these portfolios', code=403)
            return jsonify(error_response.model_dump()), 403
        include_quotes = _should_include_quotes()
        portfolios = portfolio_service.get_portfolios_by_user(user)
        result = []
        for portfolio in portfolios:
            result.append(_serialize_portfolio(portfolio, include_quotes=include_quotes))
        return jsonify(result), 200
    except Exception as e:
        msg = str(e)
        if 'Unauthorized' in msg:
            code = 403
        elif 'not found' in msg:
            code = 404
        else:
            code = 400
        error_response = ErrorResponse(error=msg, code=code)
        return jsonify(error_response.model_dump()), code


@portfolio_bp.route('/', methods=['POST'])
@require_auth
def create_portfolio():
    req_data = PortfolioCreateSchema.model_validate(request.get_json(silent=True) or {})
    user = user_service.get_user_by_username(g.username)
    if user is None:
        error_response = ErrorResponse(error=f'User {g.username} not found', code=403)
        return jsonify(error_response.model_dump()), 403
    portfolio = portfolio_service.create_portfolio(
        name=req_data.name,
        description=req_data.description,
        user=user,
    )
    if portfolio is None:
        error_response = ErrorResponse(error='Invalid portfolio input', code=400)
        return jsonify(error_response.model_dump()), 400
    db.session.commit()
    return jsonify({'message': 'Portfolio created successfully', 'portfolio_id': portfolio.id}), 201





@portfolio_bp.route('/<int:portfolio_id>/transactions', methods=['GET'])
@require_auth
def get_portfolio_transactions(portfolio_id):
    if not portfolio_service.has_portfolio_access(portfolio_id, g.username, ['Owner', 'Manager', 'Viewer']):
        error_response = ErrorResponse(error='Unauthorized to view this portfolio info', code=403)
        return jsonify(error_response.model_dump()), 403
    transactions = transaction_service.get_transactions_by_portfolio_id(portfolio_id)
    return jsonify([transaction.__to_dict__() for transaction in transactions]), 200

@portfolio_bp.route('/<int:portfolio_id>', methods=['GET'])
@require_auth
def get_portfolio(portfolio_id):
    try:
        portfolio = portfolio_service.get_portfolio_by_id(portfolio_id)
        if portfolio is None:
            error_response = ErrorResponse(error=f'Portfolio {portfolio_id} not found', code=404)
            return jsonify(error_response.model_dump()), 404
        # Authorization check
        if not portfolio_service.has_portfolio_access(portfolio_id, g.username, ['Owner', 'Manager', 'Viewer']):
            error_response = ErrorResponse(error='Unauthorized to view this portfolio info', code=403)
            return jsonify(error_response.model_dump()), 403
        return jsonify(_serialize_portfolio(portfolio, include_quotes=True)), 200
    except Exception as e:
        logger.exception('Error in get_portfolio: %s', e)
        error_response = ErrorResponse(error=INTERNAL_SERVER_ERROR_MESSAGE, code=500)
        return jsonify(error_response.model_dump()), 500

@portfolio_bp.route('/<int:portfolio_id>/access', methods=['POST'])
@require_auth
def grant_access(portfolio_id):
    # Validate request data first so ValidationError reaches the global 422 handler
    req_data = AccessGrantSchema.model_validate(request.get_json(silent=True) or {})
    try:
        if not portfolio_service.has_portfolio_access(portfolio_id, g.username, ['Owner']):
            error_response = ErrorResponse(error='Only the Owner can grant access to this portfolio', code=403)
            return jsonify(error_response.model_dump()), 403
        result = portfolio_service.grant_portfolio_access(portfolio_id, req_data.username, req_data.role)
        if result is None:
            error_response = ErrorResponse(error='Invalid portfolio access grant', code=400)
            return jsonify(error_response.model_dump()), 400
        db.session.commit()
        return jsonify({'message': 'Portfolio access granted successfully'}), 200
    except Exception as e:
        logger.exception('Error in grant_access: %s', e)
        error_response = ErrorResponse(error=INTERNAL_SERVER_ERROR_MESSAGE, code=500)
        return jsonify(error_response.model_dump()), 500

@portfolio_bp.route('/<int:portfolio_id>', methods=['DELETE'])
@require_auth
def delete_portfolio(portfolio_id):
    try:
        logger.debug('delete_portfolio called for id: %s', portfolio_id)
        
        claims = g.user.get('claims', {})
        is_admin = _get_admin_status_from_claims(claims)

        if not portfolio_service.has_portfolio_access(portfolio_id, g.username, ['Owner']) and not is_admin:
            logger.debug('No access for user: %s', g.username)
            error_response = ErrorResponse(error='Only the Owner (or an Admin) can delete this portfolio', code=403)
            return jsonify(error_response.model_dump()), 403
        portfolio_service.delete_portfolio(portfolio_id)
        db.session.commit()
        logger.debug('Portfolio deleted and committed: %s', portfolio_id)
        return jsonify({'message': 'Portfolio deleted successfully'}), 200
    except portfolio_service.UnsupportedPortfolioOperationError as e:
        error_response = ErrorResponse(error=str(e), code=400)
        return jsonify(error_response.model_dump()), 400
    except portfolio_service.PortfolioOperationError as e:
        logger.debug('Portfolio not found for delete: %s', portfolio_id)
        error_response = ErrorResponse(error=str(e), code=404)
        return jsonify(error_response.model_dump()), 404
    except Exception as e:
        logger.exception('Error in delete_portfolio: %s', e)
        error_response = ErrorResponse(error='Internal server error', code=500)
        return jsonify(error_response.model_dump()), 500

@portfolio_bp.route('/<int:portfolio_id>/access/<username>', methods=['DELETE'])
@require_auth
def revoke_access(portfolio_id, username):
    if not portfolio_service.has_portfolio_access(portfolio_id, g.username, ['Owner']):
        error_response = ErrorResponse(error='Only the Owner can revoke access to this portfolio', code=403)
        return jsonify(error_response.model_dump()), 403
    portfolio_service.revoke_portfolio_access(portfolio_id, username)
    db.session.commit()
    return jsonify({'message': 'Portfolio access revoked successfully'}), 200
