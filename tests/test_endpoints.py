"""Tests for API endpoints"""
from typing import Union
from unittest.mock import patch, MagicMock

import pytest
from flask import json
from flask.testing import FlaskClient
from sqlalchemy.exc import NoResultFound, IntegrityError

from app.db import db_session, Student, Course, Group
from app import create_app
from app.constants import TESTING


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

@pytest.fixture(scope="module")
def client() -> FlaskClient:
    """Create test client

    Returns:
        Flask Client for test purpose.
    """
    app = create_app(TESTING)
    return app.test_client()


class TestPostStudent:
    """Tests for POST "/api/v1/students/"."""

    @pytest.mark.parametrize("request_body, status_code",
                             [({"first_name": "David", "last_name": "Bo"}, 201),
                              ({"first_name": "David"}, 400)])
    @patch("app.api.students.Student.create_student", return_value=1)
    def test_response_status_code(self,
                                  mock_create_student: MagicMock,
                                  client: FlaskClient,
                                  request_body: dict,
                                  status_code: int):
        """Test status code.

        Args:
            mock_create_student: Mocked method.
            client: Flask test client.
            request_body: Request body with student data.
            status_code: Response status code.
        """
        response = client.post("/api/v1/students/",
                               data=json.dumps(request_body),
                               content_type="application/json")
        assert response.status_code == status_code

    def test_response_when_error(self, client: FlaskClient):
        """Test response when IntegrityError raises.

        Args:
            client: Flask test client.
        """
        response = client.post("/api/v1/students/",
                               data=json.dumps({"first_name": "David",
                                                "last_name": "Bo",
                                                "group_id": 1000}),
                               content_type="application/json")
        assert response.status_code == 400
        assert response.json == {"message": "Group id '1000' does not exist."}

    @patch("app.api.students.Student.create_student",
           return_value=1)
    def test_response_location_in_header(self, mock_create_student: MagicMock, client: FlaskClient):
        """Test location of created user.

        Args:
            mock_create_student: Mocked method.
            client: Flask test client.

        """
        response = client.post("/api/v1/students/",
                               data=json.dumps({"first_name": "David", "last_name": "Bo"}),
                               content_type="application/json")
        assert "api/v1/students/1/" in response.headers["Location"]


class TestDeleteStudent:
    """Tests for DELETE "/api/v1/students/<student_id>"."""

    @patch("app.api.students.Student.delete_student", return_value=None)
    def test_response_status_code_when_success(self,
                                               mock_delete_student: MagicMock,
                                               client: FlaskClient):
        """Test response status code when student is deleted.

        Args:
            mock_delete_student: Mocked method.
            client: Flask test client.
        """
        response = client.delete("/api/v1/students/1/",
                                 content_type="application/json")
        assert response.status_code == 200

    @patch("app.api.students.Student.delete_student", side_effect=UserWarning)
    def test_response_when_error(self, mock_delete_student: MagicMock, client: FlaskClient):
        """Test response when student is not found.

        Args:
            mock_delete_student: Mocked method.
            client: Flask test client.
        """
        response = client.delete("/api/v1/students/1/",
                                 content_type="application/json")
        assert response.status_code == 404
        assert response.json == {"message": "A student with ID '1' was not found."}


class TestPutStudentCourses:
    """Tests for PUT /students/<student_id>/courses/"""

    def test_response_status_code_when_no_courses(self, client: FlaskClient):
        """Test response when courses are not provided.

        Args:
            client: Flask test client.
        """
        response = client.put("api/v1/students/1/courses/",
                              data=json.dumps({"test": "test"}),
                              content_type="application/json")
        assert response.status_code == 400
        assert response.json == {"message": "No courses were provided."}

    @patch("app.api.students.Student.add_student_to_course", return_value=None)
    def test_response_status_code_when_success(self,
                                               mock_put_student_courses: MagicMock,
                                               client: FlaskClient):
        """Test response status code.

        When student is added to the course.

        Args:
            mock_put_student_courses: Mocked method
            client: Flask test client.
        """
        response = client.put("api/v1/students/1/courses/",
                              data=json.dumps({"courses": "test"}),
                              content_type="application/json")
        assert response.status_code == 200

    @patch("app.api.students.Student.add_student_to_course", side_effect=NoResultFound)
    def test_response_when_error(self,
                                 mock_put_student_courses: MagicMock,
                                 client: FlaskClient):
        """Test response when either student or course was not found.

        Args:
            mock_put_student_courses: Mocked method
            client: Flask test client.
        """
        response = client.put("api/v1/students/1/courses/",
                              data=json.dumps({"courses": "test"}),
                              content_type="application/json")
        assert response.status_code == 404
        assert response.json == {"message": "Either student or course was not found."}


class TestDeleteStudentCourses:
    """Tests for DELETE /students/<student_id>/courses/"""

    def test_response_when_no_course_provided(self, client: FlaskClient):
        """Test response when course is not provided.

        Args:
            client: Flask test client.
        """
        response = client.delete("api/v1/students/1/courses/",
                                 content_type="application/json")
        assert response.status_code == 400
        assert response.json == {"message": "No courses were provided."}

    @patch("app.api.students.Student.remove_student_from_course", return_value=None)
    def test_response_status_code_when_success(self,
                                               mock_remove_student_from_course: MagicMock,
                                               client: FlaskClient):
        """Test response status code.

        When student is removed from the course.

        Args:
            mock_remove_student_from_course: Mocked method
            client: Flask test client.
        """
        response = client.delete("api/v1/students/1/courses/?course=test",
                                 content_type="application/json")
        assert response.status_code == 200

    @pytest.mark.parametrize(
        "error, message, status_code",
        [(ValueError, {"message": "Student is not assigned to the course."}, 400),
         (NoResultFound, {"message": "Either student or course was not found."}, 404)])
    @patch("app.api.students.Student.remove_student_from_course")
    def test_response_when_error(self,
                                 mock_remove_student_from_course: MagicMock,
                                 error: Union[ValueError, NoResultFound],
                                 message: dict,
                                 status_code: int,
                                 client: FlaskClient):
        """Test response when error is raised.

        Args:
            mock_remove_student_from_course: Mocked method.
            error: Raised exception.
            message: Error message in response body.
            status_code: Response status code.
            client: Flask test client.
        """
        mock_remove_student_from_course.side_effect = error
        response = client.delete("api/v1/students/1/courses/?course=test",
                                 content_type="application/json")
        assert response.json == message
        assert response.status_code == status_code


class TestGetCourseStudents:
    """Tests for GET /courses/<course>/students/"""

    @patch("app.api.courses.Course.find_students_in_course",
           return_value=1)
    @patch("app.api.courses.dict_helper", return_value=[{"id": 1,
                                                         "first_name": "David",
                                                         "last_name": "Bo",
                                                         "group_id": "AA-11"}])
    def test_response_when_success(self,
                                   mock_dict_helper: MagicMock,
                                   mock_find_method: MagicMock,
                                   client: FlaskClient):
        """Test response when students were found.

        Args:
            mock_dict_helper: Mocked method.
            mock_find_method: Mocked method.
            client: Flask test client.
        """
        response = client.get("api/v1/courses/Art/students",
                              content_type="application/json")
        assert response.status_code == 200
        assert [{"id": 1,
                 "first_name": "David",
                 "last_name": "Bo",
                 "group_id": "AA-11"}] == response.json

    @patch("app.api.courses.Course.find_students_in_course",
           return_value=None)
    def test_response_when_no_students_found(self,
                                             mock_find_method: MagicMock,
                                             client: FlaskClient):
        """Test response when no student found

        Args:
            mock_find_method: Mocked method.
            client: Flask test client.
        """
        response = client.get("api/v1/courses/Art/students",
                              content_type="application/json")
        assert response.status_code == 404
        assert response.json == {"message": "No students were found."}


class TestGetGroups:
    """Tests for GET /groups/"""

    @patch("app.api.groups.Group.get_all_groups_not_bigger_then",
           return_value=["AA-11", "BB-22", "CC-33"])
    def test_response_when_success(self, mock_get_groups: MagicMock, client: FlaskClient):
        """Test response when groups found.

        Args:
            mock_get_groups: Mocked method.
            client: Flask test client.
        """
        response = client.get("api/v1/groups/?student_count=11",
                              content_type="application/json")
        assert response.status_code == 200
        assert response.json == ["AA-11", "BB-22", "CC-33"]

    @patch("app.api.groups.Group.get_all_groups_not_bigger_then",
           return_value=None)
    def test_response_when_no_groups_found(self, mock_get_groups: MagicMock, client: FlaskClient):
        """Test response when no groups were found.

        Args:
            mock_get_groups: Mocked method.
            client: Flask test client.
        """
        response = client.get("api/v1/groups/?student_count=1",
                              content_type="application/json")
        assert response.status_code == 404
        assert response.json == {"message": "No groups were found"}

    @pytest.mark.parametrize(
        "message, url",
        [({"message": "parameter 'student_count' should be integer."},
          "api/v1/groups/?student_count=test"),
         ({"message": "argument 'student_count' should be provided."},
          "api/v1/groups/")])
    def test_response_with_bad_parameter(self,
                                         message: dict,
                                         url: str,
                                         client: FlaskClient):
        """Test response when no groups were found.

        Args:
            message: Error message in response body.
            url: Request url.
            client: Flask test client.
        """
        response = client.get(url,
                              content_type="application/json")
        assert response.status_code == 400
        assert response.json == message
