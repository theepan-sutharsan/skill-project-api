from flask import Blueprint, request, jsonify
from flask_jwt_extended import current_user

from app.controllers import user_controller
from app.middleware import admin_required, login_required

user_bp = Blueprint("users", __name__, url_prefix="/api/users")


@user_bp.route("", methods=["GET"])
@login_required
def get_users():
    search = request.args.get("search")
    location = request.args.get("location")
    response, status = user_controller.get_users(search=search, location=location)
    return jsonify(response), status


@user_bp.route("/me", methods=["GET"])
@login_required
def get_me():
    response, status = user_controller.get_user(current_user.users_id)
    return jsonify(response), status


@user_bp.route("/<int:user_id>", methods=["GET"])
@login_required
def get_user(user_id):
    response, status = user_controller.get_user(user_id)
    return jsonify(response), status


@user_bp.route("/<int:user_id>", methods=["PUT"])
@login_required
def update_user(user_id):
    data = request.get_json() or {}
    response, status = user_controller.update_user(
        user_id, data, acting_user=current_user
    )
    return jsonify(response), status


@user_bp.route("/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id):
    response, status = user_controller.delete_user(user_id, acting_user=current_user)
    return jsonify(response), status
