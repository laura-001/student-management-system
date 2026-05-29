from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.user_id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(20), default="active", nullable=False)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    dropped_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("status IN ('active', 'dropped', 'waitlisted')", name="check_registration_status"),
        UniqueConstraint("student_id", "course_id", name="unique_active_registration"),
    )

    student = relationship("Student", back_populates="registrations")
    course = relationship("Course", back_populates="registrations")

    def to_dict(self):
        return {
            "registration_id": self.id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "course_code": self.course.course_code if self.course else None,
            "course_name": self.course.course_name if self.course else None,
            "credit_units": self.course.credit_units if self.course else None,
            "semester": self.course.semester if self.course else None,
            "status": self.status,
            "registered_at": str(self.registered_at),
            "dropped_at": str(self.dropped_at) if self.dropped_at else None,
        }

    def __repr__(self):
        return f"<Registration student={self.student_id} course={self.course_id} status={self.status}>"
