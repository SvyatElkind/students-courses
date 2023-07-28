"""Module for constants"""

# Configuration
TESTING = "testing"
DEVELOPMENT = "development"
DEFAULT = "default"
SWAGGER_TEMPLATE = "./api/static/docs/swagger.yaml"

# Logging
LOGGING_FORMAT = f"%(asctime)s %(levelname)s %(name)s : %(message)s"
LOGGING_FILE = {"development": "debug.log", "testing": "testing.log"}

