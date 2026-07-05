from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.utils import utc_now

USER_ROLES = ("member", "admin")


class User(db.Model):
    """
    A registered member of the skill-swap platform.
    Has a public profile and can both offer and request skills.
    """

    __tablename__ = "users"

    users_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)  # stored as a hash
    location = db.Column(db.String(150), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="member")
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    user_skills = db.relationship(
        "UserSkill", back_populates="user", cascade="all, delete-orphan"
    )
    sent_requests = db.relationship(
        "SwapRequest",
        foreign_keys="SwapRequest.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    received_requests = db.relationship(
        "SwapRequest",
        foreign_keys="SwapRequest.reciver_id",
        back_populates="reciver",
        cascade="all, delete-orphan",
    )

    # --- Password helpers ---
    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    @property
    def is_admin(self):
        return self.role == "admin"

    def to_dict(self):
        return {
            "users_id": self.users_id,
            "user_name": self.user_name,
            "user_email": self.user_email,
            "location": self.location,
            "profile_image": self.profile_image,
            "role": self.role or "member",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
