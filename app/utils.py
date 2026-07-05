from datetime import datetime, timezone


def utc_now():
    """
    Returns the current UTC time.
    Used as the default value for created_at columns across all models.
    """
    return datetime.now(timezone.utc)
