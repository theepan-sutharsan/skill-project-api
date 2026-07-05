from flask import Blueprint, request, jsonify

from app.controllers import auth_controller

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    response, status = auth_controller.register_user(data)
    return jsonify(response), status


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    response, status = auth_controller.login_user(data)
    return jsonify(response), status
