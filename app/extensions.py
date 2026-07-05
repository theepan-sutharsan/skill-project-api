from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Shared extension instances.
# Created here (not inside create_app) so models and controllers
# can import them without circular-import issues.
db = SQLAlchemy()
jwt = JWTManager()
