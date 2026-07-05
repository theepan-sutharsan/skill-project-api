from app.extensions import db


class Session(db.Model):
    """
    A scheduled meeting created once a swap_request has been accepted.
    One-to-one with swap_requests (each accepted request gets one session).
    """

    __tablename__ = "sessions"

    session_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(
        db.Integer, db.ForeignKey("swap_requests.request_id"), nullable=False, unique=True
    )
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.Time, nullable=False)
    meeting_link = db.Column(db.String(255), nullable=True)
    status = db.Column(
        db.Enum("scheduled", "completed", "cancelled", name="session_status"),
        default="scheduled",
        nullable=False,
    )

    # Relationships
    request = db.relationship("SwapRequest", back_populates="session")

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "request_id": self.request_id,
            "session_date": self.session_date.isoformat() if self.session_date else None,
            "session_time": self.session_time.strftime("%H:%M:%S")
            if self.session_time
            else None,
            "meeting_link": self.meeting_link,
            "status": self.status,
        }
