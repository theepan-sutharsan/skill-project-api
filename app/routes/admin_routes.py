from flask import Blueprint, Response, request, jsonify

from app.controllers import admin_controller
from app.middleware import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _file_response(content, filename, mimetype):
    return Response(
        content,
        mimetype=mimetype,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@admin_bp.route("/export/members.csv", methods=["GET"])
@admin_required
def export_members_csv():
    content, filename, mimetype = admin_controller.export_members_csv()
    return _file_response(content, filename, mimetype)


@admin_bp.route("/export/members.pdf", methods=["GET"])
@admin_required
def export_members_pdf():
    content, filename, mimetype = admin_controller.export_members_pdf()
    return _file_response(content, filename, mimetype)


@admin_bp.route("/export/skills.csv", methods=["GET"])
@admin_required
def export_skills_csv():
    content, filename, mimetype = admin_controller.export_skills_csv()
    return _file_response(content, filename, mimetype)


@admin_bp.route("/export/skills.pdf", methods=["GET"])
@admin_required
def export_skills_pdf():
    content, filename, mimetype = admin_controller.export_skills_pdf()
    return _file_response(content, filename, mimetype)


@admin_bp.route("/import/members", methods=["POST"])
@admin_required
def import_members():
    file = request.files.get("file")
    response, status = admin_controller.import_members_csv(file)
    return jsonify(response), status


@admin_bp.route("/import/skills", methods=["POST"])
@admin_required
def import_skills():
    file = request.files.get("file")
    response, status = admin_controller.import_skills_csv(file)
    return jsonify(response), status
