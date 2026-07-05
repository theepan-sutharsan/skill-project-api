from datetime import datetime

from app.extensions import db
from app.models.session_model import Session
from app.models.swap_request_model import SwapRequest

VALID_STATUSES = ("scheduled", "completed", "cancelled")


def _parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def _parse_time(value):
    return datetime.strptime(value, "%H:%M").time()


def _validate_session_payload(data):
    errors = []

    request_id = data.get("request_id")
    swap_request = None

    if not request_id:
        errors.append("request_id is required.")
    else:
        swap_request = SwapRequest.query.get(request_id)
        if not swap_request:
            errors.append("request_id does not match an existing swap request.")
        elif swap_request.status != "accepted":
            errors.append("A session can only be scheduled for an accepted swap request.")
        elif swap_request.session:
            errors.append("This swap request already has a scheduled session.")

    if not data.get("session_date"):
        errors.append("session_date is required (format YYYY-MM-DD).")
    else:
        try:
            _parse_date(data["session_date"])
        except ValueError:
            errors.append("session_date must be in format YYYY-MM-DD.")

    if not data.get("session_time"):
        errors.append("session_time is required (format HH:MM).")
    else:
        try:
            _parse_time(data["session_time"])
        except ValueError:
            errors.append("session_time must be in format HH:MM (24-hour).")

    return errors


def create_session(data):
    """
    Schedule an agreed-upon session for an accepted swap request.
    """
    errors = _validate_session_payload(data)
    if errors:
        return {"errors": errors}, 400

    try:
        session = Session(
            request_id=data["request_id"],
            session_date=_parse_date(data["session_date"]),
            session_time=_parse_time(data["session_time"]),
            meeting_link=data.get("meeting_link"),
            status="scheduled",
        )
        db.session.add(session)
        db.session.commit()
        return {
            "message": "Session scheduled successfully.",
            "session": session.to_dict(),
        }, 201
    except Exception:
        db.session.rollback()
        return {"error": "Something went wrong while scheduling the session."}, 500


def get_sessions(user_id=None, status=None):
    """
    Dashboard support: list confirmed sessions, optionally filtered by
    a participating user_id (as sender or receiver) and/or status.
    """
    query = Session.query.join(SwapRequest)

    if user_id:
        query = query.filter(
            (SwapRequest.sender_id == user_id) | (SwapRequest.reciver_id == user_id)
        )
    if status:
        query = query.filter(Session.status == status)

    sessions = query.order_by(Session.session_date.asc(), Session.session_time.asc()).all()
    return {"sessions": [s.to_dict() for s in sessions]}, 200


def get_session(session_id):
    session = Session.query.get(session_id)
    if not session:
        return {"error": "Session not found."}, 404
    return {"session": session.to_dict()}, 200


def update_session(session_id, data):
    session = Session.query.get(session_id)
    if not session:
        return {"error": "Session not found."}, 404

    if "status" in data and data["status"] not in VALID_STATUSES:
        return {"errors": ["status must be one of: scheduled, completed, cancelled."]}, 400

    try:
        if "session_date" in data:
            session.session_date = _parse_date(data["session_date"])
        if "session_time" in data:
            session.session_time = _parse_time(data["session_time"])
        if "meeting_link" in data:
            session.meeting_link = data["meeting_link"]
        if "status" in data:
            session.status = data["status"]

        db.session.commit()
        return {"message": "Session updated successfully.", "session": session.to_dict()}, 200
    except ValueError:
        return {"errors": ["Invalid date or time format."]}, 400
    except Exception:
        db.session.rollback()
        return {"error": "Something went wrong while updating the session."}, 500


def delete_session(session_id):
    session = Session.query.get(session_id)
    if not session:
        return {"error": "Session not found."}, 404

    try:
        db.session.delete(session)
        db.session.commit()
        return {"message": "Session deleted successfully."}, 200
    except Exception:
        db.session.rollback()
        return {"error": "Something went wrong while deleting the session."}, 500
