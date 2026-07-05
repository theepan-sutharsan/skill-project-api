from flask import Blueprint, jsonify

from app.controllers import dashboard_controller
from app.middleware import login_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/<int:user_id>", methods=["GET"])
@login_required
def get_dashboard(user_id):
    response, status = dashboard_controller.get_dashboard(user_id)
    return jsonify(response), status
