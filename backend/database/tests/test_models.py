import os
import sys

# ensure backend is on path so `import database` resolves
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest
from sqlalchemy.exc import IntegrityError

from database.models import User, Student, Admin, Department, Course, Registration


def test_user_student_relationship(db_session):
    user = User(full_name="Test Student", email="stu@example.com", password_hash="x", is_active=True, role="student")
    db_session.add(user)
    db_session.flush()

    student = Student(user_id=user.id, student_number="S100", year_of_study=2)
    db_session.add(student)
    db_session.commit()

    u = db_session.get(User, user.id)
    assert u is not None
    assert u.student is not None
    assert u.student.student_number == "S100"


def test_course_registration_relationship(db_session):
    dept = Department(code="CS", name="Computer Science")
    db_session.add(dept)
    db_session.flush()

    course = Course(course_code="CS101", course_name="Intro", department_id=dept.id, credit_units=3, year_of_study=1, semester=1, total_slots=50, available_slots=50)
    db_session.add(course)
    db_session.flush()

    user = User(full_name="Another Student", email="stu2@example.com", password_hash="y", is_active=True, role="student")
    db_session.add(user)
    db_session.flush()
    student = Student(user_id=user.id, student_number="S101", year_of_study=1)
    db_session.add(student)
    db_session.flush()

    reg = Registration(student_id=student.user_id, course_id=course.id, status="active")
    db_session.add(reg)
    db_session.commit()

    r = db_session.query(Registration).filter_by(id=reg.id).one()
    assert r.student.user_id == student.user_id
    assert r.course.course_code == "CS101"


def test_admin_relationship_and_uniqueness(db_session):
    admin_user = User(full_name="Admin", email="admin@example.com", password_hash="z", is_active=True, role="admin")
    db_session.add(admin_user)
    db_session.flush()

    admin = Admin(user_id=admin_user.id, staff_number="STF001", admin_level=2)
    db_session.add(admin)
    db_session.commit()

    a = db_session.get(User, admin_user.id)
    assert a.admin is not None
    assert a.admin.staff_number == "STF001"

    # uniqueness constraint on staff_number should raise on commit
    another_admin_user = User(full_name="Admin2", email="admin2@example.com", password_hash="z2", is_active=True, role="admin")
    db_session.add(another_admin_user)
    db_session.flush()
    duplicate_admin = Admin(user_id=another_admin_user.id, staff_number="STF001", admin_level=1)
    db_session.add(duplicate_admin)
    with pytest.raises(IntegrityError):
        db_session.commit()
