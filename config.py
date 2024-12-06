from os import environ, path
from dotenv import load_dotenv
from datetime import timedelta

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config:
    SECRET_KEY = environ.get("SECRET_KEY")
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1.0)
    # SESSION_PERMANENT = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + path.join(basedir, 'database.sqlite3')
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False

class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = False
    TESTING = False