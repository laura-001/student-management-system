from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database.connection import Base


class Student(Base):
    __tablename__ = "students"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    student_number = Column(String(20), unique=True, nullable=False, index=True)
    year_of_study = Column(Integer, nullable=True)

    user = relationship("User", back_populates="student")
    registrations = relationship("Registration", back_populates="student", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("year_of_study BETWEEN 1 AND 4", name="check_year_of_study"),
    )

    def __repr__(self):
        return f"<Student user_id={self.user_id} number={self.student_number}>"
