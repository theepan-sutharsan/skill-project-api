from flask import Blueprint, request, jsonify

from app.controllers import skill_controller
from app.middleware import admin_required, login_required

skill_bp = Blueprint("skills", __name__, url_prefix="/api/skills")


@skill_bp.route("", methods=["POST"])
@admin_required
def create_skill():
    data = request.get_json() or {}
    response, status = skill_controller.create_skill(data)
    return jsonify(response), status


@skill_bp.route("", methods=["GET"])
@login_required
def get_skills():
    search = request.args.get("search")
    category = request.args.get("category")
    response, status = skill_controller.get_skills(search=search, category=category)
    return jsonify(response), status


@skill_bp.route("/<int:skill_id>", methods=["GET"])
@login_required
def get_skill(skill_id):
    response, status = skill_controller.get_skill(skill_id)
    return jsonify(response), status


@skill_bp.route("/<int:skill_id>", methods=["PUT"])
@admin_required
def update_skill(skill_id):
    data = request.get_json() or {}
    response, status = skill_controller.update_skill(skill_id, data)
    return jsonify(response), status


@skill_bp.route("/<int:skill_id>", methods=["DELETE"])
@admin_required
def delete_skill(skill_id):
    response, status = skill_controller.delete_skill(skill_id)
    return jsonify(response), status
