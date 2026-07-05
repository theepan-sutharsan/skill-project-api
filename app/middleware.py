from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, current_user


def login_required(fn):
    """
    Decorator to protect a route — requires a valid JWT access token.
    Use on any route that should only be reachable by a logged-in user.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        if current_user is None:
            return jsonify({"error": "User not found."}), 401
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    """Decorator — requires a valid JWT and an admin role."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        if current_user is None:
            return jsonify({"error": "User not found."}), 401
        if not current_user.is_admin:
            return jsonify({"error": "Admin access required."}), 403
        return fn(*args, **kwargs)

    return wrapper
