from flask import Blueprint, jsonify, request, g

from app.db import db
from app.schemas.request_schemas import TradeSchema
from app.service import trade_service
from app.service.trade_service import TradeExecutionException
from app.service.portfolio_service import has_portfolio_access
from app.service.alpha_vantage_client import AlphaVantageError, get_price_data
from app.auth.auth import require_auth
from app.schemas.error_schemas import ErrorResponse

trade_bp = Blueprint('trade', __name__)


@trade_bp.route('/buy', methods=['POST'])
@require_auth
def buy_trade():
    req_data = TradeSchema.model_validate(request.get_json(silent=True) or {})
    if not has_portfolio_access(req_data.portfolio_id, g.username, ['Owner', 'Manager']):
        error_response = ErrorResponse(error='Unauthorized to trade on this portfolio', code=403)
        return jsonify(error_response.model_dump()), 403
    trade_service.execute_purchase_order(
        portfolio_id=req_data.portfolio_id,
        ticker=req_data.ticker,
        quantity=req_data.quantity,
    )
    db.session.commit()
    return jsonify({'message': 'Purchase order executed successfully'}), 201


@trade_bp.route('/sell', methods=['POST'])
@require_auth
def sell_trade():
    req_data = TradeSchema.model_validate(request.get_json(silent=True) or {})
    if not has_portfolio_access(req_data.portfolio_id, g.username, ['Owner', 'Manager']):
        error_response = ErrorResponse(error='Unauthorized to trade on this portfolio', code=403)
        return jsonify(error_response.model_dump()), 403
    try:
        price_data = get_price_data(req_data.ticker)
    except AlphaVantageError as e:
        raise TradeExecutionException(str(e)) from e
    if not price_data:
        raise TradeExecutionException(f'Could not fetch price for {req_data.ticker}')
    trade_service.liquidate_investment(
        portfolio_id=req_data.portfolio_id,
        ticker=req_data.ticker,
        quantity=req_data.quantity,
        sale_price=price_data['price'],
    )
    db.session.commit()
    return jsonify({'message': 'Investment liquidated successfully'}), 200
