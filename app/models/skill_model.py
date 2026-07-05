from app.extensions import db


class Skill(db.Model):
    """
    Master catalog of skills (e.g. "Guitar", "Python", "Cooking").
    Linked to users through the user_skills join table (many-to-many).
    """

    __tablename__ = "skills"

    skill_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    skill_name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(100), nullable=True)

    # Relationships
    user_skills = db.relationship(
        "UserSkill", back_populates="skill", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "skill_id": self.skill_id,
            "skill_name": self.skill_name,
            "category": self.category,
        }
