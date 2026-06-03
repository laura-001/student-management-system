courses=[]

def add_course(course_id,code,course):
    course={
        'Course_id':course_id,
        'Code':code,
        'Course':course
    }
    courses.append(course)
    return course

def get_all_courses():
    return courses