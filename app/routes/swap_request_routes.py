from flask import Blueprint, request, jsonify
from flask_jwt_extended import current_user

from app.controllers import swap_request_controller
from app.middleware import login_required

swap_request_bp = Blueprint("swap_requests", __name__, url_prefix="/api/swap-requests")


@swap_request_bp.route("", methods=["POST"])
@login_required
def create_swap_request():
    data = request.get_json() or {}
    response, status = swap_request_controller.create_swap_request(data)
    return jsonify(response), status


@swap_request_bp.route("", methods=["GET"])
@login_required
def get_swap_requests():
    sender_id = request.args.get("sender_id", type=int)
    reciver_id = request.args.get("reciver_id", type=int)
    status_filter = request.args.get("status")
    response, status = swap_request_controller.get_swap_requests(
        sender_id=sender_id, reciver_id=reciver_id, status=status_filter
    )
    return jsonify(response), status


@swap_request_bp.route("/<int:request_id>", methods=["GET"])
@login_required
def get_swap_request(request_id):
    response, status = swap_request_controller.get_swap_request(request_id)
    return jsonify(response), status


@swap_request_bp.route("/<int:request_id>/status", methods=["PUT"])
@login_required
def update_swap_request_status(request_id):
    """
    Recipient accepts or declines the request.
    Body: { "status": "accepted" } or { "status": "declined" }
    """
    data = request.get_json() or {}
    response, status = swap_request_controller.update_swap_request_status(
        request_id, data, acting_user_id=current_user.users_id
    )
    return jsonify(response), status


@swap_request_bp.route("/<int:request_id>", methods=["DELETE"])
@login_required
def delete_swap_request(request_id):
    response, status = swap_request_controller.delete_swap_request(request_id)
    return jsonify(response), status
