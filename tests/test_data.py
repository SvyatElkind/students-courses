"""Tests for functions for test data generation for database"""

import re

from app.db.test_data import generate_groups, generate_students, students_to_groups,\
    get_courses_with_description


def test_generate_groups():
    """Test generate_groups function"""
    groups = generate_groups()

    pattern = re.compile("[A-Z][A-Z]-[0-9][0-9]")
    match = False
    if pattern.match(groups[0]):
        match = True
    assert len(groups) == 10
    assert match


def test_generate_students():
    """Test generate_students function"""
    students = generate_students()

    assert len(students) == 200


def test_student_to_groups():
    """Test student_to_groups function"""
    student_groups = students_to_groups()

    count = 0
    for students in student_groups.values():
        count += len(students)

    # Count of students
    assert count == 200
    # 11 keys appear when there is student with no group attached.
    assert len(student_groups.keys()) in [10, 11]


def test_get_courses_with_description():
    """Test get_courses_with_description function."""
    course_description = get_courses_with_description()

    assert len(course_description.keys()) == 10
    assert len(course_description.values()) == 10





