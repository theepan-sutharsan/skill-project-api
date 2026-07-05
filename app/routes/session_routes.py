from flask import Blueprint, request, jsonify

from app.controllers import session_controller
from app.middleware import login_required

session_bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")


@session_bp.route("", methods=["POST"])
@login_required
def create_session():
    data = request.get_json() or {}
    response, status = session_controller.create_session(data)
    return jsonify(response), status


@session_bp.route("", methods=["GET"])
@login_required
def get_sessions():
    user_id = request.args.get("user_id", type=int)
    status_filter = request.args.get("status")
    response, status = session_controller.get_sessions(user_id=user_id, status=status_filter)
    return jsonify(response), status


@session_bp.route("/<int:session_id>", methods=["GET"])
@login_required
def get_session(session_id):
    response, status = session_controller.get_session(session_id)
    return jsonify(response), status


@session_bp.route("/<int:session_id>", methods=["PUT"])
@login_required
def update_session(session_id):
    data = request.get_json() or {}
    response, status = session_controller.update_session(session_id, data)
    return jsonify(response), status


@session_bp.route("/<int:session_id>", methods=["DELETE"])
@login_required
def delete_session(session_id):
    response, status = session_controller.delete_session(session_id)
    return jsonify(response), status
