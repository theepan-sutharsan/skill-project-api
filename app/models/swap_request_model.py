from app.extensions import db
from app.utils import utc_now


class SwapRequest(db.Model):
    """
    A request from one user (sender) to another (receiver) to swap skills.
    offter_skill_id  -> the user_skills row of the skill the SENDER is offering
    wanted_skill_id  -> the user_skills row of the skill the SENDER wants
                        (this should belong to the receiver)
    status: pending / accepted / declined
    """

    __tablename__ = "swap_requests"

    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.users_id"), nullable=False)
    reciver_id = db.Column(db.Integer, db.ForeignKey("users.users_id"), nullable=False)
    offter_skill_id = db.Column(
        db.Integer, db.ForeignKey("user_skills.user_skills_id"), nullable=False
    )
    wanted_skill_id = db.Column(
        db.Integer, db.ForeignKey("user_skills.user_skills_id"), nullable=False
    )
    status = db.Column(
        db.Enum("pending", "accepted", "declined", name="swap_request_status"),
        default="pending",
        nullable=False,
    )
    request_date = db.Column(db.DateTime, default=utc_now)

    # Relationships
    sender = db.relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_requests"
    )
    reciver = db.relationship(
        "User", foreign_keys=[reciver_id], back_populates="received_requests"
    )
    offered_skill = db.relationship(
        "UserSkill", foreign_keys=[offter_skill_id], back_populates="offered_in_requests"
    )
    wanted_skill = db.relationship(
        "UserSkill", foreign_keys=[wanted_skill_id], back_populates="wanted_in_requests"
    )
    session = db.relationship(
        "Session", back_populates="request", uselist=False, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "request_id": self.request_id,
            "sender_id": self.sender_id,
            "sender_name": self.sender.user_name if self.sender else None,
            "reciver_id": self.reciver_id,
            "reciver_name": self.reciver.user_name if self.reciver else None,
            "offter_skill_id": self.offter_skill_id,
            "offered_skill_name": self.offered_skill.skill.skill_name
            if self.offered_skill and self.offered_skill.skill
            else None,
            "wanted_skill_id": self.wanted_skill_id,
            "wanted_skill_name": self.wanted_skill.skill.skill_name
            if self.wanted_skill and self.wanted_skill.skill
            else None,
            "status": self.status,
            "request_date": self.request_date.isoformat() if self.request_date else None,
        }
