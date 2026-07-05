from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.config import Config
from app.extensions import db, jwt
from app.routes import register_blueprints


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- Extensions ---
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # --- Import all models so db.create_all() can discover them ---
    from app import models  # noqa: F401

    # --- JWT user lookup: loads a User instance from the token's `sub` claim ---
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from app.models.user_model import User

        identity = jwt_data["sub"]
        return User.query.get(int(identity))

    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        return jsonify({"error": "Missing or invalid authorization token."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"error": "Invalid or expired token."}), 401

    # --- Blueprints ---
    register_blueprints(app)

    # --- Global error handlers ---
    @app.errorhandler(OperationalError)
    def handle_operational_error(e):
        return jsonify({"error": "Database connection failed. Please try again later."}), 500

    @app.errorhandler(ProgrammingError)
    def handle_programming_error(e):
        return jsonify({"error": "A database error occurred."}), 500

    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"error": "The requested resource was not found."}), 404

    @app.errorhandler(405)
    def handle_405(e):
        return jsonify({"error": "Method not allowed."}), 405

    @app.route("/")
    def index():
        return jsonify({"message": "Community Skill-Swap API is running."})

    return app
