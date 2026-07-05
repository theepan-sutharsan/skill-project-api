import os

from app.extensions import db
from app.models.skill_model import Skill
from app.models.user_model import User

DEFAULT_ADMIN = {
    "user_name": os.getenv("ADMIN_NAME", "Platform Admin"),
    "user_email": os.getenv("ADMIN_EMAIL", "admin@skillswap.com"),
    "password": os.getenv("ADMIN_PASSWORD", "admin123"),
    "location": "Head Office",
    "role": "admin",
}

DEFAULT_USERS = [
    {
        "user_name": "Alice Johnson",
        "user_email": "alice@skillswap.com",
        "password": "member123",
        "location": "New York, USA",
        "role": "member",
    },
    {
        "user_name": "Bob Martinez",
        "user_email": "bob@skillswap.com",
        "password": "member123",
        "location": "Austin, USA",
        "role": "member",
    },
    {
        "user_name": "Priya Sharma",
        "user_email": "priya@skillswap.com",
        "password": "member123",
        "location": "Colombo, Sri Lanka",
        "role": "member",
    },
]

DEFAULT_SKILLS = [
    ("Python", "Programming"),
    ("JavaScript", "Programming"),
    ("Guitar", "Music"),
    ("Piano", "Music"),
    ("Cooking", "Life Skills"),
    ("Public Speaking", "Communication"),
    ("Photography", "Arts"),
    ("Yoga", "Wellness"),
    ("Spanish", "Languages"),
    ("Web Design", "Design"),
]


def seed_admin_user():
    admin_data = DEFAULT_ADMIN
    admin = User.query.filter_by(user_email=admin_data["user_email"]).first()

    if admin:
        if admin.role != "admin":
            admin.role = "admin"
            db.session.commit()
        return {"created": 0, "skipped": 1}

    admin = User(
        user_name=admin_data["user_name"],
        user_email=admin_data["user_email"],
        location=admin_data["location"],
        role=admin_data["role"],
    )
    admin.set_password(admin_data["password"])
    db.session.add(admin)
    db.session.commit()
    return {"created": 1, "skipped": 0}


def seed_default_users():
    created = 0
    skipped = 0

    for user_data in DEFAULT_USERS:
        existing = User.query.filter_by(user_email=user_data["user_email"]).first()
        if existing:
            skipped += 1
            continue

        user = User(
            user_name=user_data["user_name"],
            user_email=user_data["user_email"],
            location=user_data["location"],
            role=user_data["role"],
        )
        user.set_password(user_data["password"])
        db.session.add(user)
        created += 1

    db.session.commit()
    return {"created": created, "skipped": skipped}


def seed_default_skills():
    created = 0
    skipped = 0

    for skill_name, category in DEFAULT_SKILLS:
        existing = Skill.query.filter_by(skill_name=skill_name).first()
        if existing:
            skipped += 1
            continue

        db.session.add(Skill(skill_name=skill_name, category=category))
        created += 1

    db.session.commit()
    return {"created": created, "skipped": skipped}


def run_seeds():
    admin_result = seed_admin_user()
    users_result = seed_default_users()
    skills_result = seed_default_skills()

    return {
        "admin": admin_result,
        "users": users_result,
        "skills": skills_result,
    }
