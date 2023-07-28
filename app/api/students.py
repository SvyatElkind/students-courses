"""Module for Student related endpoints."""

from flask import request, Response, abort, current_app
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError, NoResultFound
from flasgger import swag_from

from app.api import api
from app.api.constants import (
    FIRST_NAME, GROUP_ID, LAST_NAME, STUDENTS_FULL_NAME_MISSING,
    STUDENTS_INTEGRITY_ERROR, NEW_STUDENT_LOCATION_URL, LOCATION_HEADER,
    STUDENT_ID_NOT_FOUND, COURSES_NOT_PROVIDED, COURSES, NO_STUDENT_OR_COURSE,
    NO_STUDENT_COURSE_RELATION,
    STUDENT_DELETE_DOC, STUDENT_CREATE_DOC, ADD_COURSE, DELETE_COURSE)
from app.db import Student


class Students(Resource):
    """Class provides CRUD operations with students table."""

    @swag_from(STUDENT_CREATE_DOC)
    def post(self) -> Response:
        """Adds new student.

        New student data is provided in request body.

        Returns:
            Response object with location of new student in header.
        """
        # Get students data from request body.
        from_json = request.json
        first_name = from_json.get(FIRST_NAME)
        last_name = from_json.get(LAST_NAME)
        group_id = from_json.get(GROUP_ID)

        # Check if first and last name were provided.
        if not all([first_name, last_name]):
            current_app.logger.info(STUDENTS_FULL_NAME_MISSING)
            abort(400, description=STUDENTS_FULL_NAME_MISSING)
        try:
            student_id = Student.create_student(first_name, last_name, group_id)
        except IntegrityError:
            # If group name does not exist.
            current_app.logger.info(STUDENTS_INTEGRITY_ERROR.format(group_id))
            abort(400, description=STUDENTS_INTEGRITY_ERROR.format(group_id))
        return Response(status=201,
                        headers={LOCATION_HEADER: NEW_STUDENT_LOCATION_URL.format(student_id)})


class SingleStudent(Resource):
    """Class provides CRUD operations with single student."""

    @swag_from(STUDENT_DELETE_DOC)
    def delete(self, student_id) -> Response:
        """Deletes student with specific id.

        Args:
            student_id: Student ID.

        Returns:
            Response object.
        """
        try:
            Student.delete_student(student_id)
        except UserWarning:
            current_app.logger.info(STUDENT_ID_NOT_FOUND.format(student_id))
            abort(404, description=STUDENT_ID_NOT_FOUND.format(student_id))
        return Response(status=200)


class StudentCourses(Resource):
    """Class provides CRUD operations with student-courses association."""

    @swag_from(ADD_COURSE)
    def put(self, student_id) -> Response:
        """Add a student to the course (from a list).

        Args:
            student_id: Student ID.

        Returns:
            Response object.
        """
        from_json = request.json
        # Get list of courses
        courses = from_json.get(COURSES)
        if not courses:
            current_app.logger.info(COURSES_NOT_PROVIDED)
            abort(400, description=COURSES_NOT_PROVIDED)
        try:
            # Add a student to the course
            Student.add_student_to_course(student_id, courses)
        except NoResultFound:
            current_app.logger.info(NO_STUDENT_OR_COURSE)
            abort(404, description=NO_STUDENT_OR_COURSE)
        return Response(status=200)

    @swag_from(DELETE_COURSE)
    def delete(self, student_id: int) -> Response:
        """Remove the student from one of his or her courses.

        Args:
            student_id: Student ID.

        Returns:
            Response object.
        """
        course_name = request.args.get("course")
        if not course_name:
            current_app.logger.info(COURSES_NOT_PROVIDED)
            abort(400, description=COURSES_NOT_PROVIDED)
        try:
            Student.remove_student_from_course(student_id, course_name)
        except NoResultFound:
            current_app.logger.info(NO_STUDENT_OR_COURSE)
            abort(404, description=NO_STUDENT_OR_COURSE)
        except ValueError:
            current_app.logger.info(NO_STUDENT_COURSE_RELATION)
            abort(400, description=NO_STUDENT_COURSE_RELATION)
        return Response(status=200)


api.add_resource(Students, "/students/")
api.add_resource(SingleStudent, "/students/<student_id>/")
api.add_resource(StudentCourses, "/students/<student_id>/courses/")
