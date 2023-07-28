"""Module for generating test data and adding them to database"""
import random
import string
from typing import Optional, Union

from app.db import Student, Group, Course, db_session

# 20 first names.
FIRST_NAME = ['Monica', 'Rachel', 'Phoeby', 'Daniela', 'Rebecca', 'Eva',
              'Alexandra', 'Katherine', 'Lisa', 'Hannah', 'Sonny', 'Pedro',
              'Kasey', 'George', 'Jan', 'Devon', 'Alexander', 'Markus',
              'Logan', 'Israel']
# 20 last names.
LAST_NAME = ['Mcneil', 'Fritz', 'Hansen', 'Hampton', 'Neal', 'Phelps',
             'Mccormick', 'Sullivan', 'Bass', 'Madden', 'Brock', 'Jarvis',
             'Vance', 'Delgado', 'Harrison', 'Hart', 'Wong', 'Wong', 'Newton',
             'Hopkins']
# 10 courses.
LIST_OF_COURSES = ['Mathematics', 'History', 'Literature', 'Art', 'Computer Science',
                   'Philosophy', 'Biology', 'Chemistry', 'Physics', 'Sociology']
# Number of randomly generated groups.
NUMBER_OF_GROUPS = 10
# Number of choices.
NUMBER_OF_CHOICES = 2
# Number of randomly generated students.
NUMBER_OF_STUDENTS = 200

# Number of students in the group (from 10 to 30)
START_RANGE = 10
END_RANGE = 31

# Random course number (from 1 to 3)
COURSE_START_RANGE = 1
COURSE_END_RANGE = 4


def generate_groups() -> list[str]:
    """Generates random groups.

    Generates 10 groups with randomly generated names.
    The name contain 2 characters, hyphen, 2 numbers.

    Example:
        Group name: AB-21.

    Returns:
        List of group names.
    """
    groups = []
    for _ in range(NUMBER_OF_GROUPS):
        # Get 2 random characters.
        letters = ''.join(random.choices(string.ascii_uppercase, k=NUMBER_OF_CHOICES))
        # Get 2 random digits.
        numbers = ''.join(random.choices(string.digits, k=NUMBER_OF_CHOICES))
        # Generate group name.
        group_name = '-'.join([letters, numbers])
        groups.append(group_name)

    return groups


def generate_students() -> list[str]:
    """Generates random students.

    Generates 200 students randomly combining 20 first names and 20 last names.

    Returns:
        List of students.
    """
    students = []
    for _ in range(NUMBER_OF_STUDENTS):
        # Generate student full name.
        student = ' '.join([random.choice(FIRST_NAME), random.choice(LAST_NAME)])
        students.append(student)

    return students


def students_to_groups() -> dict[Optional[str]: Union[list[str], list]]:
    """Randomly assigns students to  groups.

    Each group could contain from 10 to 30 students. It is possible
    that some groups will be without students or students without groups.

    Returns:
        Dictionary of groups and students.
    """
    # Get names of group.
    groups = generate_groups()
    # Get names of students.
    students = generate_students()
    student_groups = {}
    while True:
        # Get random number of students.
        number = random.choice(range(START_RANGE, END_RANGE))
        # Check if number of students left is not less than random number and
        # empty group is available.
        if len(students) >= number and groups:
            # Shuffle list of students and groups.
            random.shuffle(students)
            random.shuffle(groups)
            # get randomly generated number of students.
            random_students = students[:number]
            # Update list of students.
            students = students[number:]
            # Add students to the group, where group is key
            # and list of students is value.
            student_groups[groups.pop(-1)] = random_students
        else:
            break

    while groups:
        # Assign empty list to group.
        student_groups[groups.pop(-1)] = []

    if students:
        # Assign student list with no group to None.
        student_groups[None] = students

    return student_groups


def get_courses_with_description() -> dict[str: str]:
    """Create courses with description.

    Returns:
        Dictionary where key is course and value is description.
    """
    course_description = {course: f'Subject of {course}' for course in LIST_OF_COURSES}
    return course_description


def add_test_data_to_groups_table(list_of_groups: list) -> None:
    """Adds test data to groups table.

    Args:
        list_of_groups: list of randomly generated groups.
    """
    Group.create_multiple_groups(list_of_groups)


def add_test_data_to_students_table(
        students_groups: dict[Optional[str]: Union[list[str], list]]) -> None:
    """Add test data to students table.

    Args:
        students_groups: dictionary of groups and students.
    """
    for group, students in students_groups.items():
        # Create students in single group.
        Student.create_multiple_students(students, group)


def add_test_data_to_course_table() -> None:
    """Add test data to course table."""
    # Get input data.
    course_dict = get_courses_with_description()
    Course.create_multiple_courses(course_dict)


def add_students_to_course() -> None:
    """Assign course to student.

    Randomly assign from 1 to 3 courses for each student.
    """
    with db_session() as session:
        # Get all students.
        students = session.query(Student).all()
        for student in students:
            # For each student get random number from 1 to 3 and get equivalent
            # number of unique courses from list of courses.
            number = random.choice(range(COURSE_START_RANGE, COURSE_END_RANGE))
            course_list = random.sample(LIST_OF_COURSES, k=number)
            for course_name in course_list:
                # Assign each course to student.
                course = session.query(Course).filter(Course.course_name == course_name).first()
                student.courses.append(course)
        session.commit()


def add_test_data_to_database() -> None:
    """Adds test data to database"""
    # Check if DB already have test data in it.
    with db_session() as session:
        if not session.query(Student).first():
            # Get randomly generated groups and students.
            students_groups = students_to_groups()

            # Remove all None value keys to create groups.
            group_list = [group
                          for group in list(students_groups.keys())
                          if group is not None]
            add_test_data_to_groups_table(group_list)

            add_test_data_to_students_table(students_groups)
            add_test_data_to_course_table()
            add_students_to_course()
