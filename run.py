import logging
import time

from sqlalchemy import inspect, text

from app import create_app
from app.extensions import db
from app.seeds import run_seeds

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()


def ensure_role_column():
    inspector = inspect(db.engine)
    columns = {col["name"] for col in inspector.get_columns("users")}
    if "role" not in columns:
        db.session.execute(
            text("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'member'")
        )
        db.session.commit()


def init_db(retries=5, delay=3):
    """Create tables and seed data. Retries so the app survives a DB that
    is still starting up (common on Railway), instead of crashing on boot."""
    for attempt in range(1, retries + 1):
        try:
            with app.app_context():
                db.create_all()
                ensure_role_column()
                run_seeds()
            logger.info("Database initialized and seeded.")
            return
        except Exception as exc:
            logger.warning(
                "Database init attempt %s/%s failed: %s", attempt, retries, exc
            )
            if attempt < retries:
                time.sleep(delay)

    logger.error(
        "Database initialization failed after %s attempts. "
        "The server will start anyway; check DATABASE_URL / DB_* variables.",
        retries,
    )


# Runs on import so production servers (gunicorn on Railway) also initialize the DB.
init_db()

if __name__ == "__main__":
    app.run(debug=app.config["FLASK_DEBUG"])
