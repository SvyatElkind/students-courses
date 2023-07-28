from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint("api", __name__)
api = Api(api_bp, prefix="/api/v1")

from . import students, groups, courses

