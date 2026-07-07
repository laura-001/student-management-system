from pathlib import Path
import sys
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.config import settings
from core.dependencies import get_current_user
from core.security import create_access_token, hash_password, verify_password
from database.connection import get_db, init_db
from database.models import Admin, Course, Registration, Student, User


app = FastAPI(title=settings.APP_NAME)

allowed_origins = [
    origin.strip()
    for origin in settings.ALLOWED_ORIGINS.split(",")
    if origin.strip()
]
for dev_origin in ("http://127.0.0.1:5500", "http://localhost:5500", "null"):
    if dev_origin not in allowed_origins:
        allowed_origins.append(dev_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if "*" in allowed_origins else allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8)
    role: str = Field(pattern="^(student|admin)$")
    student_number: Optional[str] = None
    year_of_study: Optional[int] = Field(default=1, ge=1, le=4)
    staff_number: Optional[str] = None


class StudentUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    email: Optional[str] = Field(default=None, min_length=3, max_length=100)
    student_number: Optional[str] = Field(default=None, min_length=1, max_length=20)
    year_of_study: Optional[int] = Field(default=None, ge=1, le=4)


class RegisterCourseRequest(BaseModel):
    status: str = Field(default="active", pattern="^(active|waitlisted)$")


class CourseWriteRequest(BaseModel):
    course_code: Optional[str] = Field(default=None, min_length=1, max_length=15)
    course_name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    department_id: Optional[int] = None
    credit_units: Optional[int] = Field(default=None, ge=1, le=6)
    year_of_study: Optional[int] = Field(default=None, ge=1, le=4)
    semester: Optional[int] = Field(default=None, ge=1, le=2)
    total_slots: Optional[int] = Field(default=None, ge=0)
    available_slots: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None


def _student_number_for(user_id: int) -> str:
    return f"STU/{user_id:05d}/26"


def _staff_number_for(user_id: int) -> str:
    return f"STAFF/{user_id:05d}/26"


def _serialize_student(user: User) -> dict:
    student = user.student
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "student_number": student.student_number if student else None,
        "year_of_study": student.year_of_study if student else None,
    }


def _serialize_admin(user: User) -> dict:
    admin = user.admin
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "staff_number": admin.staff_number if admin else None,
        "admin_level": admin.admin_level if admin else None,
        "created_at": str(user.created_at) if user.created_at else None,
    }


def _serialize_user_summary(user: User) -> dict:
    payload = {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": str(user.created_at) if user.created_at else None,
    }
    if user.role == "student" and user.student:
        payload.update(
            {
                "student_number": user.student.student_number,
                "year_of_study": user.student.year_of_study,
            }
        )
    if user.role == "admin" and user.admin:
        payload.update(
            {
                "staff_number": user.admin.staff_number,
                "admin_level": user.admin.admin_level,
            }
        )
    return payload


def _serialize_course(course: Course) -> dict:
    department_name = course.department.name if course.department else None
    return {
        "id": course.id,
        "course_code": course.course_code,
        "course_name": course.course_name,
        "department": department_name,
        "credit_units": course.credit_units,
        "year_of_study": course.year_of_study,
        "semester": course.semester,
        "total_slots": course.total_slots,
        "available_slots": course.available_slots,
        "is_active": course.is_active,
    }


def _serialize_registration(registration: Registration) -> dict:
    payload = registration.to_dict()
    if registration.course and registration.course.department:
        payload["department"] = registration.course.department.name
    else:
        payload["department"] = None
    return payload


def _serialize_admin_registration(registration: Registration) -> dict:
    payload = _serialize_registration(registration)
    student_user = registration.student.user if registration.student else None
    payload.update(
        {
            "student_name": student_user.full_name if student_user else None,
            "student_email": student_user.email if student_user else None,
            "student_number": registration.student.student_number if registration.student else None,
        }
    )
    return payload


def _current_student(user: User = Depends(get_current_user)) -> User:
    if user.role != "student" or user.student is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="A student account is required for this action.",
        )
    return user


def _current_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin" or user.admin is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="An admin account is required for this action.",
        )
    return user


def _apply_course_payload(course: Course, payload: CourseWriteRequest, *, creating: bool = False) -> None:
    data = payload.model_dump(exclude_unset=not creating)
    required_fields = ("course_code", "course_name", "credit_units", "year_of_study", "semester")
    if creating:
        missing = [field for field in required_fields if data.get(field) in (None, "")]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Missing required course fields: {', '.join(missing)}.",
            )

    for field, value in data.items():
        if value is None and field not in {"department_id"}:
            continue
        if field == "course_code" and value is not None:
            value = value.strip().upper()
        if field == "course_name" and value is not None:
            value = value.strip()
        setattr(course, field, value)

    if course.total_slots is None:
        course.total_slots = 60
    if course.available_slots is None:
        course.available_slots = course.total_slots
    if course.available_slots > course.total_slots:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Available slots cannot be greater than total slots.",
        )


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> dict:
    email = payload.email.strip().lower()
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        full_name=payload.full_name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    db.flush()

    if payload.role == "student":
        student_number = (payload.student_number or _student_number_for(user.id)).strip()
        db.add(
            Student(
                user_id=user.id,
                student_number=student_number,
                year_of_study=payload.year_of_study or 1,
            )
        )
    else:
        staff_number = (payload.staff_number or _staff_number_for(user.id)).strip()
        db.add(Admin(user_id=user.id, staff_number=staff_number, admin_level=1))

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The generated student or staff number already exists.",
        )

    return {"message": "Account created successfully."}


@app.post("/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict:
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email, User.is_active.is_(True)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token({"user_id": user.id, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": _serialize_student(user) if user.role == "student" else {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
        },
    }


@app.get("/admin/me")
def get_my_admin_profile(current_user: User = Depends(_current_admin)) -> dict:
    return _serialize_admin(current_user)


@app.get("/admin/users")
def list_admin_users(
    role: Optional[str] = Query(default=None, pattern="^(student|admin)$"),
    active_only: bool = True,
    current_user: User = Depends(_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    query = db.query(User).options(joinedload(User.student), joinedload(User.admin))
    if role:
        query = query.filter(User.role == role)
    if active_only:
        query = query.filter(User.is_active.is_(True))
    users = query.order_by(User.role, User.full_name).all()
    return {"users": [_serialize_user_summary(user) for user in users]}


@app.get("/admin/courses")
def list_admin_courses(
    current_user: User = Depends(_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    courses = (
        db.query(Course)
        .options(joinedload(Course.department))
        .order_by(Course.year_of_study, Course.semester, Course.course_code)
        .all()
    )
    return {"courses": [_serialize_course(course) for course in courses]}


@app.post("/admin/courses", status_code=status.HTTP_201_CREATED)
def create_admin_course(
    payload: CourseWriteRequest,
    current_user: User = Depends(_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    course = Course()
    _apply_course_payload(course, payload, creating=True)
    if course.is_active is None:
        course.is_active = True
    db.add(course)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A course with this code already exists.",
        )
    db.refresh(course)
    return _serialize_course(course)


@app.patch("/admin/courses/{course_id}")
def update_admin_course(
    course_id: int,
    payload: CourseWriteRequest,
    current_user: User = Depends(_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
    _apply_course_payload(course, payload)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A course with this code already exists.",
        )
    db.refresh(course)
    return _serialize_course(course)


@app.patch("/admin/courses/{course_id}/deactivate")
def deactivate_admin_course(
    course_id: int,
    current_user: User = Depends(_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
    course.is_active = False
    db.commit()
    db.refresh(course)
    return _serialize_course(course)


@app.get("/admin/registrations")
def list_admin_registrations(
    status_filter: Optional[str] = Query(default=None, alias="status", pattern="^(active|waitlisted|dropped)$"),
    current_user: User = Depends(_current_admin),
    db: Session = Depends(get_db),
) -> dict:
    query = (
        db.query(Registration)
        .options(
            joinedload(Registration.course).joinedload(Course.department),
            joinedload(Registration.student).joinedload(Student.user),
        )
    )
    if status_filter:
        query = query.filter(Registration.status == status_filter)
    registrations = query.order_by(Registration.registered_at.desc()).all()
    items = [_serialize_admin_registration(registration) for registration in registrations]
    return {
        "registrations": items,
        "summary": {
            "total": len(items),
            "active": sum(1 for item in items if item["status"] == "active"),
            "waitlisted": sum(1 for item in items if item["status"] == "waitlisted"),
            "dropped": sum(1 for item in items if item["status"] == "dropped"),
        },
    }


@app.get("/students/me")
def get_my_student_profile(current_user: User = Depends(_current_student)) -> dict:
    return _serialize_student(current_user)


@app.patch("/students/me")
def update_my_student_profile(
    payload: StudentUpdateRequest,
    current_user: User = Depends(_current_student),
    db: Session = Depends(get_db),
) -> dict:
    user = db.query(User).options(joinedload(User.student)).filter(User.id == current_user.id).one()

    if payload.email is not None:
        email = payload.email.strip().lower()
        duplicate = db.query(User).filter(User.email == email, User.id != user.id).first()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another account is already using this email.",
            )
        user.email = email

    if payload.full_name is not None:
        user.full_name = payload.full_name.strip()

    if payload.student_number is not None:
        student_number = payload.student_number.strip()
        duplicate = (
            db.query(Student)
            .filter(Student.student_number == student_number, Student.user_id != user.id)
            .first()
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another student is already using this student number.",
            )
        user.student.student_number = student_number

    if payload.year_of_study is not None:
        user.student.year_of_study = payload.year_of_study

    db.commit()
    db.refresh(user)
    return _serialize_student(user)


@app.get("/students/me/registrations")
def get_my_registrations(
    current_user: User = Depends(_current_student),
    db: Session = Depends(get_db),
) -> dict:
    registrations = (
        db.query(Registration)
        .options(joinedload(Registration.course).joinedload(Course.department))
        .filter(Registration.student_id == current_user.id)
        .order_by(Registration.registered_at.desc())
        .all()
    )
    items = [_serialize_registration(registration) for registration in registrations]
    active_items = [item for item in items if item["status"] == "active"]
    return {
        "registrations": items,
        "summary": {
            "registered_count": len(active_items),
            "total_units": sum(item["credit_units"] or 0 for item in active_items),
        },
    }


@app.post("/students/me/registrations/{course_id}", status_code=status.HTTP_201_CREATED)
def register_for_course(
    course_id: int,
    payload: RegisterCourseRequest,
    current_user: User = Depends(_current_student),
    db: Session = Depends(get_db),
) -> dict:
    course = db.query(Course).filter(Course.id == course_id, Course.is_active.is_(True)).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")

    existing = (
        db.query(Registration)
        .filter(Registration.student_id == current_user.id, Registration.course_id == course_id)
        .first()
    )
    if existing and existing.status != "dropped":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already registered for this course.",
        )

    registration = Registration(
        student_id=current_user.id,
        course_id=course_id,
        status=payload.status,
    )
    db.add(registration)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to register for this course.",
        )
    db.refresh(registration)
    return _serialize_registration(registration)


@app.get("/courses")
def list_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(_current_student),
) -> dict:
    registered_course_ids = {
        row.course_id
        for row in db.query(Registration.course_id)
        .filter(Registration.student_id == current_user.id, Registration.status != "dropped")
        .all()
    }
    courses = (
        db.query(Course)
        .options(joinedload(Course.department))
        .filter(Course.is_active.is_(True))
        .order_by(Course.year_of_study, Course.semester, Course.course_code)
        .all()
    )
    return {
        "courses": [
            {
                **_serialize_course(course),
                "is_registered": course.id in registered_course_ids,
            }
            for course in courses
        ]
    }


FRONTEND_DIR = BACKEND_DIR.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
