import csv
import io
from datetime import datetime

from fpdf import FPDF

from app.extensions import db
from app.models.skill_model import Skill
from app.models.user_model import USER_ROLES, User


def _csv_response(content, filename):
    return content, filename, "text/csv"


def _pdf_response(pdf_bytes, filename):
    return pdf_bytes, filename, "application/pdf"


def _build_members_pdf(users):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Community Skill-Swap - Members", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ln=True)
    pdf.ln(4)

    headers = ["ID", "Name", "Email", "Location", "Role", "Joined"]
    col_widths = [12, 35, 55, 35, 20, 33]
    pdf.set_font("Helvetica", "B", 9)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1)
    pdf.ln()

    pdf.set_font("Helvetica", "", 8)
    for user in users:
        row = [
            str(user.users_id),
            (user.user_name or "")[:28],
            (user.user_email or "")[:40],
            (user.location or "-")[:28],
            user.role or "member",
            user.created_at.strftime("%Y-%m-%d") if user.created_at else "-",
        ]
        for i, value in enumerate(row):
            pdf.cell(col_widths[i], 7, value, border=1)
        pdf.ln()

    return pdf.output()


def _build_skills_pdf(skills):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Community Skill-Swap - Skill Catalog", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ln=True)
    pdf.ln(4)

    headers = ["ID", "Skill Name", "Category"]
    col_widths = [15, 90, 85]
    pdf.set_font("Helvetica", "B", 9)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, header, border=1)
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    for skill in skills:
        row = [
            str(skill.skill_id),
            (skill.skill_name or "")[:60],
            (skill.category or "-")[:50],
        ]
        for i, value in enumerate(row):
            pdf.cell(col_widths[i], 7, value, border=1)
        pdf.ln()

    return pdf.output()


def export_members_csv():
    users = User.query.order_by(User.user_name.asc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["user_name", "user_email", "location", "role", "created_at"])
    for user in users:
        writer.writerow(
            [
                user.user_name,
                user.user_email,
                user.location or "",
                user.role or "member",
                user.created_at.isoformat() if user.created_at else "",
            ]
        )
    return _csv_response(output.getvalue(), "members.csv")


def export_members_pdf():
    users = User.query.order_by(User.user_name.asc()).all()
    pdf_bytes = bytes(_build_members_pdf(users))
    return _pdf_response(pdf_bytes, "members.pdf")


def export_skills_csv():
    skills = Skill.query.order_by(Skill.skill_name.asc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["skill_name", "category"])
    for skill in skills:
        writer.writerow([skill.skill_name, skill.category or ""])
    return _csv_response(output.getvalue(), "skills.csv")


def export_skills_pdf():
    skills = Skill.query.order_by(Skill.skill_name.asc()).all()
    pdf_bytes = bytes(_build_skills_pdf(skills))
    return _pdf_response(pdf_bytes, "skills.pdf")


def import_members_csv(file_storage):
    if not file_storage:
        return {"error": "No file uploaded."}, 400

    try:
        raw = file_storage.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        return {"error": "File must be UTF-8 encoded CSV."}, 400

    reader = csv.DictReader(io.StringIO(raw))
    if not reader.fieldnames:
        return {"error": "CSV file is empty or missing headers."}, 400

    required = {"user_name", "user_email", "password"}
    missing = required - {h.strip().lower() for h in reader.fieldnames if h}

    if missing:
        return {
            "error": f"CSV must include columns: {', '.join(sorted(required))}."
        }, 400

    created = 0
    updated = 0
    skipped = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):
        data = {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}
        user_name = data.get("user_name")
        user_email = data.get("user_email")
        password = data.get("password")
        location = data.get("location") or None
        role = (data.get("role") or "member").lower()

        if not user_name or not user_email or not password:
            skipped += 1
            errors.append(f"Row {row_num}: missing required fields.")
            continue

        if role not in USER_ROLES:
            skipped += 1
            errors.append(f"Row {row_num}: invalid role '{role}'.")
            continue

        existing = User.query.filter_by(user_email=user_email).first()
        try:
            if existing:
                existing.user_name = user_name
                existing.location = location
                existing.role = role
                if len(password) >= 6:
                    existing.set_password(password)
                updated += 1
            else:
                user = User(
                    user_name=user_name,
                    user_email=user_email,
                    location=location,
                    role=role,
                )
                user.set_password(password)
                db.session.add(user)
                created += 1
        except Exception:
            db.session.rollback()
            skipped += 1
            errors.append(f"Row {row_num}: could not save user.")

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return {"error": "Failed to import members."}, 500

    return {
        "message": "Members imported successfully.",
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "errors": errors[:20],
    }, 200


def import_skills_csv(file_storage):
    if not file_storage:
        return {"error": "No file uploaded."}, 400

    try:
        raw = file_storage.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        return {"error": "File must be UTF-8 encoded CSV."}, 400

    reader = csv.DictReader(io.StringIO(raw))
    if not reader.fieldnames:
        return {"error": "CSV file is empty or missing headers."}, 400

    normalized = {h.strip().lower() for h in reader.fieldnames if h}
    if "skill_name" not in normalized:
        return {"error": "CSV must include a skill_name column."}, 400

    created = 0
    updated = 0
    skipped = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):
        data = {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}
        skill_name = data.get("skill_name")
        category = data.get("category") or None

        if not skill_name:
            skipped += 1
            errors.append(f"Row {row_num}: skill_name is required.")
            continue

        existing = Skill.query.filter_by(skill_name=skill_name).first()
        try:
            if existing:
                existing.category = category
                updated += 1
            else:
                db.session.add(Skill(skill_name=skill_name, category=category))
                created += 1
        except Exception:
            db.session.rollback()
            skipped += 1
            errors.append(f"Row {row_num}: could not save skill.")

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return {"error": "Failed to import skills."}, 500

    return {
        "message": "Skills imported successfully.",
        "created": created,
        "updated": updated,
        "skipped": skipped,
        "errors": errors[:20],
    }, 200
