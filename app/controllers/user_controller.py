from app.extensions import db
from app.models.user_model import USER_ROLES, User


def _validate_user_update_payload(data, user_id):
    errors = []

    if "user_email" in data and data["user_email"]:
        existing = User.query.filter(
            User.user_email == data["user_email"], User.users_id != user_id
        ).first()
        if existing:
            errors.append("user_email is already in use by another account.")

    if "role" in data and data["role"] and data["role"] not in USER_ROLES:
        errors.append("role must be 'member' or 'admin'.")

    return errors


def get_users(search=None, location=None):
    """
    Browse/search members. Optional filters:
    - search: matches user_name (partial, case-insensitive)
    - location: matches location (partial, case-insensitive)
    """
    query = User.query

    if search:
        query = query.filter(User.user_name.ilike(f"%{search}%"))
    if location:
        query = query.filter(User.location.ilike(f"%{location}%"))

    users = query.order_by(User.user_name.asc()).all()
    return {"users": [u.to_dict() for u in users]}, 200


def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found."}, 404
    return {"user": user.to_dict()}, 200


def update_user(user_id, data, acting_user=None):
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found."}, 404

    is_admin = acting_user is not None and acting_user.is_admin
    is_self = acting_user is not None and acting_user.users_id == user_id

    if not is_admin and not is_self:
        return {"error": "You can only update your own profile."}, 403

    if not is_admin and "role" in data:
        return {"error": "Only admins can change user roles."}, 403

    errors = _validate_user_update_payload(data, user_id)
    if errors:
        return {"errors": errors}, 400

    try:
        if "user_name" in data:
            user.user_name = data["user_name"]
        if "user_email" in data:
            user.user_email = data["user_email"]
        if "location" in data:
            user.location = data["location"]
        if "profile_image" in data:
            user.profile_image = data["profile_image"]
        if "password" in data and data["password"]:
            user.set_password(data["password"])
        if is_admin and "role" in data and data["role"]:
            if user.is_admin and data["role"] != "admin":
                admin_count = User.query.filter_by(role="admin").count()
                if admin_count <= 1:
                    return {"error": "Cannot demote the last admin account."}, 400
            user.role = data["role"]

        db.session.commit()
        return {"message": "User profile updated successfully.", "user": user.to_dict()}, 200
    except Exception:
        db.session.rollback()
        return {"error": "Something went wrong while updating the user."}, 500


def delete_user(user_id, acting_user=None):
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found."}, 404

    is_admin = acting_user is not None and acting_user.is_admin
    is_self = acting_user is not None and acting_user.users_id == user_id

    if not is_admin and not is_self:
        return {"error": "You can only delete your own account."}, 403

    if user.is_admin:
        admin_count = User.query.filter_by(role="admin").count()
        if admin_count <= 1:
            return {"error": "Cannot delete the last admin account."}, 400

    try:
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted successfully."}, 200
    except Exception:
        db.session.rollback()
        return {"error": "Something went wrong while deleting the user."}, 500
