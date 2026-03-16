from flask import Blueprint, jsonify, request, g

import app.service.transaction_service as transaction_service
import app.service.user_service as user_service
from app.db import db
from app.schemas.user_schemas import UserCreateRequest, UserUpdateBalanceRequest
from app.auth import require_auth
from sqlalchemy.exc import IntegrityError
from app.schemas.error_schemas import ErrorResponse

user_bp = Blueprint('user', __name__)


@user_bp.route('/', methods=['GET'])
@require_auth
def get_users():
    try:
        user = user_service.get_user_by_username(g.username)
        if user is None:
            error_response = ErrorResponse(error=f'User {g.username} not found', code=403)
            return jsonify(error_response.model_dump()), 403
        return jsonify([user.__to_dict__()]), 200
    except user_service.UnsupportedUserOperationError as e:
        error_response = ErrorResponse(error=str(e), code=400)
        return jsonify(error_response.model_dump()), 400


@user_bp.route('/<username>', methods=['GET'])
@require_auth
def get_user(username):
    try:
        if g.username != username:
            error_response = ErrorResponse(error='Unauthorized to view this user', code=403)
            return jsonify(error_response.model_dump()), 403
        user = user_service.get_user_by_username(username)
        if user is None:
            error_response = ErrorResponse(error=f'User {username} not found', code=403)
            return jsonify(error_response.model_dump()), 403
        return jsonify(user.__to_dict__()), 200
    except user_service.UnsupportedUserOperationError as e:
        error_response = ErrorResponse(error=str(e), code=400)
        return jsonify(error_response.model_dump()), 400


@user_bp.route('/', methods=['POST'])
@require_auth
def create_user():
    req_data = UserCreateRequest(**(request.get_json(silent=True) or {}))
    existing_user = user_service.get_user_by_username(req_data.username)
    if existing_user:
        error_response = ErrorResponse(error='Username already exists', code=403)
        return jsonify(error_response.model_dump()), 403
    try:
        user_service.create_user(
            username=req_data.username,
            password=req_data.password,
            firstname=req_data.firstname,
            lastname=req_data.lastname,
            balance=req_data.balance,
        )
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except IntegrityError:
        db.session.rollback()
        error_response = ErrorResponse(error='Username already exists', code=403)
        return jsonify(error_response.model_dump()), 403


@user_bp.route('/update-balance', methods=['PUT'])
@require_auth
def update_balance():
    req_data = UserUpdateBalanceRequest(**(request.get_json(silent=True) or {}))
    if req_data.username != g.username:
        error_response = ErrorResponse(error='Unauthorized to update this user balance', code=403)
        return jsonify(error_response.model_dump()), 403
    user = user_service.get_user_by_username(req_data.username)
    if user is None:
        error_response = ErrorResponse(error=f'User {req_data.username} not found', code=403)
        return jsonify(error_response.model_dump()), 403
    user_service.update_user_balance(username=req_data.username, new_balance=req_data.new_balance)
    db.session.commit()
    return jsonify({'message': 'User balance updated successfully'}), 200


@user_bp.route('/<username>', methods=['DELETE'])
@require_auth
def delete_user(username):
    if g.username != username:
        error_response = ErrorResponse(error='Unauthorized to delete this user', code=403)
        return jsonify(error_response.model_dump()), 403
    if username == 'admin':
        error_response = ErrorResponse(error='Cannot delete admin user', code=400)
        return jsonify(error_response.model_dump()), 400
    user = user_service.get_user_by_username(username)
    if user is None:
        error_response = ErrorResponse(error=f'User {username} not found', code=403)
        return jsonify(error_response.model_dump()), 403
    user_service.delete_user(username)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200


@user_bp.route('/<username>/transactions', methods=['GET'])
@require_auth
def get_user_transactions(username):
    if g.username != username:
        error_response = ErrorResponse(error='Unauthorized to view these transactions', code=403)
        return jsonify(error_response.model_dump()), 403
    user = user_service.get_user_by_username(username)
    if user is None:
        error_response = ErrorResponse(error=f'User {username} not found', code=403)
        return jsonify(error_response.model_dump()), 403
    transactions = transaction_service.get_transactions_by_user(username)
    return jsonify([transaction.__to_dict__() for transaction in transactions]), 200
