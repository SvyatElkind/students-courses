# Abort messages:
NO_STUDENTS_FOUND = "No students were found."
NO_GROUPS_FOUND = "No groups were found"
GROUP_VALUE_ERROR = "parameter 'student_count' should be integer."
GROUP_TYPE_ERROR = "argument 'student_count' should be provided."
STUDENTS_FULL_NAME_MISSING = "First name and last name should be provided."
STUDENTS_INTEGRITY_ERROR = "Group id '{}' does not exist."
NEW_STUDENT_LOCATION_URL = "api/v1/students/{}/"
STUDENT_ID_NOT_FOUND = "A student with ID '{}' was not found."
COURSES_NOT_PROVIDED = "No courses were provided."
NO_STUDENT_OR_COURSE = "Either student or course was not found."
NO_STUDENT_COURSE_RELATION = "Student is not assigned to the course."

# Query parameters:
STUDENT_COUNT = "student_count"

# Data from request body:
FIRST_NAME = "first_name"
LAST_NAME = "last_name"
GROUP_ID = "group_id"
COURSES = "courses"

# Response headers:
LOCATION_HEADER = "Location"

# API documentation path
# For single student
STUDENT_DELETE_DOC = "./static/docs/single_student/delete_student.yaml"
STUDENT_CREATE_DOC = "./static/docs/single_student/create_student.yaml"
# For students courses relation
ADD_COURSE = "./static/docs/student_courses/add_student_to_course.yaml"
DELETE_COURSE = "./static/docs/student_courses/delete_student_from_course.yaml"
# For courses students relation
GET_STUDENTS_FROM_COURSE = "./static/docs/course_students/get_students_from_course.yaml"
# For groups
FIND_ALL_GROUPS = "./static/docs/groups/find_all_groups.yaml"


# Retry parameters
TRIES = 3
DELAY = 1



