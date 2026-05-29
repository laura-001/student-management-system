from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(15), unique=True, nullable=False, index=True)
    course_name = Column(String(150), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    credit_units = Column(Integer, nullable=False)
    year_of_study = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    total_slots = Column(Integer, nullable=False, default=60)
    available_slots = Column(Integer, nullable=False, default=60)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("credit_units BETWEEN 1 AND 6", name="check_credit_units"),
        CheckConstraint("year_of_study BETWEEN 1 AND 4", name="check_course_year"),
        CheckConstraint("semester IN (1, 2)", name="check_semester"),
        CheckConstraint("available_slots >= 0", name="check_slots_non_negative"),
        CheckConstraint("available_slots <= total_slots", name="check_slots_not_exceed"),
    )

    department = relationship("Department", back_populates="courses")
    registrations = relationship("Registration", back_populates="course", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "course_code": self.course_code,
            "course_name": self.course_name,
            "department_id": self.department_id,
            "credit_units": self.credit_units,
            "year_of_study": self.year_of_study,
            "semester": self.semester,
            "total_slots": self.total_slots,
            "available_slots": self.available_slots,
            "is_active": self.is_active,
        }

    def __repr__(self):
        return f"<Course code={self.course_code} name={self.course_name} slots={self.available_slots}>"
