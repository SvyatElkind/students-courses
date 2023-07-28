"""Tests for models"""
import pytest
from sqlalchemy.exc import IntegrityError

from app.db import db_session, Student, Course, Group


@pytest.fixture(scope="module", autouse=True)
def cleanup(request):
    """Cleanup a database once tests are finished."""

    def cleanup_db():
        with db_session() as session:
            session.query(Student).delete()
            session.query(Group).delete()
            session.query(Course).delete()
            session.commit()

    request.addfinalizer(cleanup_db)


def test_create_group():
    """Test create group."""
    Group.create_group("AA-11")
    with db_session() as session:
        group = session.query(Group).first()
    assert group.id == "AA-11"


def test_create_group_with_same_id():
    """Test create group with id that already exists."""
    with pytest.raises(IntegrityError):
        Group.create_group("AA-11")


def test_create_multiple_groups():
    """Test create multiple groups."""
    Group.create_multiple_groups(["BB-11", "CC-11"])
    with db_session() as session:
        group_b = session.query(Group).filter_by(id="BB-11").first()
        group_c = session.query(Group).filter_by(id="CC-11").first()
    assert group_b.id == "BB-11"
    assert group_c.id == "CC-11"


def test_create_student_without_group():
    """Test create student without group."""
    Student.create_student(first_name="David", last_name="Bo")
    with db_session() as session:
        david = session.query(Student).first()
    assert david.first_name == "David"
    assert david.last_name == "Bo"
    assert david.group_id is None


def test_create_student_with_existing_group():
    """Test create student with existing group."""
    Student.create_student(first_name="David", last_name="Bo", group_id="AA-11")
    with db_session() as session:
        david = session.query(Student).filter_by(group_id="AA-11").first()
    assert david.first_name == "David"
    assert david.last_name == "Bo"
    assert david.group_id == "AA-11"


def test_create_student_with_non_existing_group():
    """Test create student with non-existing group."""
    with pytest.raises(IntegrityError):
        Student.create_student(first_name="David", last_name="Bo", group_id="DD-11")


def test_get_all_groups_not_bigger_then():
    """Test for finds all groups with less or equals student count."""
    groups = Group.get_all_groups_not_bigger_then(1)
    assert len(groups) == 3


def test_create_multiple_students():
    """Tests for creating multiple student."""
    Student.create_multiple_students(student_list=["Karl First", "Karl Second"],
                                     group_id="AA-11")
    with db_session() as session:
        first = session.query(Student).filter_by(last_name="First").first()
        second = session.query(Student).filter_by(last_name="Second").first()
    assert first.first_name == "Karl"
    assert first.group_id == "AA-11"
    assert second.first_name == "Karl"
    assert second.group_id == "AA-11"


def test_get_student():
    """Test get student."""
    with db_session() as session:
        first = session.query(Student).filter_by(last_name="First").first()
    assert first is not None

def test_get_all_students():
    """Test get all students."""
    students = Student.get_all_students()
    # Already created students during test.
    assert len(students) == 4


def test_delete_student():
    """Test get student."""
    with db_session() as session:
        first = session.query(Student).filter_by(last_name="First").first()
    student_id = first.id
    Student.delete_student(student_id)
    with db_session() as session:
        first = session.query(Student).filter_by(last_name="First").first()
    assert first is None


def test_delete_non_existing_student():
    """Test get student."""
    with pytest.raises(UserWarning):
        Student.delete_student(0)


# Create course for further tests
def test_create_course():
    """Test create course."""
    Course.create_course("Art", "Course about Art")
    with db_session() as session:
        course = session.query(Course).filter_by(course_name="Art").first()
    assert course.course_name == "Art"


def test_create_course_that_exists():
    """Test create course that already exists."""
    with pytest.raises(IntegrityError):
        Course.create_course("Art", "Course about Art")


def test_create_multiple_courses():
    """Test multiple courses."""
    Course.create_multiple_courses({"History": "Course about History",
                                    "Biology": "Course about Biology"})
    with db_session() as session:
        history = session.query(Course).filter_by(course_name="History").first()
        biology = session.query(Course).filter_by(course_name="Biology").first()
    assert history.course_name == "History"
    assert biology.course_name == "Biology"


# Tests for Students - Courses relation
def test_add_students_to_course():
    """Test for add student to course."""
    with db_session() as session:
        karl = session.query(Student).filter_by(first_name="Karl").first()
    Student.add_student_to_course(karl.id, ["Art", "History"])
    with db_session() as session:
        karl = session.query(Student).filter_by(first_name="Karl").first()
        assert len(karl.courses) == 2


def test_remove_student_from_course():
    """Test remove student from course."""
    with db_session() as session:
        karl = session.query(Student).filter_by(first_name="Karl").first()
    Student.remove_student_from_course(karl.id, "Art")
    with db_session() as session:
        karl = session.query(Student).filter_by(first_name="Karl").first()
        assert len(karl.courses) == 1


def test_find_students_in_course():
    """Test find all students related to the course with a given name."""
    students = Course.find_students_in_course("History")
    assert len(students) == 1


def test_student_to_dict():
    """Test student object to dictionary"""
    with db_session() as session:
        karl = session.query(Student).filter_by(first_name="Karl").first()
    karl_id = karl.id
    karl_first_name = karl.first_name
    karl_last_name = karl.last_name
    karl_group_id = karl.group_id
    karl_dict = karl.to_dict()
    assert karl_dict == {"id": karl_id,
                         "first_name": karl_first_name,
                         "last_name": karl_last_name,
                         "group_id": karl_group_id}
