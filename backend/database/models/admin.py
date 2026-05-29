from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base


class Admin(Base):
    __tablename__ = "admins"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    staff_number = Column(String(20), unique=True, nullable=False, index=True)
    admin_level = Column(Integer, default=1, nullable=False)

    user = relationship("User", back_populates="admin")

    def __repr__(self):
        return f"<Admin user_id={self.user_id} staff_number={self.staff_number}>"
