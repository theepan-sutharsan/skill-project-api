def register_blueprints(app):
    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    from app.routes.skill_routes import skill_bp
    from app.routes.user_skill_routes import user_skill_bp
    from app.routes.swap_request_routes import swap_request_bp
    from app.routes.session_routes import session_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(skill_bp)
    app.register_blueprint(user_skill_bp)
    app.register_blueprint(swap_request_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
