from app.extensions import db
from app.models.user_skill_model import UserSkill
from app.models.skill_model import Skill
from app.models.user_model import User

VALID_TYPES = ("offer", "wanted")
VALID_LEVELS = ("beginner", "Intermediate", "advanced")


def _validate_user_skill_payload(data, user_skills_id=None):
    errors = []

    if not data.get("user_id"):
        errors.append("user_id is required.")
    elif not User.query.get(data["user_id"]):
        errors.append("user_id does not match an existing user.")

    if not data.get("skill_id"):
        errors.append("skill_id is required.")
    elif not Skill.query.get(data["skill_id"]):
        errors.append("skill_id does not match an existing skill.")

    if not data.get("type"):
        errors.append("type is required (offer/wanted).")
    elif data["type"] not in VALID_TYPES:
        errors.append("type must be one of: offer, wanted.")

    if not data.get("level"):
        errors.append("level is required (beginner/Intermediate/advanced).")
    elif data["level"] not in VALID_LEVELS:
        errors.append("level must be one of: beginner, Intermediate, advanced.")

    return errors


def create_user_skill(data):
    errors = _validate_user_skill_payload(data)
    if errors:
        return {"errors": errors}, 400

    try:
        user_skill = UserSkill(
            user_id=data["user_id"],
            skill_id=data["skill_id"],
            type=data["type"],
            level=data["level"],
        )
        db.session.add(user_skill)
        db.session.commit()
        return {
            "message": "Skill posted successfully.",
            "user_skill": user_skill.to_dict(),
        }, 201
    except Exception:
        db.session.rollback()
        return {"error": "Something went wrong while posting the skill."}, 500


def get_user_skills(user_id=None, type_=None, category=None, search=None):
    """
    Browse/search skills posted by members.
    Filters: user_id, type (offer/wanted), category, search (skill name)
    """
    query = UserSkill.query.join(Skill)

    if user_id:
        query = query.filter(UserSkill.user_id == user_id)
    if type_:
        query = query.filter(UserSkill.type == type_)
    if category:
        query = query.filter(Skill.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(Skill.skill_name.ilike(f"%{search}%"))

    user_skills = query.all()
    return {"user_skills": [us.to_dict() for us in user_skills]}, 200


def get_user_skill(user_skills_id):
    user_skill = UserSkill.query.get(user_skills_id)
    if not user_skill:
        return {"error": "User skill not found."}, 404
    return {"user_skill": user_skill.to_dict()}, 200


def update_user_skill(user_skills_id, data):
    user_skill = UserSkill.query.get(user_skills_id)
    if not user_skill:
        return {"error": "User skill not found."}, 404

    if "type" in data and data["type"] not in VALID_TYPES:
        return {"errors": ["type must be one of: offer, wanted."]}, 400
    if "level" in data and data["level"] not in VALID_LEVELS:
        return {"errors": ["level must be one of: beginner, Intermediate, advanced."]}, 400

    try:
        if "skill_id" in data:
            if not Skill.query.get(data["skill_id"]):
                return {"errors": ["skill_id does not match an existing skill."]}, 400
            user_skill.skill_id = data["skill_id"]
        if "type" in data:
            user_skill.type = data["type"]
        if "level" in data:
            user_skill.level = data["level"]

        db.session.commit()
        return {
            "message": "User skill updated successfully.",
            "user_skill": user_skill.to_dict(),
        }, 200
    except Exception:
        db.session.rollback()
        return {"error": "Something went wrong while updating the user skill."}, 500


def delete_user_skill(user_skills_id):
    user_skill = UserSkill.query.get(user_skills_id)
    if not user_skill:
        return {"error": "User skill not found."}, 404

    try:
        db.session.delete(user_skill)
        db.session.commit()
        return {"message": "User skill deleted successfully."}, 200
    except Exception:
        db.session.rollback()
        return {"error": "Something went wrong while deleting the user skill."}, 500
