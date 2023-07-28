"""Module contains app configurations"""
import logging

from sqlalchemy import URL

from app.constants import LOGGING_FILE, LOGGING_FORMAT, DEVELOPMENT, TESTING, DEFAULT


url_object = URL.create(
        'postgresql',
        username='principal',
        password='password',
        host='localhost',
        database='students'
)


class Config:
    """Base configuration class.

    Contains default configuration."""
    FLASK_ENV = "development"
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Configuration for development"""
    DEBUG = True

    @staticmethod
    def init_app(config_name: str):
        """Method allows additional application configuration."""

        logging.basicConfig(filename=LOGGING_FILE[config_name],
                            level=logging.DEBUG,
                            format=LOGGING_FORMAT)

        from app.db.test_data import add_test_data_to_database
        add_test_data_to_database()


class TestingConfig(Config):
    """Configuration for testing"""
    TESTING = True

    @staticmethod
    def init_app(config_name: str):
        """Method allows additional application configuration."""

        logging.basicConfig(filename=LOGGING_FILE[config_name],
                            level=logging.DEBUG,
                            format=LOGGING_FORMAT)

        from app.db.test_data import add_test_data_to_database
        add_test_data_to_database()


config = {
    DEVELOPMENT: DevelopmentConfig,
    TESTING: TestingConfig,
    DEFAULT: DevelopmentConfig
}
