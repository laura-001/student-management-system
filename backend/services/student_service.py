students=[]

def add_student(student_id,name,Course,email,phone,password):
    student={
        'Student_id':student_id,
        'Name':name,
        'Course':Course,
        'Email':email,
        'Phone':phone,
        'Password':password
    }
    students.append(student)
    return student

def get_all_students():
    return students