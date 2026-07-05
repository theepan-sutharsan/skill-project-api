from app.extensions import db
from app.models.skill_model import Skill


def _validate_skill_payload(data, skill_id=None):
    errors = []

    if not data.get("skill_name"):
        errors.append("skill_name is required.")
    else:
        query = Skill.query.filter(Skill.skill_name == data["skill_name"])
        if skill_id:
            query = query.filter(Skill.skill_id != skill_id)
        if query.first():
            errors.append("skill_name already exists.")

    return errors


def create_skill(data):
    errors = _validate_skill_payload(data)
    if errors:
        return {"errors": errors}, 400

    try:
        skill = Skill(skill_name=data["skill_name"], category=data.get("category"))
        db.session.add(skill)
        db.session.commit()
        return {"message": "Skill created successfully.", "skill": skill.to_dict()}, 201
    except Exception:
        db.session.rollback()
        return {"error": "Something went wrong while creating the skill."}, 500


def get_skills(search=None, category=None):
    query = Skill.query

    if search:
        query = query.filter(Skill.skill_name.ilike(f"%{search}%"))
    if category:
        query = query.filter(Skill.category.ilike(f"%{category}%"))

    skills = query.order_by(Skill.skill_name.asc()).all()
    return {"skills": [s.to_dict() for s in skills]}, 200


def get_skill(skill_id):
    skill = Skill.query.get(skill_id)
    if not skill:
        return {"error": "Skill not found."}, 404
    return {"skill": skill.to_dict()}, 200


def update_skill(skill_id, data):
    skill = Skill.query.get(skill_id)
    if not skill:
        return {"error": "Skill not found."}, 404

    errors = _validate_skill_payload(data, skill_id=skill_id)
    if errors:
        return {"errors": errors}, 400

    try:
        if "skill_name" in data:
            skill.skill_name = data["skill_name"]
        if "category" in data:
            skill.category = data["category"]

        db.session.commit()
        return {"message": "Skill updated successfully.", "skill": skill.to_dict()}, 200
    except Exception:
        db.session.rollback()
        return {"error": "Something went wrong while updating the skill."}, 500


def delete_skill(skill_id):
    skill = Skill.query.get(skill_id)
    if not skill:
        return {"error": "Skill not found."}, 404

    try:
        db.session.delete(skill)
        db.session.commit()
        return {"message": "Skill deleted successfully."}, 200
    except Exception:
        db.session.rollback()
        return {"error": "Something went wrong while deleting the skill."}, 500
