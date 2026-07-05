from sqlalchemy import inspect, text

from app import create_app
from app.extensions import db
from app.seeds import run_seeds

app = create_app()


def ensure_role_column():
    inspector = inspect(db.engine)
    columns = {col["name"] for col in inspector.get_columns("users")}
    if "role" not in columns:
        db.session.execute(
            text("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'member'")
        )
        db.session.commit()


def init_db():
    with app.app_context():
        db.create_all()
        ensure_role_column()
        run_seeds()


# Runs on import so production servers (gunicorn on Railway) also initialize the DB.
init_db()

if __name__ == "__main__":
    app.run(debug=app.config["FLASK_DEBUG"])
