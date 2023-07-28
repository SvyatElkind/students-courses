"""Module for Course related endpoints."""

from flask import abort, current_app
from flask_restful import Resource
from flasgger import swag_from

from app.api import api
from app.api.constants import NO_STUDENTS_FOUND, GET_STUDENTS_FROM_COURSE
from app.api.helper_functions import dict_helper
from app.db import Course


class CourseStudents(Resource):
    """Class provides CRUD operations with course-students association table."""
    @swag_from(GET_STUDENTS_FROM_COURSE)
    def get(self, course: str) -> list[dict]:
        """Finds all students related to the course with a given name.

        Args:
            course: Name of the course.

        Returns:
            List with student objects.
        """
        students = Course.find_students_in_course(course)
        if not students:
            current_app.logger.info(NO_STUDENTS_FOUND)
            abort(404, description=NO_STUDENTS_FOUND)
        return dict_helper(students)


api.add_resource(CourseStudents, "/courses/<course>/students")
