import os
from dotenv import load_dotenv

load_dotenv()


def _build_database_uri():
    """
    Prefer a full connection string (Railway provides DATABASE_URL / MYSQL_URL);
    fall back to individual DB_* variables for local development.
    """
    url = (
        os.getenv("DATABASE_URL")
        or os.getenv("MYSQL_URL")
        or os.getenv("MYSQL_PUBLIC_URL")
    )
    if url:
        # SQLAlchemy needs the pymysql driver in the scheme.
        if url.startswith("mysql://"):
            url = url.replace("mysql://", "mysql+pymysql://", 1)
        return url

    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "skill_swap_db")
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


class Config:
    """
    Central app configuration.
    All values are pulled from environment variables (.env file).
    """

    # --- Database ---
    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # --- JWT ---
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES = int(
        os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 1440)
    )

    # --- Flask ---
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
