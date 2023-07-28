"""Module for Group related endpoints."""

from flask import request, abort, current_app
from flask_restful import Resource
from flasgger import swag_from

from app.api import api
from app.api.constants import STUDENT_COUNT, GROUP_VALUE_ERROR, GROUP_TYPE_ERROR, NO_GROUPS_FOUND, FIND_ALL_GROUPS
from app.db import Group


class Groups(Resource):
    """Class provides CRUD operations with group table."""
    @swag_from(FIND_ALL_GROUPS)
    def get(self) -> list:
        """Find all groups with less or equals student count.

        Returns:
            List of groups.
        """
        # Get student count.
        student_count = request.args.get(STUDENT_COUNT)
        try:
            # Get list of groups.
            groups = Group.get_all_groups_not_bigger_then(int(student_count))
        except ValueError:
            current_app.logger.info(GROUP_VALUE_ERROR)
            abort(400, description=GROUP_VALUE_ERROR)
        except TypeError:
            current_app.logger.info(GROUP_TYPE_ERROR)
            abort(400, description=GROUP_TYPE_ERROR)
        if not groups:
            current_app.logger.info(NO_GROUPS_FOUND)
            abort(404, description=NO_GROUPS_FOUND)
        return groups


api.add_resource(Groups, '/groups/')
