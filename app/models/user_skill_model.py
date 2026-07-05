from app.extensions import db


class UserSkill(db.Model):
    """
    Join table linking a user to a skill, either as something they OFFER
    (can teach) or something they WANT (wish to learn).
    This is the many-to-many link between users <-> skills.
    """

    __tablename__ = "user_skills"

    user_skills_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.users_id"), nullable=False
    )
    skill_id = db.Column(
        db.Integer, db.ForeignKey("skills.skill_id"), nullable=False
    )
    type = db.Column(db.Enum("offer", "wanted", name="user_skill_type"), nullable=False)
    level = db.Column(
        db.Enum("beginner", "Intermediate", "advanced", name="user_skill_level"),
        nullable=False,
    )

    # Relationships
    user = db.relationship("User", back_populates="user_skills")
    skill = db.relationship("Skill", back_populates="user_skills")

    offered_in_requests = db.relationship(
        "SwapRequest",
        foreign_keys="SwapRequest.offter_skill_id",
        back_populates="offered_skill",
    )
    wanted_in_requests = db.relationship(
        "SwapRequest",
        foreign_keys="SwapRequest.wanted_skill_id",
        back_populates="wanted_skill",
    )

    def to_dict(self):
        return {
            "user_skills_id": self.user_skills_id,
            "user_id": self.user_id,
            "skill_id": self.skill_id,
            "skill_name": self.skill.skill_name if self.skill else None,
            "category": self.skill.category if self.skill else None,
            "type": self.type,
            "level": self.level,
        }
