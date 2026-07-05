from app.models.user_model import User
from app.models.user_skill_model import UserSkill
from app.models.swap_request_model import SwapRequest
from app.models.session_model import Session


def get_dashboard(user_id):
    """
    Returns a single dashboard payload for a user:
    - my_offers: skills this user is offering
    - my_wanted: skills this user wants to learn
    - requests_sent: swap requests this user has sent
    - requests_received: swap requests this user has received
    - confirmed_sessions: scheduled sessions this user is part of
    """
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found."}, 404

    my_offers = UserSkill.query.filter_by(user_id=user_id, type="offer").all()
    my_wanted = UserSkill.query.filter_by(user_id=user_id, type="wanted").all()

    requests_sent = (
        SwapRequest.query.filter_by(sender_id=user_id)
        .order_by(SwapRequest.request_date.desc())
        .all()
    )
    requests_received = (
        SwapRequest.query.filter_by(reciver_id=user_id)
        .order_by(SwapRequest.request_date.desc())
        .all()
    )

    confirmed_sessions = (
        Session.query.join(SwapRequest)
        .filter(
            (SwapRequest.sender_id == user_id) | (SwapRequest.reciver_id == user_id)
        )
        .order_by(Session.session_date.asc(), Session.session_time.asc())
        .all()
    )

    return {
        "user": user.to_dict(),
        "my_offers": [s.to_dict() for s in my_offers],
        "my_wanted": [s.to_dict() for s in my_wanted],
        "requests_sent": [r.to_dict() for r in requests_sent],
        "requests_received": [r.to_dict() for r in requests_received],
        "confirmed_sessions": [s.to_dict() for s in confirmed_sessions],
    }, 200
