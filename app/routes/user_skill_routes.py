from flask import Blueprint, request, jsonify

from app.controllers import user_skill_controller
from app.middleware import login_required

user_skill_bp = Blueprint("user_skills", __name__, url_prefix="/api/user-skills")


@user_skill_bp.route("", methods=["POST"])
@login_required
def create_user_skill():
    data = request.get_json() or {}
    response, status = user_skill_controller.create_user_skill(data)
    return jsonify(response), status


@user_skill_bp.route("", methods=["GET"])
@login_required
def get_user_skills():
    user_id = request.args.get("user_id", type=int)
    type_ = request.args.get("type")
    category = request.args.get("category")
    search = request.args.get("search")
    response, status = user_skill_controller.get_user_skills(
        user_id=user_id, type_=type_, category=category, search=search
    )
    return jsonify(response), status


@user_skill_bp.route("/<int:user_skills_id>", methods=["GET"])
@login_required
def get_user_skill(user_skills_id):
    response, status = user_skill_controller.get_user_skill(user_skills_id)
    return jsonify(response), status


@user_skill_bp.route("/<int:user_skills_id>", methods=["PUT"])
@login_required
def update_user_skill(user_skills_id):
    data = request.get_json() or {}
    response, status = user_skill_controller.update_user_skill(user_skills_id, data)
    return jsonify(response), status


@user_skill_bp.route("/<int:user_skills_id>", methods=["DELETE"])
@login_required
def delete_user_skill(user_skills_id):
    response, status = user_skill_controller.delete_user_skill(user_skills_id)
    return jsonify(response), status
