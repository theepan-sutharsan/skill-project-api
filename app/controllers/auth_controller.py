from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models.user_model import User


def _validate_register_payload(data):
    errors = []

    if not data.get("user_name"):
        errors.append("user_name is required.")
    if not data.get("user_email"):
        errors.append("user_email is required.")
    if not data.get("password"):
        errors.append("password is required.")
    elif len(data.get("password", "")) < 6:
        errors.append("password must be at least 6 characters long.")

    if data.get("user_email"):
        existing = User.query.filter_by(user_email=data["user_email"]).first()
        if existing:
            errors.append("user_email is already registered.")

    return errors


def register_user(data):
    errors = _validate_register_payload(data)
    if errors:
        return {"errors": errors}, 400

    try:
        user = User(
            user_name=data["user_name"],
            user_email=data["user_email"],
            location=data.get("location"),
            profile_image=data.get("profile_image"),
            role="member",
        )
        user.set_password(data["password"])

        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity=str(user.users_id))

        return {
            "message": "User registered successfully.",
            "access_token": access_token,
            "user": user.to_dict(),
        }, 201
    except Exception:
        db.session.rollback()
        return {"error": "Something went wrong while registering the user."}, 500


def login_user(data):
    user_email = data.get("user_email")
    password = data.get("password")

    if not user_email or not password:
        return {"errors": ["user_email and password are required."]}, 400

    user = User.query.filter_by(user_email=user_email).first()

    if not user or not user.check_password(password):
        return {"error": "Invalid email or password."}, 401

    access_token = create_access_token(identity=str(user.users_id))

    return {
        "message": "Login successful.",
        "access_token": access_token,
        "user": user.to_dict(),
    }, 200
