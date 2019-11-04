# This file defines classes for flask configuration
import os

class Config(object):
    DEBUG = True
    TESTING = True
    ENV = 'development'
    SECRET_KEY = os.urandom(16)
    DB_HOST = 'localhost'
    DB_PORT = 26257
    DB_USER = 'root'
    DEFAULT_DATABASE_URI = 'cockroachdb://{}@{}:{}/{}'.format(DB_USER, DB_HOST, DB_PORT, 'defaultdb')


class DevConfig(Config):
    SECRET_KEY = os.environ['SECRET_KEY']
    DB_HOST = os.environ['DB_HOST']
    DB_PORT = os.environ['DB_PORT']
    DB_USER = os.environ['DB_USER']
    DB_NAME = 'movr'
    DEFAULT_DATABASE_URI = 'cockroachdb://{}@{}:{}/{}'.format(DB_USER, DB_HOST, DB_PORT, 'defaultdb')
    DATABASE_URI = 'cockroachdb://{}@{}:{}/{}'.format(DB_USER, DB_HOST, DB_PORT, DB_NAME)


class ProductionConfig(DevConfig):
    ENV = 'production'
    DEBUG = False
    TESTING = False