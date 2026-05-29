DROP TABLE IF EXISTS registrations CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS admins CASCADE;
DROP TABLE IF EXISTS departments CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'admin')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    course_code VARCHAR(15) UNIQUE NOT NULL,
    course_name VARCHAR(150) NOT NULL,
    department_id INT REFERENCES departments(id) ON DELETE SET NULL,
    credit_units INT NOT NULL CHECK (credit_units BETWEEN 1 AND 6),
    year_of_study INT CHECK (year_of_study BETWEEN 1 AND 4),
    semester INT CHECK (semester IN (1, 2)),
    total_slots INT NOT NULL DEFAULT 60,
    available_slots INT NOT NULL DEFAULT 60,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT slots_valid CHECK (available_slots >= 0),
    CONSTRAINT slots_not_exceed CHECK (available_slots <= total_slots)
);

CREATE TABLE students (
    user_id INT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    student_number VARCHAR(20) UNIQUE NOT NULL,
    year_of_study INT CHECK (year_of_study BETWEEN 1 AND 4)
);

CREATE TABLE admins (
    user_id INT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    staff_number VARCHAR(20) UNIQUE NOT NULL,
    admin_level INT DEFAULT 1
);

CREATE TABLE registrations (
    id SERIAL PRIMARY KEY,
    student_id INT NOT NULL REFERENCES students(user_id) ON DELETE CASCADE,
    course_id INT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'dropped', 'waitlisted')),
    registered_at TIMESTAMP DEFAULT NOW(),
    dropped_at TIMESTAMP,

    CONSTRAINT unique_active_registration UNIQUE (student_id, course_id)
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_students_number ON students(student_number);
CREATE INDEX idx_admins_staff_number ON admins(staff_number);
CREATE INDEX idx_courses_code ON courses(course_code);
CREATE INDEX idx_courses_department ON courses(department_id);
CREATE INDEX idx_registrations_student ON registrations(student_id);
CREATE INDEX idx_registrations_course ON registrations(course_id);

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_courses_updated_at
    BEFORE UPDATE ON courses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE OR REPLACE FUNCTION manage_course_slots()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.status = 'active' THEN
        UPDATE courses
        SET available_slots = available_slots - 1
        WHERE id = NEW.course_id AND available_slots > 0;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'No available slots for this course';
        END IF;

    ELSIF TG_OP = 'UPDATE' AND OLD.status = 'active' AND NEW.status = 'dropped' THEN
        UPDATE courses
        SET available_slots = available_slots + 1
        WHERE id = NEW.course_id;

        NEW.dropped_at = NOW();
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_manage_slots
    BEFORE INSERT OR UPDATE ON registrations
    FOR EACH ROW EXECUTE FUNCTION manage_course_slots();

INSERT INTO departments (code, name) VALUES
    ('BIT',  'Business Information Technology'),
    ('CS',   'Computer Science'),
    ('MATH', 'Mathematics'),
    ('BCOM', 'Business Commerce');

INSERT INTO courses (course_code, course_name, department_id, credit_units, year_of_study, semester, total_slots, available_slots) VALUES
    ('BIT1101', 'Introduction to Programming',         1, 3, 1, 1, 60, 60),
    ('BIT1102', 'Computer Mathematics',                4, 3, 1, 1, 60, 60),
    ('BIT1201', 'Object Oriented Programming',         1, 3, 1, 2, 60, 60),
    ('BIT1202', 'Database Systems I',                  1, 3, 1, 2, 60, 60),
    ('BIT2101', 'Data Structures and Algorithms',      1, 3, 2, 1, 50, 50),
    ('BIT2102', 'Systems Analysis and Design',         1, 3, 2, 1, 50, 50),
    ('BIT2201', 'Web Application Development',         1, 3, 2, 2, 50, 50),
    ('BIT2202', 'Database Systems II',                 1, 3, 2, 2, 50, 50),
    ('BIT3101', 'Software Engineering',                1, 3, 3, 1, 45, 45),
    ('BIT3102', 'Network and Communications',          2, 3, 3, 1, 45, 45),
    ('BIT3201', 'Information Security',                2, 3, 3, 2, 45, 45),
    ('BIT3202', 'Mobile Application Development',      1, 3, 3, 2, 45, 45),
    ('BIT4101', 'Final Year Project I',                1, 6, 4, 1, 40, 40),
    ('BIT4102', 'Entrepreneurship and Innovation',     4, 3, 4, 1, 40, 40),
    ('MATH1101','Calculus and Linear Algebra',         3, 3, 1, 1, 80, 80);

INSERT INTO users (full_name, email, password_hash, role) VALUES
    ('John Kamau', 'john.kamau@strathmore.edu',
     '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMaJobMSdNFECLcnU9Lq5Vz8Gy', 'student');

INSERT INTO students (user_id, student_number, year_of_study) VALUES
    ((SELECT id FROM users WHERE email='john.kamau@strathmore.edu'), 'BIT/00001/24', 2);

-- Sample admin seed
INSERT INTO users (full_name, email, password_hash, role) VALUES
    ('Admin User', 'admin@strathmore.edu',
     '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMaJobMSdNFECLcnU9Lq5Vz8Gy', 'admin');

INSERT INTO admins (user_id, staff_number, admin_level) VALUES
    ((SELECT id FROM users WHERE email='admin@strathmore.edu'), 'STAFF/00001/24', 1);
