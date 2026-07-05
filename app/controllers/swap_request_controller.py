from app.extensions import db
from app.models.swap_request_model import SwapRequest
from app.models.user_skill_model import UserSkill
from app.models.user_model import User

VALID_STATUSES = ("pending", "accepted", "declined")


def _validate_swap_request_payload(data):
    errors = []

    if not data.get("sender_id"):
        errors.append("sender_id is required.")
    elif not User.query.get(data["sender_id"]):
        errors.append("sender_id does not match an existing user.")

    if not data.get("reciver_id"):
        errors.append("reciver_id is required.")
    elif not User.query.get(data["reciver_id"]):
        errors.append("reciver_id does not match an existing user.")

    if data.get("sender_id") and data.get("reciver_id") and data["sender_id"] == data["reciver_id"]:
        errors.append("sender_id and reciver_id cannot be the same user.")

    offered_skill = None
    wanted_skill = None

    if not data.get("offter_skill_id"):
        errors.append("offter_skill_id is required.")
    else:
        offered_skill = UserSkill.query.get(data["offter_skill_id"])
        if not offered_skill:
            errors.append("offter_skill_id does not match an existing user skill.")
        elif offered_skill.type != "offer":
            errors.append("offter_skill_id must reference a skill of type 'offer'.")
        elif data.get("sender_id") and offered_skill.user_id != data["sender_id"]:
            errors.append("offter_skill_id must belong to the sender.")

    if not data.get("wanted_skill_id"):
        errors.append("wanted_skill_id is required.")
    else:
        wanted_skill = UserSkill.query.get(data["wanted_skill_id"])
        if not wanted_skill:
            errors.append("wanted_skill_id does not match an existing user skill.")
        elif wanted_skill.type != "offer":
            errors.append(
                "wanted_skill_id must reference a skill the receiver is offering."
            )
        elif data.get("reciver_id") and wanted_skill.user_id != data["reciver_id"]:
            errors.append("wanted_skill_id must belong to the receiver.")

    return errors


def create_swap_request(data):
    """
    Sender sends a swap request to a receiver:
    "I'll teach you my offered skill, in exchange for your offered skill."
    """
    errors = _validate_swap_request_payload(data)
    if errors:
        return {"errors": errors}, 400

    try:
        swap_request = SwapRequest(
            sender_id=data["sender_id"],
            reciver_id=data["reciver_id"],
            offter_skill_id=data["offter_skill_id"],
            wanted_skill_id=data["wanted_skill_id"],
            status="pending",
        )
        db.session.add(swap_request)
        db.session.commit()
        return {
            "message": "Swap request sent successfully.",
            "swap_request": swap_request.to_dict(),
        }, 201
    except Exception:
        db.session.rollback()
        return {"error": "Something went wrong while sending the swap request."}, 500


def get_swap_requests(sender_id=None, reciver_id=None, status=None):
    """
    Dashboard support: filter by sender_id (requests sent),
    reciver_id (requests received), and/or status.
    """
    query = SwapRequest.query

    if sender_id:
        query = query.filter(SwapRequest.sender_id == sender_id)
    if reciver_id:
        query = query.filter(SwapRequest.reciver_id == reciver_id)
    if status:
        query = query.filter(SwapRequest.status == status)

    requests = query.order_by(SwapRequest.request_date.desc()).all()
    return {"swap_requests": [r.to_dict() for r in requests]}, 200


def get_swap_request(request_id):
    swap_request = SwapRequest.query.get(request_id)
    if not swap_request:
        return {"error": "Swap request not found."}, 404
    return {"swap_request": swap_request.to_dict()}, 200


def update_swap_request_status(request_id, data, acting_user_id=None):
    """
    Receiver accepts or declines a pending request.
    Only the receiver of the request is allowed to change its status.
    """
    swap_request = SwapRequest.query.get(request_id)
    if not swap_request:
        return {"error": "Swap request not found."}, 404

    new_status = data.get("status")
    if not new_status or new_status not in VALID_STATUSES:
        return {"errors": ["status must be one of: pending, accepted, declined."]}, 400

    if swap_request.status != "pending":
        return {"error": "This swap request has already been responded to."}, 400

    if acting_user_id is not None and swap_request.reciver_id != acting_user_id:
        return {"error": "Only the receiver can accept or decline this request."}, 403

    try:
        swap_request.status = new_status
        db.session.commit()
        return {
            "message": f"Swap request {new_status} successfully.",
            "swap_request": swap_request.to_dict(),
        }, 200
    except Exception:
        db.session.rollback()
        return {"error": "Something went wrong while updating the swap request."}, 500


def delete_swap_request(request_id):
    swap_request = SwapRequest.query.get(request_id)
    if not swap_request:
        return {"error": "Swap request not found."}, 404

    try:
        db.session.delete(swap_request)
        db.session.commit()
        return {"message": "Swap request deleted successfully."}, 200
    except Exception:
        db.session.rollback()
        return {"error": "Something went wrong while deleting the swap request."}, 500
