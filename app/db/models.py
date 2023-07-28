"""Module for database models"""

from flask import abort
from sqlalchemy.exc import NoResultFound, IntegrityError, DisconnectionError
from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from reretry import retry

from app.api.constants import TRIES, DELAY
from app.db import get_engine, db_session


# Constructs a base class
Base = declarative_base()


class Student(DeferredReflection, Base):
    """Class represents table 'students'."""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    first_name = Column(String(20), nullable=False)
    last_name = Column(String(20), nullable=False)
    group_id = Column(String(5), ForeignKey("groups.id", ondelete="SET NULL"))

    courses = relationship("Course", secondary="student_course", back_populates="students", cascade="all, delete")
    group = relationship("Group", back_populates="students")

    def __int__(self, first_name: str, last_name: str, group_id: str = None):
        """Initialize student object.

        Args:
            first_name: Student first name.
            last_name: Student last name.
            group_id: Group id to which student is assigned to.
        """
        self.first_name = first_name
        self.last_name = last_name
        self.group_id = group_id

    def __repr__(self):
        return f"<{self.first_name} {self.last_name}, in group: {self.group_id}>"

    @classmethod
    @retry(exceptions=DisconnectionError, tries=TRIES, delay=DELAY)
    def create_student(cls, first_name, last_name, group_id: str = None) -> int:
        """Create new student.

        Args:
            first_name: Student first name.
            last_name: Student last name.
            group_id: ID of group to which student is assigned.

        Returns:
            Created student id.

        Raises:
            IntegrityError: When group_id does not exist.
        """
        print("Hello")
        with db_session() as session:
            student = Student(first_name=first_name,
                              last_name=last_name,
                              group_id=group_id)
            try:
                session.add(student)
            except IntegrityError:
                # Raise when group_id does not exist.
                raise IntegrityError
            session.commit()
            created_id = student.id
        return created_id

    @classmethod
    @retry(exceptions=DisconnectionError, tries=TRIES, delay=DELAY)
    def create_multiple_students(cls, student_list: list, group_id: str = None) -> None:
        """Create multiple students for list of students.

        Args:
            student_list: list of students.
            group_id: ID of group to which students are assigned.
        """
        with db_session() as session:
            for student_name in student_list:
                f_name, l_name = student_name.split(" ")
                student = Student(first_name=f_name,
                                  last_name=l_name,
                                  group_id=group_id)
                session.add(student)
            session.commit()

    @classmethod
    @retry(exceptions=DisconnectionError, tries=TRIES, delay=DELAY)
    def get_student(cls, student_id: int, session=None):
        """Get students with specific id.

        Args:
            student_id: Student ID.
            session: SQLAlchemy session.

        Returns:
            student object.
        """
        if session:
            return session.query(Student).filter_by(id=student_id).one()

        with db_session() as session:
            student = session.query(Student).filter_by(id=student_id).one()
        return student

    @classmethod
    @retry(exceptions=DisconnectionError, tries=TRIES, delay=DELAY)
    def get_all_students(cls) -> list[dict]:
        """Get list of all students.

        Returns:
            list of dictionary of students.
        """
        with db_session() as session:
            students = session.query(Student).all()
        return students

    @classmethod
    @retry(exceptions=DisconnectionError, tries=TRIES, delay=DELAY)
    def delete_student(cls, student_id: int) -> None:
        """Delete student by specific ID.

        Args:
            student_id: Student ID.

        Raises:
            UserWarning: When 0 rows was deleted.
        """
        with db_session() as session:
            deleted_rows = session.query(Student).filter(Student.id == student_id).delete()
            if deleted_rows == 0:
                raise UserWarning
            session.commit()

    @classmethod
    @retry(exceptions=DisconnectionError, tries=TRIES, delay=DELAY)
    def add_student_to_course(cls, student_id: int, course_list: list[str]) -> None:
        """Add students to the course.

        Assign specific student to the courses from the list.

        Args:
            student_id: student ID.
            course_list: list of courses.

        Raises:
            NoResultFound: If either student or course was not found.
        """
        with db_session() as session:
            try:
                # Get student.
                student = Student.get_student(student_id, session)
                for course_name in course_list:
                    # Get course.
                    course = session.query(Course).filter(Course.course_name == course_name).one()
                    # Assign course to student.
                    student.courses.append(course)
            except NoResultFound:
                raise NoResultFound
            session.commit()

    @classmethod
    @retry(exceptions=DisconnectionError, tries=TRIES, delay=DELAY)
    def remove_student_from_course(cls, student_id: int, course_name: str) -> None:
        """Remove student from course.

        Remove specific student from the specific course.

        Args:
            student_id: student ID.
            course_name: course name.

        Raises:
            NoResultFound: If either student or course was not found.
            ValueError: If course is not assigned to the student.
        """
        with db_session() as session:
            try:
                student = session.query(Student).filter_by(id=student_id).one()
                course = session.query(Course).filter(Course.course_name == course_name).one()
                student.courses.remove(course)
            except NoResultFound:
                raise NoResultFound
            except ValueError:
                raise ValueError
            session.commit()

    def to_dict(self) -> dict:
        """Creates dictionary from student object.

        Result is used to build Responses object.

        Result:
            Dictionary with students data.
        """
        result = {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "group_id": self.group_id
        }
        return result


class Course(DeferredReflection, Base):
    """Class represents table 'course'."""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    course_name = Column(String(50), nullable=False)
    description = Column(String(200), nullable=False)
    students = relationship("Student", secondary="student_course", back_populates="courses", passive_deletes=True)

    def __int__(self, course_name: str, description: str) -> None:
        """Initialize course object.

        Args:
            course_name: Name of the course.
            description: Description of the course.

        Raises:
            IntegrityError: If the course with this name already exists.
        """
        self.course_name = course_name
        self.description = description

    def __repr__(self):
        return f"<Course: {self.course_name}>"

    @classmethod
    @retry(exceptions=DisconnectionError, tries=TRIES, delay=DELAY)
    def create_course(cls, course_name: str, description: str):
        """Create new course.

        Args:
            course_name: Name of the course.
            description: Description of the course.
        """
        with db_session() as session:
            # Create course object.
            course = Course(course_name=course_name, description=description)
            try:
                session.add(course)
            except IntegrityError:
                raise IntegrityError
            session.commit()

    @classmethod
    @retry(exceptions=DisconnectionError, tries=TRIES, delay=DELAY)
    def create_multiple_courses(cls, courses: dict[str: str]) -> None:
        """Create courses from dict of courses.

        Either one or multiple courses can be passed through argument.

        Args:
            courses:
                dictionary where key is course name and
                value is course description.

        Raises:
            IntegrityError: If the course with this name already exists.
        """
        with db_session() as session:
            for name, desc in courses.items():
                # Create course object.
                course = Course(course_name=name, description=desc)
                try:
                    session.add(course)
                except IntegrityError:
                    raise IntegrityError
            session.commit()

    @classmethod
    @retry(exceptions=DisconnectionError, tries=TRIES, delay=DELAY)
    def find_students_in_course(cls, course_name: str) -> list[dict]:
        """Find all students related to the course with a given name.

        Args:
            course_name: Name of specific course.

        Returns:
            List of dictionary of students.
        """
        with db_session() as session:
            students = session.query(Student).join(Student.courses).filter(Course.course_name == course_name).all()
        return students


class StudentCourse(DeferredReflection, Base):
    """Class represents association table 'student_course'."""
    __tablename__ = "student_course"

    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True)


class Group(DeferredReflection, Base):
    """Class represents table 'groups'."""
    __tablename__ = "groups"

    id = Column(String, primary_key=True, unique=True)
    students = relationship("Student", back_populates="group")

    def __init__(self, id: str):
        """Initialize group object.

        Args:
            id: ID of the group.
        """
        self.id = id

    def __repr__(self):
        return f"<Group id: {self.id}>"

    @classmethod
    @retry(exceptions=DisconnectionError, tries=TRIES, delay=DELAY)
    def create_group(cls, group_name: str) -> None:
        """Creates new group.

        Args:
            group_name: Name of new group.

        Raises:
            IntegrityError: If the group with given id already exists.
        """
        with db_session() as session:
            group = Group(id=group_name)
            try:
                session.add(group)
            except IntegrityError:
                raise IntegrityError
            session.commit()

    @classmethod
    @retry(exceptions=DisconnectionError, tries=TRIES, delay=DELAY)
    def create_multiple_groups(cls, group_list: list[str]) -> None:
        """Creates multiple groups from list of groups.

        Args:
            group_list: list of groups.

        Raises:
            IntegrityError: If the group with given id already exists.
        """
        with db_session() as session:
            for group_name in group_list:
                group = Group(id=group_name)
                try:
                    session.add(group)
                except IntegrityError:
                    raise IntegrityError
            session.commit()

    @classmethod
    @retry(exceptions=DisconnectionError, tries=TRIES, delay=DELAY)
    def get_all_groups_not_bigger_then(cls,
                                       student_count: int) -> list[str]:
        """Finds all groups with less or equals student count.

        Args:
            student_count: max student number in the group.

        Returns:
            list of groups.
        """
        with db_session() as session:
            groups = [group.id
                      for group in session.query(Group).all()
                      if len(group.students) <= student_count]

        return groups


DeferredReflection.prepare(get_engine())
